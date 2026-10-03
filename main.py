"""Altron's application entry point and background-work coordinator."""

from __future__ import annotations

import threading
from pathlib import Path

import webview

from actions.research import research_answer
from bridge.server import BridgeServer
from command_logger import CommandLogger
from config import LOGS_DIR, VOSK_MODEL_DIR, load_settings
from groq_client import GroqClient
from intent_router import IntentRouter
from voice.speech_to_text import SpeechToText
from voice.text_to_speech import Speaker
from voice.wake_word import WakeWordListener


class AltronController:
    """Connects the pywebview desktop window to Groq, voice, and local actions."""

    def __init__(self, api_key: str) -> None:
        # Start WebSocket bridge so the HTML UI can talk to Python
        self.bridge = BridgeServer(self.submit_text, self.listen_from_microphone)
        self.bridge.start()

        self.groq = GroqClient(api_key)
        self.router = IntentRouter(self.groq)
        self.logger = CommandLogger(LOGS_DIR / "history.jsonl")
        self.speaker = Speaker(self.set_status)
        self.stt = SpeechToText(VOSK_MODEL_DIR)

        self.wake_listener = WakeWordListener(self._wake_detected, self._wake_error)
        self.is_listening = False
        self.wake_listener.start()

        # Slight delay so the UI is loaded before first log appears
        threading.Timer(1.5, lambda: self.add_system_log("Voice engine ready. Click MIC to speak.")).start()

    def run(self) -> None:
        """Open the HTML/CSS/JS frontend as a real native desktop window via pywebview."""
        html_path = Path(__file__).parent / "src-ui" / "index.html"
        webview.create_window(
            "ALTRON // AI DESKTOP ASSISTANT",
            url=html_path.as_uri(),
            width=1280,
            height=780,
            min_size=(1050, 680),
            background_color="#03060B",
        )
        webview.start()
        self.shutdown()

    def set_status(self, status: str) -> None:
        self.bridge.broadcast({"type": "status", "payload": status})

    def add_chat(self, speaker: str, text: str) -> None:
        self.bridge.broadcast({"type": "chat", "speaker": speaker, "text": text})

    def add_system_log(self, message: str, success: bool = True) -> None:
        self.bridge.broadcast({"type": "log", "text": message, "success": success})

    def submit_text(self, text: str, from_voice: bool = False) -> None:
        """Submit typed or spoken text without blocking the event loop."""
        if not text.strip():
            return
        if from_voice:
            self.add_chat("YOU", text)
        threading.Thread(target=self._process_request, args=(text,), daemon=True, name="Altron-Groq").start()

    def _process_request(self, text: str) -> None:
        self.set_status("Thinking...")
        try:
            route = self.router.route(text)
            self.add_system_log(f"Groq classified input as {route.type.upper()}.")
            if route.type == "research":
                reply = research_answer(self.groq, text)
                self.logger.write(text, "research", True, reply)
                self.add_system_log("Research completed.")
            else:
                def report(action: str, message: str, success: bool) -> None:
                    self.logger.write(text, action, success, message)
                    self.add_system_log(message, success)

                reply = self.router.execute(route, report)
                if not reply:
                    reply = "Done."
            self.router.remember_reply(reply)
            self.add_chat("ALTRON", reply)
            self.speaker.speak(reply)
        except Exception as error:
            message = f"I could not complete that request: {error}"
            self.logger.write(text, "error", False, message)
            self.add_system_log(message, False)
            self.add_chat("ALTRON", message)
            self.speaker.speak(message)
        finally:
            self.set_status("Idle")

    def listen_from_microphone(self) -> None:
        """Begin voice command transcription."""
        self._listen("Direct mic request")

    def _wake_detected(self) -> None:
        self.add_system_log("Listening for voice command.")
        self._listen("Voice request")

    def _listen(self, source: str) -> None:
        if self.is_listening:
            return
        self.is_listening = True
        threading.Thread(target=self._record_voice, args=(source,), daemon=True, name="Altron-STT").start()

    def _record_voice(self, _source: str) -> None:
        self.set_status("Listening...")
        try:
            transcript = self.stt.listen_once()
            if transcript:
                self.add_system_log(f"Transcript: {transcript}")
                self.submit_text(transcript, from_voice=True)
            else:
                message = "I did not catch that. Please try again."
                self.add_system_log(message, False)
                self.speaker.speak(message)
        except Exception as error:
            message = str(error)
            self.add_system_log(message, False)
            self.add_chat("ALTRON", message)
        finally:
            self.is_listening = False
            self.set_status("Idle")

    def _wake_error(self, message: str) -> None:
        self.add_system_log(message, False)

    def shutdown(self) -> None:
        self.wake_listener.stop()
        self.speaker.stop()


def main() -> None:
    try:
        api_key = load_settings()
    except RuntimeError as error:
        print(f"\nALTRON SETUP NEEDED: {error}\n")
        return
    AltronController(api_key).run()


if __name__ == "__main__":
    main()

