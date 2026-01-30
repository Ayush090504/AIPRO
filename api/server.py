from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path

from main import AIPROSCore

# -----------------------------
# App
# -----------------------------
app = FastAPI(title="AIPROS API")
core = AIPROSCore()

# -----------------------------
# Paths
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

# -----------------------------
# Serve static frontend
# -----------------------------
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/", response_class=HTMLResponse)
def serve_ui():
    index_file = FRONTEND_DIR / "index.html"
    return index_file.read_text(encoding="utf-8")


# -----------------------------
# API models
# -----------------------------
class CommandRequest(BaseModel):
    text: str


class ResumeRequest(BaseModel):
    choice: str
    data: dict


# -----------------------------
# Command endpoint
# -----------------------------
@app.post("/command")
def run_command(req: CommandRequest):
    print("API_HIT:", req.text)

    try:
        result = core.process_input(req.text)

        # 🟢 Chat response
        if result.get("mode") == "chat":
            return JSONResponse({
                "type": "chat",
                "message": result.get("response", "")
            })

        # 🔵 Command chain
        if result.get("mode") == "chain":
            return JSONResponse({
                "type": "chain",
                "intents": result.get("intents", [])
            })

        # 🟡 Needs confirmation
        if result.get("needs_confirmation"):
            return JSONResponse({
                "type": "needs_confirmation",
                "message": "Multiple matches found",
                "data": result
            })

        # 🟢 Executed successfully
        if result.get("executed"):
            return JSONResponse({
                "type": "success",
                "message": "Command executed successfully"
            })

        # 🔴 Fallback failure
        return JSONResponse({
            "type": "error",
            "message": "Command could not be executed"
        })

    except Exception as e:
        return JSONResponse({
            "type": "error",
            "message": str(e)
        })


# -----------------------------
# Resume after confirmation
# -----------------------------
@app.post("/resume")
def resume_after_confirmation(req: ResumeRequest):
    """
    Used when user selects one option (folder/app/etc.)
    """
    try:
        result = core.process_input(req.choice)

        return JSONResponse({
            "type": "success",
            "message": "Action resumed successfully",
            "result": result
        })

    except Exception as e:
        return JSONResponse({
            "type": "error",
            "message": str(e)
        })

from voice.speech_to_text import listen_once

@app.post("/voice")
def voice_command():
    try:
        text = listen_once()
        if not text:
            return {"status": "error", "message": "Could not understand speech"}

        result = core.process_input(text)

        return {
            "status": "ok",
            "spoken_text": text,
            "result": result
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}