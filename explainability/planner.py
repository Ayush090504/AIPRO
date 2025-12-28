def build_plan(intent: dict) -> dict:
    """
    Converts structured intent into explainable steps
    """

    if not intent or intent.get("intent") == "unknown":
        return {
            "summary": "I could not clearly understand the request.",
            "steps": [],
            "safe_to_execute": False
        }

    action = intent.get("action")
    target = intent.get("target")

    steps = []

    if action == "launch":
        steps.append(f"Locate the application '{target}'")
        steps.append(f"Launch '{target}'")

    elif action == "search":
        steps.append(f"Search for '{target}' on the system")

    else:
        steps.append("Determine appropriate system action")

    return {
        "summary": f"I will {action} {target}.",
        "steps": steps,
        "safe_to_execute": True
    }
