"""Application-wide settings and safe loading of the Groq API key."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent
# Load this once before reading optional values such as GROQ_MODEL as well as the key.
load_dotenv(PROJECT_ROOT / ".env")
LOGS_DIR = PROJECT_ROOT / "logs"
VOSK_MODEL_DIR = PROJECT_ROOT / "models" / "vosk-model-small-en-us-0.15"
WAKE_WORD_NAME = "hey jarvis"  # openWakeWord's temporary built-in replacement for "Altron".
GROQ_MODEL = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
HISTORY_LIMIT = 10


def load_settings() -> str:
    """Load .env and return the Groq API key, with a friendly beginner-facing error."""
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is missing. Open the .env file beside main.py, then add "
            "GROQ_API_KEY=your_key_here. Get a free key at https://console.groq.com"
        )
    LOGS_DIR.mkdir(exist_ok=True)
    return api_key
