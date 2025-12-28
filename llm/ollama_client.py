import requests
from config import OLLAMA_HOST, OLLAMA_MODEL

def call_ollama(prompt: str) -> str:
    url = f"{OLLAMA_HOST}/api/generate"

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(
        url,
        json=payload,
        timeout=120
    )

    response.raise_for_status()
    data = response.json()

    return data.get("response", "")
