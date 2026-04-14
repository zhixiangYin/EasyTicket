import logging
import os


LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"


def configure_logging() -> None:
    log_level_name = os.getenv("EASYTICKET_LOG_LEVEL", "WARNING").upper()
    log_level = getattr(logging, log_level_name, logging.WARNING)

    logging.basicConfig(
        level=log_level,
        format=LOG_FORMAT,
        force=True,
    )
