import os
import subprocess
from pathlib import Path

def open_file(filepath: str):
    path = Path(filepath)

    if not path.exists():
        return False

    # Directory → open Explorer
    if path.is_dir():
        subprocess.Popen(["explorer.exe", str(path)])
        return True

    # File → open normally
    os.startfile(str(path))
    return True


def search_files(query: str):
    base = Path.home()
    matches = []

    for path in base.rglob("*"):
        if query.lower() in path.name.lower():
            matches.append(str(path))
            if len(matches) >= 10:
                break

    return matches
