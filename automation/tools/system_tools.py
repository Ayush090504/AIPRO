import os
import webbrowser
import subprocess
import shutil
import time
from pathlib import Path
import pyautogui
import platform

# -------------------------
# FILE & DIRECTORY TOOLS
# -------------------------

def open_file(filepath: str):
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"{filepath} does not exist")
    os.startfile(path)


SAFE_ROOTS = [
    Path.home(),
    Path.home() / "Documents",
    Path.home() / "Downloads",
    Path.home() / "Desktop"
]

def open_folder_by_name(folder_name: str):
    folder_name = folder_name.lower()

    # First: direct known folders
    for root in SAFE_ROOTS:
        candidate = root / folder_name
        if candidate.exists() and candidate.is_dir():
            subprocess.Popen(["explorer", str(candidate)])
            return True

    # Fallback: recursive search (limited)
    for root in SAFE_ROOTS:
        try:
            for path in root.rglob(folder_name):
                if path.is_dir():
                    subprocess.Popen(["explorer", str(path)])
                    return True
        except PermissionError:
            continue

    return False

def search_files(query: str, base_path: str = "C:/"):
    matches = []
    for root, _, files in os.walk(base_path):
        for f in files:
            if query.lower() in f.lower():
                matches.append(os.path.join(root, f))
        if len(matches) >= 10:
            break
    return matches


def index_directory(path: str):
    p = Path(path)
    if not p.exists():
        return []
    return [str(x) for x in p.rglob("*")]


# -------------------------
# WEB / URL TOOLS
# -------------------------

def open_url(url: str):
    if not url.startswith("http"):
        url = "https://" + url
    webbrowser.open(url)


def search_web(query: str):
    q = query.replace(" ", "+")
    webbrowser.open(f"https://www.google.com/search?q={q}")


def play_youtube_video(topic: str):
    q = topic.replace(" ", "+")
    webbrowser.open(f"https://www.youtube.com/results?search_query={q}")


# -------------------------
# APP & SYSTEM TOOLS
# -------------------------

def open_app(app_name: str) -> bool:
    """
    Opens applications ONLY.
    Never opens folders.
    No Explorer guessing.
    """

    if platform.system().lower() != "windows":
        return False

    name = app_name.lower().strip()

    # 1️⃣ URI-based Windows apps
    URI_APPS = {
        "microsoft edge": "microsoft-edge:",
        "edge": "microsoft-edge:",
        "microsoft store": "ms-windows-store:",
        "windows store": "ms-windows-store:",
    }

    if name in URI_APPS:
        subprocess.Popen(["explorer.exe", URI_APPS[name]])
        return True

    # 2️⃣ Known Windows executables
    KNOWN_APPS = {
        "calculator": "calc.exe",
        "calc": "calc.exe",
        "notepad": "notepad.exe",
        "paint": "mspaint.exe",
        "cmd": "cmd.exe",
        "command prompt": "cmd.exe",
        "powershell": "powershell.exe",
        "vs code": "code",
        "visual studio code": "code",
    }

    if name in KNOWN_APPS:
        subprocess.Popen([KNOWN_APPS[name]])
        return True

    # 3️⃣ PATH-based executables
    exe = shutil.which(name.replace(" ", ""))
    if exe:
        subprocess.Popen([exe])
        return True

    # ❌ DO NOT FALL BACK TO EXPLORER
    return False
# -------------------------
# WHATSAPP (WEB)
# -------------------------

def send_whatsapp(recipient: str, message: str):
    text = message.replace(" ", "%20")
    url = f"https://wa.me/{recipient}?text={text}"
    webbrowser.open(url)


# -------------------------
# INPUT / AUTOMATION TOOLS
# -------------------------

def type_text(text: str):
    pyautogui.write(text, interval=0.03)


def paste_text(text: str):
    pyautogui.write(text)


def mouse_move(x: int, y: int):
    pyautogui.moveTo(x, y)


def mouse_click(x: int, y: int, button="left"):
    pyautogui.click(x, y, button=button)


def mouse_scroll(amount: int):
    pyautogui.scroll(amount)


def keyboard_press(key: str):
    pyautogui.press(key)


def press_hotkey(keys: list):
    pyautogui.hotkey(*keys)


def get_screen_size():
    return pyautogui.size()


def take_screenshot(filename: str):
    pyautogui.screenshot(filename)


def wait(seconds: int):
    time.sleep(seconds)
