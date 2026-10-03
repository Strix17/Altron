"""Windows-only local system actions used by the command dispatcher."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from ctypes import POINTER, cast

from actions import ActionResult


SYSTEM_ALIASES: dict[str, str] = {
    "settings": "ms-settings:",
    "windows settings": "ms-settings:",
    "setting": "ms-settings:",
    "calculator": "calc.exe",
    "calc": "calc.exe",
    "notepad": "notepad.exe",
    "file explorer": "explorer.exe",
    "explorer": "explorer.exe",
    "my computer": "explorer.exe",
    "this pc": "explorer.exe",
    "task manager": "taskmgr.exe",
    "taskmgr": "taskmgr.exe",
    "control panel": "control.exe",
    "control": "control.exe",
    "paint": "mspaint.exe",
    "mspaint": "mspaint.exe",
    "snipping tool": "snippingtool.exe",
    "cmd": "cmd.exe",
    "command prompt": "cmd.exe",
    "powershell": "powershell.exe",
    "chrome": "chrome.exe",
    "google chrome": "chrome.exe",
    "edge": "msedge.exe",
    "microsoft edge": "msedge.exe",
    "browser": "https://www.google.com",
    "spotify": "spotify:",
    "discord": "discord:",
    "steam": "steam:",
    "word": "winword.exe",
    "microsoft word": "winword.exe",
    "excel": "excel.exe",
    "microsoft excel": "excel.exe",
    "powerpoint": "powerpnt.exe",
}


def _find_windows_app(name: str) -> tuple[str, str]:
    """Search system aliases, Start Menu shortcuts, Desktop, and WindowsApps for any app."""
    query = name.lower().strip()
    if query in SYSTEM_ALIASES:
        return ("alias", SYSTEM_ALIASES[query])

    search_dirs = [
        os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"),
        r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
        os.path.expandvars(r"%USERPROFILE%\Desktop"),
        os.path.expandvars(r"%PUBLIC%\Desktop"),
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WindowsApps"),
    ]

    clean_query = re.sub(r"[^a-z0-9]", "", query)
    matches: list[str] = []

    for directory in search_dirs:
        if not os.path.exists(directory):
            continue
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith((".lnk", ".url", ".exe")):
                    base_name = os.path.splitext(file)[0].lower()
                    clean_base = re.sub(r"[^a-z0-9]", "", base_name)
                    if clean_query in clean_base or clean_base in clean_query:
                        matches.append(os.path.join(root, file))

    if matches:
        return ("shortcut", matches[0])

    return ("fallback", query)


def open_app(name: str) -> ActionResult:
    """Dynamically launch any installed Windows application, shortcut, URI, or setting."""
    normalized = name.lower().strip()
    if not normalized:
        return ActionResult(False, "Please specify an application name to open.")

    kind, target = _find_windows_app(normalized)
    try:
        if kind == "alias":
            if target.endswith(".exe"):
                subprocess.Popen([target], shell=False)
            elif ":" in target:
                os.startfile(target)
            else:
                subprocess.Popen(["cmd", "/c", "start", "", target], shell=True)
        elif kind == "shortcut":
            os.startfile(target)
        else:
            try:
                os.startfile(target)
            except Exception:
                subprocess.Popen(["cmd", "/c", "start", "", target], shell=True)
        return ActionResult(True, f"Opened {name}.")
    except Exception as error:
        return ActionResult(False, f"I could not launch '{name}': {error}")



def system_volume(direction: str, amount: int | float = 10) -> ActionResult:
    """Change the Windows master volume through pycaw."""
    if sys.platform != "win32":
        return ActionResult(False, "Volume control is only implemented for Windows in this version.")
    try:
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

        amount = max(0, min(100, int(amount)))
        device = AudioUtilities.GetSpeakers()
        if hasattr(device, "EndpointVolume") and device.EndpointVolume is not None:
            endpoint = device.EndpointVolume
        elif hasattr(device, "Activate"):
            interface = device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            endpoint = cast(interface, POINTER(IAudioEndpointVolume))
        elif hasattr(device, "_dev") and hasattr(device._dev, "Activate"):
            interface = device._dev.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            endpoint = cast(interface, POINTER(IAudioEndpointVolume))
        else:
            return ActionResult(False, "Could not access system audio endpoint.")
        current = endpoint.GetMasterVolumeLevelScalar() * 100
        direction = direction.lower().strip()
        if direction == "mute":
            endpoint.SetMute(1, None)
            return ActionResult(True, "Muted the system volume.")
        endpoint.SetMute(0, None)
        change = amount if direction in {"up", "increase", "volume_up"} else -amount
        endpoint.SetMasterVolumeLevelScalar(max(0, min(100, current + change)) / 100, None)
        return ActionResult(True, f"Volume is now about {round(max(0, min(100, current + change)))}%.")
    except Exception as error:
        return ActionResult(False, f"I could not change the volume: {error}")


def system_brightness(amount: int | float) -> ActionResult:
    """Set the primary display brightness to a percentage from 0 to 100."""
    try:
        import screen_brightness_control as sbc

        target = max(0, min(100, int(amount)))
        sbc.set_brightness(target)
        return ActionResult(True, f"Set screen brightness to {target}%.")
    except Exception as error:
        return ActionResult(False, f"I could not change brightness: {error}")
