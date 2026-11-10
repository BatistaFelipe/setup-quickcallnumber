import logging

import requests
from defusedxml import ElementTree as DefusedET

from .utils.helpers import RequestError, digest_authenticator
from .utils.xml_helpers import (
    build_key_cfg_xml,
    parse_key_cfg_xml,
    parse_response_status_xml,
)

logger = logging.getLogger(__name__)
session = requests.Session()

REQUEST_TIMEOUT_SECONDS = 15


def get_key_cfg(address):
    try:
        url = f"{address}/ISAPI/VideoIntercom/keyCfg/1"
        response = session.get(url, auth=digest_authenticator(), timeout=REQUEST_TIMEOUT_SECONDS)
        if response.ok:
            return {"message": parse_key_cfg_xml(response.text), "error": False}

        raise RequestError(
            error=True,
            message=f"HTTP GET /keyCfg: {response.status_code} {response.reason}",
        )
    except RequestError as error:
        return error.toJson()
    except DefusedET.ParseError as error:
        return {"message": f"❌ get_key_cfg() invalid XML: {error}", "error": True}
    except Exception as error:
        return {"message": f"❌ get_key_cfg(): {error}", "error": True}


def put_key_cfg(address, call_number):
    try:
        key_cfg = get_key_cfg(address)
        if key_cfg["error"]:
            raise RequestError(error=True, message=key_cfg["message"])

        fields = {**key_cfg["message"], "callNumber": str(call_number)}

        url = f"{address}/ISAPI/VideoIntercom/keyCfg/1"
        headers = {"Content-Type": "application/xml"}
        body = build_key_cfg_xml(fields)

        response = session.put(
            url,
            headers=headers,
            data=body,
            auth=digest_authenticator(),
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        if response.ok:
            return {"message": parse_response_status_xml(response.text), "error": False}

        raise RequestError(
            error=True,
            message=f"HTTP PUT /keyCfg: {response.status_code} {response.reason}",
        )
    except RequestError as error:
        return error.toJson()
    except DefusedET.ParseError as error:
        return {"message": f"❌ put_key_cfg() invalid XML: {error}", "error": True}
    except Exception as error:
        return {"message": f"❌ put_key_cfg(): {error}", "error": True}
