# automation/tool_router.py

from automation.tools.file_tools import (
    open_file,
    search_files,
)

from automation.tools.folder_finder import (
    find_folder_by_name,
)

from automation.tools.input_tools import (
    type_text,
    paste_text,
    mouse_move,
    mouse_click,
    mouse_scroll,
    keyboard_press,
    press_hotkey,
    get_screen_size,
    take_screenshot,
)

from automation.tools.system_tools import (
    open_app,
)

from automation.tools.web_tools import (
    open_url,
    search_web,
    send_whatsapp,
)

from automation.tools.media_tools import (
    play_youtube_video,
)

from automation.tools.ui_tools import (
    wait,
)

from automation.tools.report_tools import (
    summarize_url_to_app,
    research_topic_to_app,
    write_report_to_app,
    gather_topic_to_word,
)
# -----------------------------
# 🔑 SINGLE SOURCE OF TRUTH
# -----------------------------
TOOL_REGISTRY = {
    # Files
    "open_file": open_file,
    "search_files": search_files,

    # Folders
    "open_folder_by_name": find_folder_by_name,

    # Apps & system
    "open_app": open_app,

    # Web
    "open_url": open_url,
    "search_web": search_web,
    "send_whatsapp": send_whatsapp,

    # Media
    "play_youtube_video": play_youtube_video,

    # Input automation
    "type_text": type_text,
    "paste_text": paste_text,
    "mouse_move": mouse_move,
    "mouse_click": mouse_click,
    "mouse_scroll": mouse_scroll,
    "keyboard_press": keyboard_press,
    "press_hotkey": press_hotkey,

    # Utilities
    "get_screen_size": get_screen_size,
    "take_screenshot": take_screenshot,
    "wait": wait,

    # Reports / research
    "summarize_url_to_app": summarize_url_to_app,
    "research_topic_to_app": research_topic_to_app,
    "write_report_to_app": write_report_to_app,
    "gather_topic_to_word": gather_topic_to_word,
}
