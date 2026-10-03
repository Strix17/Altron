"""Append-only, local JSONL debugging history. No cloud logging is used."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class CommandLogger:
    def __init__(self, log_file: Path) -> None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        self.log_file = log_file

    def write(self, user_input: str, action: str, success: bool, result: str) -> None:
        record: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "input": user_input,
            "action": action,
            "success": success,
            "result": result,
        }
        with self.log_file.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")
