import re
import time
import os
from datetime import datetime
from html import unescape
from urllib.parse import quote_plus, urlparse, parse_qs, unquote

import requests

from automation.tools.system_tools import open_app
from automation.tools.web_tools import open_url
from automation.tools.input_tools import type_text
from llm.ollama_client import call_ollama
from config import REPORTS_DIR
import importlib


APP_URLS = {
    "google docs": "https://docs.google.com/document/u/0/",
    "notion": "https://www.notion.so/",
}


def _open_target_app(app_name: str) -> dict:
    name_l = app_name.lower().strip()
    if name_l in APP_URLS:
        open_url(APP_URLS[name_l])
        return {"executed": True, "via": "url"}
    return open_app(app_name)


def _strip_html(text: str) -> str:
    text = re.sub(r"(?is)<script.*?>.*?</script>", " ", text)
    text = re.sub(r"(?is)<style.*?>.*?</style>", " ", text)
    text = re.sub(r"(?is)<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return unescape(text).strip()


def _normalize_url(url: str) -> str:
    if not url.startswith("http"):
        return "https://" + url
    return url


def _jina_proxy_url(url: str) -> str:
    url = _normalize_url(url)
    stripped = url.replace("https://", "").replace("http://", "")
    return f"https://r.jina.ai/http://{stripped}"


def _fetch_url_text(url: str, max_chars: int = 8000) -> str | None:
    url = _normalize_url(url)
    try:
        res = requests.get(
            url,
            timeout=20,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        res.raise_for_status()
        text = _strip_html(res.text)
        return text[:max_chars]
    except Exception:
        # Fallback: text proxy (handles many JS-heavy pages)
        try:
            proxy = _jina_proxy_url(url)
            res = requests.get(proxy, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
            res.raise_for_status()
            text = _strip_html(res.text)
            return text[:max_chars]
        except Exception:
            return None


def _duckduckgo_search(query: str, max_results: int = 3) -> list[str]:
    urls = [
        f"https://duckduckgo.com/html/?q={quote_plus(query)}",
        f"https://html.duckduckgo.com/html/?q={quote_plus(query)}",
        f"https://lite.duckduckgo.com/lite/?q={quote_plus(query)}",
        _jina_proxy_url(f"https://duckduckgo.com/html/?q={quote_plus(query)}"),
    ]

    for url in urls:
        try:
            res = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
            res.raise_for_status()
            html = res.text

            links = re.findall(r'class="result__a" href="([^"]+)"', html)
            if not links:
                links = re.findall(r'class="result-link" href="([^"]+)"', html)
            if not links:
                links = re.findall(r'href="(https?://[^"]+)"', html)

            cleaned = []
            for link in links:
                if link.startswith("//"):
                    link = "https:" + link
                if not link.startswith("http"):
                    continue
                # Unwrap DuckDuckGo redirect links
                if "duckduckgo.com/l/?" in link and "uddg=" in link:
                    try:
                        qs = parse_qs(urlparse(link).query)
                        if "uddg" in qs:
                            link = unquote(qs["uddg"][0])
                    except Exception:
                        pass
                if "duckduckgo.com" in link:
                    continue
                cleaned.append(link)
                if len(cleaned) >= max_results:
                    break

            if cleaned:
                return cleaned
        except Exception:
            continue

    return []


def _topic_keywords(topic: str) -> list[str]:
    words = re.findall(r"[a-zA-Z0-9]{3,}", topic.lower())
    return list(dict.fromkeys(words))


def _summary_mentions_topic(summary: str, topic: str) -> bool:
    summary_l = summary.lower()
    for w in _topic_keywords(topic):
        if w in summary_l:
            return True
    return False


def _is_relevant(text: str, topic: str) -> bool:
    keywords = _topic_keywords(topic)
    if not keywords:
        return True
    text_l = text.lower()
    hits = sum(1 for w in keywords if w in text_l)
    if len(keywords) == 1:
        return hits >= 1
    if len(keywords) == 2:
        return hits >= 2
    return hits >= max(2, len(keywords) // 2)


def _wikipedia_opensearch(topic: str, max_results: int = 3) -> list[str]:
    try:
        url = (
            "https://en.wikipedia.org/w/api.php"
            f"?action=opensearch&search={quote_plus(topic)}&limit={max_results}&namespace=0&format=json"
        )
        res = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        res.raise_for_status()
        data = res.json()
        if not isinstance(data, list) or len(data) < 4:
            return []
        return data[1] if isinstance(data[1], list) else []
    except Exception:
        return []


def _fetch_wikipedia_summary(topic: str, max_chars: int = 6000) -> str | None:
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote_plus(topic)}"
        res = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        res.raise_for_status()
        data = res.json()
        extract = data.get("extract")
        if not extract:
            return None
        return extract[:max_chars]
    except Exception:
        return None


def _duckduckgo_instant_answer(topic: str, max_chars: int = 2500) -> str | None:
    try:
        res = requests.get(
            "https://api.duckduckgo.com/",
            params={
                "q": topic,
                "format": "json",
                "no_html": 1,
                "skip_disambig": 1,
            },
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        res.raise_for_status()
        data = res.json()
        parts = []
        abstract = (data.get("AbstractText") or "").strip()
        answer = (data.get("Answer") or "").strip()
        if abstract:
            parts.append(abstract)
        if answer and answer not in parts:
            parts.append(answer)
        if not parts:
            for item in data.get("RelatedTopics", []):
                if isinstance(item, dict):
                    txt = (item.get("Text") or "").strip()
                    if txt:
                        parts.append(txt)
                if len(parts) >= 5:
                    break
        if not parts:
            return None
        return "\n".join(parts)[:max_chars]
    except Exception:
        return None


def _extract_relevant_snippet(text: str, topic: str, max_chars: int = 1400) -> str:
    keywords = _topic_keywords(topic)
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chosen = []
    used = 0
    for sent in sentences:
        s = sent.strip()
        if not s:
            continue
        s_l = s.lower()
        if keywords and not any(k in s_l for k in keywords):
            continue
        chosen.append(s)
        used += len(s) + 1
        if used >= max_chars:
            break
    if not chosen:
        return text[:max_chars]
    return " ".join(chosen)[:max_chars]


def _compose_research_text(topic: str, wiki: str | None, instant: str | None, parts: list[str]) -> str:
    sections = [f"Topic: {topic}", ""]
    if wiki:
        sections.append("Wikipedia summary:")
        sections.append(wiki.strip())
        sections.append("")
    if instant:
        sections.append("Instant web answer:")
        sections.append(instant.strip())
        sections.append("")
    if parts:
        sections.append("Web excerpts:")
        for idx, p in enumerate(parts[:3], start=1):
            sections.append(f"{idx}. {p.strip()}")
        sections.append("")
    return "\n".join(sections).strip()


def _summarize_text(text: str, topic: str | None, mode: str = "summary") -> str:
    if mode == "report":
        style = (
            "Write a concise report with headings and short paragraphs. "
            "Include: Title, Overview, Key Points, Conclusion. "
            "No citations or links. Use only the provided content."
        )
    else:
        style = (
            "Summarize concisely in plain text with short paragraphs. "
            "No citations or links. Use only the provided content."
        )

    prompt = f"{style}\n\n"
    if topic:
        prompt += f"Topic: {topic}\n\n"
    prompt += f"Content:\n{text}\n\nSummary:"
    return call_ollama(prompt)


def _focus_app_window(app_name: str) -> bool:
    try:
        import pygetwindow as gw
    except Exception:
        return False

    hints = {
        "word": ["word", "microsoft word"],
        "ms word": ["word", "microsoft word"],
        "notepad": ["notepad"],
        "vs code": ["visual studio code", "code"],
        "vscode": ["visual studio code", "code"],
        "google docs": ["google docs", "docs"],
        "notion": ["notion"],
        "onenote": ["onenote"],
        "libreoffice": ["libreoffice", "writer"],
    }

    search_terms = hints.get(app_name.lower().strip(), [app_name])
    for term in search_terms:
        wins = gw.getWindowsWithTitle(term)
        if not wins:
            continue
        win = wins[0]
        try:
            win.activate()
        except Exception:
            try:
                win.minimize()
                win.restore()
                win.activate()
            except Exception:
                pass
        time.sleep(0.3)
        try:
            cx = win.left + max(40, win.width // 2)
            cy = win.top + max(40, win.height // 2)
            import pyautogui

            pyautogui.click(cx, cy)
        except Exception:
            pass
        return True

    return False


def _type_into_app(text: str, app_name: str):
    # Give the app time to open
    time.sleep(2.0)
    _focus_app_window(app_name)
    time.sleep(0.2)
    type_text(text)


def _is_word_app(name: str) -> bool:
    return name.lower().strip() in {"word", "ms word", "microsoft word"}


def _write_to_word(text: str, title: str | None = None) -> dict:
    try:
        win32 = importlib.import_module("win32com.client")
    except Exception:
        return {"executed": False, "error": "pywin32 not installed"}

    try:
        word = win32.Dispatch("Word.Application")
        word.Visible = False
        doc = word.Documents.Add()
        if title:
            doc.Content.Text = f"{title}\n\n{text}"
        else:
            doc.Content.Text = text
        # Leave document open for user to review/save
        word.Visible = True
        return {"executed": True}
    except Exception as e:
        # Fallback: write to temp txt and open with Word
        try:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            base = title or "report"
            safe = re.sub(r"[^a-zA-Z0-9_-]+", "_", base)[:40] or "report"
            path = REPORTS_DIR / f"{safe}_{ts}.txt"
            path.write_text(text, encoding="utf-8", errors="ignore")
            os.startfile(str(path))
            return {"executed": True, "warning": f"COM failed ({e}); opened fallback {path.name}"}
        except Exception as inner:
            return {"executed": False, "error": f"{e} / fallback failed: {inner}"}


def summarize_url_to_app(url: str, app_name: str, include_sources: bool = False) -> dict:
    if not app_name:
        return {"executed": False, "error": "No app provided"}

    content = _fetch_url_text(url)
    if not content:
        return {"executed": False, "error": "Could not fetch URL"}

    summary = _summarize_text(content, topic=url, mode="summary")

    if _is_word_app(app_name):
        word_result = _write_to_word(summary, title=url)
        if word_result.get("executed"):
            return {"executed": True, "summary": summary}
        # fall back to normal typing if Word automation fails

    open_result = _open_target_app(app_name)
    if not open_result.get("executed"):
        return {"executed": False, "error": "Could not open target app"}

    _type_into_app(summary, app_name)
    return {"executed": True, "summary": summary}


def research_topic_to_app(topic: str, app_name: str, include_sources: bool = False) -> dict:
    if not app_name:
        return {"executed": False, "error": "No app provided"}

    # Prefer Wikipedia if available (more reliable for named topics)
    titles = _wikipedia_opensearch(topic, max_results=3)
    wiki = None
    for title in titles or [topic]:
        wiki = _fetch_wikipedia_summary(title)
        if wiki:
            break
    instant = _duckduckgo_instant_answer(topic)

    parts = []
    links = _duckduckgo_search(topic, max_results=3)
    for link in links:
        text = _fetch_url_text(link, max_chars=6000)
        if text and _is_relevant(text, topic):
            parts.append(_extract_relevant_snippet(text, topic))

    if not parts and not wiki and not instant:
            return {
                "executed": False,
                "error": "Could not fetch search results. Try a direct URL with 'summarize <url> in <app>'.",
            }
    summary = _compose_research_text(topic, wiki, instant, parts)

    if _is_word_app(app_name):
        word_result = _write_to_word(summary, title=topic)
        if word_result.get("executed"):
            return {"executed": True, "summary": summary}
        return {"executed": False, "error": word_result.get("error", "Could not write to Word")}

    open_result = _open_target_app(app_name)
    if not open_result.get("executed"):
        return {"executed": False, "error": "Could not open target app"}

    _type_into_app(summary, app_name)
    return {"executed": True, "summary": summary}


def write_report_to_app(topic: str, app_name: str, include_sources: bool = False) -> dict:
    if not app_name:
        return {"executed": False, "error": "No app provided"}

    titles = _wikipedia_opensearch(topic, max_results=3)
    wiki = None
    for title in titles or [topic]:
        wiki = _fetch_wikipedia_summary(title)
        if wiki:
            break
    instant = _duckduckgo_instant_answer(topic)

    parts = []
    links = _duckduckgo_search(topic, max_results=4)
    for link in links:
        text = _fetch_url_text(link, max_chars=7000)
        if text and _is_relevant(text, topic):
            parts.append(_extract_relevant_snippet(text, topic))

    if not parts and not wiki and not instant:
            return {
                "executed": False,
                "error": "Could not fetch search results. Try a direct URL with 'summarize <url> in <app>'.",
            }
    evidence = _compose_research_text(topic, wiki, instant, parts)
    report = _summarize_text(evidence, topic=topic, mode="report")
    if not _summary_mentions_topic(report, topic):
        report = evidence

    if _is_word_app(app_name):
        word_result = _write_to_word(report, title=topic)
        if word_result.get("executed"):
            return {"executed": True, "summary": report}
        return {"executed": False, "error": word_result.get("error", "Could not write to Word")}

    open_result = _open_target_app(app_name)
    if not open_result.get("executed"):
        return {"executed": False, "error": "Could not open target app"}

    _type_into_app(report, app_name)
    return {"executed": True, "summary": report}


def gather_topic_to_word(topic: str, include_sources: bool = False) -> dict:
    # Prefer Wikipedia summary if available
    titles = _wikipedia_opensearch(topic, max_results=3)
    wiki = None
    for title in titles or [topic]:
        wiki = _fetch_wikipedia_summary(title)
        if wiki:
            break
    instant = _duckduckgo_instant_answer(topic)

    parts = []
    links = _duckduckgo_search(topic, max_results=4)
    for link in links:
        text = _fetch_url_text(link, max_chars=7000)
        if text and _is_relevant(text, topic):
            parts.append(_extract_relevant_snippet(text, topic))

    if not parts and not wiki and not instant:
        return {
            "executed": False,
            "error": "Could not fetch search results. Try a direct URL with 'summarize <url> in word'.",
        }

    combined = _compose_research_text(topic, wiki, instant, parts)

    result = _write_to_word(combined, title=topic)
    if not result.get("executed"):
        return result

    return {"executed": True, "summary": combined}
