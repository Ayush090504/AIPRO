import speech_recognition as sr

def listen_once() -> str | None:
    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=5)

        return recognizer.recognize_google(audio)

    except Exception:
        return None
