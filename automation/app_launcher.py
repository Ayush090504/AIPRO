import subprocess
import shutil
import platform


def open_app(app_name: str):
    if platform.system().lower() != "windows":
        return False

    exe = shutil.which(app_name.replace(" ", ""))
    if exe:
        subprocess.Popen([exe])
        return True

    return False
