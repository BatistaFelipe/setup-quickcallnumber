import json
import logging
import os

from .key_cfg import put_key_cfg
from .reboot import reboot_device
from .utils.helpers import RequestError, digest_authenticator, send_alert_via_slack
from .utils.http import REQUEST_TIMEOUT_SECONDS, session

logger = logging.getLogger(__name__)


def get_sip_params(address: str) -> dict[str, object]:
    try:
        url = f"{address}/ISAPI/System/Network/SIP/StandardSipParam"
        response = session.get(url, auth=digest_authenticator(), timeout=REQUEST_TIMEOUT_SECONDS)
        if response.ok:
            return {"message": response.json(), "error": False}

        raise RequestError(
            error=True, message=f"HTTP GET /: {response.status_code} {response.reason}"
        )
    except RequestError as error:
        return error.to_dict()
    except Exception as error:
        return {"message": f"get_sip_params(): {error}", "error": True}


def put_sip_params(address: str, quick_call_number: str) -> dict[str, object]:
    try:
        url = f"{address}/ISAPI/System/Network/SIP/StandardSipParam?format=json"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "x-requested-with": "XMLHttpRequest",
        }

        sip_params = get_sip_params(address)
        if sip_params["error"]:
            raise RequestError(error=True, message=str(sip_params["message"]))

        source = sip_params["message"]
        updated_list = [
            {**source["standardSipParamList"][0], "quickCallNumber": quick_call_number},
            *source["standardSipParamList"][1:],
        ]
        payload = {**source, "standardSipParamList": updated_list}
        payload.pop("registerStatus", None)

        response = session.put(
            url=url,
            headers=headers,
            data=json.dumps(payload),
            auth=digest_authenticator(),
            timeout=REQUEST_TIMEOUT_SECONDS,
        )

        if response.ok:
            return {"message": response.json(), "error": False}

        raise RequestError(
            error=True,
            message=f"HTTP PUT /: {response.status_code} {response.reason}",
        )
    except RequestError as error:
        return error.to_dict()
    except Exception as error:
        return {"message": f"put_sip_params(): {error}", "error": True}


def _report_failure(
    step: str, address: str, quick_call_number: str, response: dict[str, object]
) -> None:
    # Message stays in Portuguese: it is forwarded to Slack where operators
    # (portaria) read it in pt-BR.
    error_message = (
        f"ERRO ao definir quick call number {quick_call_number} em {address} "
        f"na etapa {step}: {response['message']}"
    )
    logger.error(error_message)
    send_alert_via_slack(message=error_message)


def set_quick_call_number(quick_call_number: str) -> None:
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

            status_string = sip_response["message"]["statusString"]
            logger.info(
                f"OK: address={address} quick_call_number={quick_call_number} "
                f"(SIP+keyCfg+reboot) statusString={status_string}"
            )

    except Exception as error:
        logger.error(f"set_quick_call_number(): {error}")
