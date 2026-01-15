# automation/executor.py

from automation.tool_router import TOOL_REGISTRY

def execute_plan(intent: dict) -> dict:
    tool_name = intent.get("tool")
    args = intent.get("args", {})

    if tool_name not in TOOL_REGISTRY:
        return {
            "executed": False,
            "error": f"Tool '{tool_name}' not found"
        }

    try:
        result = TOOL_REGISTRY[tool_name](**args)
        return {
            "executed": True,
            "result": result
        }
    except Exception as e:
        return {
            "executed": False,
            "error": str(e)
        }
