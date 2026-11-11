"""
UI Components Module
Contains reusable UI components for the Streamlit app
"""

import streamlit as st
from config import ALLOWED_FILE_TYPES


def render_header():
    """Render the main header of the application"""
    st.markdown(
        """
        <div class="header-main">
            <h1>📊 Document Evaluation Tutor</h1>
            <p>Intelligent document analysis with AI-powered question generation and evaluation</p>
        </div>
    """,
        unsafe_allow_html=True,
    )


def render_features():
    """Render feature boxes showcasing app capabilities"""
    st.markdown("### Key Features")
    st.markdown(
        """
        <div class="feature-box">
            <div class="feature-item">
                <h3>📄 Document Upload</h3>
                <p>Upload and analyze your study documents quickly</p>
            </div>
            <div class="feature-item">
                <h3>❓ Question Generation</h3>
                <p>Automatic MCQ and descriptive question creation</p>
            </div>
            <div class="feature-item">
                <h3>🤖 AI Chat</h3>
                <p>Chat with AI about your document content</p>
            </div>
            <div class="feature-item">
                <h3>📈 Evaluation</h3>
                <p>Instant feedback and performance analytics</p>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )


def render_upload_section():
    """Render the document upload interface"""
    st.markdown("### Upload Your Document")

    col1, col2 = st.columns([2, 1])

    with col1:
        uploaded_file = st.file_uploader(
            "Choose a document",
            type=ALLOWED_FILE_TYPES,
            key="document_uploader",
            help="Supported formats: PDF, TXT, MD, CSV, JSON, DOCX, PPTX, XLSX",
        )

    with col2:
        st.write("")  # Spacing

    return uploaded_file


def render_success_message(filename):
    """Render success message after file upload"""
    st.markdown(
        f"""
        <div class="card card-success">
            <span class="badge badge-success">✓ Success</span>
            <p><strong>{filename}</strong> uploaded successfully!</p>
        </div>
    """,
        unsafe_allow_html=True,
    )


def render_loading_state(message="Processing your document..."):
    """Render loading state with spinner"""
    with st.spinner(message):
        return True


def render_error_message(error_text):
    """Render error message"""
    st.markdown(
        f"""
        <div class="card card-warning">
            <span class="badge badge-warning">⚠ Error</span>
            <p>{error_text}</p>
        </div>
    """,
        unsafe_allow_html=True,
    )


def render_info_badge(text, badge_type="info"):
    """Render an info badge"""
    badge_class = f"badge badge-{badge_type}"
    st.markdown(f'<span class="{badge_class}">{text}</span>', unsafe_allow_html=True)


def render_stats_display(total_chunks, total_questions, total_mcq):
    """Render document statistics"""
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Document Chunks", total_chunks)

    with col2:
        st.metric("Questions Generated", total_questions)

    with col3:
        st.metric("MCQ Questions", total_mcq)
