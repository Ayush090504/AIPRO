import streamlit as st
from main import AIPROSCore

st.set_page_config(page_title="AIPROS", layout="centered")

st.markdown("<h1 style='text-align:center;'>🧠 AIPROS</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>AI Powered Productivity Layer</p>", unsafe_allow_html=True)

core = AIPROSCore()
command = st.text_input("Enter a command or message")

if st.button("▶ Send") and command.strip():
    with st.spinner("AIPROS is thinking..."):
        result = core.process_input(command)

    if result["mode"] == "chat":
        st.markdown(f"**AIPROS:** {result['response']}")
    else:
        if result["executed"]:
            st.success("Got it. I’ve run that for you.")
        else:
            st.error("Could not execute the command.")
