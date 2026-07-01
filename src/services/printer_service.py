from __future__ import annotations

from datetime import datetime
from html import escape
import logging
import subprocess
import sys
from typing import Any

from PySide6.QtCore import QObject

from src.core.errors import SpoolerError


logger = logging.getLogger(__name__)


class PrinterService(QObject):
    """Lists available printers and sends RAW label jobs to the OS print backend."""

    def __init__(self, encoding: str = "utf-8") -> None:
        super().__init__()
        self._encoding = encoding

    def installed_printers(self) -> list[str]:
        printers = self._printers_from_win32print()
        if not printers:
            printers = self._printers_from_qt_print_support()
        unique_printers = sorted(dict.fromkeys(printers), key=str.casefold)
        logger.info("Loaded %s installed printer(s)", len(unique_printers))
        return unique_printers

    def print_raw(self, printer_name: str, zpl_pages: list[str]) -> None:
        if not printer_name or not printer_name.strip():
            raise SpoolerError("Thi\u1ebfu t\u00ean m\u00e1y in.")
        if not zpl_pages:
            raise SpoolerError("D\u1eef li\u1ec7u in \u0111ang tr\u1ed1ng.")
        logger.info(
            "Dispatching RAW print job: printer=%s pages=%s platform=%s",
            printer_name,
            len(zpl_pages),
            sys.platform,
        )
        if sys.platform == "win32":
            self._print_raw_windows(printer_name, zpl_pages)
            return
        if sys.platform.startswith("linux"):
            self._print_raw_cups(printer_name, zpl_pages)
            return
        raise SpoolerError(f"Ch\u01b0a h\u1ed7 tr\u1ee3 in RAW tr\u00ean h\u1ec7 \u0111i\u1ec1u h\u00e0nh: {sys.platform}")

    def _print_raw_windows(self, printer_name: str, zpl_pages: list[str]) -> None:
        win32print = self._load_win32print()

        printer_handle: Any | None = None
        document_started = False
        try:
            logger.info("Opening Windows printer %s", printer_name)
            printer_handle = win32print.OpenPrinter(printer_name)
            job_id = win32print.StartDocPrinter(
                printer_handle,
                1,
                ("Zebra Label", None, "RAW"),
            )
            if not job_id:
                raise SpoolerError(f"Kh\u00f4ng th\u1ec3 t\u1ea1o job in tr\u00ean {printer_name}.")
            document_started = True
            logger.info(
                "Started Windows RAW print job: printer=%s job_id=%s pages=%s",
                printer_name,
                job_id,
                len(zpl_pages),
            )

            for page in zpl_pages:
                self._write_page(win32print, printer_handle, page)
        except SpoolerError:
            logger.exception("Windows RAW print job failed with spooler error")
            raise
        except Exception as exc:
            logger.exception("Windows RAW print job failed")
            raise SpoolerError(f"Kh\u00f4ng th\u1ec3 in t\u1edbi {printer_name}: {exc}") from exc
        finally:
            if printer_handle is not None:
                self._close_job(win32print, printer_handle, document_started)
                logger.info("Closed Windows printer %s", printer_name)

    def _print_raw_cups(self, printer_name: str, zpl_pages: list[str]) -> None:
        payload = self._encode_pages(zpl_pages)
        if not payload:
            raise SpoolerError("D\u1eef li\u1ec7u in \u0111ang tr\u1ed1ng.")

        command = [
            "lp",
            "-d",
            printer_name,
            "-o",
            "raw",
            "-t",
            "Zebra Label",
            "-",
        ]
        try:
            logger.info(
                "Running CUPS RAW print command: printer=%s pages=%s bytes=%s",
                printer_name,
                len(zpl_pages),
                len(payload),
            )
            result = subprocess.run(
                command,
                input=payload,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
        except FileNotFoundError as exc:
            logger.exception("CUPS lp command was not found")
            raise SpoolerError("Kh\u00f4ng t\u00ecm th\u1ea5y l\u1ec7nh lp. C\u1ea7n c\u00e0i CUPS \u0111\u1ec3 in tr\u00ean Ubuntu.") from exc
        except OSError as exc:
            logger.exception("CUPS RAW print command failed to start")
            raise SpoolerError(f"Kh\u00f4ng th\u1ec3 g\u1eedi l\u1ec7nh in qua CUPS: {exc}") from exc

        if result.returncode != 0:
            message = result.stderr.decode(self._encoding, errors="replace").strip()
            if not message:
                message = result.stdout.decode(self._encoding, errors="replace").strip()
            logger.error(
                "CUPS RAW print command failed: printer=%s returncode=%s message=%s",
                printer_name,
                result.returncode,
                message,
            )
            raise SpoolerError(
                f"Kh\u00f4ng th\u1ec3 in RAW qua CUPS t\u1edbi {printer_name}: {message or result.returncode}"
            )
        logger.info("CUPS RAW print command completed for printer=%s", printer_name)

    def print_test_document(self, printer_name: str, labels: list[dict[str, str]]) -> None:
        if not printer_name or not printer_name.strip():
            raise SpoolerError("Thi\u1ebfu t\u00ean m\u00e1y in.")
        if not labels:
            raise SpoolerError("D\u1eef li\u1ec7u in \u0111ang tr\u1ed1ng.")

        try:
            from PySide6.QtGui import QTextDocument
            from PySide6.QtPrintSupport import QPrinter
        except ImportError as exc:
            logger.exception("Qt print support is unavailable")
            raise SpoolerError("C\u1ea7n Qt print support \u0111\u1ec3 in test th\u00f4ng th\u01b0\u1eddng.") from exc

        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setPrinterName(printer_name)
        printer.setDocName("iWMS Print Test")
        if not printer.isValid():
            raise SpoolerError(f"M\u00e1y in kh\u00f4ng kh\u1ea3 d\u1ee5ng: {printer_name}")

        document = QTextDocument()
        document.setHtml(self._build_test_document_html(printer_name, labels))
        document.print_(printer)
        logger.info("Qt test document sent to printer=%s labels=%s", printer_name, len(labels))

    def _printers_from_win32print(self) -> list[str]:
        try:
            import win32print
        except ImportError:
            return []
        flags = win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
        try:
            printers = [
                str(printer[2])
                for printer in win32print.EnumPrinters(flags)
                if len(printer) > 2 and printer[2]
            ]
            logger.info("Loaded %s printer(s) from win32print", len(printers))
            return printers
        except Exception:
            logger.exception("Failed to enumerate printers with win32print")
            return []

    def _printers_from_qt_print_support(self) -> list[str]:
        try:
            from PySide6.QtPrintSupport import QPrinterInfo
        except ImportError:
            return []
        try:
            printers = [printer.printerName() for printer in QPrinterInfo.availablePrinters()]
            logger.info("Loaded %s printer(s) from Qt print support", len(printers))
            return printers
        except Exception:
            logger.exception("Failed to enumerate printers with Qt print support")
            return []

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
            logger.debug("Wrote RAW page payload with %s byte(s)", len(payload))
        finally:
            if page_started:
                win32print.EndPagePrinter(printer_handle)

    def _encode_page(self, page: str) -> bytes:
        if isinstance(page, bytes):
            return page
        if page is None:
            return b""
        return str(page).encode(self._encoding)

    def _encode_pages(self, pages: list[str]) -> bytes:
        return b"".join(self._encode_page(page) for page in pages)

    def _close_job(self, win32print: Any, printer_handle: Any, document_started: bool) -> None:
        try:
            if document_started:
                win32print.EndDocPrinter(printer_handle)
        finally:
            win32print.ClosePrinter(printer_handle)

    def _load_win32print(self) -> Any:
        if sys.platform != "win32":
            raise SpoolerError("Windows Print Spooler ch\u1ec9 kh\u1ea3 d\u1ee5ng tr\u00ean Windows.")
        try:
            import win32print
        except ImportError as exc:
            raise SpoolerError("C\u1ea7n pywin32 \u0111\u1ec3 in RAW qua Windows.") from exc
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
