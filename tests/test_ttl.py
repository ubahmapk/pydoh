from pydoh.ttl import format_ttl


def test_full_pretty_format():
    assert format_ttl(90061, short=False) == "25h1m1s"


def test_short_strips_leading_and_trailing_zero_units():
    assert format_ttl(86400) == "24h"
    assert format_ttl(300) == "5m"
    assert format_ttl(90) == "1m30s"


def test_zero_ttl_keeps_one_unit():
    assert format_ttl(0) == "0s"


def test_round_ttls_truncates_to_nearest_minute():
    assert format_ttl(125, round_=True) == "2m"


def test_pretty_false_returns_raw_seconds():
    assert format_ttl(300, pretty=False) == "300"
