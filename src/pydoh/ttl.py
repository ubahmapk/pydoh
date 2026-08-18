"""TTL formatting: pretty (h/m/s), short (strip trailing zero units), round (nearest minute)."""

from __future__ import annotations


def format_ttl(
    seconds: int, *, pretty: bool = True, short: bool = True, round_: bool = False
) -> str:
    if round_:
        seconds = (seconds // 60) * 60

    if not pretty:
        return str(seconds)

    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    units = [(hours, "h"), (minutes, "m"), (secs, "s")]

    if short:
        while len(units) > 1 and units[0][0] == 0:
            units.pop(0)
        while len(units) > 1 and units[-1][0] == 0:
            units.pop()

    return "".join(f"{value}{suffix}" for value, suffix in units)
