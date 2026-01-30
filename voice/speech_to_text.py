import speech_recognition as sr

def listen_once(timeout=5, phrase_time_limit=8) -> str:
    r = sr.Recognizer()

    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        audio = r.listen(
            source,
            timeout=timeout,
            phrase_time_limit=phrase_time_limit
        )

    try:
        return r.recognize_google(audio)
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        return ""