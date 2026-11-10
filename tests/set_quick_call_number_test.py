import json
import logging

import pytest

from src import sip_params as sip_params_module
from src.sip_params import set_quick_call_number

SIP_PATH = "/ISAPI/System/Network/SIP/StandardSipParam"
KEY_CFG_PATH = "/ISAPI/VideoIntercom/keyCfg/1"
REBOOT_PATH = "/ISAPI/System/reboot"

HOST = "127.0.0.1"
PORT_A = "8085"
PORT_B = "8086"
ADDR_A = f"http://{HOST}:{PORT_A}"
ADDR_B = f"http://{HOST}:{PORT_B}"


@pytest.fixture(autouse=True)
def _env(mock_env):
    yield


@pytest.fixture
def slack_mock(requests_mock):
    return requests_mock.post("https://hooks.slack.com/services/TEST", json={"ok": True})


def _mock_port_ok(
    requests_mock,
    address,
    sample_sip_json,
    sip_ok_response_json,
    sample_key_cfg_xml,
    sample_ok_status_xml,
):
    requests_mock.get(f"{address}{SIP_PATH}", json=sample_sip_json)
    requests_mock.put(f"{address}{SIP_PATH}", json=sip_ok_response_json)
    requests_mock.get(f"{address}{KEY_CFG_PATH}", text=sample_key_cfg_xml)
    requests_mock.put(f"{address}{KEY_CFG_PATH}", text=sample_ok_status_xml)
    requests_mock.put(f"{address}{REBOOT_PATH}", text=sample_ok_status_xml)


def test_full_flow_success(
    requests_mock,
    sample_sip_json,
    sip_ok_response_json,
    sample_key_cfg_xml,
    sample_ok_status_xml,
):
    _mock_port_ok(
        requests_mock,
        ADDR_A,
        sample_sip_json,
        sip_ok_response_json,
        sample_key_cfg_xml,
        sample_ok_status_xml,
    )
    _mock_port_ok(
        requests_mock,
        ADDR_B,
        sample_sip_json,
        sip_ok_response_json,
        sample_key_cfg_xml,
        sample_ok_status_xml,
    )

    set_quick_call_number("3001")

    history = [(r.method, r.url) for r in requests_mock.request_history]
    # Each port emits: GET SIP, PUT SIP, GET keyCfg, PUT keyCfg, PUT reboot
    assert sum(1 for m, u in history if ADDR_A in u) == 5
    assert sum(1 for m, u in history if ADDR_B in u) == 5

    # Check ordering within port A: SIP -> keyCfg -> reboot
    port_a_methods = [(m, u) for m, u in history if ADDR_A in u]
    assert SIP_PATH in port_a_methods[0][1]
    assert KEY_CFG_PATH in port_a_methods[2][1]
    assert REBOOT_PATH in port_a_methods[-1][1]


def test_sip_failure_skips_keycfg_and_reboot(
    requests_mock,
    sample_sip_json,
    sip_ok_response_json,
    sample_key_cfg_xml,
    sample_ok_status_xml,
    slack_mock,
):
    requests_mock.get(f"{ADDR_A}{SIP_PATH}", status_code=500, reason="SIP down")
    # Mock remaining endpoints so test is robust — they should NOT be called.
    key_get = requests_mock.get(f"{ADDR_A}{KEY_CFG_PATH}", text=sample_key_cfg_xml)
    key_put = requests_mock.put(f"{ADDR_A}{KEY_CFG_PATH}", text=sample_ok_status_xml)
    reboot_put = requests_mock.put(f"{ADDR_A}{REBOOT_PATH}", text=sample_ok_status_xml)
    _mock_port_ok(
        requests_mock,
        ADDR_B,
        sample_sip_json,
        sip_ok_response_json,
        sample_key_cfg_xml,
        sample_ok_status_xml,
    )

    set_quick_call_number("3001")

    assert key_get.call_count == 0
    assert key_put.call_count == 0
    assert reboot_put.call_count == 0
    assert slack_mock.call_count >= 1
    slack_body = json.loads(slack_mock.last_request.text)
    assert "SIP" in slack_body["text"]


