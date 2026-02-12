from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Data paths
DATA_DIR = BASE_DIR / "data"
LOG_DIR = DATA_DIR / "logs"
CHROMA_DIR = DATA_DIR / "chroma"
KEY_DIR = DATA_DIR / "keys"
SCREENSHOT_DIR = DATA_DIR / "screenshots"
REPORTS_DIR = DATA_DIR / "reports"

# Ensure directories exist
for d in [DATA_DIR, LOG_DIR, CHROMA_DIR, KEY_DIR, SCREENSHOT_DIR, REPORTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# LLM Configuration
OLLAMA_MODEL = "llama3:latest"
OLLAMA_HOST = "http://localhost:11434"
EMBEDDING_MODEL = "nomic-embed-text"
INTENT_SIM_THRESHOLD = 0.78

# Voice
ENABLE_VOICE = True
PREFERRED_MIC_NAME = ""  # Optional substring to match a mic device name

# Automation
DRY_RUN = False   # If True, actions are only simulated

# Security
ENCRYPT_LOGS = True
    
