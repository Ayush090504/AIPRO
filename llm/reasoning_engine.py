from llm.ollama_client import call_ollama
import json

SYSTEM_PROMPT = """
You are an intent classifier.

If the user wants to open or run something on their computer,
return JSON:
{
  "mode": "command",
  "action": "open",
  "target": "<application name>"
}

If the user is chatting normally, return:
{
  "mode": "chat",
  "response": "<natural reply>"
}
ONLY return JSON.
"""

def generate_intent(user_input: str) -> dict:
    prompt = f"{SYSTEM_PROMPT}\nUser: {user_input}"

    raw = call_ollama(prompt)

    try:
        parsed = json.loads(raw)
    except Exception:
        return {
            "mode": "chat",
            "response": raw
        }

    if parsed.get("mode") == "command":
        return {
            "mode": "command",
            "action": parsed.get("action", "open"),
            "target": parsed.get("target", "")
        }

    return {
        "mode": "chat",
        "response": parsed.get("response", "")
    }
