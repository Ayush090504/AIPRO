import streamlit as st
from main import AIPROSCore
from ui.layout import setup_page, header, command_input, show_plan, confirmation_buttons

setup_page()
header()

if "pending" not in st.session_state:
    st.session_state.pending = None

core = AIPROSCore()

command, send = command_input()

if send and command:
    st.session_state.pending = core.process_input(command)

if st.session_state.pending:
    result = st.session_state.pending

    if result["mode"] == "chat":
        st.divider()
        st.markdown("💬 **AIPROS**")
        st.write(result["response"])
        st.session_state.pending = None

    else:
        st.divider()
        show_plan(result["plan"])

        yes, no = confirmation_buttons()

        if yes:
            exec_result = core.execute(result["intent"], result["plan"])
            if exec_result.get("executed"):
                st.success("✅ Action executed")
            else:
                st.error("❌ Could not execute the command")
            st.session_state.pending = None

        if no:
            st.warning("❌ Action cancelled")
            st.session_state.pending = None
