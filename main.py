from llm.reasoning_engine import generate_intent
from explainability.planner import build_plan
from automation.executor import execute_plan
from llm.ollama_service_manager import is_ollama_running, start_ollama


class AIPROSCore:
    def __init__(self):
        self._ensure_llm()

    def _ensure_llm(self):
        if not is_ollama_running():
            start_ollama()

    def process_input(self, user_input: str):
        intent = self._reason(user_input)
        plan = self._explain(intent)

        return {
            "intent": intent,
            "plan": plan
        }

    def execute(self, intent: dict, plan: dict):
        return execute_plan(intent, plan)

    def _reason(self, user_input: str):
        return generate_intent(user_input)

    def _explain(self, intent: dict):
        return build_plan(intent)
