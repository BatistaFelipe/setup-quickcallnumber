import logging

import pytest

from src import main as main_module
from src.main import _require_env, main


@pytest.fixture(autouse=True)
def _env(mock_env):
    yield


def test_require_env_returns_value(monkeypatch):
    monkeypatch.setenv("FOO_BAR", "value")
    assert _require_env("FOO_BAR") == "value"


def test_require_env_raises_when_missing(monkeypatch):
    monkeypatch.delenv("FOO_BAR", raising=False)
    with pytest.raises(SystemExit, match="FOO_BAR"):
        _require_env("FOO_BAR")


def test_require_env_raises_when_empty(monkeypatch):
    monkeypatch.setenv("FOO_BAR", "")
    with pytest.raises(SystemExit, match="FOO_BAR"):
        _require_env("FOO_BAR")


def test_main_runs_with_cli_number(monkeypatch, caplog):
    monkeypatch.setattr("sys.argv", ["setup-intercom", "-n", "3001"])
    called_with = {}

    def fake_set(qcn):
        called_with["qcn"] = qcn

    monkeypatch.setattr(main_module, "set_quick_call_number", fake_set)
    monkeypatch.setattr(main_module, "setup_logger", lambda: None)
    monkeypatch.setattr(main_module, "setup", lambda: None)

    with caplog.at_level(logging.INFO, logger=main_module.__name__):
        main()

    assert called_with["qcn"] == "3001"
    assert any("Starting" in r.message for r in caplog.records)
    assert any("Finished" in r.message for r in caplog.records)


def test_main_falls_back_to_env_quick_call_number(monkeypatch):
    monkeypatch.setattr("sys.argv", ["setup-intercom"])
    captured = {}
    monkeypatch.setattr(
        main_module, "set_quick_call_number", lambda qcn: captured.setdefault("qcn", qcn)
    )
    monkeypatch.setattr(main_module, "setup_logger", lambda: None)
    monkeypatch.setattr(main_module, "setup", lambda: None)

    main()

    assert captured["qcn"] == "3001"  # from mock_env fixture


def test_main_exits_when_required_env_missing(monkeypatch):
    monkeypatch.delenv("INTERCOM_HOST", raising=False)
    monkeypatch.setattr("sys.argv", ["setup-intercom", "-n", "3001"])
    monkeypatch.setattr(main_module, "setup_logger", lambda: None)
    monkeypatch.setattr(main_module, "setup", lambda: None)

    with pytest.raises(SystemExit, match="INTERCOM_HOST"):
        main()


def test_main_exits_when_quick_call_number_env_missing(monkeypatch):
    monkeypatch.delenv("QUICK_CALL_NUMBER", raising=False)
    monkeypatch.setattr("sys.argv", ["setup-intercom"])
    monkeypatch.setattr(main_module, "setup_logger", lambda: None)
    monkeypatch.setattr(main_module, "setup", lambda: None)

    with pytest.raises(SystemExit, match="QUICK_CALL_NUMBER"):
        main()
