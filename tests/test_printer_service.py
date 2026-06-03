from __future__ import annotations

import subprocess

from src.core.errors import SpoolerError
from src.services.printer_service import PrinterService


def test_print_raw_cups_sends_zpl_to_lp(monkeypatch):
    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return subprocess.CompletedProcess(command, 0, stdout=b"request id is Zebra-1", stderr=b"")

    monkeypatch.setattr("src.services.printer_service.sys.platform", "linux")
    monkeypatch.setattr("src.services.printer_service.subprocess.run", fake_run)

    PrinterService().print_raw("Zebra_ZD421", ["^XA", "^XZ"])

    command, kwargs = calls[0]
    assert command == ["lp", "-d", "Zebra_ZD421", "-o", "raw", "-t", "Zebra Label", "-"]
    assert kwargs["input"] == b"^XA^XZ"


def test_print_raw_cups_raises_spooler_error_on_lp_failure(monkeypatch):
    def fake_run(command, **kwargs):
        return subprocess.CompletedProcess(command, 1, stdout=b"", stderr=b"printer not found")

    monkeypatch.setattr("src.services.printer_service.sys.platform", "linux")
    monkeypatch.setattr("src.services.printer_service.subprocess.run", fake_run)

    try:
        PrinterService().print_raw("MissingPrinter", ["^XA^XZ"])
    except SpoolerError as exc:
        assert "printer not found" in str(exc)
    else:
        raise AssertionError("Expected SpoolerError")
