import csv
import io
import json
import re
from typing import Dict, List

import fitz  # PyMuPDF
from docx import Document
from openpyxl import load_workbook
from pptx import Presentation

EXCLUDED_SECTIONS = [
    "INTRODUCTION",
    "ABSTRACT",
    "SUMMARY",
    "CONCLUSION",
    "REFERENCES",
    "BIBLIOGRAPHY",
    "ACKNOWLEDGEMENT",
    "ACKNOWLEDGMENTS",
    "PREFACE",
]


def _get_extension(uploaded_file) -> str:
    name = getattr(uploaded_file, "name", "")
    if "." not in name:
        return ""
    return name.rsplit(".", 1)[-1].lower()


def _read_file_bytes(uploaded_file) -> bytes:
    uploaded_file.seek(0)
    data = uploaded_file.read()
    uploaded_file.seek(0)
    return data


def _extract_pdf_text_from_bytes(file_bytes: bytes) -> str:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    try:
        full_text = []
        for page_num in range(len(doc)):
            text = doc.load_page(page_num).get_text()
            if text and text.strip():
                full_text.append(text)
        return "\n".join(full_text)
    finally:
        doc.close()


def _extract_docx_text(file_bytes: bytes) -> str:
    document = Document(io.BytesIO(file_bytes))
    lines = [p.text.strip() for p in document.paragraphs if p.text and p.text.strip()]
    return "\n".join(lines)


def _extract_pptx_text(file_bytes: bytes) -> str:
    presentation = Presentation(io.BytesIO(file_bytes))
    lines = []
    for slide in presentation.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text") and shape.text and shape.text.strip():
                lines.append(shape.text.strip())
    return "\n".join(lines)


def _extract_xlsx_text(file_bytes: bytes) -> str:
    workbook = load_workbook(io.BytesIO(file_bytes), data_only=True, read_only=True)
    lines = []
    try:
        for sheet in workbook.worksheets:
            lines.append(f"Sheet: {sheet.title}")
            for row in sheet.iter_rows(values_only=True):
                values = [
                    str(v).strip() for v in row if v is not None and str(v).strip()
                ]
                if values:
                    lines.append(" | ".join(values))
    finally:
        workbook.close()
    return "\n".join(lines)


def _extract_text_like(file_bytes: bytes, ext: str) -> str:
    if ext == "json":
        try:
            parsed = json.loads(file_bytes.decode("utf-8", errors="replace"))
            return json.dumps(parsed, ensure_ascii=False, indent=2)
        except Exception:
            return file_bytes.decode("utf-8", errors="replace")
    if ext == "csv":
        decoded = file_bytes.decode("utf-8", errors="replace")
        reader = csv.reader(io.StringIO(decoded))
        rows = [
            " | ".join(cell.strip() for cell in row if cell.strip()) for row in reader
        ]
        return "\n".join(row for row in rows if row)

    for encoding in ("utf-8", "utf-16", "latin-1"):
        try:
            return file_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue
    return file_bytes.decode("utf-8", errors="replace")


def extract_document_text(uploaded_file) -> str:
    file_bytes = _read_file_bytes(uploaded_file)
    if not file_bytes:
        return ""

    ext = _get_extension(uploaded_file)

    if ext == "pdf":
        return _extract_pdf_text_from_bytes(file_bytes)
    if ext == "docx":
        try:
            return _extract_docx_text(file_bytes)
        except Exception:
            return _extract_text_like(file_bytes, ext)
    if ext == "pptx":
        try:
            return _extract_pptx_text(file_bytes)
        except Exception:
            return _extract_text_like(file_bytes, ext)
    if ext == "xlsx":
        try:
            return _extract_xlsx_text(file_bytes)
        except Exception:
            return _extract_text_like(file_bytes, ext)
    if ext in {"txt", "md", "csv", "json"}:
        return _extract_text_like(file_bytes, ext)

    return _extract_text_like(file_bytes, ext)


def _build_sections_from_text(text: str) -> Dict[str, List[str]]:
    sections: Dict[str, List[str]] = {}
    current_section = "General"

    for raw_line in text.splitlines():
        clean_line = raw_line.strip()
        if not clean_line:
            continue

        upper_line = clean_line.upper()

        if re.match(r"(CHAPTER|UNIT|MODULE|SECTION)\s+\d+", upper_line):
            current_section = clean_line
            sections.setdefault(current_section, [])
            continue

        if any(keyword in upper_line for keyword in EXCLUDED_SECTIONS):
            current_section = "__EXCLUDED__"
            continue

        if current_section != "__EXCLUDED__":
            sections.setdefault(current_section, []).append(clean_line)

    if not sections:
        return {"General": [line.strip() for line in text.splitlines() if line.strip()]}

    return {k: v for k, v in sections.items() if v}


def extract_document_sections(uploaded_file) -> Dict[str, List[str]]:
    text = extract_document_text(uploaded_file)
    if not text or not text.strip():
        return {}
    return _build_sections_from_text(text)


def extract_pdf_sections(pdf_file) -> Dict[str, List[str]]:
    return extract_document_sections(pdf_file)


def extract_pdf_text(pdf_file) -> str:
    return extract_document_text(pdf_file)
