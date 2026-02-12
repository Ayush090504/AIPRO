import json
import math
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

from config import (
    OLLAMA_HOST,
    OLLAMA_MODEL,
    EMBEDDING_MODEL,
    INTENT_SIM_THRESHOLD,
    SCREENSHOT_DIR,
)


INTENT_CATALOG = [
    {
        "tool": "open_folder_by_name",
        "examples": [
            "open my documents folder",
            "show me downloads",
            "open the desktop folder",
            "go to my pictures",
            "find the music folder",
        ],
    },
    {
        "tool": "open_app",
        "examples": [
            "open notepad",
            "launch chrome",
            "start calculator",
            "open visual studio code",
            "open microsoft edge",
        ],
    },
    {
        "tool": "search_web",
        "examples": [
            "search the web for python decorators",
            "look up bitcoin price",
            "google ai news",
            "find information about tesla",
        ],
    },
    {
        "tool": "open_url",
        "examples": [
            "open https://openai.com",
            "go to github.com",
            "visit https://example.com",
        ],
    },
    {
        "tool": "play_youtube_video",
        "examples": [
            "play lo-fi on youtube",
            "search youtube for python tutorial",
            "play meditation music on youtube",
        ],
    },
    {
        "tool": "send_whatsapp",
        "examples": [
            "send whatsapp to 911234567890 hello",
            "message 911234567890 on whatsapp saying hi",
        ],
    },
    {
        "tool": "take_screenshot",
        "examples": [
            "take a screenshot",
            "capture the screen",
            "screenshot now",
        ],
    },
    {
        "tool": "get_screen_size",
        "examples": [
            "what is my screen size",
            "get screen resolution",
            "screen size",
        ],
    },
    {
        "tool": "wait",
        "examples": [
            "wait 3 seconds",
            "pause for 5 seconds",
            "sleep 2 seconds",
        ],
    },
    {
        "tool": "type_text",
        "examples": [
            "type hello world",
            "type my email",
        ],
    },
    {
        "tool": "paste_text",
        "examples": [
            "paste hello world",
            "paste this text",
        ],
    },
    {
        "tool": "keyboard_press",
        "examples": [
            "press enter",
            "press tab",
        ],
    },
    {
        "tool": "press_hotkey",
        "examples": [
            "press ctrl shift s",
            "press alt f4",
        ],
    },
    {
        "tool": "mouse_move",
        "examples": [
            "move mouse to 100 200",
            "move cursor to 400 600",
        ],
    },
    {
        "tool": "mouse_click",
        "examples": [
            "click at 300 400",
            "right click at 500 600",
        ],
    },
    {
        "tool": "mouse_scroll",
        "examples": [
            "scroll down 300",
            "scroll up 200",
        ],
    },
    {
        "tool": "open_file",
        "examples": [
            "open file C:\\Users\\me\\notes.txt",
            "open file \"C:\\Users\\me\\Desktop\\todo.txt\"",
        ],
    },
    {
        "tool": "search_files",
        "examples": [
            "search files for report",
            "find files named budget",
        ],
    },
    {
        "tool": "summarize_url_to_app",
        "examples": [
            "summarize https://example.com in word",
            "summarize https://openai.com in google docs",
        ],
    },
    {
        "tool": "research_topic_to_app",
        "examples": [
            "research ai agents in word",
            "research quantum computing in notion",
        ],
    },
    {
        "tool": "write_report_to_app",
        "examples": [
            "write report on climate change in word",
            "write a report on ai in google docs",
        ],
    },
    {
        "tool": "gather_topic_to_word",
        "examples": [
            "gather ai agents into word",
            "collect info on climate change in word",
            "gather virat kohli in word",
        ],
    },
]


_EXAMPLE_EMBEDS: dict[str, list[float]] = {}


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _embed(text: str) -> list[float] | None:
    try:
        res = requests.post(
            f"{OLLAMA_HOST}/api/embeddings",
            json={"model": EMBEDDING_MODEL, "prompt": text},
            timeout=20,
        )
        res.raise_for_status()
        data = res.json()
        return data.get("embedding")
    except Exception:
        return None


