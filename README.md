# AIPRO
AIPROS.
# AIPROS Ai-Powered productivity layer for smart desktop interaction
A privacy-preserving, fully offline AI assistant for your PC.

AIPROS is an AI-powered desktop productivity layer designed to automate workflows, open apps, summarize files, execute system commands, and intelligently interact with your PC — all completely offline.

It uses local LLMs (Ollama), local embeddings (ChromaDB), Whisper speech recognition, TTS, Streamlit UI, and an encrypted SQLite logging system to provide a secure, explainable, voice-enabled AI assistant.

🚀 Project Highlights
✔ 100% Local & Privacy-Preserving

No cloud calls, no server dependencies, no data leaving your machine.

✔ Context-Aware AI

Uses ChromaDB RAG to recall past instructions, documents, and user context.

✔ System-Level Automation

Natural-language commands can:

Open applications

Search files/folders

Automate repetitive tasks

Summarize documents

Perform keyboard/mouse actions (via pyautogui)

✔ Voice + Text Interface

Voice input: Whisper / SpeechRecognition

Voice output: TTS

Clean Streamlit UI with a minimal circular avatar

✔ Explainable AI

Shows:

Intent

Proposed Plan

Execution Summary

before automating anything.

✔ Secure Logging

All logs are encrypted using Fernet before being saved in SQLite.

🏗 Architecture Overview
AIPROS
│
├── 1. User Interaction Layer 
│     - Streamlit UI (text + voice)
│     - Microphone input, TTS output
│
├── 2. Local LLM Reasoning Layer
│     - Ollama model (llama3, mistral, etc.)
│     - Task interpretation + planning
│
├── 3. RAG Context Layer
│     - ChromaDB vector store
│     - Local embeddings + memory
│
├── 4. Explainability Layer
│     - Shows reasoning before execution
│
├── 5. Automation Layer
│     - pyautogui
│     - os / subprocess commands
│
├── 6. Secure Logging Layer
│     - SQLite database
│     - Encrypted with Fernet
│
└── 7. Streamlit UI Layer
      - Clean, minimal dashboard

⚙️ Technologies Used
Component	Technology
Local LLM	Ollama
RAG	ChromaDB
UI	Streamlit
Voice Input	Whisper / SpeechRecognition
Voice Output	pyttsx3 / TTS
Automation	pyautogui, os, subprocess
Logging	SQLite + Fernet
Deployment	PyInstaller (creates .exe)
🧩 Core Features (Detailed)
🔹 1. Local LLM Reasoning Engine

Runs offline via Ollama

Interprets natural commands

Generates step-by-step execution plans

🔹 2. RAG Memory System

Stores user context, documents, history

Retrieves relevant info for better answers

Uses local embeddings only

🔹 3. Explainability Layer

Before performing a task, AIPROS shows:

Intent: “Open Microsoft Word”
Plan: [1] Search app path  [2] Run .exe
Execute? (Yes/No)

🔹 4. Full Desktop Automation

Examples:

“Open Chrome”

“Search for files containing ‘invoice’”

“Summarize this PDF”

“Click the top right button”

“Type this message in Notepad”

🔹 5. Secure Logging

Every action & command is encrypted before saving

Protects sensitive user inputs
