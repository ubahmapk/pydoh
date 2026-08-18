from pathlib import Path

from pydoh import config


def test_merge_cli_wins():
    assert config.merge("cli", "config", "default") == "cli"


def test_merge_config_wins_when_cli_none():
    assert config.merge(None, "config", "default") == "config"


def test_merge_default_when_both_none():
    assert config.merge(None, None, "default") == "default"


def test_merge_false_cli_value_is_respected():
    # explicit False must not be treated as "unset"
    assert config.merge(False, True, True) is False


def test_load_config_missing_file_returns_defaults(tmp_path: Path):
    cfg = config.load_config(tmp_path / "does-not-exist.toml")
    assert cfg == config.Config()


def test_load_config_reads_known_keys(tmp_path: Path):
    path = tmp_path / "config.toml"
    path.write_text('server = "https://dns.google/dns-query"\nstats = true\n')
    cfg = config.load_config(path)
    assert cfg.server == "https://dns.google/dns-query"
    assert cfg.stats is True
    assert cfg.method is None


def test_init_config_refuses_to_overwrite(tmp_path: Path):
    path = tmp_path / "config.toml"
    config.init_config(path)
    try:
        config.init_config(path)
    except FileExistsError:
        pass
    else:
        raise AssertionError("expected FileExistsError")
