import argparse
import logging
import os

import requests
from dotenv import load_dotenv
from requests.auth import HTTPDigestAuth

from .http import REQUEST_TIMEOUT_SECONDS


def setup() -> None:
    load_dotenv()


def setup_logger() -> None:
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    file_handler = logging.FileHandler(os.getenv("LOG_PATH", "app.log"), encoding="utf-8")
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def digest_authenticator() -> HTTPDigestAuth:
    return HTTPDigestAuth(os.getenv("INTERCOM_USER"), os.getenv("INTERCOM_PASSWORD"))


def get_arg_parser() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="SETUP INTERCOM QUICK CALL NUMBER")
    parser.add_argument(
        "-n",
        "--number",
        type=int,
        choices=[61, 3001],
        help="Quick call number to set (61 or 3001)",
    )
    return parser.parse_args()


def send_alert_via_slack(message: str) -> None:
    logger = logging.getLogger(__name__)
    try:
        url = os.getenv("SLACK_URL")
        headers = {"Content-Type": "application/json"}
        data = {"text": message}
        response = requests.post(url, headers=headers, json=data, timeout=REQUEST_TIMEOUT_SECONDS)
        if not response.ok:
            raise RequestError(
                message=f"HTTP POST/ {response.status_code} {response.reason}",
                error=True,
            )

        logger.info("OK: Slack alert sent")
    except Exception as error:
        logger.error(f"ERROR send_alert_via_slack(): {error}")


class RequestError(Exception):
    def __init__(self, message: str, error: bool = False) -> None:
        super().__init__(message)
        self.message = message
        self.error = error

    def to_dict(self) -> dict[str, object]:
        return {"error": self.error, "message": self.message}
