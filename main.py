from llm.reasoning_engine import generate_intent
from automation.executor import execute_plan


class AIPROSCore:
    def process_input(self, user_input: str):
        intent = generate_intent(user_input)

        if intent["mode"] == "chat":
            return {
                "mode": "chat",
                "response": intent["response"]
            }

        execution = execute_plan(intent)

        return {
            "mode": "command",
            "executed": execution.get("executed", False)
        }
