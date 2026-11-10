# UniMind AI — System Architecture

## 1. Project Overview

UniMind AI is an AI-powered academic knowledge assistant designed for university students. It helps students interact with academic documents and research materials through Retrieval-Augmented Generation (RAG) and an AI Agent.

## 2. Technology Stack

| Component | Technology |
|---|---|
| Frontend | Streamlit |
| Backend | FastAPI |
| HTTP Communication | Requests |
| AI Model | Google Gemini |
| Document Search | ChromaDB |
| RAG Pipeline | DocuSense |
| AI Agent | LangGraph |
| Authentication | API Key |
| Testing | Pytest |
| Logging | Python Logging |

## 3. System Architecture

The application follows a frontend-backend architecture.

**Request Flow:**

Streamlit Frontend → HTTP Request → FastAPI Backend → Authentication → Rate Limiting → Mode Routing → RAG or Agent → Response → Streamlit Frontend.

The frontend communicates with the backend exclusively through HTTP APIs. It does not directly import or execute RAG or Agent functionality.

## 4. Backend API Endpoints

### GET /health

Checks whether the backend service is running.

### POST /ask

Accepts academic questions and routes them according to the selected mode.

Request fields:
- `query`: User's question.
- `mode`: `rag` or `agent`.
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
5. Returns the answer and source information.

Two retrieval strategies are supported:
- Fixed-size chunking.
- Sentence-based chunking.

## 6. Agent Architecture

The Agent mode uses the NexusAgent implementation built with LangGraph.

Available tools:
- Calculator: Performs mathematical calculations.
- RAG Search: Retrieves relevant academic document information.
- DateTime: Provides current date and time.

The agent uses a bounded execution process with a maximum iteration limit.

## 7. Authentication and Rate Limiting

The `/ask` endpoint requires a valid API key.

Rate limiting:
- Maximum 10 requests per API key.
- 60-second sliding time window.
- Returns HTTP 429 when the limit is exceeded.
- Returns a Retry-After header when applicable.

The current rate limiter uses in-memory storage. Its counters reset when the backend restarts and are not shared across multiple worker processes.

## 8. Structured Logging

The backend records request information in `logs/app.log`.

Each log entry is structured as JSON and includes:
- Timestamp.
- Log level.
- Logger name.
- Message.
- HTTP method.
- Request path.
- Response status code.
- Response time in milliseconds.

API keys are not included in request logs.

## 9. Frontend Architecture

The Streamlit frontend provides:
- Academic question input.
- RAG and Agent mode selection.
- RAG retrieval settings.
- Chat history.
- AI answer display.
- RAG source display.
- Error handling.

The frontend sends HTTP requests to the FastAPI backend using the Requests library.

## 10. Project Execution

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

## 11. Testing

Automated tests are executed using:

```powershell
python -m pytest -v
```

The current test suite covers:
- Request logging.
- Unauthorized request logging.
- Rate limiting.
- Invalid API key rejection.

Latest recorded result: 6 tests passed.

## 12. Security Considerations

- API keys are stored in environment variables.
- `.env` files are excluded from Git.
- API keys are not written to request logs.
- The `/ask` endpoint requires authentication.
- Rate limiting helps control excessive requests.

## 13. Current MVP Limitations

- Rate limiting is in-memory and resets after backend restart.
- The application currently uses a configured academic document collection.
- Persistent user accounts and multi-user document management are not included in this MVP.