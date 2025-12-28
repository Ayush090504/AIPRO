from llm.ollama_client import call_ollama

def chat_response(user_input: str) -> str:
    prompt = f"""
You are AIPROS, a friendly, concise AI assistant.
Respond naturally like a human.

User: {user_input}
Assistant:
"""
    return call_ollama(prompt)
