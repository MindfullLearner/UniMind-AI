# UniMind AI — Deployment Guide

## 1. Overview

UniMind AI is a full-stack academic knowledge assistant built using FastAPI, Streamlit, Gemini, RAG, and LangGraph.

The application uses two separate Render web services:

- **Backend:** FastAPI API service.
- **Frontend:** Streamlit user interface.

Both services use the same GitHub repository and Dockerfile.

## 2. Requirements

- GitHub repository
- Render account
- Gemini API key
- UniMind API key
- Dockerfile
- `.env.example`

Docker Desktop is optional for cloud deployment because Render can build the Docker image.

## 3. Docker Configuration

The production Dockerfile:

- Uses Python 3.13 slim.
- Installs dependencies from `requirements.txt`.
- Copies the application into the image.
- Runs the application as a non-root user.
- Starts FastAPI by default.

The `.dockerignore` file excludes environment secrets, virtual environments, Git files, and temporary files from the Docker build context.

## 4. Environment Variables

Configure environment variables in the Render dashboard. Do not commit real secrets to GitHub.

| Variable | Backend | Frontend |
|---|---|---|
| GEMINI_API_KEY | Required | Not required |
| GEMINI_MODEL | Required | Not required |
| UNIMIND_API_KEY | Required | Required |
| API_BASE_URL | Not required | Required |

For the frontend, `API_BASE_URL` must contain the public URL of the deployed backend.

## 5. Deploy the Backend on Render

1. Create a new Web Service on Render.
2. Connect the UniMind AI GitHub repository.
3. Select Docker as the runtime.
4. Use the repository's root directory.
5. Keep the Dockerfile path as `./Dockerfile`.
6. Configure the required backend environment variables.
7. Keep the Dockerfile's default start command.
8. Set the health check path to `/health`.
9. Deploy the service.

After deployment, copy the backend's public URL.

Example: `https://your-backend-name.onrender.com`

## 6. Deploy the Frontend on Render

1. Create another Web Service using the same repository.
2. Select Docker as the runtime.
3. Use the same Dockerfile.
4. Override the Docker start command with:

   `streamlit run frontend/app.py --server.address 0.0.0.0 --server.port $PORT`

5. Configure `UNIMIND_API_KEY`.
6. Configure `API_BASE_URL` with the deployed backend URL.
7. Deploy the frontend.

The frontend communicates with FastAPI using HTTP requests.

## 7. API Endpoints

### Health Check

`GET /health`

Returns the backend health status.

### Ask Question

`POST /ask`

Requires the `X-API-Key` request header.

Example request:

```json
{
  "query": "What is generative AI?",
  "mode": "rag",
  "top_k": 3,
  "strategy": "fixed"
}
```

Supported modes:

- `rag`
- `agent`

## 8. Authentication and Rate Limiting

- API-key authentication protects the `/ask` endpoint.
- Invalid or missing API keys receive HTTP 401.
- Each API key is limited to 10 requests per 60 seconds.
- Requests exceeding the limit receive HTTP 429.
- API keys are not written to request logs.

The current rate limiter uses in-memory storage and is not shared between multiple backend workers or instances.

## 9. Logging

The backend writes structured JSON request logs to:

`logs/app.log`

Logs include:

- Timestamp
- Log level
- HTTP method
- Request path
- Response status
- Response time

Render's container filesystem is ephemeral, so local log files may not survive restarts or redeployments. Use Render logs for persistent operational visibility unless persistent storage or external logging is configured.

## 10. GitHub Actions CI

The workflow is located at:

`.github/workflows/ci.yml`

It automatically:

1. Checks out the repository.
2. Sets up Python 3.13.
3. Installs project dependencies.
4. Runs pytest.

The workflow runs on pushes and pull requests targeting `main`.

## 11. Deployment Verification

After deployment:

- Open the backend `/health` endpoint.
- Open the frontend public URL.
- Submit a question using RAG mode.
- Submit a question using Agent mode.
- Verify authentication and error handling.
- Check the Render service logs.

## 12. Knowledge Base

The prebuilt ChromaDB database and academic PDF documents are included in the Docker image.

Changes to the knowledge base require rebuilding and redeploying the image. The container's filesystem is ephemeral, so changes made inside a running container should not be treated as permanent.

## 13. Security Notes

- Never commit `.env` files.
- Configure real secrets through Render environment variables.
- Do not expose Gemini API keys in frontend code.
- Keep API authentication enabled.
- Avoid logging API keys or other sensitive credentials.