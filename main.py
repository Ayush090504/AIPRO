from llm.reasoning_engine import generate_intent
from llm.chat_engine import chat_response
from automation.executor import execute_plan
from llm.ollama_service_manager import is_ollama_running, start_ollama
import time

class AIPROSCore:
    def __init__(self, auto_execute: bool = True):
        self.auto_execute = auto_execute

    def process_input(self, user_input: str):
        # 🔑 ENSURE OLLAMA IS RUNNING
        if not is_ollama_running():
            start_ollama()
            time.sleep(2)  # give Ollama time to bind port

        intent = generate_intent(user_input)

        # Chat mode
        if intent.get("mode") == "chat":
            return {
                "mode": "chat",
                "response": intent.get("response")
            }

        # Command mode (auto-execute)
        execution = execute_plan(intent)
        return {
            "mode": "command",
            "message": "Got it. I’m running that for you.",
            "execution": execution
        }
