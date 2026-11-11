
import os
import logging
import secrets
from pathlib import Path
import time
from backend.logging_config import configure_logging

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import APIKeyHeader
import hashlib
import threading

from collections import defaultdict, deque
from math import ceil
from backend.guardrails import scan_text

# Load environment variables from project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

from backend.models import AskRequest, AskResponse




RATE_LIMIT = 10
WINDOW_SECONDS = 60

request_timestamps = defaultdict(deque)
rate_limit_lock = threading.Lock()

configure_logging()
logger = logging.getLogger(__name__)
app = FastAPI(
    title="UniMind AI",
    description="Academic Knowledge Assistant API",
    version="1.0.0"
)

api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False
)


@app.middleware("http")
async def log_requests(request, call_next):
    start_time = time.perf_counter()
    status_code = 500

    try:
        response = await call_next(request)
        status_code = response.status_code
        return response

    finally:
        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2
        )

        logging.getLogger("unimind.requests").info(
            "HTTP request completed",
            extra={
                "request_data": {
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": status_code,
                    "response_time_ms": duration_ms,
                }
            }
        )
    
def verify_api_key(api_key: str | None = Depends(api_key_header)):
    expected_key = os.getenv("UNIMIND_API_KEY")

    # Check whether the server has an API key configured.
    if not expected_key:
        logger.error("UNIMIND_API_KEY is not configured.")
        raise HTTPException(
            status_code=500,
            detail="API authentication is not configured."
        )

    # Authenticate the request first.
    if not api_key or not secrets.compare_digest(api_key, expected_key):
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key."
        )

    # Create a hashed identifier instead of storing the actual API key.
    key_id = hashlib.sha256(api_key.encode()).hexdigest()

    now = time.monotonic()

    with rate_limit_lock:
        timestamps = request_timestamps[key_id]

        # Remove requests older than the 60-second window.
        while timestamps and now - timestamps[0] >= WINDOW_SECONDS:
            timestamps.popleft()

        # Reject requests if the limit has been reached.
        if len(timestamps) >= RATE_LIMIT:
            retry_after = max(
                1,
                ceil(WINDOW_SECONDS - (now - timestamps[0]))
            )

            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Try again later.",
                headers={"Retry-After": str(retry_after)}
            )

        # Record this authenticated request.
        timestamps.append(now)

    return True



@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": "UniMind AI"
    }




@app.post(
    "/ask",
    response_model=AskResponse,
    dependencies=[Depends(verify_api_key)]
)
def ask_question(request: AskRequest):
    try:
        # 1. Scan input for prompt injection and PII
        guardrail_result = scan_text(request.query)

        # 2. Reject suspicious prompt-injection attempts
        if guardrail_result["is_suspicious"]:
            logger.warning(
                "Prompt injection detected",
                extra={
                    "request_data": {
                        "event": "prompt_injection_blocked",
                        "matched_patterns": guardrail_result[
                            "matched_patterns"
                        ]
                    }
                }
            )

            raise HTTPException(
                status_code=400,
                detail="Your request was rejected by input safety guardrails."
            )

        # 3. Use redacted query for AI processing
        safe_query = guardrail_result["redacted_text"]

        if guardrail_result["has_pii"]:
            logger.info("PII detected and redacted from user query")

        # 4. Process RAG requests
        if request.mode in ("agent", "auto"):
            from backend.docusense.src.rag import answer_question

            result = answer_question(
                query=safe_query,
                top_k=request.top_k,
                strategy=request.strategy
            )

            citation_validation = result.get("citation_validation")

            return AskResponse(
                mode="rag",
                answer=result.get("answer", ""),
                sources=result.get("sources", []),
                refused=result.get("refused", False),
                citations_valid=(
                    citation_validation.get("valid")
                    if citation_validation is not None
                    else None
                )
            )

        # 5. Process Agent requests
        if request.mode == "agent":
            from backend.nexus_agent.agent import run_agent

            answer = run_agent(safe_query)

            return AskResponse(
                mode=request.mode,
                answer=answer
            )

        raise HTTPException(
            status_code=400,
            detail="Unsupported mode."
        )

    except HTTPException:
        raise

    except Exception:
        logger.exception("Error while processing /ask request")

        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while processing your request."
        )
