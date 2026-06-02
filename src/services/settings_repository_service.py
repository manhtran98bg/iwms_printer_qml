from __future__ import annotations

import json
from json import JSONDecodeError
from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject

from src.core.runtime_paths import CONFIG_PATH
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
        if not self._config_path.exists():
            config = PrinterConfig()
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
        stamp_columns = config.stamp_columns
        try:
            stamp_columns = int(stamp_columns)
        except (TypeError, ValueError):
            stamp_columns = PrinterConfig().stamp_columns
        if stamp_columns < 1:
            stamp_columns = 1
        return PrinterConfig(
            api_url=api_url or PrinterConfig().api_url,
            template_path=str(config.template_path or ""),
            data_path=str(config.data_path or ""),
            printer_name=str(config.printer_name or ""),
            stamp_columns=stamp_columns,
            required_fields=list(config.required_fields or []),
        )
