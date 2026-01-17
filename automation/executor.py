# automation/executor.py

from automation.tool_router import TOOL_REGISTRY

def execute_plan(intent: dict) -> dict:
    tool = intent.get("tool")
    args = intent.get("args", {})

    if tool not in TOOL_REGISTRY:
        return {"executed": False, "error": "Tool not found"}

    try:
        TOOL_REGISTRY[tool](**args)
        return {"executed": True}
    except Exception as e:
        return {"executed": False, "error": str(e)}
