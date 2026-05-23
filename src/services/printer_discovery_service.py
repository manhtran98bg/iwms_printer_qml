from __future__ import annotations

from PySide6.QtCore import QObject


class PrinterDiscoveryService(QObject):
    """Lists Windows printers. Implementation will use pywin32."""

    def installed_printers(self) -> list[str]:
        return []
