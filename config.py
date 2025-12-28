from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Data paths
DATA_DIR = BASE_DIR / "data"
LOG_DIR = DATA_DIR / "logs"
CHROMA_DIR = DATA_DIR / "chroma"
KEY_DIR = DATA_DIR / "keys"

# Ensure directories exist
for d in [DATA_DIR, LOG_DIR, CHROMA_DIR, KEY_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# LLM Configuration
OLLAMA_MODEL = "llama3:latest"
OLLAMA_HOST = "http://localhost:11434"

# Voice
ENABLE_VOICE = True

# Automation
DRY_RUN = False   # If True, actions are only simulated

# Security
ENCRYPT_LOGS = True
    