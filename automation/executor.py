from automation.app_control import open_application

def execute_plan(intent: dict) -> bool:
    if intent.get("action") == "open":
        return open_application(intent.get("target", ""))
    return False
