import os
from src.sip_params import get_sip_params, put_sip_params
from src.utils.helpers import setup

setup()


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
