"""Offline single-command transcription using a manually downloaded Vosk model."""

from __future__ import annotations

import json
import queue
import time
from pathlib import Path

import sounddevice as sd
from vosk import KaldiRecognizer, Model


class SpeechToText:
    SAMPLE_RATE = 16_000

    def __init__(self, model_path: Path) -> None:
        self.model_path = model_path
        self._model: Model | None = None

    def is_ready(self) -> bool:
        return self.model_path.is_dir()

    def _get_model(self) -> Model:
        if not self.is_ready():
            raise FileNotFoundError(
                "Vosk model not found. Download and extract vosk-model-small-en-us-0.15 into "
                f"{self.model_path} (see README.md)."
            )
        if self._model is None:
            self._model = Model(str(self.model_path))
        return self._model

    def listen_once(self, max_seconds: float = 8.0) -> str:
        """Listen briefly, then return one offline transcript or a useful empty-state message."""
        model = self._get_model()
        audio: queue.Queue[bytes] = queue.Queue()
        recognizer = KaldiRecognizer(model, self.SAMPLE_RATE)
        recognizer.SetWords(False)

        def callback(indata: bytes, _frames: int, _time: object, status: sd.CallbackFlags) -> None:
            if status:
                return
            audio.put(bytes(indata))

        started = time.monotonic()
        final_text = ""
        with sd.RawInputStream(
            samplerate=self.SAMPLE_RATE,
            blocksize=8000,
            dtype="int16",
            channels=1,
            callback=callback,
        ):
            while time.monotonic() - started < max_seconds:
                try:
                    chunk = audio.get(timeout=0.25)
                except queue.Empty:
                    continue
                if recognizer.AcceptWaveform(chunk):
                    final_text = json.loads(recognizer.Result()).get("text", "").strip()
                    if final_text:
                        break
        if not final_text:
            final_text = json.loads(recognizer.FinalResult()).get("text", "").strip()
        return final_text
