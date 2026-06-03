from __future__ import annotations

import json
from json import JSONDecodeError
from pathlib import Path
import shutil
from typing import Any

from PySide6.QtCore import QObject

from src.core.constants import DEFAULT_SCHEMA_FILENAME, DEFAULT_TEMPLATE_FILENAME
from src.core.runtime_paths import ASSETS_TEMPLATE_ROOT, CONFIG_PATH, DEFAULT_TEMPLATE_DIR
from src.models.printer_config import PrinterConfig


class SettingsRepositoryService(QObject):
    """Loads and saves user-level printer app settings."""

    def __init__(self, config_path: Path = CONFIG_PATH) -> None:
        super().__init__()
        self._config_path = config_path

    @property
    def config_path(self) -> Path:
        return self._config_path

    def load(self) -> PrinterConfig:
        self._ensure_default_template_files()
        if not self._config_path.exists():
            config = self._default_config()
            self.save(config)
            return config
        try:
            payload = json.loads(self._config_path.read_text(encoding="utf-8"))
        except (OSError, JSONDecodeError):
            return PrinterConfig()
        if not isinstance(payload, dict):
            return PrinterConfig()
        return self._normalize_config(payload)

    def save(self, config: PrinterConfig) -> None:
        self._config_path.parent.mkdir(parents=True, exist_ok=True)
        self._config_path.write_text(
            json.dumps(config.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _normalize_config(self, payload: dict[str, Any]) -> PrinterConfig:
        config = PrinterConfig.from_dict(payload)
        api_url = str(config.api_url or "")
        if api_url and not api_url.endswith("/"):
            api_url += "/"
        return PrinterConfig(
            api_url=api_url or PrinterConfig().api_url,
            template_path=str(config.template_path or ""),
            data_path=str(config.data_path or ""),
            printer_name=str(config.printer_name or ""),
            required_fields=list(config.required_fields or []),
        )

    def _default_config(self) -> PrinterConfig:
        schema_path = DEFAULT_TEMPLATE_DIR / DEFAULT_SCHEMA_FILENAME
        template_path = DEFAULT_TEMPLATE_DIR / DEFAULT_TEMPLATE_FILENAME
        return PrinterConfig(
            data_path=str(schema_path),
            template_path=str(template_path),
        )

    def _ensure_default_template_files(self) -> None:
        DEFAULT_TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
        self._copy_default_file(
            source=ASSETS_TEMPLATE_ROOT / DEFAULT_SCHEMA_FILENAME,
            destination=DEFAULT_TEMPLATE_DIR / DEFAULT_SCHEMA_FILENAME,
        )
        self._copy_default_file(
            source=ASSETS_TEMPLATE_ROOT / DEFAULT_TEMPLATE_FILENAME,
            destination=DEFAULT_TEMPLATE_DIR / DEFAULT_TEMPLATE_FILENAME,
        )

    def _copy_default_file(self, source: Path, destination: Path) -> None:
        if destination.exists():
            return
        shutil.copyfile(source, destination)
