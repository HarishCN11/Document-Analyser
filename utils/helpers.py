"""
Helper Utilities Module
Contains utility functions for the PDF Analyzer app
"""

import hashlib
import re
from typing import List, Dict, Any


def get_file_hash(file_content: bytes) -> str:
    """
    Generate a unique hash for a file

    Args:
        file_content: Bytes content of the file

    Returns:
        MD5 hash of the file content
    """
    return hashlib.md5(file_content).hexdigest()


def parse_mcqs(mcq_text: str) -> List[Dict[str, Any]]:
    """
    Parse MCQ questions from generated text

    Args:
        mcq_text: Raw MCQ text from AI

    Returns:
        List of parsed MCQ dictionaries with options as dict
    """
    mcqs = []

    # Split by question pattern
    questions = [q.strip() for q in mcq_text.split("\n\n") if q.strip()]

    for question in questions:
        lines = question.split("\n")
        if len(lines) >= 5:
            mcq_obj = {
                "question": lines[0].replace("**", ""),
                "options": {},
                "answer": None,
                "explanation": "",
            }

            for line in lines[1:]:
                if line.startswith("A)"):
                    mcq_obj["options"]["A"] = line[3:].strip()
                elif line.startswith("B)"):
                    mcq_obj["options"]["B"] = line[3:].strip()
                elif line.startswith("C)"):
                    mcq_obj["options"]["C"] = line[3:].strip()
                elif line.startswith("D)"):
                    mcq_obj["options"]["D"] = line[3:].strip()
                elif "Correct" in line or "Answer" in line:
                    # Extract correct answer letter more precisely
                    # Look for patterns like "Answer: B" or "Correct: B" or just "B"
                    match = re.search(r"\b([A-D])\b", line)
                    if match:
                        mcq_obj["answer"] = match.group(1)
                elif "Explanation" in line or "Reason" in line:
                    mcq_obj["explanation"] = line.split(":", 1)[-1].strip()

            if mcq_obj["options"] and mcq_obj["answer"]:
                mcqs.append(mcq_obj)

    return mcqs


def parse_descriptive_questions(questions_text: str) -> List[Dict[str, str]]:
    """
    Parse descriptive questions from generated text

    Args:
        questions_text: Raw questions text from AI

    Returns:
        List of parsed question dictionaries
    """
    questions = []

    # Split by numbered questions
    items = [q.strip() for q in questions_text.split("\n") if q.strip()]

    for item in items:
        if item and (item[0].isdigit() or item.startswith("-")):
            # Remove numbering
            question = item.lstrip("0123456789.-) ")
            if question:
                questions.append({"question": question, "answer": ""})

    return questions


def format_evaluation_result(result: str) -> Dict[str, Any]:
    """
    Parse evaluation result from AI

    Args:
        result: Raw evaluation text from AI

    Returns:
        Structured evaluation dictionary
    """
    evaluation = {"score": 0, "feedback": "", "strengths": [], "improvements": []}

    lines = result.split("\n")

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if (
            "score" in line.lower()
            or "marks" in line.lower()
            or "points" in line.lower()
        ):
            # Try to extract numeric score
            import re

            numbers = re.findall(r"\d+", line)
            if numbers:
                evaluation["score"] = int(numbers[0])

        elif line.startswith("Strengths"):
            evaluation["strengths"].append(line.replace("Strengths:", "").strip())

        elif line.startswith("Improvements"):
            evaluation["improvements"].append(line.replace("Improvements:", "").strip())

        elif line.startswith("Feedback") or line.startswith("Comment"):
            evaluation["feedback"] = line.split(":", 1)[-1].strip()

    return evaluation


def validate_pdf_text(text: str, min_length: int = 100) -> bool:
    """
    Validate if extracted PDF text is meaningful

    Args:
        text: Extracted text from PDF
        min_length: Minimum text length to consider valid

    Returns:
        True if text is valid, False otherwise
    """
    if not text or len(text.strip()) < min_length:
        return False

    # Check if text has meaningful content (not just numbers/symbols)
    alpha_count = sum(1 for c in text if c.isalpha())
    if alpha_count < len(text) * 0.3:  # At least 30% alphabetic characters
        return False

    return True


def truncate_text(text: str, max_length: int = 500) -> str:
    """
    Truncate text to a maximum length

    Args:
        text: Text to truncate
        max_length: Maximum allowed length

    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text

    return text[:max_length].rsplit(" ", 1)[0] + "..."


def format_chat_message(role: str, content: str) -> Dict[str, str]:
    """
    Format a chat message

    Args:
        role: 'user' or 'assistant'
        content: Message content

    Returns:
        Formatted message dictionary
    """
    return {"role": role, "content": content}
