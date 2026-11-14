"""Voice input/output for JARVIS.

Imports of audio libraries are lazy, so text mode works on machines
without a microphone, speakers, or the voice dependencies installed.
"""

_tts_engine = None


def speak(text: str) -> None:
    """Say text out loud using the OS text-to-speech engine."""
    global _tts_engine
    import pyttsx3

    if _tts_engine is None:
        _tts_engine = pyttsx3.init()
        _tts_engine.setProperty("rate", 180)
        # Prefer a British male voice for the proper JARVIS feel, if available.
        for voice in _tts_engine.getProperty("voices"):
            name = (voice.name or "").lower()
            if "daniel" in name or "british" in name or "en-gb" in str(voice.id).lower():
                _tts_engine.setProperty("voice", voice.id)
                break
    _tts_engine.say(text)
    _tts_engine.runAndWait()


def listen(timeout: float = 6.0, phrase_limit: float = 12.0) -> str | None:
    """Listen on the microphone and return the transcribed text, or None."""
    import speech_recognition as sr

    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.3)
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)
        except sr.WaitTimeoutError:
            return None
    try:
        return recognizer.recognize_google(audio)
    except (sr.UnknownValueError, sr.RequestError):
        return None


def voice_available() -> bool:
    """True if the voice dependencies are installed and a microphone exists."""
    try:
        import pyttsx3  # noqa: F401
        import speech_recognition as sr

        return bool(sr.Microphone.list_microphone_names())
    except Exception:  # noqa: BLE001 — any failure means voice can't be used
        return False
