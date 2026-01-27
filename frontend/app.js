console.log("app.js loaded");
const input = document.getElementById("commandInput");
const sendBtn = document.getElementById("sendBtn");
const toast = document.querySelector(".toast");

function showToast(message, type = "info") {
  toast.innerText = message;
  toast.style.opacity = "1";

  toast.style.background =
    type === "success"
      ? "rgba(0,180,120,0.9)"
      : type === "error"
      ? "rgba(220,80,80,0.9)"
      : "rgba(20,24,36,0.95)";

  setTimeout(() => {
    toast.style.opacity = "0";
  }, 2800);
}

async function sendCommand() {
  const text = input.value.trim();
  if (!text) return;

  showToast("AIPROS is thinking…");

  try {
    const res = await fetch("/command", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });

    const data = await res.json();

    switch (data.status) {
      case "chat":
        showToast(data.message, "info");
        break;

      case "success":
        showToast(data.message, "success");
        break;

      case "needs_confirmation":
        showToast("Confirmation required (UI coming next)", "info");
        break;

      case "error":
      default:
        showToast(data.message || "Execution failed", "error");
    }

  } catch (err) {
    showToast("Backend not reachable", "error");
  }

  input.value = "";
}

sendBtn.addEventListener("click", sendCommand);

input.addEventListener("keydown", (e) => {
  if (e.ctrlKey && e.key === "Enter") {
    sendCommand();
  }
});