"""Safe browser actions: opening a page and searching the web."""

from __future__ import annotations

import webbrowser
from urllib.parse import quote_plus

from actions import ActionResult


def open_url(url: str) -> ActionResult:
    """Open a URL in the user's default browser."""
    try:
        clean_url = url.strip()
        if not clean_url:
            return ActionResult(False, "I need a web address to open.")
        if not clean_url.startswith(("https://", "http://")):
            clean_url = f"https://{clean_url}"
        webbrowser.open_new_tab(clean_url)
        return ActionResult(True, f"Opened {clean_url}")
    except Exception as error:
        return ActionResult(False, f"I could not open that website: {error}")


def web_search(query: str) -> ActionResult:
    """Search using Google in the default browser without scraping any websites."""
    if not query.strip():
        return ActionResult(False, "I need words to search for.")
    url = f"https://www.google.com/search?q={quote_plus(query.strip())}"
    result = open_url(url)
    return ActionResult(result.success, f"Searched the web for: {query}" if result.success else result.message)
