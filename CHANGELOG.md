# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-08-17

### Added

- Requires Python 3.10+ (PEP 604 `X | None` union syntax is used throughout;
  Typer resolves annotations at runtime via `get_type_hints()`, which cannot
  evaluate `X | None` before Python 3.10, even with
  `from __future__ import annotations`).
- Initial release. `pydoh` is a command-line DNS client for DoH (RFC 8484),
  DoT (RFC 7858), and DoQ (RFC 9250), built on the
  [`py-doh-core`](https://pypi.org/project/py-doh-core/) bindings and never
  falling back to plaintext DNS.
- Transport selection by server URL scheme: `https://` (DoH), `tls://` (DoT),
  `quic://` (DoQ).
- Five output formats: `pretty`, `column`, `json`, `yaml`, `raw`.
- Section flags (`--question`/`--answer`/`--authority`/`--additional`/`--all`),
  stats block (`-S`/`--stats`), short output (`-r`/`--short`), and TTL
  formatting flags (`--pretty-ttls`, `--short-ttls`, `--round-ttls`).
- Optional TOML config file (`--config`, `--init-config`) with CLI > config >
  default precedence for every setting.
- `NO_COLOR` / `--color` / `--no-color` handling matching the `doh` CLI.

[Unreleased]: https://github.com/ubahmapk/pydoh/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/ubahmapk/pydoh/releases/tag/v0.1.0
