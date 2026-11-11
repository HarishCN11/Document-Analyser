from google import genai
import random
from tools.knowledge_service import KnowledgeService


class TutorAgent:
    def __init__(self, api_key):
        self.api_key = api_key
        self.knowledge = KnowledgeService()
        self.model = "gemini-2.5-flash"
        self.client = genai.Client(api_key=self.api_key)

    # -------------------------------
    # Estimate MCQ count dynamically
    # -------------------------------
    def estimate_mcq_count(self, text):
        word_count = len(text.split())

        if word_count < 800:
            return 5
        elif word_count < 2000:
            return 10
        elif word_count < 4000:
            return 15
        else:
            return 25

    # -------------------------------
    # Generate MCQs
    # -------------------------------
    def generate_mcqs(self, pdf_text):
        num_questions = self.estimate_mcq_count(pdf_text)

        prompt = f"""
        From the following document, generate {num_questions} multiple-choice questions (MCQs)
        to test student understanding.

        Rules:
        - Each question must have 4 options (A, B, C, D)
        - Clearly mention the correct answer using format "Answer: X" where X is one letter (A, B, C, or D)
        - Use ONLY the document content
        - Keep questions meaningful and exam-oriented

        STRICT FORMAT (follow exactly):

        Q1. Question text
        A) option
        B) option
        C) option
        D) option
        Answer: B

        Q2. Question text
        A) option
        B) option
        C) option
        D) option
        Answer: C

        Document:
        {pdf_text}
        """

        response = self.client.models.generate_content(
            model=self.model, contents=prompt
        )

        return response.text

    # ---------------------------------------------------------
    # Hybrid Extraction and Generation for Descriptive
    # ---------------------------------------------------------
    def get_comprehensive_questions(self, section_text):
        prompt = f"""
        Analyze the following text.
        
        1. If there are any pre-existing exam or review questions written in the text, extract them exactly.
        2. If no questions are found, generate 3-5 high-quality descriptive questions that test deep understanding.
        
        Return ONLY the questions, one per line.

        Content:
        {section_text}
        """

        response = self.client.models.generate_content(
            model=self.model, contents=prompt
        )

        questions = [
            q.strip()
            for q in response.text.split("\n")
            if q.strip() and len(q.strip()) > 10
        ]
        return questions

    # -------------------------------
    # Proportional question selection
    # -------------------------------
    def select_questions_proportionally(self, section_questions, max_questions=20):
        all_questions_count = sum(len(qs) for qs in section_questions.values())

        if all_questions_count <= 10:
            return [q for qs in section_questions.values() for q in qs]

        selected = []
        for section, questions in section_questions.items():
            proportion = len(questions) / all_questions_count
            count = max(1, round(proportion * max_questions))
            sampled = random.sample(questions, min(count, len(questions)))
            selected.extend(sampled)

        return selected[:max_questions]

    # ---------------------------------------------------------
    # NEW: Batch Answer Evaluation (REPLACES evaluate_answer)
    # ---------------------------------------------------------
    def evaluate_all_answers(self, pdf_text, questions_and_answers):
        """
        Evaluates multiple answers in a single API call to save quota.
        questions_and_answers: List of tuples [(question, answer), ...]
        """
        qa_block = ""
        for i, (q, a) in enumerate(questions_and_answers, 1):
            qa_block += f"ITEM {i}:\nQuestion: {q}\nStudent Answer: {a}\n\n"

        evaluation_prompt = f"""
        You are an examiner and tutor. Use ONLY the provided document as reference.
        
        Evaluate each item provided below. 
        For each item, provide a score (0-100), a short explanation, and supporting notes.

        STRICT OUTPUT FORMAT PER ITEM:
        ---ITEM [number]---
        Score: [0-100]%
        Explanation: [text]
        Supporting Notes: [text]
        ---END---

        Document:
        {pdf_text}

        Items to Evaluate:
        {qa_block}
        """

        response = self.client.models.generate_content(
            model=self.model, contents=evaluation_prompt
        )
        return response.text
