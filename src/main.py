import logging
import os

from .sip_params import set_quick_call_number
from .utils.helpers import (
    get_arg_parser,
    setup,
    setup_logger,
)


def main():
    setup()
    setup_logger()
    logger = logging.getLogger(__name__)
    args = get_arg_parser()

    quick_call_number = str(args.number) if args.number else os.getenv("QUICK_CALL_NUMBER")

    logger.info(f"⭐ Starting to set up a quick call number for {quick_call_number}")

    set_quick_call_number(quick_call_number)

    logger.info(f"🏁 Finished setting up a quick call number for {quick_call_number}")


if __name__ == "__main__":
    main()
