import speech_recognition as sr
from config import PREFERRED_MIC_NAME

LAST_ERROR = ""

def get_last_error() -> str:
    return LAST_ERROR

def _select_mic_index() -> int | None:
    name_substr = (PREFERRED_MIC_NAME or "").strip().lower()
    if not name_substr:
        return None

    try:
        mic_names = sr.Microphone.list_microphone_names()
    except Exception:
        return None

    for idx, name in enumerate(mic_names):
        if name_substr in name.lower():
            return idx

    return None

def listen_once(timeout=8, phrase_time_limit=8) -> str:
    global LAST_ERROR
    LAST_ERROR = ""

    try:
        mic_names = sr.Microphone.list_microphone_names()
        if not mic_names:
            LAST_ERROR = "No microphone device detected."
            return ""

        device_index = _select_mic_index()
        r = sr.Recognizer()
        with sr.Microphone(device_index=device_index) as source:
            # Give the mic a moment to initialize in server context
            sr.time.sleep(0.2)
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_time_limit
            )

        return r.recognize_google(audio)

    except sr.WaitTimeoutError:
        LAST_ERROR = "No speech detected. Try speaking a little sooner."
        return ""
    except sr.UnknownValueError:
        LAST_ERROR = "Could not understand audio."
        return ""
    except sr.RequestError:
        LAST_ERROR = "Speech service is unavailable or blocked."
        return ""
    except OSError:
        LAST_ERROR = "Microphone is not available or permission was denied."
        return ""
    except Exception:
        LAST_ERROR = "Unexpected microphone error."
        return ""
