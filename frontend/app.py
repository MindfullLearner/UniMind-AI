import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

import requests


# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Load environment variables from root .env file
load_dotenv(PROJECT_ROOT / ".env")

# Backend configuration
API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000"
)

API_KEY = os.getenv("UNIMIND_API_KEY")
if not API_KEY:
    st.error("API key is missing. Please configure UNIMIND_API_KEY in .env")
    st.stop()

# Streamlit page configuration
st.set_page_config(
    page_title="UniMind AI",
    page_icon="🎓",
    layout="wide"
)


st.title("🎓 UniMind AI")
st.caption("Your AI-powered academic knowledge assistant")

# Sidebar configuration
st.sidebar.title("⚙️ Settings")

mode = st.sidebar.radio(
    "Choose AI Mode",
    ["RAG", "Agent"]
)

st.sidebar.divider()

st.sidebar.subheader("About UniMind AI")
st.sidebar.write(
    "Ask questions about academic documents "
    "using RAG or an AI Agent."
)

# RAG settings
if mode == "RAG":
    top_k = st.sidebar.slider(
        "Number of sources",
        min_value=1,
        max_value=10,
        value=3
    )

    strategy = st.sidebar.selectbox(
        "Chunking Strategy",
        ["fixed", "sentence"]
    )
else:
    top_k = 3
    strategy = "fixed"


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Chat input
question = st.chat_input("Ask your academic question...")

if question:
    # Display user question
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    # Prepare API request
    payload = {
        "query": question,
        "mode": mode.lower(),
        "top_k": top_k,
        "strategy": strategy
    }

    headers = {
        "X-API-Key": API_KEY
    }

    # Send request to FastAPI
    with st.chat_message("assistant"):
        with st.spinner("UniMind AI is thinking..."):

            try:
                response = requests.post(
                    f"{API_BASE_URL}/ask",
                    json=payload,
                    headers=headers,
                    timeout=120
                )

                response.raise_for_status()

                result = response.json()

                answer = result.get(
                    "answer",
                    "No answer received."
                )

                if result.get("refused"):
                    st.warning("This request was refused by the safety guardrails.")

                if result.get("citations_valid") is False:
                    st.warning("Citation validation was unsuccessful.")

                # Display RAG sources
                sources = result.get("sources", [])

                if sources:
                    with st.expander("📚 View Sources"):
                        for index, source in enumerate(sources, 1):
                            st.write(f"Source {index}")
                            st.json(source)

                # Save assistant response
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except requests.exceptions.HTTPError as error:
                if response.status_code == 401:
                    st.error("Authentication failed. Check your API key.")
                elif response.status_code == 429:
                    st.error("Rate limit reached. Please try again later.")
                else:
                    st.error(f"Backend error: {error}")

            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to backend. Is FastAPI running?")

            except requests.exceptions.Timeout:
                st.error("Request timed out. Please try again.")

            except requests.exceptions.RequestException as error:
                st.error(f"Request failed: {error}")

            except ValueError:
                st.error("Backend returned an invalid JSON response.")