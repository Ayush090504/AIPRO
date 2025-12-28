import streamlit as st

def setup_page():
    st.set_page_config(
        page_title="AIPROS",
        layout="centered",
        initial_sidebar_state="collapsed"
    )

def header():
    st.markdown(
        """
        <style>
        .ring {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            border: 4px solid rgba(255,255,255,0.2);
            border-top: 4px solid #7c7cff;
            animation: spin 1.2s linear infinite;
            margin: auto;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        </style>

        <h1 style="text-align:center;">🧠 AIPROS</h1>
        <p style="text-align:center; color: gray;">
        AI Powered Productivity Layer
        </p>
        """,
        unsafe_allow_html=True
    )

def animated_ring(active: bool):
    if active:
        st.markdown('<div class="ring"></div>', unsafe_allow_html=True)

def command_input(disabled: bool):
    with st.form("command_form"):
        command = st.text_input(
            "",
            placeholder="Type a command… (e.g. open notepad)",
            label_visibility="collapsed",
            disabled=disabled
        )
        send = st.form_submit_button("▶ Send", disabled=disabled)

    return command, send

def show_plan(plan: dict):
    st.subheader("📝 What I will do")
    st.write(plan.get("summary", ""))

    for i, step in enumerate(plan.get("steps", []), 1):
        st.markdown(f"**{i}.** {step}")

def confirmation_buttons():
    col1, col2 = st.columns(2)
    with col1:
        confirm = st.button("✅ Yes, proceed")
    with col2:
        cancel = st.button("❌ Cancel")

    return confirm, cancel
