from __future__ import annotations

from datetime import datetime
from html import escape
import sys
from typing import Any

from PySide6.QtCore import QObject

from src.core.errors import SpoolerError


class PrintSpoolerService(QObject):
    """Sends print jobs to Windows printers."""

    def __init__(self, encoding: str = "utf-8") -> None:
        super().__init__()
        self._encoding = encoding

    def print_raw(self, printer_name: str, zpl_pages: list[str]) -> None:
        if not printer_name or not printer_name.strip():
            raise SpoolerError("Printer name is required.")
        if not zpl_pages:
            raise SpoolerError("Print data is empty.")
        win32print = self._load_win32print()

        printer_handle: Any | None = None
        document_started = False
        try:
            printer_handle = win32print.OpenPrinter(printer_name)
            job_id = win32print.StartDocPrinter(
                printer_handle,
                1,
                ("Zebra Label", None, "RAW"),
            )
            if not job_id:
                raise SpoolerError(f"Could not start print job on {printer_name}.")
            document_started = True

            for page in zpl_pages:
                self._write_page(win32print, printer_handle, page)
        except SpoolerError:
            raise
        except Exception as exc:
            raise SpoolerError(f"Could not print to {printer_name}: {exc}") from exc
        finally:
            if printer_handle is not None:
                self._close_job(win32print, printer_handle, document_started)

    def print_test_document(self, printer_name: str, labels: list[dict[str, str]]) -> None:
        if not printer_name or not printer_name.strip():
            raise SpoolerError("Printer name is required.")
        if not labels:
            raise SpoolerError("Print data is empty.")

        try:
            from PySide6.QtGui import QTextDocument
            from PySide6.QtPrintSupport import QPrinter
        except ImportError as exc:
            raise SpoolerError("Qt print support is required for standard test printing.") from exc

        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setPrinterName(printer_name)
        printer.setDocName("iWMS Print Test")
        if not printer.isValid():
            raise SpoolerError(f"Printer is not available: {printer_name}")

        document = QTextDocument()
        document.setHtml(self._build_test_document_html(printer_name, labels))
        document.print_(printer)

    def _write_page(self, win32print: Any, printer_handle: Any, page: str) -> None:
        payload = self._encode_page(page)
        if not payload:
            return

        page_started = False
        try:
            win32print.StartPagePrinter(printer_handle)
            page_started = True
            written = win32print.WritePrinter(printer_handle, payload)
            if written is not None and written != len(payload):
                raise SpoolerError(
                    f"Spooler accepted {written} of {len(payload)} byte(s)."
                )
        finally:
            if page_started:
                win32print.EndPagePrinter(printer_handle)

    def _encode_page(self, page: str) -> bytes:
        if isinstance(page, bytes):
            return page
        if page is None:
            return b""
        return str(page).encode(self._encoding)

    def _close_job(self, win32print: Any, printer_handle: Any, document_started: bool) -> None:
        try:
            if document_started:
                win32print.EndDocPrinter(printer_handle)
        finally:
            win32print.ClosePrinter(printer_handle)

    def _load_win32print(self) -> Any:
        if sys.platform != "win32":
            raise SpoolerError("Windows Print Spooler is only available on Windows.")
        try:
            import win32print
        except ImportError as exc:
            raise SpoolerError("pywin32 is required for Windows RAW printing.") from exc
        return win32print

    def _build_test_document_html(self, printer_name: str, labels: list[dict[str, str]]) -> str:
        generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        rows: list[str] = []
        for label_index, label in enumerate(labels, start=1):
            for field_name, value in label.items():
                rows.append(
                    "<tr>"
                    f"<td>{label_index}</td>"
                    f"<td>{escape(str(field_name))}</td>"
                    f"<td>{escape('' if value is None else str(value))}</td>"
                    "</tr>"
                )

        table_rows = "\n".join(rows)
        return f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{
      color: #111827;
      font-family: Arial, sans-serif;
      font-size: 11pt;
    }}
    h1 {{
      font-size: 18pt;
      margin: 0 0 8px;
    }}
    .meta {{
      color: #4b5563;
      margin-bottom: 18px;
    }}
    table {{
      border-collapse: collapse;
      width: 100%;
    }}
    th, td {{
      border: 1px solid #9ca3af;
      padding: 8px;
      text-align: left;
    }}
    th {{
      background: #e5e7eb;
      font-weight: 700;
    }}
  </style>
</head>
<body>
  <h1>iWMS Print Test</h1>
  <div class="meta">
    Printer: {escape(printer_name)}<br>
    Generated at: {escape(generated_at)}
  </div>
  <table>
    <thead>
      <tr><th>Label</th><th>Field</th><th>Value</th></tr>
    </thead>
    <tbody>{table_rows}</tbody>
  </table>
</body>
</html>
"""
