import subprocess
import shutil
import platform
import os
from pathlib import Path

from automation.utils import normalize_app_name
from automation.app_aliases import APP_ALIASES

SYSTEM_TOOLS = {
    "control panel": ["control.exe"],
    "task manager": ["taskmgr"],
}

URI_APPS = {
    "microsoft edge": "microsoft-edge:",
    "microsoft store": "ms-windows-store:",
    "whatsapp": "whatsapp:",
}

STEAM_GAMES = {
    "euro truck simulator 2": "227300",
}

START_MENU_DIRS = [
    Path(os.environ.get("PROGRAMDATA", "")) / "Microsoft/Windows/Start Menu/Programs",
    Path(os.environ.get("APPDATA", "")) / "Microsoft/Windows/Start Menu/Programs",
]

def _search_start_menu(app_name: str):
    for base in START_MENU_DIRS:
        if base.exists():
            for shortcut in base.rglob("*.lnk"):
                if app_name in shortcut.stem.lower():
                    return shortcut
    return None

def open_application(app_name: str) -> bool:
    if platform.system().lower() != "windows":
        return False

    name = normalize_app_name(app_name)
    name = APP_ALIASES.get(name, name)

    try:
        if name in SYSTEM_TOOLS:
            subprocess.Popen(SYSTEM_TOOLS[name])
            return True

        if name in URI_APPS:
            subprocess.Popen(["explorer.exe", URI_APPS[name]])
            return True

        candidates = [name.replace(" ", "")]
        if " " in name:
            candidates.append(name.split()[-1])

        for exe_name in dict.fromkeys(candidates):
            exe = shutil.which(exe_name)
            if exe:
                if exe.lower().endswith((".cmd", ".bat")):
                    subprocess.Popen(exe, shell=True)
                else:
                    subprocess.Popen([exe])
                return True

        if name in STEAM_GAMES:
            subprocess.Popen(
                ["explorer.exe", f"steam://rungameid/{STEAM_GAMES[name]}"]
            )
            return True

        shortcut = _search_start_menu(name)
        if shortcut:
            subprocess.Popen([str(shortcut)])
            return True

    except Exception as e:
        print("[ERROR]", e)
        return False

    return False
