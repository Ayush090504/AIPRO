import pyautogui
import time

def type_text(text):
    pyautogui.write(text)
    return True

def paste_text(text):
    pyautogui.write(text)
    return True

def mouse_move(x, y):
    pyautogui.moveTo(x, y)
    return True

def mouse_click(x, y, button="left"):
    pyautogui.click(x, y, button=button)
    return True

def mouse_scroll(amount):
    pyautogui.scroll(amount)
    return True

def keyboard_press(key):
    pyautogui.press(key)
    return True

def press_hotkey(keys):
    pyautogui.hotkey(*keys)
    return True

def get_screen_size():
    return pyautogui.size()

def wait(seconds):
    time.sleep(seconds)
    return True

def take_screenshot(filename):
    pyautogui.screenshot(filename)
    return True