def _get_example_embedding(example: str) -> list[float] | None:
    cached = _EXAMPLE_EMBEDS.get(example)
    if cached:
        return cached
    emb = _embed(example)
    if emb:
        _EXAMPLE_EMBEDS[example] = emb
    return emb


def _extract_after_keywords(text: str, keywords: list[str]) -> str | None:
    text_l = text.lower()
    for kw in keywords:
        if kw in text_l:
            idx = text_l.find(kw) + len(kw)
            value = text[idx:].strip()
            if value:
                return value
    return None


def _extract_quoted(text: str) -> str | None:
    m = re.search(r"['\"]([^'\"]+)['\"]", text)
    if m:
        return m.group(1).strip()
    return None


def _extract_open_target(text: str) -> str | None:
    quoted = _extract_quoted(text)
    if quoted:
        return quoted
    return _extract_after_keywords(text, ["open ", "launch ", "start ", "run ", "show me ", "go to ", "take me to "])


def _extract_search_query(text: str) -> str | None:
    return _extract_after_keywords(text, ["search for ", "search ", "look up ", "google ", "find "])


def _extract_url(text: str) -> str | None:
    m = re.search(r"(https?://[^\s]+)", text, re.IGNORECASE)
    if m:
        return m.group(1)
    m = re.search(r"\b([a-z0-9\-]+\.)+[a-z]{2,}\b", text, re.IGNORECASE)
    if m:
        return m.group(0)
    return None


def _extract_numbers(text: str) -> list[int]:
    return [int(n) for n in re.findall(r"-?\d+", text)]


def _extract_wait_seconds(text: str) -> int | None:
    nums = _extract_numbers(text)
    if not nums:
        return None
    return max(1, nums[0])


def _extract_text_payload(text: str, verbs: list[str]) -> str | None:
    return _extract_after_keywords(text, [v + " " for v in verbs])


def _extract_file_path(text: str) -> str | None:
    quoted = _extract_quoted(text)
    if quoted:
        return quoted
    return _extract_after_keywords(text, ["open file ", "open the file "])


def _split_for_app(text: str) -> tuple[str, str | None]:
    text_l = text.lower()
    for sep in [" in ", " into "]:
        if sep in text_l:
            head, app = text.rsplit(sep, 1)
            return head.strip(), app.strip()
    return text, None


def _strip_prefix(text: str, prefixes: list[str]) -> str:
    text_l = text.lower()
    for p in prefixes:
        if text_l.startswith(p):
            return text[len(p):].strip()
    return text.strip()


def _default_screenshot_path() -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screenshot_{ts}.png"
    return str(Path(SCREENSHOT_DIR) / filename)


def _extract_whatsapp(text: str) -> dict[str, Any] | None:
    parts = text.split()
    if not parts:
        return None
    recipient = None
    for p in parts:
        if p.isdigit() and len(p) >= 8:
            recipient = p
            break
    if not recipient:
        return None
    message = text.split(recipient, 1)[-1].strip()
    return {"recipient": recipient, "message": message}


