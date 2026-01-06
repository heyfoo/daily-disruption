#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from shutil import get_terminal_size
from typing import Any

try:
    import requests
except ModuleNotFoundError:
    print(
        "Missing dependency 'requests'. Install it with: pip install -r requirements.txt",
        file=sys.stderr,
    )
    raise SystemExit(1)

API_URL = "https://api.quotable.io/random"
DEFAULT_TIMEOUT = (3.05, 10)


@dataclass(frozen=True)
class Quote:
    content: str
    author: str
    tags: tuple[str, ...] = ()


def _supports_color(stream: Any) -> bool:
    if os.environ.get("NO_COLOR") is not None:
        return False

    if not hasattr(stream, "isatty") or not stream.isatty():
        return False

    term = os.environ.get("TERM", "")
    return term.lower() != "dumb"


def _style(text: str, *codes: str, enable: bool) -> str:
    if not enable or not codes:
        return text
    start = "\x1b[" + ";".join(codes) + "m"
    end = "\x1b[0m"
    return f"{start}{text}{end}"


def fetch_random_quote() -> Quote:
    try:
        response = requests.get(API_URL, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
    except requests.Timeout as exc:
        raise RuntimeError("Request timed out while contacting the Quotable API.") from exc
    except requests.ConnectionError as exc:
        raise RuntimeError("Network error while contacting the Quotable API.") from exc
    except requests.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else None
        if status is not None:
            raise RuntimeError(f"Quotable API returned an error (HTTP {status}).") from exc
        raise RuntimeError("Quotable API returned an error response.") from exc
    except requests.RequestException as exc:
        raise RuntimeError("Unexpected error while contacting the Quotable API.") from exc

    try:
        payload: dict[str, Any] = response.json()
    except json.JSONDecodeError as exc:
        raise RuntimeError("Quotable API returned invalid JSON.") from exc

    content = payload.get("content")
    author = payload.get("author")
    tags = payload.get("tags")

    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("Quotable API response was missing quote content.")
    if not isinstance(author, str) or not author.strip():
        raise RuntimeError("Quotable API response was missing the author.")

    tag_list: tuple[str, ...] = ()
    if isinstance(tags, list):
        tag_list = tuple(str(t) for t in tags if str(t).strip())

    return Quote(content=content.strip(), author=author.strip(), tags=tag_list)


def _wrap_lines(text: str, width: int) -> list[str]:
    words = text.split()
    if not words:
        return [""]

    lines: list[str] = []
    current: list[str] = []
    current_len = 0

    for word in words:
        additional = len(word) + (1 if current else 0)
        if current and (current_len + additional) > width:
            lines.append(" ".join(current))
            current = [word]
            current_len = len(word)
        else:
            current.append(word)
            current_len += additional

    if current:
        lines.append(" ".join(current))

    return lines


def format_quote(quote: Quote, *, color: bool) -> str:
    term_width = max(40, min(120, get_terminal_size(fallback=(80, 20)).columns))
    rule = "─" * term_width

    quote_lines = _wrap_lines(f"“{quote.content}”", width=term_width - 2)

    parts: list[str] = [
        _style(rule, "2", enable=color),
        "",
        *[_style(line, "36", "1", enable=color) for line in quote_lines],
        "",
        _style(f"— {quote.author}", "33", "1", enable=color),
    ]

    if quote.tags:
        tags_text = ", ".join(quote.tags)
        parts.append(_style(f"Tags: {tags_text}", "2", enable=color))

    parts.extend(["", _style(rule, "2", enable=color)])

    return "\n".join(parts)


def main() -> int:
    use_color = _supports_color(sys.stdout)

    try:
        quote = fetch_random_quote()
    except RuntimeError as exc:
        msg = (
            "Couldn't fetch a quote right now. "
            "Please check your internet connection and try again.\n"
            f"Details: {exc}"
        )
        print(_style(msg, "31", "1", enable=_supports_color(sys.stderr)), file=sys.stderr)
        return 1

    print(format_quote(quote, color=use_color))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
