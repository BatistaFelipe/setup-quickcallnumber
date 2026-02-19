import os
from requests.auth import HTTPDigestAuth
from dotenv import load_dotenv
import argparse
import requests
import logging


def setup():
    load_dotenv()


def setup_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    file_handler = logging.FileHandler(
        os.getenv("LOG_PATH", "app.log"), encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def digest_authenticator():
    return HTTPDigestAuth(os.getenv("INTERCOM_USER"), os.getenv("INTERCOM_PASSWORD"))


def get_arg_parser():
    parser = argparse.ArgumentParser(description="SETUP INTERCOM QUICK CALL NUMBER")
    parser.add_argument(
        "-n",
        "--number",
        type=int,
        choices=[61, 3001],
        help="Número para chamada (61 ou 3001)",
    )
    args = parser.parse_args()

    return args


def send_alert_via_slack(message):
    logger = logging.getLogger(__name__)
    try:
        url = os.getenv("SLACK_URL")
        headers = {"Content-Type": "application/json"}
        data = {"text": message}
        response = requests.request("POST", url, headers=headers, json=data)
        if not response.ok:
            raise RequestError(
                message=f"HTTP POST/ {response.status_code} {response.reason}",
                error=True,
            )

        logger.info(f"✉️  OK: Mensagem de alerta enviada via Slack")
    except Exception as error:
        logger.error(f"❌ ERROR send_alert_via_slack(): {str(error)}")


class RequestError(Exception):
    def __init__(self, message, error=False):
        super().__init__(message)
        self.message = message
        self.error = error

    def toJson(self):
        return {"error": self.error, "message": self.message}
