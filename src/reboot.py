import logging

import requests

from .utils.helpers import RequestError, digest_authenticator
from .utils.xml_helpers import parse_response_status_xml

logger = logging.getLogger(__name__)
session = requests.Session()

REBOOT_TIMEOUT_SECONDS = 10


def reboot_device(address):
    url = f"{address}/ISAPI/System/reboot"
    try:
        response = session.put(
            url,
            auth=digest_authenticator(),
            timeout=REBOOT_TIMEOUT_SECONDS,
        )
        if response.ok:
            return {"message": parse_response_status_xml(response.text), "error": False}

        raise RequestError(
            error=True,
            message=f"HTTP PUT /reboot: {response.status_code} {response.reason}",
        )
    except (requests.ConnectionError, requests.Timeout) as error:
        # Device may have already started rebooting before responding;
        # treat as success to avoid false alarms.
        logger.warning(
            f"🔄 reboot_device(): device unreachable after PUT (likely rebooting): {error}"
        )
        return {"message": "reboot sent (device unreachable)", "error": False}
    except RequestError as error:
        return error.toJson()
    except Exception as error:
        return {"message": f"❌ reboot_device(): {error}", "error": True}
