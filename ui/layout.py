import streamlit as st

def command_input():
    col1, col2, col3 = st.columns([7, 1, 2])

    with col1:
        command = st.text_input(
            "",
            placeholder="Type or speak a command…",
            label_visibility="collapsed"
        )

    with col2:
        voice = st.button("🎤", use_container_width=True)

    with col3:
        send = st.button("▶ Send", use_container_width=True)

    return command, send, voice
