import json
from types import SimpleNamespace

from pydoh.output import Format, RenderOptions, render


class _EnumLike:
    def __init__(self, text: str):
        self._text = text

    def __str__(self) -> str:
        return self._text


def make_answer(name="example.com.", record_type="A", ttl=300, rdata="1.2.3.4"):
    return SimpleNamespace(name=name, record_type=record_type, ttl=ttl, rdata=rdata)


def make_response(answers=None, authorities=None, additionals=None):
    return SimpleNamespace(
        id=1,
        op_code=_EnumLike("OpCode.QUERY"),
        response_code=_EnumLike("ResponseCode.NOERROR"),
        authoritative=False,
        truncated=False,
        recursion_desired=True,
        recursion_available=True,
        authentic_data=False,
        checking_disabled=False,
        question_name="example.com.",
        question_type="A",
        answers=answers or [make_answer()],
        authorities=authorities or [],
        additionals=additionals or [],
        wire_size=42,
    )


def make_result(record_type="A", response=None, error=None):
    return SimpleNamespace(record_type=record_type, response=response, error=error)


def test_pretty_render_includes_answer_row():
    results = [make_result(response=make_response())]
    out = render(results, RenderOptions(format=Format.PRETTY))
    assert "example.com." in out
    assert "1.2.3.4" in out


def test_short_render_is_rdata_only():
    results = [make_result(response=make_response())]
    out = render(results, RenderOptions(format=Format.PRETTY, short=True))
    assert out.strip() == "1.2.3.4"


def test_error_result_is_reported_and_no_response_access():
    results = [make_result(error="unknown record type 'BOGUS'")]
    out = render(results, RenderOptions(format=Format.PRETTY))
    assert "error (A): unknown record type 'BOGUS'" in out


def test_json_render_shape():
    results = [make_result(response=make_response())]
    out = render(results, RenderOptions(format=Format.JSON))
    data = json.loads(out)
    assert data[0]["answer"][0]["rdata"] == "1.2.3.4"


def test_yaml_render_shape():
    results = [make_result(response=make_response())]
    out = render(results, RenderOptions(format=Format.YAML))
    assert "rdata: 1.2.3.4" in out


def test_column_render_no_headers():
    results = [make_result(response=make_response())]
    out = render(results, RenderOptions(format=Format.COLUMN))
    assert "Answer:" not in out
    assert "1.2.3.4" in out


def test_raw_render_has_dig_style_sections():
    results = [make_result(response=make_response())]
    out = render(results, RenderOptions(format=Format.RAW))
    assert ";; ANSWER SECTION:" in out
    assert "opcode: QUERY" in out
