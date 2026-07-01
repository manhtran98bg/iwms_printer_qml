from __future__ import annotations

import logging
import os


DEFAULT_LOG_LEVEL = "INFO"
LOG_LEVEL_ENV_VAR = "IWMS_LOG_LEVEL"


def configure_logging() -> None:
    """Configure application-wide console logging."""
    level_name = os.getenv(LOG_LEVEL_ENV_VAR, DEFAULT_LOG_LEVEL).strip().upper()
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
