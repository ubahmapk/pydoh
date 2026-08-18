"""TOML config file loading and CLI > config > default precedence merging."""

from __future__ import annotations

import sys
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any, TypeVar

from platformdirs import user_config_dir

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

APP_NAME = "pydoh"

INIT_TEMPLATE = """\
# pydoh config file
# Every key is optional; CLI flags always override values set here.

# server = "https://dns.google/dns-query"
# method = "get"                          # "get" | "post"
# default_record_types = ["A", "AAAA", "NS", "MX", "TXT", "CNAME"]

# format = "pretty"                       # "pretty" | "column" | "json" | "yaml" | "raw"

# question = false
# answer = true
# authority = false
# additional = false
# all = false
# stats = false
# short = false

# pretty_ttls = true
# short_ttls = true
# round_ttls = false

# color = true
"""

T = TypeVar("T")


@dataclass
class Config:
    server: str | None = None
    method: str | None = None
    default_record_types: list[str] | None = None
    format: str | None = None
    question: bool | None = None
    answer: bool | None = None
    authority: bool | None = None
    additional: bool | None = None
    all: bool | None = None
    stats: bool | None = None
    short: bool | None = None
    pretty_ttls: bool | None = None
    short_ttls: bool | None = None
    round_ttls: bool | None = None
    color: bool | None = None


def default_config_path() -> Path:
    return Path(user_config_dir(APP_NAME)) / "config.toml"


def load_config(path: Path | None) -> Config:
    config_path = path or default_config_path()
    if not config_path.exists():
        return Config()

    with config_path.open("rb") as f:
        data: dict[str, Any] = tomllib.load(f)

    known = {f.name for f in fields(Config)}
    return Config(**{k: v for k, v in data.items() if k in known})


def init_config(path: Path | None) -> Path:
    config_path = path or default_config_path()
    if config_path.exists():
        raise FileExistsError(f"config file already exists: {config_path}")
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(INIT_TEMPLATE)
    return config_path


def merge(cli_value: T | None, config_value: T | None, default: T) -> T:
    """CLI flag > TOML config > built-in default."""
    if cli_value is not None:
        return cli_value
    if config_value is not None:
        return config_value
    return default
