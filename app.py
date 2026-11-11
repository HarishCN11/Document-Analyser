"""
Main Streamlit Application
Document Analysis and Evaluation Tool with AI-powered question generation and chatbot
"""

import streamlit as st
import time

# Import modules
from tools.pdf_utils import extract_document_sections
from agents.tutor_agent import TutorAgent
from analytics.performance_charts import show_descriptive_charts, show_mcq_charts
from ui.floating_chatbot import floating_chatbot
from ui.styles import apply_styles
from ui.components import (
    render_header,
    render_features,
    render_upload_section,
    render_success_message,
    render_error_message,
)
from config import (
    GEMINI_API_KEY,
    SESSION_KEYS,
    init_session_state,
    get_session_value,
    set_session_value,
)
from utils.helpers import get_file_hash, parse_mcqs

# ========================
# Page Configuration
# ========================
st.set_page_config(
    page_title="AI Evaluation Tutor",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "AI-powered Document Analysis & Evaluation Tool"},
)

# ========================
# Initialize
# ========================
apply_styles()
init_session_state()

# Initialize Agent
agent = TutorAgent(api_key=GEMINI_API_KEY)

# ========================
# Header Section
# ========================
render_header()
render_features()

# ========================
# Upload Section
# ========================

uploaded_document = render_upload_section()

