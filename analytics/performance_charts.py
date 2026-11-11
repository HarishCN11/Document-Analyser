import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


# =====================================================
# DESCRIPTIVE ANALYTICS
# =====================================================
def show_descriptive_charts(analysis_results):
    """
    analysis_results:
    [
      {"topic": "Networking", "score": 65},
      {"topic": "OSI Model", "score": 40},
      ...
    ]
    """

    df = pd.DataFrame(analysis_results)

    if df.empty:
        st.warning("No descriptive analytics data available")
        return

    # ------------------------
    # Overall Descriptive Performance (AVG SCORE PIE)
    # ------------------------
    avg_score = df["score"].mean()
    remaining = 100 - avg_score

    st.subheader("📊 Overall Descriptive Performance")

    col1, col2 = st.columns([1, 2])

    with col1:
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.pie(
            [avg_score, remaining],
            labels=["Achieved", "Remaining"],
            autopct="%1.1f%%",
            startangle=90,
        )
        ax.axis("equal")
        st.pyplot(fig, width="stretch")
        st.metric("Overall Performance (%)", f"{avg_score:.1f}%")

    with col2:
        # Topic-wise Average Score
        topic_avg = df.groupby("topic")["score"].mean().sort_values(ascending=False)
        st.subheader("📈 Topics")
        st.bar_chart(topic_avg, width="stretch", height=300)

    # Score Distribution
    st.subheader("📉 Score Distribution")
    col1, col2 = st.columns([1, 1])

    with col1:
        fig, ax = plt.subplots(figsize=(5, 4))
        ax.hist(df["score"], bins=5, color="skyblue", edgecolor="black")
        ax.set_xlabel("Score (%)")
        ax.set_ylabel("Number of Questions")
        st.pyplot(fig, width="stretch")


# =====================================================
# MCQ ANALYTICS
# =====================================================
def show_mcq_charts(analysis_results):
    """
    analysis_results:
    [
      {"topic": "MCQ", "is_correct": True},
      ...
    ]
    """

    df = pd.DataFrame(analysis_results)

    if df.empty:
        st.warning("No MCQ analytics data available")
        return

    correct = df["is_correct"].sum()
    wrong = len(df) - correct

    # Accuracy Pie Chart
    st.subheader("📊 MCQ Accuracy")

    col1, col2 = st.columns([1, 1])

    with col1:
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.pie(
            [correct, wrong],
            labels=["Correct", "Wrong"],
            autopct="%1.1f%%",
            startangle=90,
            colors=["#90EE90", "#FFB6C6"],
        )
        ax.axis("equal")
        st.pyplot(fig, width="stretch")

    with col2:
        # Accuracy %
        accuracy = (correct / len(df)) * 100
        st.metric("Accuracy", f"{accuracy:.1f}%", delta=f"{correct}/{len(df)} correct")
        st.info(f"✓ Correct: {correct}\n✗ Wrong: {wrong}")
