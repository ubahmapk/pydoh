# pydoh

A command-line DNS client for secure DNS transports: DoH ([RFC 8484](https://www.rfc-editor.org/rfc/rfc8484)),
DoT ([RFC 7858](https://www.rfc-editor.org/rfc/rfc7858)), and DoQ ([RFC 9250](https://www.rfc-editor.org/rfc/rfc9250)).
Never falls back to classic plaintext UDP/TCP DNS.

`pydoh` is a Python/[Typer](https://typer.tiangolo.com/) CLI built on top of
[`py-doh-core`](https://pypi.org/project/py-doh-core/), the Python bindings for
[`doh-core`](https://github.com/ubahmapk/doh). It follows the same flags,
output formats, and config-file conventions as the companion Rust CLI, `doh`.

## Install

```console
uv tool install pydoh
# or
pip install pydoh
```

## Usage

```console
$ pydoh example.com A AAAA --server https://dns.google/dns-query
Answer:
example.com.	5m	A	104.20.23.154
example.com.	5m	A	172.66.147.243
──
Answer:
example.com.	5m	AAAA	2606:4700:10::6814:179a
example.com.	5m	AAAA	2606:4700:10::ac42:93f3
```

If no record types are given, `pydoh` queries `A AAAA NS MX TXT CNAME`.

### Transports

The scheme of `--server`/`-s` selects the transport:

| Scheme | Transport | Default port |
|---|---|---|
| `https://host/path` | DoH | 443 |
| `tls://host[:port]` | DoT | 853 |
| `quic://host[:port]` | DoQ | 853 |

```console
$ pydoh example.com A --server tls://dns.google
$ pydoh example.com A --server quic://dns.adguard.com
```

### Output formats

`-f/--format pretty|column|json|yaml|raw` (default `pretty`):

```console
$ pydoh example.com A --server https://dns.google/dns-query -f json
$ pydoh example.com A --server https://dns.google/dns-query -f yaml -S
$ pydoh example.com A --server https://dns.google/dns-query -r   # rdata only
```

### Flags

| Flag | Default | Notes |
|---|---|---|
| `-s, --server <url>` | none | required (or set in config) |
| `--config <path>` | OS default | override config file location |
| `--init-config` | | write a commented template config and exit |
| `--method get\|post` | `get` | DoH only |
| `-f, --format <fmt>` | `pretty` | `pretty\|column\|json\|yaml\|raw` |
| `--question` / `--no-question` | off | |
| `--answer` / `--no-answer` | on | |
| `--authority` / `--no-authority` | off | |
| `--additional` / `--no-additional` | off | |
| `--all` / `--no-all` | off | show everything + stats |
| `-S, --stats` / `--no-stats` | off | timing, response size, flags, section counts |
| `-r, --short` / `--no-short` | off | rdata only |
| `--pretty-ttls` / `--no-pretty-ttls` | on | e.g. `24h0m0s` |
| `--short-ttls` / `--no-short-ttls` | on | strips zero units: `24h` |
| `--round-ttls` / `--no-round-ttls` | off | round down to nearest minute |
| `--color` / `--no-color` | auto | honors `NO_COLOR`, TTY-detected otherwise |

### Config file

Optional TOML file, every key optional, `--config` overrides the location
(default: your OS's standard config dir for `pydoh`, e.g.
`~/.config/pydoh/config.toml` on Linux, `~/Library/Application Support/pydoh/config.toml`
on macOS). Precedence for every setting is **CLI flag > config file > built-in
default**.

```console
$ pydoh --init-config
wrote config template to /Users/you/Library/Application Support/pydoh/config.toml
```

```toml
server = "https://dns.google/dns-query"
method = "get"
default_record_types = ["A", "AAAA"]
format = "pretty"
answer = true
stats = false
short_ttls = true
color = true
```

Note: `pydoh` uses its own config directory, independent of the Rust `doh`
CLI's config file.

### Exit codes

`0` on full success. `NXDOMAIN` is a normal, successful result — not a
failure. `1` if any queried record type failed to resolve, or on a top-level
error (bad server URL, unknown record type, network failure) before any query
runs.

## Development

```console
uv sync
uv run pytest
uv run ruff check .
uv run ty check
```

## License

MIT
