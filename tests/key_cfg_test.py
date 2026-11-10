import pytest

from src import key_cfg as key_cfg_module
from src.key_cfg import get_key_cfg, put_key_cfg

KEY_CFG_URL_PATH = "/ISAPI/VideoIntercom/keyCfg/1"


@pytest.fixture(autouse=True)
def _env(mock_env):
    yield


def test_get_key_cfg_success(requests_mock, base_address, sample_key_cfg_xml):
    requests_mock.get(f"{base_address}{KEY_CFG_URL_PATH}", text=sample_key_cfg_xml)

    response = get_key_cfg(base_address)

    assert response["error"] is False
    assert response["message"]["callNumber"] == "61"
    assert response["message"]["callMethod"] == "callNumber"
    assert response["message"]["selectRoomingType"] == "oneColumn"


def test_get_key_cfg_http_error(requests_mock, base_address):
    requests_mock.get(
        f"{base_address}{KEY_CFG_URL_PATH}",
        status_code=500,
        reason="Internal Server Error",
    )

    response = get_key_cfg(base_address)

    assert response["error"] is True
    assert "HTTP GET" in response["message"]


def test_get_key_cfg_invalid_xml(requests_mock, base_address):
    requests_mock.get(f"{base_address}{KEY_CFG_URL_PATH}", text="<unclosed>")

    response = get_key_cfg(base_address)

    assert response["error"] is True
    assert "invalid XML" in response["message"] or "get_key_cfg()" in response["message"]


def test_put_key_cfg_success(requests_mock, base_address, sample_key_cfg_xml, sample_ok_status_xml):
    url = f"{base_address}{KEY_CFG_URL_PATH}"
    requests_mock.get(url, text=sample_key_cfg_xml)
    put_matcher = requests_mock.put(url, text=sample_ok_status_xml)

    response = put_key_cfg(base_address, "3001")

    assert response["error"] is False
    assert response["message"]["statusCode"] == "1"
    assert response["message"]["statusString"] == "OK"

    sent_body = put_matcher.last_request.text
    assert "<callNumber>3001</callNumber>" in sent_body
    assert 'xmlns="http://www.isapi.org/ver20/XMLSchema"' in sent_body
    assert put_matcher.last_request.headers["Content-Type"] == "application/xml"


def test_put_key_cfg_preserves_other_fields(
    requests_mock, base_address, sample_key_cfg_xml, sample_ok_status_xml
):
    url = f"{base_address}{KEY_CFG_URL_PATH}"
    requests_mock.get(url, text=sample_key_cfg_xml)
    put_matcher = requests_mock.put(url, text=sample_ok_status_xml)

    put_key_cfg(base_address, "3001")

    sent_body = put_matcher.last_request.text
    assert "<enableCallCenter>false</enableCallCenter>" in sent_body
    assert "<callMethod>callNumber</callMethod>" in sent_body
    assert "<selectBuildingType>singleBuilding</selectBuildingType>" in sent_body
    assert "<selectRoomingType>oneColumn</selectRoomingType>" in sent_body
    assert "<id>1</id>" in sent_body


def test_put_key_cfg_invalid_xml_response(requests_mock, base_address, sample_key_cfg_xml):
    url = f"{base_address}{KEY_CFG_URL_PATH}"
    requests_mock.get(url, text=sample_key_cfg_xml)
    requests_mock.put(url, text="<broken>")

    response = put_key_cfg(base_address, "3001")

    assert response["error"] is True


def test_put_key_cfg_get_fails(requests_mock, base_address):
    url = f"{base_address}{KEY_CFG_URL_PATH}"
    requests_mock.get(url, status_code=401, reason="Unauthorized")
    put_matcher = requests_mock.put(url, text="<ok/>")

    response = put_key_cfg(base_address, "3001")

    assert response["error"] is True
    assert put_matcher.call_count == 0


def test_get_key_cfg_generic_exception(monkeypatch, base_address):
    def boom(*_args, **_kwargs):
        raise ValueError("unexpected")

    monkeypatch.setattr(key_cfg_module.session, "get", boom)

    response = get_key_cfg(base_address)

    assert response["error"] is True
    assert "get_key_cfg()" in response["message"]
    assert "unexpected" in response["message"]


def test_put_key_cfg_generic_exception(
    monkeypatch, requests_mock, base_address, sample_key_cfg_xml
):
    requests_mock.get(f"{base_address}{KEY_CFG_URL_PATH}", text=sample_key_cfg_xml)

    def boom(*_args, **_kwargs):
        raise ValueError("unexpected")

    monkeypatch.setattr(key_cfg_module.session, "put", boom)

    response = put_key_cfg(base_address, "3001")

    assert response["error"] is True
    assert "put_key_cfg()" in response["message"]
    assert "unexpected" in response["message"]
