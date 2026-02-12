console.log("app.js loaded");

const input = document.getElementById("commandInput");
const sendBtn = document.getElementById("sendBtn");
const toast = document.querySelector(".toast");
const status = document.getElementById("status");

/* -------------------------
   Toast (RESULT feedback)
------------------------- */
function showToast(message, type = "info", duration = null) {
  toast.innerText = message;
  toast.style.opacity = "1";

  toast.style.background =
    type === "success"
      ? "rgba(0,180,120,0.9)"
      : type === "error"
      ? "rgba(220,80,80,0.9)"
      : "rgba(20,24,36,0.95)";
  toast.style.color = "#fff";

  // Clear any existing timer
  if (toast.hideTimer) {
    clearTimeout(toast.hideTimer);
    toast.hideTimer = null;
  }

  // Only auto-hide when duration is explicitly provided
  if (duration !== null) {
    toast.hideTimer = setTimeout(() => {
      toast.style.opacity = "0";
    }, duration);
  }
}
/* -------------------------
   Thinking STATE
------------------------- */
function showThinking() {
  status.classList.remove("hidden");
  status.innerText = "AIPROS is thinking…";

  sendBtn.disabled = true;
  input.disabled = true;
}

function hideThinking() {
  status.classList.add("hidden");

  sendBtn.disabled = false;
  input.disabled = false;
}

/* -------------------------
   🔹 NEW: Quick Command Runner
------------------------- */
function runQuickCommand(commandText) {
  // Remove emojis / symbols safely
  const clean = commandText.replace(/[^\w\s]/g, "").trim();
  input.value = clean;
  sendCommand();
}

/* -------------------------
   Command execution
------------------------- */
async function sendCommand() {
  const text = input.value.trim();
  if (!text) return;

  showThinking();

  try {
    const res = await fetch("/command", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });

    const data = await res.json();
    hideThinking();

    switch (data.status) {
      case "chat":
        // ✅ Persistent until next command
        showToast(data.message || "No response from model.", "info", null);
        break;

      case "chain":
        showToast("Multiple actions queued. Run them one by one.", "info", 8000);
        break;

      case "success":
        showToast(data.message, "success", 6000);
        break;

      case "needs_confirmation":
        showToast(
          "Multiple matches found. Please be more specific.",
          "info",
          8000
        );
        break;

      case "error":
      default:
        showToast(data.message || "Execution failed", "error", 2800);
    }
  } catch (err) {
    hideThinking();
    showToast("Backend not reachable", "error", 2800);
  }

  input.value = "";
}
/* -------------------------
   Events
------------------------- */
sendBtn.addEventListener("click", sendCommand);

input.addEventListener("keydown", (e) => {
  if (e.ctrlKey && e.key === "Enter") {
    sendCommand();
  }
});

/* -------------------------
   🔹 NEW: Button Wiring
------------------------- */
document.querySelectorAll(".cmd-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    runQuickCommand(btn.innerText);
  });
});

const micBtn = document.querySelector(".mic-btn");

async function startVoice() {
  showToast("Listening… Speak now", "info", null);

  try {
    const res = await fetch("/voice", {
      method: "POST"
    });

    const data = await res.json();

    if (data.status !== "ok") {
      showToast(data.message || "Voice failed", "error", 3000);
      return;
    }

    // Show what was heard
    input.value = data.spoken_text;

    // Auto-run it
    sendCommand();

  } catch (err) {
    showToast("Microphone error", "error", 3000);
  }
}

micBtn.addEventListener("click", startVoice);
