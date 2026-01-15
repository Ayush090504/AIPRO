import webbrowser

def open_url(url):
    webbrowser.open(url)
    return True

def search_web(query):
    webbrowser.open(f"https://www.google.com/search?q={query}")
    return True

def download_file(url, filename):
    import requests
    r = requests.get(url)
    with open(filename, "wb") as f:
        f.write(r.content)
    return True

# automation/tools/web_tools.py

import urllib.parse

def send_whatsapp(recipient: str, message: str = "") -> bool:
    """
    Opens WhatsApp Web chat with pre-filled message.
    """
    if not recipient:
        return False

    encoded_msg = urllib.parse.quote(message)
    url = f"https://wa.me/{recipient}?text={encoded_msg}"

    webbrowser.open(url)
    return True
