import pytest
import requests

from src import reboot as reboot_module
from src.reboot import reboot_device

REBOOT_URL_PATH = "/ISAPI/System/reboot"


@pytest.fixture(autouse=True)
def _env(mock_env):
    yield


def test_reboot_device_success(requests_mock, base_address, sample_ok_status_xml):
    requests_mock.put(f"{base_address}{REBOOT_URL_PATH}", text=sample_ok_status_xml)

    response = reboot_device(base_address)

    assert response["error"] is False
    assert response["message"]["statusCode"] == "1"


def test_reboot_device_http_error(requests_mock, base_address):
    requests_mock.put(
        f"{base_address}{REBOOT_URL_PATH}",
        status_code=503,
        reason="Service Unavailable",
    )

    response = reboot_device(base_address)

    assert response["error"] is True
    assert "HTTP PUT /reboot" in response["message"]


def test_reboot_device_sends_empty_body(requests_mock, base_address, sample_ok_status_xml):
    matcher = requests_mock.put(f"{base_address}{REBOOT_URL_PATH}", text=sample_ok_status_xml)

    reboot_device(base_address)

    assert matcher.last_request.body is None


def test_reboot_device_connection_error_is_success(requests_mock, base_address):
    requests_mock.put(
        f"{base_address}{REBOOT_URL_PATH}",
        exc=requests.ConnectionError("device unreachable"),
    )

    response = reboot_device(base_address)

    assert response["error"] is False
    assert "unreachable" in response["message"]


def test_reboot_device_read_timeout_is_success(requests_mock, base_address):
    requests_mock.put(
        f"{base_address}{REBOOT_URL_PATH}",
        exc=requests.ReadTimeout("read timeout"),
    )

    response = reboot_device(base_address)

    assert response["error"] is False


def test_reboot_device_generic_exception(monkeypatch, base_address):
    def boom(*_args, **_kwargs):
        raise ValueError("unexpected")

    monkeypatch.setattr(reboot_module.session, "put", boom)

    response = reboot_device(base_address)

    assert response["error"] is True
    assert "reboot_device()" in response["message"]
    assert "unexpected" in response["message"]
