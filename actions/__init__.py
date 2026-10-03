"""Small shared types used by Altron's local action modules."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ActionResult:
    """A result that is safe to show in the GUI and save to the local log."""

    success: bool
    message: str
