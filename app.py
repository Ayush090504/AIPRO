import streamlit as st
from main import AIPROSCore

st.set_page_config(page_title="AIPROS", layout="centered")

st.markdown(
    "<h1 style='text-align:center;'>🧠 AIPROS</h1>"
    "<p style='text-align:center;'>AI Powered Productivity Layer</p>",
    unsafe_allow_html=True
)

core = AIPROSCore(auto_execute=True)

command = st.text_input("Enter a command or message")

if st.button("▶ Send") and command.strip():
    with st.spinner("AIPROS is thinking..."):
        result = core.process_input(command)

    if result["mode"] == "chat":
        st.markdown(f"**AIPROS:** {result['response']}")

    elif result["mode"] == "command":
        st.success(result["message"])
        if not result.get("execution"):
            st.error("Could not execute the command.")
