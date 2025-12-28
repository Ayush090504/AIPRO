import subprocess
import requests
import time

OLLAMA_URL = "http://localhost:11434"

def is_ollama_running() -> bool:
    try:
        requests.get(OLLAMA_URL, timeout=1)
        return True
    except requests.RequestException:
        return False

def start_ollama():
    subprocess.Popen(
        ["ollama", "serve"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        shell=True
    )

    # Wait until server is ready
    for _ in range(10):
        if is_ollama_running():
            return True
        time.sleep(1)

    return False
