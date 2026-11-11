# UniMind AI — System Architecture

## 1. Project Overview

UniMind AI is an AI-powered academic knowledge assistant designed for university students. It helps students interact with academic documents and research materials through Retrieval-Augmented Generation (RAG) and an AI Agent.

The application supports three modes:
- **Auto:** NexusAgent decides whether to answer directly or use an available tool.
- **RAG:** Retrieves information from the academic knowledge base.
- **Agent:** Uses NexusAgent and its available tools.

## 2. Technology Stack

| Component | Technology |
|---|---|
| Frontend | Streamlit |
| Backend | FastAPI |
| HTTP Communication | Requests |
| AI Model | Google Gemini |
| Document Search | ChromaDB |
| Embeddings | Sentence Transformers |
| RAG Pipeline | DocuSense |
| AI Agent | LangGraph |
| Authentication | API Key |
| Testing | Pytest |
| Logging | Python Logging |
| CI | GitHub Actions |

## 3. System Architecture

The application follows a frontend-backend architecture.

**Request Flow:**

Streamlit Frontend → HTTP Request → FastAPI Backend → API-Key Authentication → Rate Limiting → Input Guardrails → Mode Routing → RAG or Agent → Response → Streamlit Frontend.

The frontend communicates with the backend exclusively through HTTP APIs. It does not directly import or execute RAG or Agent functionality.

## 4. Backend API Endpoints

### GET /health

Checks whether the backend service is running.

### POST /ask

Accepts academic questions and routes them according to the selected mode.

Request fields:
- `query`: User's question.
- `mode`: `auto`, `rag`, or `agent`.
- `top_k`: Number of retrieved document results.
- `strategy`: `fixed` or `sentence`.

Authentication:
- Requires the `X-API-Key` request header.
- API key is stored in an environment variable named `UNIMIND_API_KEY`.

Response includes:
- `mode`
- `answer`
- `sources`
- `refused`
- `citations_valid`

## 5. RAG Architecture

The RAG mode uses the DocuSense pipeline.

1. Receives the user's question.
2. Searches relevant document chunks in ChromaDB.
3. Retrieves the most relevant context.
4. Generates an answer using the available context.
5. Validates generated citation labels.
6. Returns the answer and source information.

The knowledge base includes academic documents such as:
- Google AI documentation.
- NIST Generative AI documentation.
- Stanford Foundation Models report.

Two retrieval strategies are supported:
- Fixed-size chunking.
- Sentence-based chunking.

The system can refuse questions when relevant document context is insufficient.

## 6. Agent Architecture

The Agent implementation uses NexusAgent, built with LangGraph.

Available tools:
- **Calculator:** Performs mathematical calculations.
- **RAG Search:** Retrieves relevant academic document information.
- **DateTime:** Provides the current date and time.

The agent can decide whether a question requires a tool or can be answered directly. It uses a bounded execution process with a maximum iteration limit.

## 7. Authentication and Rate Limiting

The `/ask` endpoint requires a valid API key.

Rate limiting:
- Maximum 10 requests per API key.
- 60-second time window.
- Returns HTTP 429 when the limit is exceeded.
- Provides a Retry-After header when applicable.

The current rate limiter uses in-memory storage. Its counters reset when the backend restarts and are not shared across multiple worker processes.

## 8. Input Guardrails

The backend scans incoming queries before AI processing.

Guardrail functionality includes:
- Detecting common prompt-injection patterns.
- Blocking suspicious requests with HTTP 400.
- Detecting and redacting supported email addresses and Pakistani mobile phone numbers before AI processing.

These checks provide basic input protection but do not guarantee protection against every prompt-injection technique.

## 9. Structured Logging

The backend records request information in `logs/app.log`.

Log entries use structured JSON and include:
- Timestamp.
- Log level.
- Logger name.
- Message.
- HTTP method.
- Request path.
- Response status code.
- Response time in milliseconds.

API keys are not included in request logs.

## 10. Frontend Architecture

The Streamlit frontend provides:
- Academic question input.
- Auto, RAG, and Agent mode selection.
- RAG retrieval settings.
- Chat history.
- AI answer display.
- RAG source display.
- Error handling.

The frontend sends HTTP requests to the FastAPI backend using the Requests library.

## 11. Project Execution

### Start the Backend

From the project root:

```powershell
uvicorn backend.main:app --reload
```

Backend address: `http://127.0.0.1:8000`

API documentation: `http://127.0.0.1:8000/docs`

### Start the Frontend

Open a second terminal:

```powershell
streamlit run frontend/app.py
```

Frontend address: `http://localhost:8501`

## 12. Testing and CI

Automated tests are executed using:

```powershell
python -m pytest -v
```

The test suite covers request logging, rate limiting, invalid API keys, and semantic search functionality.

Latest recorded result: **6 tests passed**.

GitHub Actions CI is configured to:
1. Check out the repository.
2. Set up Python 3.13.
3. Install project dependencies.
4. Run the Pytest suite on pushes and pull requests targeting `main`.

An actual successful GitHub Actions run should be verified separately.

## 13. Security Considerations

- API keys are stored in environment variables.
- `.env` files are excluded from Git.
- API keys are not written to request logs.
- The `/ask` endpoint requires authentication.
- Rate limiting helps control excessive requests.
- Input guardrails detect common prompt-injection patterns and redact supported PII.

## 14. Current MVP Limitations

- Rate limiting is in-memory and resets after backend restart.
- The application uses a configured academic document collection.
- Persistent user accounts and multi-user document management are not included.
- Input guardrails cannot detect every possible prompt-injection attack.
- Agent and RAG responses depend on external model availability and API quotas.