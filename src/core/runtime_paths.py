from __future__ import annotations

from pathlib import Path

from src.core.constants import (
    CONFIG_FILENAME,
    TEMPLATE_DIRNAME,
    USER_CONFIG_DIRNAME,
)


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = PACKAGE_ROOT.parent
APP_ENVIRONMENT_ROOT = Path.home() / USER_CONFIG_DIRNAME
CONFIG_PATH = APP_ENVIRONMENT_ROOT / CONFIG_FILENAME
ASSETS_TEMPLATE_ROOT = PACKAGE_ROOT / "assets" / "template"
DEFAULT_TEMPLATE_DIR = APP_ENVIRONMENT_ROOT / TEMPLATE_DIRNAME
