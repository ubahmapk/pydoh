"""pydoh: a command-line DNS client for DoH/DoT/DoQ, built on py_doh_core.

Never falls back to classic plaintext UDP/TCP DNS.
"""

from __future__ import annotations

import enum
import signal
import time
from pathlib import Path

import py_doh_core as doh
import typer

from pydoh import color, records
from pydoh import config as config_mod
from pydoh.output import Format, RenderOptions, render

if hasattr(signal, "SIGPIPE"):
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)

app = typer.Typer(add_completion=False, no_args_is_help=True)


class Method(str, enum.Enum):
    GET = "get"
    POST = "post"


def _build_transport(server: str, method: Method):
    if server.startswith("https://"):
        return doh.DohTransport(server, method=method.value)
    if server.startswith("tls://"):
        return doh.DotTransport(server[len("tls://") :])
    if server.startswith("quic://"):
        return doh.DoqTransport(server[len("quic://") :])
    raise typer.BadParameter(
        f"unrecognized server scheme in '{server}' (expected https://, tls://, or quic://)"
    )


@app.command()
def main(
    name: str | None = typer.Argument(None, help="Name to resolve, e.g. example.com"),
    record_types: list[str] | None = typer.Argument(
        None, help="DNS record type(s) to query, e.g. A AAAA MX"
    ),
    server: str | None = typer.Option(
        None, "-s", "--server", help="DoH (https://), DoT (tls://), or DoQ (quic://) server"
    ),
    config_path: Path | None = typer.Option(None, "--config", help="Path to config file"),
    init_config: bool = typer.Option(
        False, "--init-config", help="Write a template config file and exit"
    ),
    method: Method | None = typer.Option(None, "--method", help="DoH query method (get|post)"),
    fmt: Format | None = typer.Option(None, "-f", "--format", help="Output format"),
    question: bool | None = typer.Option(None, "--question/--no-question"),
    answer: bool | None = typer.Option(None, "--answer/--no-answer"),
    authority: bool | None = typer.Option(None, "--authority/--no-authority"),
    additional: bool | None = typer.Option(None, "--additional/--no-additional"),
    all_sections: bool | None = typer.Option(None, "--all/--no-all"),
    stats: bool | None = typer.Option(None, "-S", "--stats/--no-stats"),
    short: bool | None = typer.Option(None, "-r", "--short/--no-short"),
    pretty_ttls: bool | None = typer.Option(None, "--pretty-ttls/--no-pretty-ttls"),
    short_ttls: bool | None = typer.Option(None, "--short-ttls/--no-short-ttls"),
    round_ttls: bool | None = typer.Option(None, "--round-ttls/--no-round-ttls"),
    use_color: bool | None = typer.Option(None, "--color/--no-color"),
) -> None:
    if init_config:
        try:
            written = config_mod.init_config(config_path)
        except FileExistsError as exc:
            typer.echo(f"warning: {exc}", err=True)
            raise typer.Exit(1) from exc
        typer.echo(f"wrote config template to {written}")
        raise typer.Exit(0)

    if name is None:
        raise typer.BadParameter("missing required argument 'name'")

    cfg = config_mod.load_config(config_path)

    resolved_server = config_mod.merge(server, cfg.server, None)
    if not resolved_server:
        hint = ""
        if config_path is None:
            hint = f" (set 'server' in {config_mod.default_config_path()} or pass --server)"
        typer.echo(f"error: no server configured{hint}", err=True)
        raise typer.Exit(1)

    resolved_method = config_mod.merge(
        method, Method(cfg.method) if cfg.method else None, Method.GET
    )

    types = records.normalize(record_types) if record_types else None
    resolved_types = config_mod.merge(types, cfg.default_record_types, records.DEFAULT_RECORD_TYPES)

    resolved_format = config_mod.merge(
        fmt, Format(cfg.format) if cfg.format else None, Format.PRETTY
    )

    resolved_all = config_mod.merge(all_sections, cfg.all, False)
    resolved_answer = config_mod.merge(answer, cfg.answer, True) or resolved_all
    resolved_question = config_mod.merge(question, cfg.question, False) or resolved_all
    resolved_authority = config_mod.merge(authority, cfg.authority, False) or resolved_all
    resolved_additional = config_mod.merge(additional, cfg.additional, False) or resolved_all
    resolved_stats = config_mod.merge(stats, cfg.stats, False) or resolved_all
    resolved_short = config_mod.merge(short, cfg.short, False)
    resolved_pretty_ttls = config_mod.merge(pretty_ttls, cfg.pretty_ttls, True)
    resolved_short_ttls = config_mod.merge(short_ttls, cfg.short_ttls, True)
    resolved_round_ttls = config_mod.merge(round_ttls, cfg.round_ttls, False)
    resolved_color = color.resolve_color(config_mod.merge(use_color, cfg.color, None))

    try:
        transport = _build_transport(resolved_server, resolved_method)
    except doh.DohError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(1) from exc

    start = time.perf_counter()
    try:
        results = transport.resolve_many(name, resolved_types)
    except doh.DohError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(1) from exc
    elapsed = time.perf_counter() - start

    opts = RenderOptions(
        format=resolved_format,
        server=resolved_server,
        show_question=resolved_question,
        show_answer=resolved_answer,
        show_authority=resolved_authority,
        show_additional=resolved_additional,
        show_stats=resolved_stats,
        short=resolved_short,
        pretty_ttls=resolved_pretty_ttls,
        short_ttls=resolved_short_ttls,
        round_ttls=resolved_round_ttls,
        color_enabled=resolved_color,
        elapsed_seconds=elapsed,
    )

    output = render(results, opts)
    if output:
        typer.echo(output)

    if any(r.error is not None for r in results):
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
