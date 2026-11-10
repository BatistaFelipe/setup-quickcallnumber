import logging
import os

from .sip_params import set_quick_call_number
from .utils.helpers import get_arg_parser, setup, setup_logger

REQUIRED_ENV_VARS = ("INTERCOM_HOST", "INTERCOM_PORTS", "INTERCOM_USER", "INTERCOM_PASSWORD")


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise SystemExit(f"Required env var '{name}' is missing or empty")
    return value


def main() -> None:
    setup()
    setup_logger()
    logger = logging.getLogger(__name__)

    for env_name in REQUIRED_ENV_VARS:
        _require_env(env_name)

    args = get_arg_parser()
    quick_call_number = str(args.number) if args.number else _require_env("QUICK_CALL_NUMBER")

    logger.info(f"Starting to set up a quick call number for {quick_call_number}")
    set_quick_call_number(quick_call_number)
    logger.info(f"Finished setting up a quick call number for {quick_call_number}")


if __name__ == "__main__":  # pragma: no cover
    main()
