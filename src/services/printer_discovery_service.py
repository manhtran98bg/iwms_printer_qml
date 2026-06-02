from __future__ import annotations

from PySide6.QtCore import QObject


class PrinterDiscoveryService(QObject):
    """Lists printers available to the current Windows user."""

    def installed_printers(self) -> list[str]:
        printers = self._from_win32print()
        if not printers:
            printers = self._from_qt_print_support()
        return sorted(dict.fromkeys(printers), key=str.casefold)

    def _from_win32print(self) -> list[str]:
        try:
            import win32print
        except ImportError:
            return []
        flags = win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
        try:
            return [
                str(printer[2])
                for printer in win32print.EnumPrinters(flags)
                if len(printer) > 2 and printer[2]
            ]
        except Exception:
            return []

    def _from_qt_print_support(self) -> list[str]:
        try:
            from PySide6.QtPrintSupport import QPrinterInfo
        except ImportError:
            return []
        try:
            return [printer.printerName() for printer in QPrinterInfo.availablePrinters()]
        except Exception:
            return []