def _build_intent(tool: str, text: str) -> dict | None:
    if tool == "open_folder_by_name":
        folder = _extract_open_target(text)
        if folder:
            return {"mode": "tool", "tool": tool, "args": {"folder_name": folder}}
        return None

    if tool == "open_app":
        app = _extract_open_target(text)
        if app:
            return {"mode": "tool", "tool": tool, "args": {"app_name": app}}
        return None

    if tool == "search_web":
        query = _extract_search_query(text)
        if query:
            return {"mode": "tool", "tool": tool, "args": {"query": query}}
        return None

    if tool == "open_url":
        url = _extract_url(text)
        if url:
            return {"mode": "tool", "tool": tool, "args": {"url": url}}
        return None

    if tool == "play_youtube_video":
        query = _extract_search_query(text) or _extract_open_target(text)
        if query:
            return {"mode": "tool", "tool": tool, "args": {"topic": query}}
        return None

    if tool == "send_whatsapp":
        args = _extract_whatsapp(text)
        if args:
            return {"mode": "tool", "tool": tool, "args": args}
        return None

    if tool == "take_screenshot":
        filename = _extract_after_keywords(text, ["as ", "to "])
        if not filename:
            filename = _default_screenshot_path()
        return {"mode": "tool", "tool": tool, "args": {"filename": filename}}

    if tool == "get_screen_size":
        return {"mode": "tool", "tool": tool, "args": {}}

    if tool == "wait":
        seconds = _extract_wait_seconds(text)
        if seconds is None:
            return None
        return {"mode": "tool", "tool": tool, "args": {"seconds": seconds}}

    if tool == "type_text":
        payload = _extract_text_payload(text, ["type"])
        if not payload:
            return None
        return {"mode": "tool", "tool": tool, "args": {"text": payload}}

    if tool == "paste_text":
        payload = _extract_text_payload(text, ["paste"])
        if not payload:
            return None
        return {"mode": "tool", "tool": tool, "args": {"text": payload}}

    if tool == "keyboard_press":
        key = _extract_text_payload(text, ["press"])
        if not key:
            return None
        return {"mode": "tool", "tool": tool, "args": {"key": key.strip()}}

    if tool == "press_hotkey":
        keys = _extract_text_payload(text, ["press"])
        if not keys:
            return None
        return {"mode": "tool", "tool": tool, "args": {"keys": keys.strip()}}

    if tool == "mouse_move":
        nums = _extract_numbers(text)
        if len(nums) < 2:
            return None
        return {"mode": "tool", "tool": tool, "args": {"x": nums[0], "y": nums[1]}}

    if tool == "mouse_click":
        nums = _extract_numbers(text)
        if len(nums) < 2:
            return None
        button = "right" if "right" in text.lower() else "left"
        return {
            "mode": "tool",
            "tool": tool,
            "args": {"x": nums[0], "y": nums[1], "button": button},
        }

    if tool == "mouse_scroll":
        nums = _extract_numbers(text)
        if not nums:
            return None
        amt = nums[0]
        if "down" in text.lower():
            amt = -abs(amt)
        return {"mode": "tool", "tool": tool, "args": {"amount": amt}}

    if tool == "open_file":
        path = _extract_file_path(text)
        if not path:
            return None
        return {"mode": "tool", "tool": tool, "args": {"filepath": path}}

    if tool == "search_files":
        query = _extract_search_query(text)
        if not query:
            return None
        return {"mode": "tool", "tool": tool, "args": {"query": query}}

    if tool == "summarize_url_to_app":
        head, app = _split_for_app(text)
        if not app:
            return None
        url = _extract_url(head)
        if not url:
            return None
        return {"mode": "tool", "tool": tool, "args": {"url": url, "app_name": app}}

    if tool == "research_topic_to_app":
        head, app = _split_for_app(text)
        if not app:
            return None
        topic = _strip_prefix(head, ["research "])
        if not topic:
            return None
        return {"mode": "tool", "tool": tool, "args": {"topic": topic, "app_name": app}}

    if tool == "write_report_to_app":
        head, app = _split_for_app(text)
        if not app:
            return None
        topic = _strip_prefix(head, ["write report on ", "write a report on ", "write report ", "write a report "])
        if not topic:
            return None
        return {"mode": "tool", "tool": tool, "args": {"topic": topic, "app_name": app}}

    if tool == "gather_topic_to_word":
        head, app = _split_for_app(text)
        # Only Word is supported for this automation path
        if not app or app.lower() not in {"word", "ms word", "microsoft word"}:
            return None
        topic = _strip_prefix(head, ["gather ", "collect info on ", "collect "])
        if not topic:
            return None
        return {"mode": "tool", "tool": tool, "args": {"topic": topic}}

    return None


def _heuristic_common_folders(text: str) -> dict | None:
    text_l = text.lower()
    folder_names = ["documents", "document", "docs", "downloads", "desktop", "pictures", "photos", "videos", "music"]
    verbs = ["open", "show", "show me", "go to", "take me to", "launch", "start"]
    if any(v in text_l for v in verbs):
        for name in folder_names:
            if name in text_l:
                return {
                    "mode": "tool",
                    "tool": "open_folder_by_name",
                    "args": {"folder_name": name},
                }
    return None


