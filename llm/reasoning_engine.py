import re
from llm.chat_engine import chat_response

URL_REGEX = re.compile(r"(https?://[^\s]+)", re.IGNORECASE)

def generate_intent(text: str) -> dict:
    text = text.strip()
    text_l = text.lower()

    # 1️⃣ URL anywhere
    url_match = URL_REGEX.search(text)
    if url_match:
        return {
            "mode": "tool",
            "tool": "open_url",
            "args": {"url": url_match.group(1)}
        }

    # 2️⃣ Search YouTube
    if "youtube" in text_l and ("search" in text_l or "play" in text_l):
        query = text_l.replace("search", "").replace("on youtube", "").replace("youtube", "").strip()
        return {
            "mode": "tool",
            "tool": "play_youtube_video",
            "args": {"topic": query}
        }

    # 3️⃣ Search Web
    if text_l.startswith(("search", "find", "lookup")):
        query = text.split(" ", 1)[1] if " " in text else ""
        return {
            "mode": "tool",
            "tool": "search_web",
            "args": {"query": query}
        }

    # 4️⃣ Open folder by name
    if text_l.startswith("open folder"):
        folder = text.replace("open folder", "").strip()
        return {
            "mode": "tool",
            "tool": "open_folder_by_name",
            "args": {"folder_name": folder}
        }

    # 5️⃣ Open app
    if text_l.startswith("open"):
        app = text.replace("open", "").strip()
        return {
            "mode": "tool",
            "tool": "open_app",
            "args": {"app_name": app}
        }

    # 6️⃣ WhatsApp (web)
    if text_l.startswith("send whatsapp"):
        content = text.replace("send whatsapp", "").strip()
        number, *msg = content.split(" ", 1)
        return {
            "mode": "tool",
            "tool": "send_whatsapp",
            "args": {
                "recipient": number,
                "message": msg[0] if msg else ""
            }
        }

    # 7️⃣ Chat fallback
    return {
        "mode": "chat",
        "response": chat_response(text)
    }
