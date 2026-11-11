# UniMind AI

**An AI-powered academic knowledge assistant for university students.**

UniMind AI helps students understand academic materials and research papers through Retrieval-Augmented Generation (RAG), AI agents, and an interactive chat interface.

## Features

- **Auto Mode:** Automatically uses the AI agent to decide whether tools are needed.
- **RAG Mode:** Answers questions using indexed academic documents.
- **Agent Mode:** Uses an AI agent with calculator, document search, and date/time tools.
- **Document Grounding:** Retrieves relevant document chunks and provides source references.
- **Input Guardrails:** Detects suspicious prompt-injection patterns and redacts supported personal information.
- **API Authentication:** Protects the `/ask` endpoint using API-key authentication.
- **Rate Limiting:** Limits requests per API key.
- **Structured Logging:** Records API request information in JSON format.
- **Interactive Frontend:** Provides a Streamlit chat interface connected to the backend through HTTP.

## Technology Stack

- Python 3.13
- FastAPI
- Streamlit
- Google Gemini API
- LangGraph and LangChain
- ChromaDB
- Sentence Transformers
- Pytest

## Project Structure

```text
UniMind-AI/
├── backend/
│   ├── docusense/
│   ├── nexus_agent/
│   ├── guardrails.py
│   ├── main.py
│   └── models.py
├── frontend/
│   └── app.py
├── tests/
├── logs/
├── .env.example
├── .gitignore
├──