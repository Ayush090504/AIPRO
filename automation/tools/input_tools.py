import pyautogui
import time

def type_text(text: str):
    pyautogui.write(text, interval=0.05)
    return True

def paste_text(text: str):
    pyautogui.write(text)
    return True

def keyboard_press(key: str):
    pyautogui.press(key)
    return True

def press_hotkey(keys: str):
    pyautogui.hotkey(*keys.split())
    return True

def mouse_move(x: int, y: int):
    pyautogui.moveTo(x, y, duration=0.3)
    return True

def mouse_click(x: int, y: int, button="left"):
    pyautogui.click(x, y, button=button)
    return True

def mouse_scroll(amount: int):
    pyautogui.scroll(amount)
    return True

def get_screen_size():
    return pyautogui.size()

def take_screenshot(filename: str):
    pyautogui.screenshot(filename)
    return True

def wait(seconds: int):
    time.sleep(seconds)
    return True
