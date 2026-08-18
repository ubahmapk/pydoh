"""ANSI color scheme mirroring doh-cli's color.rs.

Precedence: explicit flag > NO_COLOR > isatty().
"""

from __future__ import annotations

import os
import sys

RESET = "\x1b[0m"
NAME = "\x1b[1;34m"  # purple, bold
TTL = "\x1b[1;32m"  # green, bold
TYPE = "\x1b[1;35m"  # magenta, bold
LABEL = "\x1b[1;37m"  # white, bold


def resolve_color(explicit: bool | None) -> bool:
    if explicit is not None:
        return explicit
    if os.environ.get("NO_COLOR") is not None:
        return False
    return sys.stdout.isatty()


def paint(text: str, code: str, *, enabled: bool) -> str:
    if not enabled:
        return text
    return f"{code}{text}{RESET}"
