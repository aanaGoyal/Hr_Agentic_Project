"""
Plain Python `logging` for the app lifecycle -- startup, dataset loaded,
prediction requested, model version used, prediction completed, errors.
Nothing fancier than the standard library; a proper log aggregator is an
enterprise-hardening concern, not a Day 4 one.
"""
import logging

from app.utils.config import APP_LOG_FILE


def get_logger(name: str = "hr_ai") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:  # avoid duplicate handlers on notebook re-imports
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    file_handler = logging.FileHandler(APP_LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger
