from llm.reasoning_engine import generate_intent
from llm.command_chain_parser import parse_command_chain
from automation.executor import execute_plan


class AIPROSCore:
    def process_input(self, user_input: str):
        # 🔹 Phase D1: parse command chain
        intents = parse_command_chain(user_input)

        # -----------------------------
        # Single intent (existing behavior)
        # -----------------------------
        if len(intents) == 1:
            intent = intents[0]

            # Chat mode
            if intent.get("mode") == "chat":
                return {
                    "mode": "chat",
                    "response": intent.get("response")
                }

            # Execute single command
            execution = execute_plan(intent, user_input)

            return {
                "mode": "command",
                **execution
            }

        # -----------------------------
        # Multiple intents (Phase D1 only)
        # -----------------------------
        return {
            "mode": "chain",
            "intents": intents
        }