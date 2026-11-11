import streamlit as st
from agents.chatbot_agent import ChatbotAgent


def floating_chatbot(api_key=None):
    # Only activate after document upload
    if not st.session_state.get("knowledge_ready", False):
        return

    if "chat_open" not in st.session_state:
        st.session_state.chat_open = False

    if "chatbot" not in st.session_state:
        st.session_state.chatbot = ChatbotAgent(
            api_key=api_key or st.session_state.get("api_key")
        )

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # ========================
    # CHATBOT UI
    # ========================
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="card">
            <h3 style="color: #1e88e5; margin-top: 0;">💬 Tutor Chatbot</h3>
            <p style="color: #6b7280; margin-bottom: 0;">Ask questions about your document content</p>
        </div>
    """,
        unsafe_allow_html=True,
    )

    # Chat display area
    st.markdown(
        """
        <style>
        .chat-container {
            background: #f9fafb;
            border-radius: 10px;
            padding: 15px;
            height: 300px;
            overflow-y: auto;
            border: 1px solid #e5e7eb;
            margin-bottom: 15px;
        }
        
        .chat-message-user {
            background: linear-gradient(135deg, #1e88e5 0%, #1565c0 100%);
            color: white;
            padding: 12px 15px;
            border-radius: 10px;
            margin-bottom: 10px;
            text-align: right;
            margin-left: 20%;
        }
        
        .chat-message-bot {
            background: white;
            color: #1f2937;
            padding: 12px 15px;
            border-radius: 10px;
            margin-bottom: 10px;
            margin-right: 20%;
            border-left: 3px solid #1e88e5;
        }
        </style>
    """,
        unsafe_allow_html=True,
    )

    # Display chat history
    chat_placeholder = st.container()

    with chat_placeholder:
        if st.session_state.chat_history:
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    st.markdown(
                        f"""
                        <div class="chat-message-user">{message["content"]}</div>
                    """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f"""
                        <div class="chat-message-bot">{message["content"]}</div>
                    """,
                        unsafe_allow_html=True,
                    )
        else:
            st.markdown(
                """
                <div style="text-align: center; color: #9ca3af; padding: 40px 20px;">
                    <p style="font-size: 0.9em;">👋 Hello! Ask me anything about your document...</p>
                </div>
            """,
                unsafe_allow_html=True,
            )

    # Input area
    st.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)

    col_input, col_send = st.columns([5, 1])

    with col_input:
        user_input = st.text_input(
            "Your question",
            placeholder="What would you like to know?",
            label_visibility="collapsed",
            key="chat_input",
        )

    with col_send:
        send_button = st.button("Send", use_container_width=True, key="send_chat")

    # Process message
    if send_button and user_input:
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # Get bot response
        with st.spinner("🤖 Thinking..."):
            try:
                reply = st.session_state.chatbot.chat(user_input)
                st.session_state.chat_history.append({"role": "bot", "content": reply})
            except Exception as e:
                st.session_state.chat_history.append(
                    {
                        "role": "bot",
                        "content": f"❌ Sorry, I encountered an error: {str(e)}",
                    }
                )

        st.rerun()
