# UniMind AI — Evaluation Report

## 1. Overview

This report documents the testing and evaluation of UniMind AI, an academic knowledge assistant built using RAG, an AI agent, FastAPI, and Streamlit.

## 2. Functional Testing

| Component | Evaluation | Result |
|---|---|---|
| Backend API | Application import and startup check | Passed |
| Health endpoint | Backend health check | Passed |
| API authentication | Invalid API key rejection | Passed |
| Rate limiting | Requests beyond the configured limit | Passed |
| Rate limit recovery | Requests allowed after the time window | Passed |
| Input guardrails | Suspicious prompt detection | Passed |
| RAG retrieval | Relevant academic document chunks retrieved | Passed |
| Frontend | Auto, RAG, and Agent mode selection | Verified |

## 3. Automated Test Results

Command:

```bash
python -m pytest tests/ -v
```

Latest recorded result:

- Total tests: 6
- Passed: 6
- Failed: 0
- Execution time: 79.42 seconds

## 4. RAG Evaluation

A sample query was submitted:

**Question:** What are foundation models?

The system retrieved three relevant chunks from `stanford_foundation_models.pdf`.

The generated response discussed:

- The one-model–many-models nature of foundation models.
- Expressivity of computational models.
- Scalability.

The response included references to retrieved sources using citation labels.

**Observation:** Retrieval returned relevant material, but the retrieved chunks did not provide a complete introductory definition. Improving chunk selection and retrieval quality remains a future improvement.

## 5. Guardrails Evaluation

Input guardrails were tested with normal and suspicious inputs.

Observed results:

- Normal questions were accepted.
- Prompt-injection patterns were detected.
- Suspicious requests submitted through the frontend were rejected with HTTP 400.
- Supported personal information patterns are redacted before model processing.

## 6. Performance Observations

During one RAG request, the backend successfully received a response from Gemini, but the request took approximately 145 seconds.

The frontend timeout was subsequently increased from 120 to 240 seconds.

External model response times and free-tier API quotas can affect application performance.

## 7. Evaluation Summary

The latest automated test run passed all six tests. Authentication, rate limiting, input guardrails, document retrieval, and frontend mode selection were also exercised.

Further evaluation is needed for answer quality, citation accuracy across different questions, performance under concurrent requests, and production deployment reliability.

## 8. Future Improvements

- Improve document chunking and retrieval quality.
- Expand automated evaluation datasets.
- Test citation accuracy across a wider range of questions.
- Improve response latency.
- Add more comprehensive security testing.
- Evaluate performance under concurrent user requests.