def _heuristic_simple_tools(text: str) -> dict | None:
    text_l = text.lower()
    if "screenshot" in text_l or "screen shot" in text_l or "capture screen" in text_l:
        return {"mode": "tool", "tool": "take_screenshot", "args": {"filename": _default_screenshot_path()}}
    if "screen size" in text_l or "screen resolution" in text_l:
        return {"mode": "tool", "tool": "get_screen_size", "args": {}}
    return None


def _heuristic_report_tools(text: str) -> dict | None:
    text_l = text.lower()
    if " in " not in text_l:
        return None

    if text_l.startswith("summarize"):
        url = _extract_url(text)
        head, app = _split_for_app(text)
        if url and app:
            return {
                "mode": "tool",
                "tool": "summarize_url_to_app",
                "args": {"url": url, "app_name": app},
            }

    if text_l.startswith("research "):
        head, app = _split_for_app(text)
        if app:
            topic = _strip_prefix(head, ["research "])
            if topic:
                return {
                    "mode": "tool",
                    "tool": "research_topic_to_app",
                    "args": {"topic": topic, "app_name": app},
                }

    if text_l.startswith("write report") or text_l.startswith("write a report"):
        head, app = _split_for_app(text)
        if app:
            topic = _strip_prefix(head, ["write report on ", "write a report on ", "write report ", "write a report "])
            if topic:
                return {
                    "mode": "tool",
                    "tool": "write_report_to_app",
                    "args": {"topic": topic, "app_name": app},
                }

    return None


def classify_intent_embedding(text: str) -> dict | None:
    query_vec = _embed(text)
    if not query_vec:
        return None

    best_tool = None
    best_score = 0.0

    for entry in INTENT_CATALOG:
        tool = entry["tool"]
        for example in entry["examples"]:
            ex_vec = _get_example_embedding(example)
            if not ex_vec:
                continue
            score = _cosine(query_vec, ex_vec)
            if score > best_score:
                best_score = score
                best_tool = tool

    if not best_tool or best_score < INTENT_SIM_THRESHOLD:
        return None

    return _build_intent(best_tool, text)


def classify_intent_llm(text: str) -> dict | None:
    prompt = (
        "You are an intent classifier. "
        "Return ONLY a JSON object with keys: mode, tool, args. "
        "Valid tools: open_app(app_name), open_folder_by_name(folder_name), "
        "search_web(query), open_url(url), play_youtube_video(topic), "
        "send_whatsapp(recipient, message), open_file(filepath), search_files(query), "
        "type_text(text), paste_text(text), keyboard_press(key), press_hotkey(keys), "
        "mouse_move(x,y), mouse_click(x,y,button), mouse_scroll(amount), "
        "get_screen_size(), take_screenshot(filename), wait(seconds), "
        "summarize_url_to_app(url,app_name), research_topic_to_app(topic,app_name), "
        "write_report_to_app(topic,app_name), gather_topic_to_word(topic). "
        "If you are unsure, return {\"mode\":\"unknown\"}.\n\n"
        f"Text: {text}\n"
        "JSON:"
    )

    try:
        res = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0, "num_predict": 120},
            },
            timeout=30,
        )
        res.raise_for_status()
        raw = res.json().get("response", "").strip()
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            return None
        data = json.loads(match.group(0))
    except Exception:
        return None

    if not isinstance(data, dict):
        return None

    if data.get("mode") != "tool":
        return None

    tool = data.get("tool")
    args = data.get("args")
    if not tool or not isinstance(args, dict):
        return None

    if tool == "take_screenshot" and not args.get("filename"):
        args["filename"] = _default_screenshot_path()

    if tool == "wait" and "seconds" in args:
        try:
            args["seconds"] = max(1, int(args["seconds"]))
        except Exception:
            return None

    return {"mode": "tool", "tool": tool, "args": args}


def classify_intent_hybrid(text: str) -> dict | None:
    heur = _heuristic_common_folders(text)
    if heur:
        return heur
    heur = _heuristic_simple_tools(text)
    if heur:
        return heur
    heur = _heuristic_report_tools(text)
    if heur:
        return heur

    intent = classify_intent_embedding(text)
    if intent:
        return intent
    return classify_intent_llm(text)
