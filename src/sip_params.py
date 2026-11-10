import json
import logging
import os

import requests

from .key_cfg import put_key_cfg
from .reboot import reboot_device
from .utils.helpers import RequestError, digest_authenticator, send_alert_via_slack

logger = logging.getLogger(__name__)
session = requests.Session()

REQUEST_TIMEOUT_SECONDS = 15


def get_sip_params(address):
    try:
        url = f"{address}/ISAPI/System/Network/SIP/StandardSipParam"
        response = session.get(url, auth=digest_authenticator(), timeout=REQUEST_TIMEOUT_SECONDS)
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
            sip_params["message"]["standardSipParamList"][0]["quickCallNumber"] = quick_call_number
            sip_params.pop("registerStatus", None)
            sip_params = json.dumps(sip_params["message"])

            response = session.put(
                url=url,
                headers=headers,
                data=sip_params,
                auth=digest_authenticator(),
                timeout=REQUEST_TIMEOUT_SECONDS,
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


def _report_failure(step, address, quick_call_number, response):
    error_message = (
        f"❌ ERRO ao definir quick call number {quick_call_number} em {address} "
        f"na etapa {step}: {response['message']}"
    )
    logger.error(error_message)
    send_alert_via_slack(message=error_message)


def set_quick_call_number(quick_call_number):
    try:
        host = os.environ["INTERCOM_HOST"]
        ports_list = os.environ["INTERCOM_PORTS"].split(",")

        for port in ports_list:
            address = f"http://{host}:{port}"

            sip_response = put_sip_params(address, quick_call_number)
            if sip_response["error"]:
                _report_failure("SIP", address, quick_call_number, sip_response)
                continue

            key_response = put_key_cfg(address, quick_call_number)
            if key_response["error"]:
                # Device would be left in an inconsistent state if we rebooted now.
                _report_failure("keyCfg", address, quick_call_number, key_response)
                continue

            reboot_response = reboot_device(address)
            if reboot_response["error"]:
                _report_failure("reboot", address, quick_call_number, reboot_response)
                continue

            logger.info(
                f"✅ OK: address: {address} quick_call_number {quick_call_number} "
                f"(SIP+keyCfg+reboot) statusString {sip_response['message']['statusString']}"
            )

    except Exception as error:
        logger.error(f"❌ set_quick_call_number(): {error}")
