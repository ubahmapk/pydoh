from types import SimpleNamespace
from unittest.mock import patch

from typer.testing import CliRunner

from pydoh.cli import app

runner = CliRunner()


def make_response():
    return SimpleNamespace(
        id=1,
        op_code="QUERY",
        response_code="NOERROR",
        authoritative=False,
        truncated=False,
        recursion_desired=True,
        recursion_available=True,
        authentic_data=False,
        checking_disabled=False,
        question_name="example.com.",
        question_type="A",
        answers=[SimpleNamespace(name="example.com.", record_type="A", ttl=300, rdata="1.2.3.4")],
        authorities=[],
        additionals=[],
        wire_size=42,
    )


def test_missing_server_errors_cleanly(tmp_path):
    result = runner.invoke(app, ["example.com", "--config", str(tmp_path / "nope.toml")])
    assert result.exit_code == 1
    assert "no server configured" in result.output


def test_successful_query_exits_zero():
    fake_transport = SimpleNamespace(
        resolve_many=lambda name, types: [
            SimpleNamespace(record_type="A", response=make_response(), error=None)
        ]
    )
    with patch("pydoh.cli._build_transport", return_value=fake_transport):
        result = runner.invoke(
            app, ["example.com", "A", "--server", "https://dns.google/dns-query"]
        )
    assert result.exit_code == 0
    assert "1.2.3.4" in result.output


def test_per_type_error_exits_nonzero():
    fake_transport = SimpleNamespace(
        resolve_many=lambda name, types: [
            SimpleNamespace(record_type="BOGUS", response=None, error="unknown record type")
        ]
    )
    with patch("pydoh.cli._build_transport", return_value=fake_transport):
        result = runner.invoke(
            app, ["example.com", "BOGUS", "--server", "https://dns.google/dns-query"]
        )
    assert result.exit_code == 1


def test_init_config_writes_template(tmp_path):
    path = tmp_path / "config.toml"
    result = runner.invoke(app, ["--init-config", "--config", str(path)])
    assert result.exit_code == 0
    assert path.exists()
