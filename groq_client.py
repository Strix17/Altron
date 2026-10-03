"""Thin wrapper around the Groq Python SDK (OpenAI-compatible chat API)."""

from __future__ import annotations

from groq import Groq

from config import GROQ_MODEL


class GroqClient:
    """Makes Altron's two kinds of Groq requests: routing and research/chat."""

    def __init__(self, api_key: str) -> None:
        self.client = Groq(api_key=api_key)

    def _chat(self, system_prompt: str, user_text: str, temperature: float = 0.2) -> str:
        """Base helper — send a two-turn conversation and return the reply text."""
        response = self.client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text},
            ],
            temperature=temperature,
            max_tokens=800,  # Stay within Groq free tier OTPM limit (1000 max)
        )
        return (response.choices[0].message.content or "").strip()

    def generate_route(self, system_prompt: str, user_text: str) -> str:
        """Ask the model to classify the user request and return a JSON route."""
        return self._chat(system_prompt, user_text, temperature=0.2)

    def research(self, query: str) -> str:
        """Answer a question as best the model can from its training knowledge."""
        system = (
            "You are Altron's research assistant. Answer the user's question concisely "
            "in 2–4 short sentences using your own knowledge. If the answer could have "
            "changed recently (news, stock prices, sports scores), tell the user your "
            "knowledge may be outdated and suggest they verify online."
        )
        return self._chat(system, query, temperature=0.3)
