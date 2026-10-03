"""Non-intrusive background wake word module."""

from __future__ import annotations

from collections.abc import Callable


class WakeWordListener:
    """Safe wake word listener interface — mic is handled on demand by the HUD UI mic control."""

    def __init__(self, on_detected: Callable[[], None], on_error: Callable[[str], None]) -> None:
        self.on_detected = on_detected
        self.on_error = on_error

    def start(self) -> None:
        # Background microphone locking disabled so direct mic button operates flawlessly
        pass

    def stop(self) -> None:
        pass

