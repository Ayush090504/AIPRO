from automation.app_control import open_application

def execute_plan(intent: dict, plan: dict) -> dict:
    """
    Executes the approved plan.
    """

    if not plan.get("safe_to_execute"):
        return {
            "executed": False,
            "reason": "Plan not safe to execute"
        }

    action = intent.get("action")
    target = intent.get("target")

    if action == "open":
        success = open_application(target)
        return {
            "executed": success,
            "action": action,
            "target": target
        }

    return {
        "executed": False,
        "reason": "Unsupported action"
    }
