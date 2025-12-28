import subprocess
import shutil
import platform
import os
from pathlib import Path

from automation.utils import normalize_app_name
from automation.app_aliases import APP_ALIASES

# ---------- SYSTEM TOOLS ----------
SYSTEM_TOOLS = {
    "control panel": ["control.exe"],
    "task manager": ["taskmgr"],
}

# ---------- URI-BASED APPS ----------
URI_APPS = {
    "microsoft edge": "microsoft-edge:",
    "microsoft store": "ms-windows-store:",
}

# ---------- STEAM GAMES ----------
STEAM_GAMES = {
    "euro truck simulator 2": "227300",
}

# ---------- START MENU LOCATIONS ----------
START_MENU_DIRS = [
    Path(os.environ.get("PROGRAMDATA", "")) / "Microsoft/Windows/Start Menu/Programs",
    Path(os.environ.get("APPDATA", "")) / "Microsoft/Windows/Start Menu/Programs",
]

def _search_start_menu(app_name: str) -> Path | None:
    for base in START_MENU_DIRS:
        if not base.exists():
            continue
        for shortcut in base.rglob("*.lnk"):
            if app_name in shortcut.stem.lower():
                return shortcut
    return None

def open_application(app_name: str) -> bool:
    """
    Attempts to open ANY application present on the system.
    Returns True only if a real launch attempt was made.
    """

    if platform.system().lower() != "windows":
        return False

    # Normalize + resolve aliases
    name = normalize_app_name(app_name)
    name = APP_ALIASES.get(name, name)

    # 1️⃣ System tools
    if name in SYSTEM_TOOLS:
        subprocess.Popen(SYSTEM_TOOLS[name])
        return True

    # 2️⃣ URI-based apps (Edge, Store)
    if name in URI_APPS:
        subprocess.Popen(["explorer.exe", URI_APPS[name]])
        return True

    # 3️⃣ PATH executables (chrome, code, python, etc.)
    exe_name = name.replace(" ", "")
    exe = shutil.which(exe_name)
    if exe:
        subprocess.Popen([exe])
        return True

    # 4️⃣ Steam games
    if name in STEAM_GAMES:
        subprocess.Popen(
            ["explorer.exe", f"steam://rungameid/{STEAM_GAMES[name]}"]
        )
        return True

    # 5️⃣ Start Menu shortcuts
    shortcut = _search_start_menu(name)
    if shortcut:
        subprocess.Popen([str(shortcut)])
        return True

    # ❌ Nothing matched
    return False
