from automation.tool_router import TOOL_REGISTRY

def execute_plan(intent: dict, raw_text: str | None = None) -> dict:
    tool = intent.get("tool")
    args = intent.get("args", {})

    if not tool:
        return {"executed": False}

    try:
        fn = TOOL_REGISTRY.get(tool)
        if not fn:
            return {"executed": False}

        result = fn(**args)

        # 🔑 NORMALIZE RESULT
        if isinstance(result, dict):
            if result.get("status") in ("executed", "success"):
                return {"executed": True}
            if result.get("status") == "needs_confirmation":
                return {
                    "executed": False,
                    "needs_confirmation": True,
                    **result
                }

        # Tool returned True → success
        if result is True:
            return {"executed": True}

        return {"executed": False}

    except Exception as e:
        return {
            "executed": False,
            "error": str(e)
        }