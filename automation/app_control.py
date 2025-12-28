import subprocess
import shutil
import platform

SYSTEM_TOOLS = {
    "control panel": ["control.exe"],
    "device manager": ["devmgmt.msc"],
    "services": ["services.msc"],
    "event viewer": ["eventvwr.msc"],
    "disk management": ["diskmgmt.msc"],
    "task manager": ["taskmgr"],
}

UWP_APPS = {
    "microsoft store": "Microsoft.WindowsStore_8wekyb3d8bbwe!App",
    "store": "Microsoft.WindowsStore_8wekyb3d8bbwe!App",
    "settings": "windows.immersivecontrolpanel_cw5n1h2txyewy!microsoft.windows.immersivecontrolpanel",
    "calculator": "Microsoft.WindowsCalculator_8wekyb3d8bbwe!App",
    "xbox": "Microsoft.XboxApp_8wekyb3d8bbwe!App",
}

def open_application(app_name: str) -> bool:
    """
    Safely opens known applications or system tools on Windows.
    Returns True ONLY if a valid launch method was used.
    """

    if platform.system().lower() != "windows":
        return False

    app_name = app_name.lower().strip()

    # 1️⃣ Exact system tools (most reliable)
    if app_name in SYSTEM_TOOLS:
        try:
            subprocess.Popen(SYSTEM_TOOLS[app_name], shell=False)
            return True
        except Exception:
            return False

    # 2️⃣ Direct executable (chrome, vscode, steam, games in PATH)
    exe = shutil.which(app_name)
    if exe:
        try:
            subprocess.Popen([exe], shell=False)
            return True
        except Exception:
            return False

    # 3️⃣ Known UWP apps
    if app_name in UWP_APPS:
        try:
            subprocess.Popen(
                ["explorer.exe", f"shell:AppsFolder\\{UWP_APPS[app_name]}"],
                shell=False
            )
            return True
        except Exception:
            return False

    # ❌ NO generic explorer fallback
    return False
