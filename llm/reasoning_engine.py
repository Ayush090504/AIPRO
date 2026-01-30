import re
from llm.chat_engine import chat_response

URL_REGEX = re.compile(r"(https?://[^\s]+)", re.IGNORECASE)

def generate_intent(text: str) -> dict:
    text = text.strip()
    text_l = text.lower()

    # ------------------------------
    # 1️⃣ OPEN FOLDER (explicit ONLY)
    # ------------------------------
    if text_l.startswith("open folder"):
        folder = text[11:].strip()
        return {
            "mode": "tool",
            "tool": "open_folder_by_name",
            "args": {"folder_name": folder}
        }

    # ------------------------------
    # 2️⃣ OPEN APPLICATION
    # ------------------------------
    if text_l.startswith("open "):
        target = text[5:].strip()

        # Safety: do NOT auto-convert app to folder
        return {
            "mode": "tool",
            "tool": "open_app",
            "args": {"app_name": target}
        }

    # ------------------------------
    # 3️⃣ YOUTUBE SEARCH / PLAY
    # ------------------------------
    if "youtube" in text_l and ("search" in text_l or "play" in text_l):
        query = (
            text_l
            .replace("search", "")
            .replace("play", "")
            .replace("on youtube", "")
            .replace("youtube", "")
            .strip()
        )
        return {
            "mode": "tool",
            "tool": "play_youtube_video",
            "args": {"topic": query}
        }

    # ------------------------------
    # 4️⃣ SEARCH WEB (explicit)
    # ------------------------------
    if text_l.startswith("search "):
        query = text[7:].strip()
        return {
            "mode": "tool",
            "tool": "search_web",
            "args": {"query": query}
        }

    # ------------------------------
    # 5️⃣ OPEN URL (explicit or raw)
    # ------------------------------
    if text_l.startswith("open url"):
        url = text[8:].strip()
        return {
            "mode": "tool",
            "tool": "open_url",
            "args": {"url": url}
        }

    url_match = URL_REGEX.search(text)
    if url_match:
        return {
            "mode": "tool",
            "tool": "open_url",
            "args": {"url": url_match.group(1)}
        }

    # ------------------------------
    # 6️⃣ SEND WHATSAPP (WEB)
    # ------------------------------
    if text_l.startswith("send whatsapp"):
        content = text[13:].strip()
        parts = content.split(" ", 1)
        return {
            "mode": "tool",
            "tool": "send_whatsapp",
            "args": {
                "recipient": parts[0],
                "message": parts[1] if len(parts) > 1 else ""
            }
        }

    # ------------------------------
    # 7️⃣ CHAT FALLBACK
    # ------------------------------
    return {
        "mode": "chat",
        "response": chat_response(text)
    }