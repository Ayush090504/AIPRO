import json
import re
from llm.ollama_client import call_ollama

SYSTEM_PROMPT = """
You are AIPROS, an offline desktop automation assistant.

STRICT RULES:
- Respond with ONLY valid JSON
- No explanations
- No markdown
- No extra text
- No code blocks

JSON schema:
{
  "intent": "<SHORT_INTENT_NAME>",
  "action": "<ACTION>",
  "target": "<TARGET>",
  "confidence": <NUMBER between 0 and 1>
}

Examples:
User: open notepad
Response:
{
  "intent": "launch_application",
  "action": "open",
  "target": "notepad",
  "confidence": 0.9
}
"""

def _extract_json(text: str) -> dict | None:
    """
    Safely extracts the first JSON object from model output.
    Handles extra text before/after JSON.
    """
    if not text:
        return None

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None

    try:
        return json.loads(match.group())
    except json.JSONDecodeError:
        return None

def _normalize(value) -> str:
    """
    Normalizes any value into a safe lowercase string.
    Handles None, numbers, unexpected types.
    """
    if value is None:
        return ""
    return str(value).strip().lower()

def generate_intent(user_input: str) -> dict:
    """
    Converts user input into structured intent using local LLM.
    Returns a safe, normalized intent dictionary.
    """

    prompt = f"""
{SYSTEM_PROMPT}

User command:
{user_input}
"""

    raw_output = call_ollama(prompt)
    parsed = _extract_json(raw_output)

    if not parsed:
        return {
            "intent": "unknown",
            "action": "",
            "target": "",
            "confidence": 0,
            "raw_output": raw_output
        }

    return {
        "intent": _normalize(parsed.get("intent")),
        "action": _normalize(parsed.get("action")),
        "target": _normalize(parsed.get("target")),
        "confidence": parsed.get("confidence", 0)
    }
