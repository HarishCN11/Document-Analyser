"""
Configuration Module
Contains configuration constants and session state initialization
"""

import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Model Configuration
MODEL_NAME = "gemini-2.5-flash"
TEMPERATURE = 0.7
MAX_TOKENS = 2048

# Document Processing Configuration
PDF_CHUNK_SIZE = 500  # Words per chunk
CHUNK_OVERLAP = 50  # Words overlapped between chunks

# Session State Keys
SESSION_KEYS = {
    "uploaded_file": "uploaded_file",
    "pdf_text": "pdf_text",
    "file_hash": "file_hash",
    "chunks": "chunks",
    "mcqs": "mcqs",
    "descriptive_questions": "descriptive_questions",
    "chat_history": "chat_history",
    "api_key": "api_key",
    "user_answers": "user_answers",
    "evaluation_results": "evaluation_results",
}

# Display Configuration
MAX_DISPLAY_LENGTH = 500
PREVIEW_LENGTH = 200

# File Configuration
ALLOWED_FILE_TYPES = ["pdf", "txt", "md", "csv", "json", "docx", "pptx", "xlsx"]
MAX_FILE_SIZE_MB = 50  # Maximum file size in MB


def init_session_state():
    """Initialize all session state variables"""
    defaults = {
        SESSION_KEYS["uploaded_file"]: None,
        SESSION_KEYS["pdf_text"]: None,
        SESSION_KEYS["file_hash"]: None,
        SESSION_KEYS["chunks"]: [],
        SESSION_KEYS["mcqs"]: [],
        SESSION_KEYS["descriptive_questions"]: [],
        SESSION_KEYS["chat_history"]: [],
        SESSION_KEYS["api_key"]: GEMINI_API_KEY,
        SESSION_KEYS["user_answers"]: {},
        SESSION_KEYS["evaluation_results"]: {},
    }

    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def get_api_key() -> str:
    """
    Get the API key from session state or environment

    Returns:
        API key string
    """
    return st.session_state.get(SESSION_KEYS["api_key"], GEMINI_API_KEY)


def set_api_key(api_key: str):
    """
    Set the API key in session state

    Args:
        api_key: The API key to set
    """
    st.session_state[SESSION_KEYS["api_key"]] = api_key


def reset_session():
    """Reset all session state to defaults"""
    init_session_state()


def get_session_value(key: str, default=None):
    """
    Get a value from session state

    Args:
        key: Session key (use SESSION_KEYS constants)
        default: Default value if key not found

    Returns:
        Value from session state or default
    """
    return st.session_state.get(key, default)


def set_session_value(key: str, value):
    """
    Set a value in session state

    Args:
        key: Session key (use SESSION_KEYS constants)
        value: Value to set
    """
    st.session_state[key] = value
