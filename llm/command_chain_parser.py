import re
from llm.reasoning_engine import generate_intent

SPLIT_REGEX = re.compile(r"\s+(and then|then|and)\s+", re.IGNORECASE)

def parse_command_chain(text: str) -> list[dict]:
    """
    Splits a compound command into ordered intents.
    Each intent retains its original raw command text.
    """
    parts = SPLIT_REGEX.split(text)

    # Filter out connectors like "and", "then"
    commands = [p.strip() for p in parts if p.strip() and not SPLIT_REGEX.match(p)]

    intents = []
    for cmd in commands:
        intent = generate_intent(cmd)

        # 🔹 Preserve raw command for Phase D2 execution
        intent["raw"] = cmd

        intents.append(intent)

    return intents