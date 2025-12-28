import streamlit as st
from main import AIPROSCore
from ui.layout import (
    setup_page,
    header,
    animated_ring,
    command_input,
    show_plan,
    confirmation_buttons
)

setup_page()
header()

# Session state
if "processing" not in st.session_state:
    st.session_state.processing = False
if "pending" not in st.session_state:
    st.session_state.pending = None

core = AIPROSCore()

animated_ring(st.session_state.processing)

command, send_clicked = command_input(disabled=st.session_state.processing)

if send_clicked and command:
    st.session_state.processing = True
    with st.spinner("🧠 AIPROS is thinking…"):
        st.session_state.pending = core.process_input(command)
    st.session_state.processing = False

if st.session_state.pending:
    st.divider()
    show_plan(st.session_state.pending["plan"])

    confirm, cancel = confirmation_buttons()

    if confirm:
        core.execute(
            st.session_state.pending["intent"],
            st.session_state.pending["plan"]
        )
        st.success("✅ Action executed")
        st.session_state.pending = None

    if cancel:
        st.warning("❌ Action cancelled")
        st.session_state.pending = None
