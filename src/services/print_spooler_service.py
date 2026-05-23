from __future__ import annotations

from PySide6.QtCore import QObject


class PrintSpoolerService(QObject):
    """Sends RAW ZPL bytes to Windows Print Spooler."""

    def print_raw(self, printer_name: str, zpl_pages: list[str]) -> None:
        raise NotImplementedError("Windows spooler printing will be implemented next.")
