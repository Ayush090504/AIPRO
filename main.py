from llm.reasoning_engine import generate_intent
from llm.chat_engine import chat_response
from explainability.planner import build_plan
from automation.executor import execute_plan
from llm.ollama_service_manager import is_ollama_running, start_ollama

class AIPROSCore:
    def __init__(self):
        if not is_ollama_running():
            start_ollama()

    def process_input(self, user_input: str):
        result = generate_intent(user_input)

        if result.get("mode") == "chat":
            return {
                "mode": "chat",
                "response": chat_response(user_input)
            }

        plan = build_plan(result)
        return {
            "mode": "command",
            "intent": result,
            "plan": plan
        }

    def execute(self, intent: dict, plan: dict):
        return execute_plan(intent, plan)
