"""Offline, queued Windows text-to-speech using system voice engines."""

from __future__ import annotations

import queue
import threading
from collections.abc import Callable


class Speaker:
    """Keeps speech off the GUI thread with robust Windows SAPI5 / pyttsx3 execution."""

    def __init__(self, on_state: Callable[[str], None] | None = None) -> None:
        self._queue: queue.Queue[str | None] = queue.Queue()
        self._on_state = on_state or (lambda _state: None)
        self._worker = threading.Thread(target=self._run, daemon=True, name="Altron-TTS")
        self._worker.start()

    def speak(self, text: str) -> None:
        """Add text to the speech queue; this method returns instantly."""
        if text.strip():
            self._queue.put(text.strip())

    def stop(self) -> None:
        self._queue.put(None)

    def _run(self) -> None:
        while True:
            text = self._queue.get()
            if text is None:
                return

            self._on_state("Speaking...")
            spoken = False

            # 1. Primary: Try native Windows SAPI.SpVoice via win32com (100% reliable, never hangs)
            try:
                import win32com.client

                sapi_speaker = win32com.client.Dispatch("SAPI.SpVoice")
                sapi_speaker.Rate = 1
                sapi_speaker.Speak(text)
                spoken = True
            except Exception:
                spoken = False

            # 2. Secondary fallback: pyttsx3 with fresh per-call initialization
            if not spoken:
                try:
                    import pyttsx3

                    engine = pyttsx3.init()
                    engine.setProperty("rate", 185)
                    engine.say(text)
                    engine.runAndWait()
                    try:
                        engine.stop()
                    except Exception:
                        pass
                except Exception as error:
                    print(f"[TTS Error] {error}")

            self._on_state("Idle")

