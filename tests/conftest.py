import pytest

HOST = "127.0.0.1"
PORT_A = "8085"
PORT_B = "8086"


@pytest.fixture
def base_address():
    return f"http://{HOST}:{PORT_A}"


@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("INTERCOM_HOST", HOST)
    monkeypatch.setenv("INTERCOM_PORTS", f"{PORT_A},{PORT_B}")
    monkeypatch.setenv("INTERCOM_USER", "admin")
    monkeypatch.setenv("INTERCOM_PASSWORD", "secret")
    monkeypatch.setenv("QUICK_CALL_NUMBER", "3001")
    monkeypatch.setenv("SLACK_URL", "https://hooks.slack.com/services/TEST")


@pytest.fixture
def sample_key_cfg_xml():
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<KeyCfg xmlns="http://www.isapi.org/ver20/XMLSchema" version="2.0">'
        "<id>1</id>"
        "<callNumber>61</callNumber>"
        "<enableCallCenter>false</enableCallCenter>"
        "<callMethod>callNumber</callMethod>"
        "<selectBuildingType>singleBuilding</selectBuildingType>"
        "<selectRoomingType>oneColumn</selectRoomingType>"
        "</KeyCfg>"
    )


@pytest.fixture
def sample_ok_status_xml():
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<ResponseStatus version="1.0" xmlns="http://www.hikvision.com/ver10/XMLSchema">'
        "<requestURL></requestURL>"
        "<statusCode>1</statusCode>"
        "<statusString>OK</statusString>"
        "<subStatusCode>ok</subStatusCode>"
        "</ResponseStatus>"
    )


@pytest.fixture
def sample_sip_json():
    return {
        "standardSipParamList": [
            {
                "id": 1,
                "quickCallNumber": "61",
            }
        ],
        "callMode": "audio",
        "accountSelection": "SIP1",
        "callType": "standardSip",
    }


@pytest.fixture
def sip_ok_response_json():
    return {
        "statusCode": 1,
        "statusString": "OK",
        "subStatusCode": "ok",
    }