def test_keycfg_failure_skips_reboot(
    requests_mock,
    sample_sip_json,
    sip_ok_response_json,
    sample_key_cfg_xml,
    sample_ok_status_xml,
    slack_mock,
):
    requests_mock.get(f"{ADDR_A}{SIP_PATH}", json=sample_sip_json)
    requests_mock.put(f"{ADDR_A}{SIP_PATH}", json=sip_ok_response_json)
    requests_mock.get(f"{ADDR_A}{KEY_CFG_PATH}", text=sample_key_cfg_xml)
    requests_mock.put(f"{ADDR_A}{KEY_CFG_PATH}", status_code=500, reason="keyCfg down")
    reboot_put = requests_mock.put(f"{ADDR_A}{REBOOT_PATH}", text=sample_ok_status_xml)
    _mock_port_ok(
        requests_mock,
        ADDR_B,
        sample_sip_json,
        sip_ok_response_json,
        sample_key_cfg_xml,
        sample_ok_status_xml,
    )

    set_quick_call_number("3001")

    assert reboot_put.call_count == 0
    assert slack_mock.call_count >= 1
    slack_body = json.loads(slack_mock.last_request.text)
    assert "keyCfg" in slack_body["text"]


def test_one_port_fails_other_succeeds(
    requests_mock,
    sample_sip_json,
    sip_ok_response_json,
    sample_key_cfg_xml,
    sample_ok_status_xml,
    slack_mock,
):
    # Port A: SIP failure
    requests_mock.get(f"{ADDR_A}{SIP_PATH}", status_code=500, reason="down")
    # Port B: full success
    _mock_port_ok(
        requests_mock,
        ADDR_B,
        sample_sip_json,
        sip_ok_response_json,
        sample_key_cfg_xml,
        sample_ok_status_xml,
    )

    set_quick_call_number("3001")

    port_a_requests = [r for r in requests_mock.request_history if ADDR_A in r.url]
    port_b_requests = [r for r in requests_mock.request_history if ADDR_B in r.url]
    assert len(port_a_requests) == 1  # only the failing SIP GET
    assert len(port_b_requests) == 5
    assert any(REBOOT_PATH in r.url for r in port_b_requests)


def test_reboot_failure_logs_and_continues(
    requests_mock,
    sample_sip_json,
    sip_ok_response_json,
    sample_key_cfg_xml,
    sample_ok_status_xml,
    slack_mock,
):
    requests_mock.get(f"{ADDR_A}{SIP_PATH}", json=sample_sip_json)
    requests_mock.put(f"{ADDR_A}{SIP_PATH}", json=sip_ok_response_json)
    requests_mock.get(f"{ADDR_A}{KEY_CFG_PATH}", text=sample_key_cfg_xml)
    requests_mock.put(f"{ADDR_A}{KEY_CFG_PATH}", text=sample_ok_status_xml)
    requests_mock.put(f"{ADDR_A}{REBOOT_PATH}", status_code=500, reason="reboot down")
    _mock_port_ok(
        requests_mock,
        ADDR_B,
        sample_sip_json,
        sip_ok_response_json,
        sample_key_cfg_xml,
        sample_ok_status_xml,
    )

    set_quick_call_number("3001")

    assert slack_mock.call_count >= 1
    slack_body = json.loads(slack_mock.last_request.text)
    assert "reboot" in slack_body["text"]


def test_set_quick_call_number_missing_env_logs_error(monkeypatch, caplog):
    monkeypatch.delenv("INTERCOM_HOST", raising=False)
    monkeypatch.delenv("INTERCOM_PORTS", raising=False)

    with caplog.at_level(logging.ERROR, logger=sip_params_module.__name__):
        set_quick_call_number("3001")

    assert any("set_quick_call_number()" in r.message for r in caplog.records)
