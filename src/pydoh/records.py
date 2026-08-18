"""Record-type handling. Validation is delegated to py_doh_core (raises DohError on
unknown types) — no separate record-type table is maintained here.
"""

from __future__ import annotations

DEFAULT_RECORD_TYPES = ["A", "AAAA", "NS", "MX", "TXT", "CNAME"]


def normalize(record_types: list[str]) -> list[str]:
    return [rt.upper() for rt in record_types]
