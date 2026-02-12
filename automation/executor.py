# automation/executor.py

from automation.tool_router import TOOL_REGISTRY


def execute_plan(intent: dict, user_input: str) -> dict:
    """
    Executes a single intent produced by the reasoning engine.
    """

    try:
        # Validate intent
        if not isinstance(intent, dict):
            return {"executed": False, "status": "error", "error": "Invalid intent format"}

        mode = intent.get("mode")
        tool_name = intent.get("tool")
        args = intent.get("args", {})

        # Only tool mode is executable
        if mode != "tool":
            return {
                "executed": False,
                "status": "error",
                "error": f"Unsupported mode: {mode}"
            }

        if not tool_name:
            return {
                "executed": False,
                "status": "error",
                "error": "No tool specified"
            }

        tool_fn = TOOL_REGISTRY.get(tool_name)

        if not tool_fn:
            return {
                "executed": False,
                "status": "error",
                "error": f"Tool '{tool_name}' not registered"
            }

        # Execute tool
        result = tool_fn(**args)

        # ---- FIX STARTS HERE ----
        # Normalize tool results safely

        if isinstance(result, dict):
            if result.get("status") in ("executed", "success", "ok"):
                return {
                    "executed": True,
                    "status": "success",
                    "tool": tool_name,
                    "output": result
                }

            if result.get("executed") is True:
                return {
                    "executed": True,
                    "status": "success",
                    "tool": tool_name,
                    "output": result
                }

            if result.get("executed") is False:
                return {
                    "executed": False,
                    "status": "error",
                    "tool": tool_name,
                    "error": result.get("error", result)
                }

            return {
                "executed": True,
                "status": "success",
                "tool": tool_name,
                "output": result
            }

        if result is True:
            return {
                "executed": True,
                "status": "success",
                "tool": tool_name
            }

        if result is False or result is None:
            return {
                "executed": False,
                "status": "error",
                "tool": tool_name,
                "error": "Tool returned no success flag"
            }

        # Any other return type → treat as success but attach output
        return {
            "executed": True,
            "status": "success",
            "tool": tool_name,
            "output": result
        }
        # ---- FIX ENDS HERE ----

    except Exception as e:
        print("[EXECUTOR ERROR]", e)
        return {
            "executed": False,
            "status": "error",
            "error": str(e)
        }
