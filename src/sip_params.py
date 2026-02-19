import json
import requests
from utils.helpers import digest_authenticator, RequestError, send_alert_via_slack
import os
import logging

logger = logging.getLogger(__name__)
session = requests.Session()


def get_sip_params(address):
    try:
        url = f"{address}/ISAPI/System/Network/SIP/StandardSipParam"
        response = session.get(url, auth=digest_authenticator())
        if response.ok:
            return {"message": response.json(), "error": False}

        raise RequestError(
            error=True, message=f"HTTP GET /: {response.status_code} {response.reason}"
        )
    except RequestError as error:
        return error.toJson()
    except Exception as error:
        error_message = f"❌ get_sip_params(): {str(error)}"
        return {"message": error_message, "error": True}


def put_sip_params(address, quick_call_number):
    try:
        url = f"{address}/ISAPI/System/Network/SIP/StandardSipParam?format=json"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "x-requested-with": "XMLHttpRequest",
        }

        sip_params = get_sip_params(address)
        if not sip_params["error"]:
            sip_params["message"]["standardSipParamList"][0][
                "quickCallNumber"
            ] = quick_call_number
            sip_params.pop("registerStatus", None)
            sip_params = json.dumps(sip_params["message"])

            response = session.put(
                url=url, headers=headers, data=sip_params, auth=digest_authenticator()
            )

            if response.ok:
                return {"message": response.json(), "error": False}

            raise RequestError(
                error=True,
                message=f"HTTP PUT /: {response.status_code} {response.reason}",
            )

        raise RequestError(error=sip_params["error"], message=sip_params["message"])
    except RequestError as error:
        return error.toJson()
    except Exception as error:
        error_message = f"❌ put_sip_params(): {str(error)}"
        return {"message": error_message, "error": True}


def set_quick_call_number(quick_call_number):
    try:
        ports_raw = os.getenv("INTERCOM_PORTS")
        ports_list = ports_raw.split(",")

        for port in ports_list:
            address = f"http://{os.getenv('INTERCOM_HOST')}:{port}"
            response = put_sip_params(address, quick_call_number)
            if not response["error"]:
                message = f"address: {address} quick_call_number {quick_call_number} statusString {response['message']['statusString']}"
                logger.info(f"✅ OK: {message}")
            else:
                error_message = f"❌ ERRO ao definir quick call number: {quick_call_number} em {address}: {response['message']}"
                logger.error(error_message)
                send_alert_via_slack(message=error_message)

    except Exception as error:
        logger.error(f"❌ set_quick_call_number(): {error}")
