import os
import webbrowser
import subprocess
import shutil
import time
from pathlib import Path
import pyautogui
from automation.app_aliases import APP_ALIASES


# -------------------------
# FILE & DIRECTORY TOOLS
# -------------------------

def open_file(filepath: str):
    path = Path(filepath)
    if not path.exists():
        return {"executed": False, "error": "File not found"}
    os.startfile(path)
    return {"executed": True}


SAFE_ROOTS = [
    Path.home(),
    Path.home() / "Documents",
    Path.home() / "Downloads",
    Path.home() / "Desktop"
]

def open_folder_by_name(folder_name: str) -> bool:
    folder_name = folder_name.lower().strip()

    # 1️⃣ Common user folders (instant)
    COMMON_FOLDERS = {
        "documents": Path.home() / "Documents",
        "downloads": Path.home() / "Downloads",
        "desktop": Path.home() / "Desktop",
        "pictures": Path.home() / "Pictures",
        "videos": Path.home() / "Videos",
        "music": Path.home() / "Music",
    }

    if folder_name in COMMON_FOLDERS:
        path = COMMON_FOLDERS[folder_name]
        if path.exists():
            subprocess.Popen(["explorer.exe", str(path)])
            return True   # ✅ CRITICAL

    # 2️⃣ Safe recursive search (home only)
    home = Path.home()
    try:
        for root, dirs, _ in os.walk(home):
            for d in dirs:
                if d.lower() == folder_name:
                    subprocess.Popen(
                        ["explorer.exe", str(Path(root) / d)]
                    )
                    return True   # ✅ CRITICAL
    except PermissionError:
        pass

    # 3️⃣ Not found
    return False


def search_files(query: str, base_path: str = "C:/"):
    matches = []
    for root, _, files in os.walk(base_path):
        for f in files:
            if query.lower() in f.lower():
                matches.append(os.path.join(root, f))
        if len(matches) >= 10:
            break
    return {"executed": True, "results": matches}


def index_directory(path: str):
    p = Path(path)
    if not p.exists():
        return {"executed": False, "error": "Path does not exist"}
    return {"executed": True, "items": [str(x) for x in p.rglob("*")]}


# -------------------------
# WEB / URL TOOLS
# -------------------------

def open_url(url: str):
    if not url.startswith("http"):
        url = "https://" + url
    webbrowser.open(url)
    return {"executed": True}


def search_web(query: str):
    q = query.replace(" ", "+")
    webbrowser.open(f"https://www.google.com/search?q={q}")
    return {"executed": True}


def play_youtube_video(topic: str):
    q = topic.replace(" ", "+")
    webbrowser.open(f"https://www.youtube.com/results?search_query={q}")
    return {"executed": True}


# -------------------------
# APP & SYSTEM TOOLS
# -------------------------

START_MENU_DIRS = [
    Path(os.environ.get("PROGRAMDATA", "")) / "Microsoft/Windows/Start Menu/Programs",
    Path(os.environ.get("APPDATA", "")) / "Microsoft/Windows/Start Menu/Programs",
]

def _search_start_menu(app_name: str) -> Path | None:
    name_l = app_name.lower()
    for base in START_MENU_DIRS:
        if base.exists():
            for shortcut in base.rglob("*.lnk"):
                if name_l in shortcut.stem.lower():
                    return shortcut
    return None

def open_app(app_name: str):
    key = app_name.lower().strip()
    app_name = APP_ALIASES.get(key, app_name)
    name = app_name.lower().strip()

    URI_APPS = {
        "microsoft edge": "microsoft-edge:",
        "edge": "microsoft-edge:",
        "microsoft store": "ms-windows-store:",
        "windows store": "ms-windows-store:",
    }

    if name in URI_APPS:
        subprocess.Popen(["explorer.exe", URI_APPS[name]])
        return {"executed": True}

    KNOWN_APPS = {
        "calculator": "calc.exe",
        "calc": "calc.exe",
        "notepad": "notepad.exe",
        "vs code": "code",
        "visual studio code": "code",
    }

    if name in KNOWN_APPS:
        subprocess.Popen([KNOWN_APPS[name]])
        return {"executed": True}

    exe = shutil.which(name.replace(" ", ""))
    if exe:
        subprocess.Popen([exe])
        return {"executed": True}

    # Word fallback
    if name in ("microsoft word", "word", "ms word"):
        winword = shutil.which("winword")
        candidate_paths = [
            winword,
            r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
            r"C:\Program Files (x86)\Microsoft Office\root\Office16\WINWORD.EXE",
        ]
        for path in candidate_paths:
            if path and Path(path).exists():
                subprocess.Popen([path])
                return {"executed": True}

    shortcut = _search_start_menu(name)
    if not shortcut and " " in name:
        shortcut = _search_start_menu(name.split()[-1])
    if shortcut:
        os.startfile(str(shortcut))
        return {"executed": True}

    return {"executed": False, "error": "Application not found"}


# -------------------------
# WHATSAPP (WEB)
# -------------------------

def send_whatsapp(recipient: str, message: str):
    text = message.replace(" ", "%20")
    url = f"https://wa.me/{recipient}?text={text}"
    webbrowser.open(url)
    return {"executed": True}


# -------------------------
# INPUT / AUTOMATION TOOLS
# -------------------------

def type_text(text: str):
    pyautogui.write(text, interval=0.03)
    return {"executed": True}


def paste_text(text: str):
    pyautogui.write(text)
    return {"executed": True}


def mouse_move(x: int, y: int):
    pyautogui.moveTo(x, y)
    return {"executed": True}


def mouse_click(x: int, y: int, button="left"):
    pyautogui.click(x, y, button=button)
    return {"executed": True}


def mouse_scroll(amount: int):
    pyautogui.scroll(amount)
    return {"executed": True}


def keyboard_press(key: str):
    pyautogui.press(key)
    return {"executed": True}


def press_hotkey(keys: list):
    pyautogui.hotkey(*keys)
    return {"executed": True}


def get_screen_size():
    return {"executed": True, "size": pyautogui.size()}


def take_screenshot(filename: str):
    pyautogui.screenshot(filename)
    return {"executed": True}


def wait(seconds: int):
    time.sleep(seconds)
    return {"executed": True}
