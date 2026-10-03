"""One small wrapper around Google's current ``google-genai`` Python SDK."""

from __future__ import annotations

from google import genai
from google.genai import types

from config import GEMINI_MODEL


class GeminiClient:
    """Makes Altron's two kinds of Gemini requests: routing and research."""

    def __init__(self, api_key: str) -> None:
        self.client = genai.Client(api_key=api_key)

    def generate_route(self, system_prompt: str, user_text: str) -> str:
        """Ask Gemini for a JSON route; the parser handles imperfect responses later."""
        response = self.client.models.generate_content(
            model=GEMINI_MODEL,
            contents=user_text,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                temperature=0.2,
            ),
        )
        return (response.text or "").strip()

    def research(self, query: str) -> str:
        """Answer a current-information query with Gemini's Google Search grounding."""
        grounding = types.Tool(google_search=types.GoogleSearch())
        response = self.client.models.generate_content(
            model=GEMINI_MODEL,
            contents=query,
            config=types.GenerateContentConfig(
                tools=[grounding],
                system_instruction=(
                    "You are Altron's research mode. Give a concise, factual answer in "
                    "2–4 short sentences. Mention uncertainty instead of guessing."
                ),
                temperature=0.2,
            ),
        )
        return (response.text or "I could not find a usable answer.").strip()
