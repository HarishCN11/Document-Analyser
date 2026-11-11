# Document Analyser

AI-powered document study assistant built with Streamlit and Gemini.

This project lets you upload study documents, generate descriptive and MCQ questions, evaluate answers, visualize performance, and chat with a document-aware tutor assistant.

## Features

- Multi-format document support: PDF, TXT, MD, CSV, JSON, DOCX, PPTX, XLSX
- Automatic text extraction and section detection
- AI-generated descriptive questions from document content
- AI-generated MCQ tests with answer key parsing
- Batch descriptive answer evaluation with score and feedback
- Descriptive and MCQ performance analytics charts
- Integrated chatbot that answers questions based on uploaded document chunks

## Tech Stack

- Python 3.10+
- Streamlit (UI)
- Google Gemini via `google-genai`
- PyMuPDF, python-docx, python-pptx, openpyxl (document parsing)
- pandas and matplotlib (analytics)

## Project Structure

```text
DOCUMENT-ANALYSER/
|-- app.py                       # Streamlit entry point
|-- config.py                    # App config and session state helpers
|-- requirements.txt             # Python dependencies
|-- agents/
|   |-- tutor_agent.py           # Question generation and evaluation
|   |-- chatbot_agent.py         # Document-aware chatbot logic
|-- tools/
|   |-- pdf_utils.py             # Multi-format text extraction and sectioning
|   |-- knowledge_service.py     # Ingestion pipeline controller
|   |-- vector_store.py          # Chunk storage (JSON-based placeholder)
|-- analytics/
|   |-- performance_charts.py    # Descriptive and MCQ charts
|-- ui/
|   |-- components.py            # Reusable UI blocks
|   |-- styles.py                # App styling
|   |-- floating_chatbot.py      # Chatbot UI and interactions
|-- utils/
|   |-- helpers.py               # Parsing and utility helpers
|-- data/
|   |-- knowledge_base/
|       |-- vectors/
|           |-- chunks.json      # Stored chunks used by chatbot
```

## Prerequisites

1. Python 3.10 or newer
2. A Gemini API key
3. pip (comes with most Python installations)

## Setup

### 1. Clone and enter project

```bash
git clone <your-repo-url>
cd DOCUMENT-ANALYSER
```

### 2. Create and activate virtual environment

Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Windows (CMD):

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

## Run the App

```bash
streamlit run app.py
```

After running, Streamlit will print a local URL (usually `http://localhost:8501`). Open it in your browser.

## How to Use

1. Upload a supported document.
2. Wait for ingestion and section extraction.
3. Click `Extract & Generate Questions` for descriptive questions.
4. Write answers and click `Analyze My Answers` to get scores and feedback.
5. Open the `MCQ Test` tab, generate MCQs, submit answers, and review analytics.
6. Use the chatbot at the bottom to ask document-specific questions.

## Notes

- Chatbot responses are document-grounded only after a document is uploaded.
- Stored chunks are saved in `data/knowledge_base/vectors/chunks.json`.
- Embedding storage is currently a JSON placeholder pipeline, not a vector database.
- If API rate limiting occurs, the app may partially process question generation.

## Troubleshooting

- Missing API key error:
	- Ensure `.env` exists and `GEMINI_API_KEY` is set correctly.
- Streamlit command not found:
	- Activate your virtual environment first, then reinstall requirements.
- No questions generated:
	- Verify uploaded file contains extractable text (not image-only scans).
- MCQ parsing incomplete:
	- Re-generate MCQs if model output does not follow expected format.

## Future Improvements

- Replace placeholder chunk storage with a true vector database
- Add OCR support for scanned PDFs
- Add unit and integration tests
- Add Docker-based deployment workflow
"# Document-Analyser" 
