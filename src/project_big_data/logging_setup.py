"""Single rotating log file. Replaces the old per-import-timestamped-file scheme that
created a directory per import and never wrote logs anywhere useful."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from project_big_data.config import LOGS_DIR

_FORMAT = "[%(asctime)s] %(levelname)s %(name)s:%(lineno)d - %(message)s"
_configured = False


def configure_logging(level: int = logging.INFO) -> None:
    global _configured
    if _configured:
        return
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    handler = RotatingFileHandler(
        LOGS_DIR / "app.log", maxBytes=2_000_000, backupCount=3, encoding="utf-8"
    )
    handler.setFormatter(logging.Formatter(_FORMAT))

    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(handler)
    _configured = True


def get_logger(name: str) -> logging.Logger:
    configure_logging()
    return logging.getLogger(name)
