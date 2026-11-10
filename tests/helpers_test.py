import argparse
import logging

import pytest
from requests.auth import HTTPDigestAuth

from src.utils import helpers
from src.utils.helpers import (
    RequestError,
    digest_authenticator,
    get_arg_parser,
    send_alert_via_slack,
    setup,
    setup_logger,
)


@pytest.fixture(autouse=True)
def _env(mock_env):
    yield


def test_setup_loads_dotenv(monkeypatch):
    called = {}
    monkeypatch.setattr(helpers, "load_dotenv", lambda: called.setdefault("ok", True))
    setup()
    assert called["ok"] is True


def test_setup_logger_adds_handlers(monkeypatch, tmp_path):
    monkeypatch.setenv("LOG_PATH", str(tmp_path / "app.log"))
    root = logging.getLogger()
    for handler in list(root.handlers):
        root.removeHandler(handler)

    try:
        setup_logger()

        assert root.level == logging.INFO
        assert len(root.handlers) == 2
        assert any(isinstance(h, logging.FileHandler) for h in root.handlers)
        assert any(isinstance(h, logging.StreamHandler) for h in root.handlers)
    finally:
        for handler in list(root.handlers):
            handler.close()
            root.removeHandler(handler)


def test_digest_authenticator_uses_env():
    auth = digest_authenticator()
    assert isinstance(auth, HTTPDigestAuth)
    assert auth.username == "admin"
    assert auth.password == "secret"


def test_get_arg_parser_with_number(monkeypatch):
    monkeypatch.setattr("sys.argv", ["setup-intercom", "-n", "61"])
    args = get_arg_parser()
    assert isinstance(args, argparse.Namespace)
    assert args.number == 61


def test_get_arg_parser_without_number(monkeypatch):
    monkeypatch.setattr("sys.argv", ["setup-intercom"])
    args = get_arg_parser()
    assert args.number is None


def test_send_alert_via_slack_success(requests_mock, caplog):
    requests_mock.post("https://hooks.slack.com/services/TEST", json={"ok": True})

    with caplog.at_level(logging.INFO, logger=helpers.__name__):
        send_alert_via_slack("hello")

    assert any("Slack alert sent" in r.message for r in caplog.records)


def test_send_alert_via_slack_http_error(requests_mock, caplog):
    requests_mock.post(
        "https://hooks.slack.com/services/TEST",
        status_code=500,
        reason="Server Error",
    )

    with caplog.at_level(logging.ERROR, logger=helpers.__name__):
        send_alert_via_slack("hello")

    assert any("send_alert_via_slack" in r.message for r in caplog.records)


def test_send_alert_via_slack_timeout(requests_mock, caplog):
    import requests

    requests_mock.post(
        "https://hooks.slack.com/services/TEST",
        exc=requests.Timeout("timeout"),
    )

    with caplog.at_level(logging.ERROR, logger=helpers.__name__):
        send_alert_via_slack("hello")

    assert any("send_alert_via_slack" in r.message for r in caplog.records)


def test_request_error_to_dict():
    error = RequestError(message="boom", error=True)
    assert error.to_dict() == {"error": True, "message": "boom"}


def test_request_error_default_error_false():
    error = RequestError(message="noop")
    assert error.to_dict() == {"error": False, "message": "noop"}
    assert str(error) == "noop"
