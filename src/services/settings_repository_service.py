from __future__ import annotations

import json

from PySide6.QtCore import QObject

from src.core.runtime_paths import CONFIG_PATH
from src.models.printer_config import PrinterConfig


class SettingsRepositoryService(QObject):
    """Loads and saves user-level printer app settings."""

    def load(self) -> PrinterConfig:
        if not CONFIG_PATH.exists():
            return PrinterConfig()
        payload = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        return PrinterConfig.from_dict(payload)

    def save(self, config: PrinterConfig) -> None:
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_PATH.write_text(
            json.dumps(config.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
