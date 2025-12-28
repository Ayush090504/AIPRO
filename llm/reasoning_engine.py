import json
import re
from llm.ollama_client import call_ollama

SYSTEM_PROMPT = """
You are AIPROS, an offline desktop AI assistant.

Classify the user input into ONE mode:

1. "command" → if the user wants the system to do something
2. "chat" → if the user is having a normal conversation

RULES:
- Respond ONLY with valid JSON
- No explanations
- No markdown
- No extra text

JSON schema:
{
  "mode": "command | chat",
  "intent": "",
  "action": "",
  "target": "",
  "confidence": 0.0
}

Examples:

User: open notepad
{
  "mode": "command",
  "intent": "launch_application",
  "action": "open",
  "target": "notepad",
  "confidence": 0.9
}

User: how are you?
{
  "mode": "chat",
  "intent": "",
  "action": "",
  "target": "",
  "confidence": 0.8
}
"""

def _extract_json(text: str):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group())
    except json.JSONDecodeError:
        return None

def _norm(val):
    if val is None:
        return ""
    return str(val).lower().strip()

def generate_intent(user_input: str) -> dict:
    prompt = f"{SYSTEM_PROMPT}\nUser: {user_input}"
    raw = call_ollama(prompt)
    parsed = _extract_json(raw)

    if not parsed:
        return {"mode": "chat"}

    return {
        "mode": _norm(parsed.get("mode")),
        "intent": _norm(parsed.get("intent")),
        "action": _norm(parsed.get("action")),
        "target": _norm(parsed.get("target")),
        "confidence": parsed.get("confidence", 0.0)
    }
