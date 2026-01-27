import os
import subprocess
from pathlib import Path

# Common user folders (safe + reliable)
COMMON_FOLDERS = {
    "documents": Path.home() / "Documents",
    "downloads": Path.home() / "Downloads",
    "desktop": Path.home() / "Desktop",
    "pictures": Path.home() / "Pictures",
    "videos": Path.home() / "Videos",
    "music": Path.home() / "Music",
}

def find_folder_by_name(folder_name: str):
    folder_name = folder_name.lower().strip()

    # 1️⃣ Open common folders directly
    if folder_name in COMMON_FOLDERS:
        path = COMMON_FOLDERS[folder_name]
        if path.exists():
            subprocess.Popen(["explorer.exe", str(path)])
            return {"status": "executed"}

    # 2️⃣ Search inside user home (FAST + SAFE)
    home = Path.home()
    for root, dirs, _ in os.walk(home):
        for d in dirs:
            if d.lower() == folder_name:
                subprocess.Popen(["explorer.exe", str(Path(root) / d)])
                return {"status": "executed"}

    # 3️⃣ Search top-level folders of other drives (SAFE MULTI-DRIVE SUPPORT)
    for drive in ["D:\\", "E:\\", "F:\\"]:
        if not os.path.exists(drive):
            continue

        try:
            for item in Path(drive).iterdir():
                if item.is_dir() and item.name.lower() == folder_name:
                    subprocess.Popen(["explorer.exe", str(item)])
                    return {"status": "executed"}
        except PermissionError:
            continue

    # 4️⃣ Not found anywhere
    return {"status": "not_found"}
