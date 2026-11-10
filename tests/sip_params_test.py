import os

import pytest

from src import sip_params as sip_params_module
from src.sip_params import get_sip_params, put_sip_params
from src.utils.helpers import setup

setup()

SIP_PATH = "/ISAPI/System/Network/SIP/StandardSipParam"


class TestSipParamsUnit:
    @pytest.fixture(autouse=True)
    def _env(self, mock_env):
        yield

    def test_get_sip_params_success(self, requests_mock, base_address, sample_sip_json):
        requests_mock.get(f"{base_address}{SIP_PATH}", json=sample_sip_json)

        response = get_sip_params(base_address)

        assert response["error"] is False
        assert response["message"]["standardSipParamList"][0]["quickCallNumber"] == "61"

    def test_get_sip_params_http_error(self, requests_mock, base_address):
        requests_mock.get(
            f"{base_address}{SIP_PATH}", status_code=500, reason="Internal Server Error"
        )

        response = get_sip_params(base_address)

        assert response["error"] is True
        assert "HTTP GET" in response["message"]

    def test_get_sip_params_generic_exception(self, monkeypatch, base_address):
        def boom(*_args, **_kwargs):
            raise ValueError("unexpected")

        monkeypatch.setattr(sip_params_module.session, "get", boom)

        response = get_sip_params(base_address)

        assert response["error"] is True
        assert "get_sip_params()" in response["message"]
        assert "unexpected" in response["message"]

    def test_put_sip_params_success(
        self, requests_mock, base_address, sample_sip_json, sip_ok_response_json
    ):
        requests_mock.get(f"{base_address}{SIP_PATH}", json=sample_sip_json)
        put_matcher = requests_mock.put(f"{base_address}{SIP_PATH}", json=sip_ok_response_json)

        response = put_sip_params(base_address, "3001")

        assert response["error"] is False
        assert response["message"]["statusCode"] == 1
        sent_body = put_matcher.last_request.json()
        assert sent_body["standardSipParamList"][0]["quickCallNumber"] == "3001"

    def test_put_sip_params_http_error(self, requests_mock, base_address, sample_sip_json):
        requests_mock.get(f"{base_address}{SIP_PATH}", json=sample_sip_json)
        requests_mock.put(
            f"{base_address}{SIP_PATH}", status_code=500, reason="Internal Server Error"
        )

        response = put_sip_params(base_address, "3001")

        assert response["error"] is True
        assert "HTTP PUT" in response["message"]

    def test_put_sip_params_get_fails(self, requests_mock, base_address):
        requests_mock.get(f"{base_address}{SIP_PATH}", status_code=401, reason="Unauthorized")
        put_matcher = requests_mock.put(f"{base_address}{SIP_PATH}", json={})

        response = put_sip_params(base_address, "3001")

        assert response["error"] is True
        assert "HTTP GET" in response["message"]
        assert put_matcher.call_count == 0

    def test_put_sip_params_generic_exception(
        self, monkeypatch, requests_mock, base_address, sample_sip_json
    ):
        requests_mock.get(f"{base_address}{SIP_PATH}", json=sample_sip_json)

        def boom(*_args, **_kwargs):
            raise ValueError("unexpected")

        monkeypatch.setattr(sip_params_module.session, "put", boom)

        response = put_sip_params(base_address, "3001")

        assert response["error"] is True
        assert "put_sip_params()" in response["message"]
        assert "unexpected" in response["message"]


@pytest.mark.integration
class TestClass:
    port = 8085
    address = f"http://{os.getenv('INTERCOM_HOST')}:{port}"

    quick_call_number = os.getenv("QUICK_CALL_NUMBER")

    def test_get_response(self):
        response = get_sip_params(self.address)
        response = response["message"]

        assert len(response["standardSipParamList"]) > 0

        quick_call_number = response["standardSipParamList"][0]["quickCallNumber"]

        assert int(quick_call_number) in [61, 3001]
        assert response["callMode"] == "audio"
        assert response["accountSelection"] == "SIP1"
        assert response["callType"] == "standardSip"

    def test_put_response(self):
        response = put_sip_params(self.address, self.quick_call_number)
        response = response["message"]

        assert response["statusCode"] == 1
        assert response["statusString"] == "OK"
        assert response["subStatusCode"] == "ok"
