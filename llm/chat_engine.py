from llm.ollama_service_manager import is_ollama_running, start_ollama
from llm.ollama_client import call_ollama


def chat_response(prompt: str) -> str:
    if not is_ollama_running():
        start_ollama()

    return call_ollama(prompt)
