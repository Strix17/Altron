"""Research mode — answers queries using the Groq LLM's own knowledge."""

from __future__ import annotations

from groq_client import GroqClient


def research_answer(groq: GroqClient, query: str) -> str:
    """Return a short answer using the LLM's training knowledge."""
    return groq.research(query)