if uploaded_document:
    # Show upload progress
    progress_bar = st.progress(0)
    status_text = st.empty()

    status_text.text("Processing your document...")
    progress_bar.progress(20)

    agent.knowledge.ingest_document(uploaded_document)
    progress_bar.progress(40)

    # Mark knowledge as ready for chatbot
    st.session_state.knowledge_ready = True

    set_session_value(SESSION_KEYS["uploaded_file"], uploaded_document)
    file_hash = get_file_hash(uploaded_document.getvalue())

    # Reset state if file changes
    if get_session_value(SESSION_KEYS["file_hash"]) != file_hash:
        set_session_value(SESSION_KEYS["file_hash"], file_hash)
        set_session_value("questions", None)
        set_session_value("answers", {})
        set_session_value("question_topics", None)
        set_session_value("mcqs", None)
        set_session_value("mcq_answers", {})
        set_session_value("mcq_submitted", False)

    progress_bar.progress(100)
    status_text.empty()
    progress_bar.empty()

    # Success message with file info
    render_success_message(uploaded_document.name)

    # ========================
    # Content Analysis
    # ========================
    st.markdown("<br>", unsafe_allow_html=True)

    @st.cache_data(show_spinner="Analyzing document...")
    def extract_sections_cached(file):
        return extract_document_sections(file)

    # Extract sections
    sections = extract_sections_cached(uploaded_document)
    set_session_value("sections", sections)
    document_text = "\n".join([line for lines in sections.values() for line in lines])

    # Create two columns for better layout
    col1, col2 = st.columns([2, 1])

    with col2:
        st.markdown(
            f"""
            <div class="card">
                <h3 style="color: #1e88e5; margin-top: 0;">Document Stats</h3>
                <p><strong>Sections:</strong> {len(sections)}</p>
                <p><strong>Content Lines:</strong> {sum(len(v) for v in sections.values())}</p>
                <p><strong>Words:</strong> {len(document_text.split()):,}</p>
            </div>
        """,
            unsafe_allow_html=True,
        )

    # ========================
    # Question Extraction
    # ========================
    with col1:
        if get_session_value("questions") is None:
            st.markdown(
                """
                <div class="card">
                    <h3 style="color: #1e88e5; margin-top: 0;">Generate Questions</h3>
                    <p style="color: #666; margin-bottom: 15px;">Extract AI-generated questions from your uploaded document to create an interactive learning experience.</p>
                </div>
            """,
                unsafe_allow_html=True,
            )

            if st.button("Extract & Generate Questions", use_container_width=True):
                with st.spinner("Analyzing document... (Respecting API Rate Limits)"):
                    section_questions = {}

                    for i, (section, content_lines) in enumerate(sections.items()):
                        text_block = "\n".join(content_lines)
                        try:
                            questions = agent.get_comprehensive_questions(text_block)

                            if len(sections) > 1:
                                time.sleep(6)

                        except Exception as e:
                            if "429" in str(e):
                                st.error(
                                    "Rate limit reached. The app will use what it has extracted so far."
                                )
                            else:
                                render_error_message(str(e))
                            break

                    filtered = [
                        q.strip()
                        for q in questions
                        if len(q.strip()) > 5 and not q.lower().startswith("here are")
                    ]
                    section_questions[section] = filtered

                set_session_value(
                    "questions",
                    agent.select_questions_proportionally(
                        section_questions, max_questions=20
                    ),
                )
                set_session_value("answers", {})

                topic_map = {}
                for section, qs in section_questions.items():
                    for q in qs:
                        topic_map[q] = section

                set_session_value("question_topics", topic_map)
                st.rerun()
        else:
            st.markdown(
                f"""
                <div class="card card-success">
                    <span class="badge badge-success">[READY] Done</span>
                    <strong>Questions Generated!</strong>
                    <br><small style="color: #666;">{len(get_session_value("questions"))} questions ready for evaluation</small>
                </div>
            """,
                unsafe_allow_html=True,
            )

    # ========================
    # Tabs Section
    # ========================
    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Descriptive Evaluation", "MCQ Test"])

    # ======================================================
    # TAB 1 — Descriptive
    # ======================================================
    with tab1:
        if get_session_value("questions"):
            st.subheader("Answer the Questions")

            # Initialize answers dict if needed
            answers_dict = get_session_value("answers") or {}
            for q in get_session_value("questions"):
                if q not in answers_dict:
                    answers_dict[q] = ""

            set_session_value("answers", answers_dict)

            for i, q in enumerate(get_session_value("questions")):
                st.markdown(f"**Q{i + 1}. {q}**")
                current_answer = get_session_value("answers").get(q, "")
                new_answer = st.text_area(
                    f"Your answer {i + 1}",
                    value=current_answer,
                    key=f"desc_{i}",
                )
                answers_dict[q] = new_answer
                set_session_value("answers", answers_dict)

            if st.button("Analyze My Answers"):
                qa_pairs = [
                    (q, ans)
                    for q, ans in get_session_value("answers").items()
                    if ans.strip()
                ]

                if not qa_pairs:
                    st.warning("Please answer at least one question.")
                else:
                    with st.spinner("Batch evaluating all answers (one API call)..."):
                        try:
                            batch_response = agent.evaluate_all_answers(
                                document_text, qa_pairs
                            )
                            raw_results = batch_response.split("---ITEM")[1:]

                            results = []
                            analytics_data = []
                            total_score = 0

                            for i, raw_res in enumerate(raw_results):
                                if "---END---" in raw_res:
                                    clean_res = raw_res.split("---END---")[0].strip()
                                else:
                                    clean_res = raw_res.strip()

                                results.append(clean_res)

                                score_value = 0
                                for line in clean_res.splitlines():
                                    if "score" in line.lower():
                                        digits = "".join(filter(str.isdigit, line))
                                        if digits:
                                            score_value = int(digits)
                                            total_score += score_value
                                        break

                                q_text = qa_pairs[i][0]
                                topic = get_session_value("question_topics", {}).get(
                                    q_text, "General"
                                )
                                analytics_data.append(
                                    {"topic": topic, "score": score_value}
                                )

                            if results:
                                st.success(
                                    f"🎯 Overall Performance: **{total_score // len(results)}%**"
                                )

                                for i, res in enumerate(results, 1):
                                    st.markdown(f"### Question {i}")
                                    parts = res.split("Supporting Notes")
                                    st.write(parts[0])
                                    if len(parts) > 1:
                                        with st.expander("📚 Supporting Notes"):
                                            st.write(parts[1])

                                st.divider()
                                show_descriptive_charts(analytics_data)

                        except Exception as e:
                            render_error_message(f"Evaluation Error: {str(e)}")
        else:
            st.info("👆 Click **Extract & Generate Questions** first.")

    # ======================================================
    # TAB 2 — MCQ Test
    # ======================================================
    with tab2:
        st.subheader("MCQ Test (Based on Document)")

        word_count = len(document_text.split())
        page_count = len(sections)
        expected_mcq_count = agent.estimate_mcq_count(document_text)

        st.info(
            f"Based on your document ({page_count} sections, {word_count:,} words), "
            f"I'll generate **{expected_mcq_count} MCQs**."
        )

        if st.button("Generate MCQs"):
            with st.spinner("Generating MCQs..."):
                try:
                    mcq_text = agent.generate_mcqs(document_text)
                    set_session_value("mcqs", parse_mcqs(mcq_text))
                    set_session_value("mcq_answers", {})
                    set_session_value("mcq_submitted", False)

                    if get_session_value("mcqs"):
                        st.success(
                            f"✅ Generated {len(get_session_value('mcqs'))} MCQs!"
                        )
                except Exception as e:
                    render_error_message(f"Error generating MCQs: {str(e)}")

        if get_session_value("mcqs"):
            mcq_answers = get_session_value("mcq_answers") or {}

            for i, mcq in enumerate(get_session_value("mcqs")):
                st.markdown(f"**Q{i + 1}. {mcq['question']}**")
                mcq_answers[i] = st.radio(
                    "Select an option:",
                    list(mcq["options"].keys()),
                    format_func=lambda x: f"{x}) {mcq['options'][x]}",
                    key=f"mcq_{i}",
                    index=None,
                )

            set_session_value("mcq_answers", mcq_answers)

            if st.button("Submit MCQ Test"):
                if not all(
                    get_session_value("mcq_answers", {}).get(i) is not None
                    for i in range(len(get_session_value("mcqs")))
                ):
                    st.warning("Please answer all MCQs before submitting.")
                else:
                    set_session_value("mcq_submitted", True)

            if get_session_value("mcq_submitted"):
                score = 0
                analytics_data = []
                detailed_results = []

                st.subheader("MCQ Results")
                for i, mcq in enumerate(get_session_value("mcqs")):
                    user_answer = get_session_value("mcq_answers", {}).get(i)
                    correct_answer = mcq["answer"]

                    # Normalize both answers to ensure clean comparison
                    if user_answer:
                        user_answer = str(user_answer).strip().upper()
                    if correct_answer:
                        correct_answer = str(correct_answer).strip().upper()

                    is_correct = user_answer == correct_answer

                    analytics_data.append({"topic": "MCQ", "is_correct": is_correct})
                    detailed_results.append(
                        {
                            "question": mcq["question"],
                            "user": user_answer,
                            "correct": correct_answer,
                            "options": mcq["options"],
                            "is_correct": is_correct,
                        }
                    )
                    score += int(is_correct)

                st.markdown(
                    f"### Final Score: **{score} / {len(get_session_value('mcqs'))}**"
                )
                st.markdown(
                    f"**Accuracy:** {int((score / len(get_session_value('mcqs'))) * 100)}%"
                )

                st.divider()
                st.subheader("Correct Answers Review")
                for i, item in enumerate(detailed_results, 1):
                    st.markdown(f"**Q{i}. {item['question']}**")

                    user_key = item.get("user")
                    correct_key = item.get("correct")

                    if user_key is not None and user_key in item["options"]:
                        user_text = f"{user_key}) {item['options'][user_key]}"
                    else:
                        user_text = "No answer selected"

                    correct_text = f"{correct_key}) {item['options'][correct_key]}"

                    if item["is_correct"]:
                        st.success(f"Your answer: {user_text}")
                    else:
                        st.error(f"Your answer: {user_text}")
                        st.success(f"Correct answer: {correct_text}")

                st.divider()
                st.subheader("MCQ Performance Analytics")
                show_mcq_charts(analytics_data)

    # ========================
    # Chatbot Section
    # ========================
    st.markdown("<br><hr>", unsafe_allow_html=True)
    floating_chatbot(api_key=GEMINI_API_KEY)
