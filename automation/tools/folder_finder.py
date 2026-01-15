import os
import subprocess
from pathlib import Path

# Common user folders (fast + safe)
COMMON_DIRS = [
    Path.home() / "Documents",
    Path.home() / "Desktop",
    Path.home() / "Downloads",
    Path.home() / "Pictures",
    Path.home() / "Videos",
    Path.home() / "Music",
]

def _search_common_locations(folder_name: str) -> Path | None:
    folder_name = folder_name.lower()

    for base in COMMON_DIRS:
        if base.exists() and base.name.lower() == folder_name:
            return base

    return None

def _deep_search(folder_name: str, max_depth: int = 4) -> Path | None:
    folder_name = folder_name.lower()

    for drive in ["C:\\", "D:\\", "E:\\"]:
        if not os.path.exists(drive):
            continue

        for root, dirs, _ in os.walk(drive):
            depth = root[len(drive):].count(os.sep)
            if depth > max_depth:
                dirs[:] = []
                continue

            for d in dirs:
                if d.lower() == folder_name:
                    return Path(root) / d

    return None

def open_folder_by_name(folder_name: str) -> bool:
    """
    Finds and opens a folder by name.
    Returns True ONLY if a real folder was opened.
    """

    # 1️⃣ Check common locations first
    path = _search_common_locations(folder_name)

    # 2️⃣ If not found, deep search
    if not path:
        path = _deep_search(folder_name)

    # 3️⃣ Final validation
    if not path or not path.exists():
        return False

    # 4️⃣ Open folder
    subprocess.Popen(["explorer", str(path)])
    return True
