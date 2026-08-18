"""Output rendering: Format enum and pretty/column/json/yaml/raw renderers.

Renderers read attributes duck-typed (`.name`, `.ttl`, `.record_type`, `.rdata`,
`.answers`, ...) rather than importing the compiled py_doh_core classes, so tests
can pass plain stand-in objects without a real network call.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Any, Protocol

import yaml

from pydoh import color
from pydoh.ttl import format_ttl


class Format(str, enum.Enum):
    PRETTY = "pretty"
    COLUMN = "column"
    JSON = "json"
    YAML = "yaml"
    RAW = "raw"


class Answer(Protocol):
    name: str
    record_type: str
    ttl: int
    rdata: str


class ParsedResponse(Protocol):
    id: int
    op_code: Any
    response_code: Any
    authoritative: bool
    truncated: bool
    recursion_desired: bool
    recursion_available: bool
    authentic_data: bool
    checking_disabled: bool
    question_name: str
    question_type: str
    answers: list[Answer]
    authorities: list[Answer]
    additionals: list[Answer]
    wire_size: int


class QueryResult(Protocol):
    record_type: str
    response: ParsedResponse | None
    error: str | None


@dataclass
class RenderOptions:
    format: Format = Format.PRETTY
    server: str = ""
    show_question: bool = False
    show_answer: bool = True
    show_authority: bool = False
    show_additional: bool = False
    show_stats: bool = False
    short: bool = False
    pretty_ttls: bool = True
    short_ttls: bool = True
    round_ttls: bool = False
    color_enabled: bool = False
    elapsed_seconds: float = 0.0


def _enum_name(value: Any) -> str:
    text = str(value)
    return text.rsplit(".", 1)[-1]


def _fmt_ttl(opts: RenderOptions, ttl: int) -> str:
    return format_ttl(ttl, pretty=opts.pretty_ttls, short=opts.short_ttls, round_=opts.round_ttls)


def _answer_dict(a: Answer, opts: RenderOptions) -> dict[str, Any]:
    return {"name": a.name, "ttl": _fmt_ttl(opts, a.ttl), "type": a.record_type, "rdata": a.rdata}


def _stats_dict(result: QueryResult, opts: RenderOptions) -> dict[str, Any] | None:
    resp = result.response
    if resp is None:
        return None
    return {
        "server": opts.server,
        "elapsed_ms": round(opts.elapsed_seconds * 1000, 2),
        "id": resp.id,
        "opcode": _enum_name(resp.op_code),
        "status": _enum_name(resp.response_code),
        "flags": {
            "qr": True,
            "aa": resp.authoritative,
            "tc": resp.truncated,
            "rd": resp.recursion_desired,
            "ra": resp.recursion_available,
            "ad": resp.authentic_data,
            "cd": resp.checking_disabled,
        },
        "query_size": len(resp.answers) + len(resp.authorities) + len(resp.additionals),
        "response_size": resp.wire_size,
    }


def render(results: list[QueryResult], opts: RenderOptions) -> str:
    if opts.format is Format.JSON:
        return _render_json(results, opts)
    if opts.format is Format.YAML:
        return _render_yaml(results, opts)
    if opts.format is Format.RAW:
        return _render_raw(results, opts)
    if opts.format is Format.COLUMN:
        return _render_column(results, opts)
    return _render_pretty(results, opts)


def _label(text: str, opts: RenderOptions) -> str:
    return color.paint(text, color.LABEL, enabled=opts.color_enabled)


def _row(a: Answer, opts: RenderOptions) -> str:
    name = color.paint(a.name, color.NAME, enabled=opts.color_enabled)
    ttl = color.paint(_fmt_ttl(opts, a.ttl), color.TTL, enabled=opts.color_enabled)
    rtype = color.paint(a.record_type, color.TYPE, enabled=opts.color_enabled)
    return f"{name}\t{ttl}\t{rtype}\t{a.rdata}"


def _render_pretty(results: list[QueryResult], opts: RenderOptions) -> str:
    blocks: list[str] = []
    for result in results:
        if result.error is not None:
            blocks.append(f"error ({result.record_type}): {result.error}")
            continue

        resp = result.response
        assert resp is not None
        lines: list[str] = []

        if opts.show_question:
            lines.append(_label("Question:", opts))
            lines.append(f"{resp.question_name}\t{resp.question_type}")

        if opts.show_answer:
            if opts.short:
                lines.extend(a.rdata for a in resp.answers)
            else:
                lines.append(_label("Answer:", opts))
                lines.extend(_row(a, opts) for a in resp.answers)

        if opts.show_authority:
            lines.append(_label("Authority:", opts))
            lines.extend(_row(a, opts) for a in resp.authorities)

        if opts.show_additional:
            lines.append(_label("Additional:", opts))
            lines.extend(_row(a, opts) for a in resp.additionals)

        if opts.show_stats:
            stats = _stats_dict(result, opts)
            if stats is not None:
                lines.append(_label("Stats:", opts))
                lines.append(
                    f"server={stats['server']} elapsed={stats['elapsed_ms']}ms "
                    f"id={stats['id']} opcode={stats['opcode']} status={stats['status']} "
                    f"response_size={stats['response_size']}"
                )

        blocks.append("\n".join(lines))

    return "\n──\n".join(blocks)


def _render_column(results: list[QueryResult], opts: RenderOptions) -> str:
    blocks: list[str] = []
    for result in results:
        if result.error is not None:
            blocks.append(f"error ({result.record_type}): {result.error}")
            continue

        resp = result.response
        assert resp is not None

        if opts.short:
            blocks.append("\n".join(a.rdata for a in resp.answers))
            continue

        rows = [(a.record_type, _fmt_ttl(opts, a.ttl), a.rdata) for a in resp.answers]
        type_w = max((len(r[0]) for r in rows), default=0)
        ttl_w = max((len(r[1]) for r in rows), default=0)
        blocks.append(
            "\n".join(f"{rtype:>{type_w}}  {ttl:>{ttl_w}}  {rdata}" for rtype, ttl, rdata in rows)
        )

    return "\n".join(blocks)


def _build_reply(result: QueryResult, opts: RenderOptions) -> dict[str, Any]:
    reply: dict[str, Any] = {"server": opts.server}

    if result.error is not None:
        reply["error"] = result.error
        return reply

    resp = result.response
    assert resp is not None

    if opts.show_question:
        reply["question"] = {"name": resp.question_name, "type": resp.question_type}
    if opts.show_answer:
        reply["answer"] = [_answer_dict(a, opts) for a in resp.answers]
    if opts.show_authority:
        reply["authority"] = [_answer_dict(a, opts) for a in resp.authorities]
    if opts.show_additional:
        reply["additional"] = [_answer_dict(a, opts) for a in resp.additionals]
    if opts.show_stats:
        stats = _stats_dict(result, opts)
        if stats is not None:
            reply["stats"] = stats

    return reply


def _render_json(results: list[QueryResult], opts: RenderOptions) -> str:
    import json

    replies = [_build_reply(r, opts) for r in results]
    return json.dumps(replies, indent=2)


def _render_yaml(results: list[QueryResult], opts: RenderOptions) -> str:
    replies = [_build_reply(r, opts) for r in results]
    return yaml.safe_dump(replies, sort_keys=False).rstrip("\n")


def _render_raw(results: list[QueryResult], opts: RenderOptions) -> str:
    blocks: list[str] = []
    for result in results:
        if result.error is not None:
            blocks.append(f";; error ({result.record_type}): {result.error}")
            continue

        resp = result.response
        assert resp is not None
        lines: list[str] = []
        lines.append(
            f";; opcode: {_enum_name(resp.op_code)}, "
            f"status: {_enum_name(resp.response_code)}, id: {resp.id}"
        )
        flags = []
        if resp.recursion_desired:
            flags.append("rd")
        if resp.recursion_available:
            flags.append("ra")
        if resp.authoritative:
            flags.append("aa")
        if resp.truncated:
            flags.append("tc")
        if resp.authentic_data:
            flags.append("ad")
        if resp.checking_disabled:
            flags.append("cd")
        lines.append(f";; flags: {' '.join(flags)}")

        if opts.show_question:
            lines.append(";; QUESTION SECTION:")
            lines.append(f";{resp.question_name}\tIN\t{resp.question_type}")

        if opts.show_answer:
            lines.append(";; ANSWER SECTION:")
            lines.extend(
                f"{a.name}\t{_fmt_ttl(opts, a.ttl)}\tIN\t{a.record_type}\t{a.rdata}"
                for a in resp.answers
            )

        if opts.show_authority:
            lines.append(";; AUTHORITY SECTION:")
            lines.extend(
                f"{a.name}\t{_fmt_ttl(opts, a.ttl)}\tIN\t{a.record_type}\t{a.rdata}"
                for a in resp.authorities
            )

        if opts.show_additional:
            lines.append(";; ADDITIONAL SECTION:")
            lines.extend(
                f"{a.name}\t{_fmt_ttl(opts, a.ttl)}\tIN\t{a.record_type}\t{a.rdata}"
                for a in resp.additionals
            )

        blocks.append("\n".join(lines))

    return "\n\n".join(blocks)
