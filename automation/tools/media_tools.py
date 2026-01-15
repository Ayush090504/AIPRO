import webbrowser

def play_youtube_video(topic):
    webbrowser.open(f"https://www.youtube.com/results?search_query={topic}")
    return True

def send_whatsapp(recipient, message):
    webbrowser.open(
        f"https://web.whatsapp.com/send?phone={recipient}&text={message}"
    )
    return True
