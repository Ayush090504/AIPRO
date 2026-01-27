import streamlit as st
import subprocess
from main import AIPROSCore
from memory.preference_store import get_preference, set_preference
from automation.executor import execute_plan

# -----------------------------
# Session state
# -----------------------------
if "pending_confirmation" not in st.session_state:
    st.session_state.pending_confirmation = None

if "pending_chain" not in st.session_state:
    st.session_state.pending_chain = None
    st.session_state.pending_chain_index = 0

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(page_title="AIPROS", layout="centered")

st.markdown("<h1 style='text-align:center;'>🧠 AIPROS</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>AI Powered Productivity Layer</p>", unsafe_allow_html=True)

core = AIPROSCore()

# -----------------------------
# Chain executor (FIXED)
# -----------------------------
def execute_chain(intents, start_index=0):
    for i in range(start_index, len(intents)):
        intent = intents[i]
        execution = execute_plan(intent, intent["raw"])

        # 🟡 Pause for confirmation
        if execution.get("needs_confirmation"):
            return {
                "type": "confirmation",
                "index": i,
                "data": execution
            }

        # 🔴 Stop ONLY if explicitly failed
        if execution.get("status") == 'error':
            return False

    return None

# -----------------------------
# Input
# -----------------------------
command = st.text_input("Enter a command or message")

if st.button("▶ Send") and command.strip():
    with st.spinner("AIPROS is thinking..."):
        result = core.process_input(command)

    # 🟢 Chat mode
    if result.get("mode") == "chat":
        st.markdown(f"**AIPROS:** {result['response']}")

    # 🔵 Chain mode (Phase D2)
    elif result.get("mode") == "chain":
        chain_result = execute_chain(result["intents"])

        if chain_result is None:
            st.success("All actions completed successfully.")

        elif chain_result is False:
            st.error("Stopped execution because one step failed.")

        elif chain_result["type"] == "confirmation":
            st.session_state.pending_chain = result["intents"]
            st.session_state.pending_chain_index = chain_result["index"]
            st.session_state.pending_confirmation = chain_result["data"]
            st.warning("Action paused. Please confirm to continue.")

    # 🟡 Needs confirmation (single command)
    elif result.get("needs_confirmation"):
        folder_name = result["args"]["folder_name"]
        folder_key = f"folder::{folder_name}"

        preferred_path = get_preference(folder_key)
        options = result["options"]

        if preferred_path and len(options) == 1:
            subprocess.Popen(["explorer.exe", preferred_path])
            st.success("Opened your preferred folder.")
        else:
            st.session_state.pending_confirmation = result
            st.warning("I found multiple matches. Please choose one.")

    # 🟢 Executed successfully
    elif result.get("executed"):
        st.success("Got it. I’ve run that for you.")

    # 🔴 Failed
    else:
        st.error("Could not execute the command.")

# -----------------------------
# Confirmation UI (single + chain)
# -----------------------------
if st.session_state.pending_confirmation:
    data = st.session_state.pending_confirmation
    st.subheader("Which one do you want to open?")

    folder_key = f"folder::{data['args']['folder_name']}"

    for opt in data["options"]:
        if st.button(opt["label"]):
            subprocess.Popen(["explorer.exe", opt["path"]])
            set_preference(folder_key, opt["path"])

            st.session_state.pending_confirmation = None

            # 🔁 Resume chain if needed
            if st.session_state.pending_chain:
                result = execute_chain(
                    st.session_state.pending_chain,
                    st.session_state.pending_chain_index + 1
                )

                st.session_state.pending_chain = None
                st.session_state.pending_chain_index = 0

                if result is None:
                    st.success("All actions completed successfully.")
                else:
                    st.error("Chain execution stopped.")

            else:
                st.success("Folder opened.")

            st.rerun()