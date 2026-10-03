"""Groq intent classification, tolerant JSON parsing, and local action dispatching."""

from __future__ import annotations

import json
import re
from collections import deque
from dataclasses import dataclass
from typing import Any, Callable

from actions import ActionResult
from actions.browser_actions import open_url, web_search
from actions.system_control import open_app, system_brightness, system_volume
from config import HISTORY_LIMIT
from groq_client import GroqClient


ROUTING_PROMPT = """You are Altron, a Windows desktop assistant. Classify EVERY user message.
Return only one valid JSON object, with no prose and no Markdown, in exactly this shape:
{
  "type": "command" | "chat" | "research",
  "steps": [{"action": "...", "target": "...", "value": 0}]
}

Allowed actions are: open_url, open_app, system_control, system_brightness,
web_search, and speak_response. Commands may contain several steps in the exact order
the user requested. For system_control target must be volume_up, volume_down, or mute;
value is the percentage change. For brightness, value is the requested final percentage.
For normal chat, return one speak_response action whose target is a helpful short reply.
For questions needing recent or web-verified facts, use type research and no local actions.
Never invent local actions outside this list. Do not use Markdown code fences."""


@dataclass(slots=True)
class Route:
    type: str
    steps: list[dict[str, Any]]


def parse_route(raw_text: str) -> Route | None:
    """Accept raw JSON and Gemini's occasional ```json fences, without trusting it blindly."""
    cleaned = raw_text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.IGNORECASE)
    if not cleaned.startswith("{"):
        first, last = cleaned.find("{"), cleaned.rfind("}")
        if first >= 0 and last > first:
            cleaned = cleaned[first : last + 1]
    try:
        data = json.loads(cleaned)
    except (json.JSONDecodeError, TypeError):
        return None
    if not isinstance(data, dict) or data.get("type") not in {"command", "chat", "research"}:
        return None
    steps = data.get("steps")
    if not isinstance(steps, list) or not all(isinstance(step, dict) for step in steps):
        return None
    return Route(type=data["type"], steps=steps)


class IntentRouter:
    """Retains only a short session context and turns it into validated local work."""

    def __init__(self, groq: GroqClient) -> None:
        self.groq = groq
        self.history: deque[tuple[str, str]] = deque(maxlen=HISTORY_LIMIT)

    def route(self, user_text: str) -> Route:
        context = "\n".join(f"{speaker}: {message}" for speaker, message in self.history)
        system_prompt = f"{ROUTING_PROMPT}\n\nRecent session context (may be empty):\n{context}"
        raw = self.groq.generate_route(system_prompt, user_text)
        route = parse_route(raw)
        if route is None:
            # A safe fallback: never execute a malformed AI response as a local command.
            route = Route("chat", [{"action": "speak_response", "target": raw or "I could not understand that."}])
        self.history.append(("User", user_text))
        return route

    def remember_reply(self, reply: str) -> None:
        self.history.append(("Altron", reply))

    def execute(self, route: Route, reporter: Callable[[str, str, bool], None]) -> str:
        """Run every validated step in order and report each result to the UI/logger."""
        summaries: list[str] = []
        allowed = {"open_url", "open_app", "system_control", "system_brightness", "web_search", "speak_response"}
        for step in route.steps:
            action = str(step.get("action", "")).strip()
            target = str(step.get("target", "")).strip()
            value = step.get("value", 10)
            if action not in allowed:
                result = ActionResult(False, f"I ignored an unsupported action: {action or 'missing action'}.")
            elif action == "open_url":
                result = open_url(target)
            elif action == "open_app":
                result = open_app(target)
            elif action == "web_search":
                result = web_search(target)
            elif action == "system_brightness":
                result = system_brightness(value)
            elif action == "system_control":
                direction = {"volume_up": "up", "volume_down": "down", "mute": "mute"}.get(target.lower())
                result = system_volume(direction, value) if direction else ActionResult(False, "Unsupported system control request.")
            else:
                result = ActionResult(True, target)
            reporter(action, result.message, result.success)
            summaries.append(result.message)
        return " ".join(summaries).strip()
