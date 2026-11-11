from google import genai
import os
import json
from dotenv import load_dotenv


class ChatbotAgent:
    def __init__(self, api_key=None):
        load_dotenv()
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")

        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-2.5-flash"

        # Load stored chunks as knowledge base
        try:
            with open(
                "data/knowledge_base/vectors/chunks.json", "r", encoding="utf-8"
            ) as f:
                self.chunks = json.load(f)
        except Exception:
            # Placeholder fallback if no chunks exist
            self.chunks = []

    def chat(self, user_message):
        # Check if it's a general conversation or question about capabilities
        if self._is_general_conversation(user_message):
            return self._handle_general_conversation(user_message)

        # For document-related questions
        if not self.chunks:
            return "❌ No knowledge loaded yet. Please upload a document first so I can help you learn from it!"

        # Check if asking for summary/overview - use more chunks
        if self._is_general_question_about_document(user_message):
            # Use more chunks for general questions (up to 10 or all if less)
            relevant_chunks = self._search_chunks(
                user_message, k=min(10, len(self.chunks))
            )
            if not relevant_chunks and self.chunks:
                # If no match, use first few chunks anyway for general questions
                relevant_chunks = self.chunks[:5]
        else:
            # For specific questions, find most relevant chunks
            relevant_chunks = self._search_chunks(user_message, k=3)

        if not relevant_chunks:
            return self._handle_no_match(user_message)

        context = "\n\n".join(chunk["text"] for chunk in relevant_chunks)

        # Adjust prompt based on question type
        if self._is_general_question_about_document(user_message):
            # Check if asking for suggestions/recommendations
            if any(
                word in user_message.lower()
                for word in [
                    "suggest",
                    "recommend",
                    "learn more",
                    "know more",
                    "further",
                ]
            ):
                prompt = f"""
You are a friendly and helpful AI tutor assistant.

The student has uploaded a document and wants suggestions or recommendations for learning more about the topic.

Content from the document:
{context}

Student question:
{user_message}

Based on the document content, provide helpful suggestions such as:
- Key concepts they should study deeper
- Related topics mentioned in the document
- Specific areas or chapters to focus on
- Follow-up questions they could explore
- Practical applications of the concepts

Be specific and reference the actual content from the document.
"""
            # Check if asking to generate/create content
            elif any(
                word in user_message.lower()
                for word in ["generate", "create", "make", "give me", "provide"]
            ):
                prompt = f"""
You are a friendly and helpful AI tutor assistant.

The student wants you to generate something based on the document content.

Content from the document:
{context}

Student request:
{user_message}

Fulfill their request using the document content. Be creative and helpful.
"""
            else:
                prompt = f"""
You are a friendly and helpful AI tutor assistant.

The student has uploaded a document and is asking a general question about its content.

Content from the document:
{context}

Student question:
{user_message}

Provide a clear, comprehensive answer based on the content provided. If they're asking for a summary, synthesize the main points. If they're asking about a topic or subject, explain whether and how the document covers it.
"""
        else:
            prompt = f"""
You are a friendly and helpful AI tutor assistant.
Be conversational, concise, student-friendly, and accurate.

Context from uploaded document:
{context}

Student question:
{user_message}

Provide a clear and helpful answer based on the context provided. If the context doesn't fully answer the question, say so and provide what information you can find.
"""

        response = self.client.models.generate_content(
            model=self.model, contents=prompt
        )

        return response.text

    def _is_general_question_about_document(self, message):
        """Detect if message is asking for summary/overview of the document"""
        message_lower = message.lower().strip()

        summary_keywords = [
            "summary",
            "summarize",
            "summarise",
            "overview",
            "main point",
            "what is this about",
            "what does this cover",
            "what topics",
            "tell me about",
            "what's in",
            "content of",
            "general idea",
            "key point",
            "main idea",
            "gist",
            "brief",
            "outline",
            "what is this pdf",
            "what is this document",
            "what is the pdf",
            "is this about",
            "is this related",
            "does this cover",
            "topic",
            "subject matter",
            "suggestion",
            "recommend",
            "learn more",
            "know more",
            "further reading",
            "more about",
            "generate",
            "create",
            "make",
        ]

        return any(keyword in message_lower for keyword in summary_keywords)

    def _is_general_conversation(self, message):
        """Detect if message is a greeting or general conversation"""
        message_lower = message.lower().strip()

        greetings = [
            "hi",
            "hello",
            "hey",
            "greetings",
            "good morning",
            "good afternoon",
            "good evening",
            "howdy",
        ]

        # Only treat as capability question if NOT asking about document content
        capability_patterns = [
            ("what can you do", lambda m: "pdf" not in m and "document" not in m),
            ("what are you", lambda m: "pdf" not in m and "document" not in m),
            ("who are you", lambda m: True),
            ("how do you work", lambda m: "pdf" not in m and "document" not in m),
            ("capabilities", lambda m: "pdf" not in m),
            ("features", lambda m: "pdf" not in m and len(m.split()) < 5),
        ]

        # Check for greetings
        for greeting in greetings:
            if message_lower == greeting or message_lower.startswith(greeting + " "):
                return True

        # Check for capability questions (but not if asking about document content)
        for pattern, condition in capability_patterns:
            if pattern in message_lower and condition(message_lower):
                return True

        return False

    def _handle_general_conversation(self, message):
        """Handle greetings and general queries"""
        message_lower = message.lower().strip()

        # Greetings
        greetings = [
            "hi",
            "hello",
            "hey",
            "greetings",
            "good morning",
            "good afternoon",
            "good evening",
            "howdy",
        ]

        for greeting in greetings:
            if message_lower == greeting or message_lower.startswith(greeting + " "):
                return """👋 Hi there! I'm your AI Tutor Assistant.

📚 **What I can do:**
• Answer questions about your uploaded documents
• Explain concepts from your study materials
• Help you understand complex topics
• Provide summaries and key points

💡 **How to use me:**
1. Upload a document using the file uploader
2. Ask me anything about the content
3. I'll search through the material and give you clear explanations

🎯 **Try asking:**
• "What is this document about?"
• "Explain [concept] in simple terms"
• "Summarize the main points"
• "What does the document say about [topic]?"

Ready to help you learn! What would you like to know?"""

        # Capability questions
        capability_keywords = [
            "what can you do",
            "what are you",
            "who are you",
            "help",
            "how do you work",
            "capabilities",
            "features",
        ]

        for keyword in capability_keywords:
            if keyword in message_lower:
                return """🤖 **I'm your AI-powered Document Tutor!**

📋 **My capabilities:**
• 📖 Read and understand uploaded documents
• 💬 Answer questions about the content
• 🔍 Search through uploaded materials instantly
• 📝 Explain concepts in simple, student-friendly language
• 🎯 Provide relevant information based on your questions

🚀 **How I work:**
1. You upload a document
2. I process and index the content
3. You ask questions in natural language
4. I find relevant information and explain it clearly

✨ **I'm designed to help you:**
• Study more effectively
• Understand difficult concepts
• Save time searching through documents
• Learn at your own pace

Upload a document and ask me anything about it!"""

        # Default friendly response
        return "👋 Hello! I'm here to help you learn from your documents. Upload a document and ask me questions about it!"

    def _handle_no_match(self, user_message):
        """Handle when no relevant content is found"""
        return f"""🤔 I couldn't find specific information about "{user_message}" in the uploaded document.

💡 **Here's what you can try:**
• Rephrase your question differently
• Ask about a related topic
• Check if your question is covered in the document

Or you can ask me:
• "What is this document about?"
• "What topics are covered?"

I'm here to help! 😊"""

    def _search_chunks(self, query, k=3):
        """Improved string matching for relevant chunks"""
        if not self.chunks:
            return []

        # Remove common words that don't help with matching
        stop_words = {
            "a",
            "an",
            "the",
            "is",
            "are",
            "was",
            "were",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "this",
            "that",
            "these",
            "those",
            "give",
            "me",
            "please",
            "using",
            "use",
            "simple",
            "terms",
            "term",
        }

        query_words = set(
            word
            for word in query.lower().split()
            if word not in stop_words and len(word) > 2
        )
        scored_chunks = []

        for chunk in self.chunks:
            chunk_text_lower = chunk["text"].lower()
            chunk_words = set(
                word for word in chunk_text_lower.split() if len(word) > 2
            )

            # Calculate overlap score
            overlap = len(query_words & chunk_words)

            # Boost score for substring matches (partial word matching)
            substring_matches = sum(
                1 for qword in query_words if qword in chunk_text_lower
            )

            total_score = overlap * 2 + substring_matches

            if total_score > 0:
                scored_chunks.append((chunk, total_score))

        # If no matches and we need chunks, return all chunks (for general questions)
        if not scored_chunks and k >= len(self.chunks):
            return self.chunks

        # Return top k by relevance
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        return [chunk for chunk, score in scored_chunks[:k]]
