from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote, urlparse

from PySide6.QtCore import Property, Signal, Slot

from src.core.constants import APP_TITLE
from src.models.printer_config import PrinterConfig
from src.models.print_request import PrintRequest
from src.services.api_server_service import ApiServerService
from src.services.printer_discovery_service import PrinterDiscoveryService
from src.services.print_workflow_service import PrintWorkflowService
from src.services.settings_repository_service import SettingsRepositoryService
from src.viewmodels.base_viewmodel import BaseViewModel


class MainViewModel(BaseViewModel):
    statusChanged = Signal()
    apiRunningChanged = Signal()
    configChanged = Signal()
    printersChanged = Signal()
    requestStatsChanged = Signal()
    testDataChanged = Signal()

    def __init__(
        self,
        settings_repository: SettingsRepositoryService,
        printer_discovery_service: PrinterDiscoveryService,
        api_server_service: ApiServerService,
        print_workflow_service: PrintWorkflowService,
    ) -> None:
        super().__init__()
        self._settings_repository = settings_repository
        self._printer_discovery_service = printer_discovery_service
        self._api_server_service = api_server_service
        self._print_workflow_service = print_workflow_service
        self._config = self._settings_repository.load()
        self._status = "Initialized"
        self._api_running = False
        self._printers: list[str] = []
        self._last_request_at = "-"
        self._last_request_status = "-"
        self._request_count = 0
        self._failed_count = 0
        self._test_rows = [
            {"field": "kit", "label1": "LOAI BO", "label2": "K123456"},
            {"field": "sku", "label1": "", "label2": "12345678"},
            {"field": "qty", "label1": "", "label2": "4321"},
        ]
        self._raw_zpl_preview = (
            "^XA\n"
            "^FDsku_0^FS\n"
            "^FDqty_0^FS\n"
            "^FDkit_0^FS\n"
            "^FDsku_1^FS\n"
            "^FDqty_1^FS\n"
            "^FDkit_1^FS\n"
            "^XZ"
        )

        self._api_server_service.started.connect(self._on_api_started)
        self._api_server_service.stopped.connect(self._on_api_stopped)
        self._api_server_service.failed.connect(self._on_api_failed)
        self._api_server_service.request_processed.connect(self._on_request_processed)
        self._print_workflow_service.print_started.connect(self._on_print_started)
        self._print_workflow_service.print_finished.connect(self._on_print_finished)
        self._print_workflow_service.print_failed.connect(self._on_print_failed)

    @Property(str, constant=True)
    def app_title(self) -> str:
        return APP_TITLE

    @Property(str, notify=statusChanged)
    def status(self) -> str:
        return self._status

    @Property(bool, notify=apiRunningChanged)
    def api_running(self) -> bool:
        return self._api_running

    @Property(str, notify=configChanged)
    def api_url(self) -> str:
        return self._config.api_url

    @Property(str, notify=configChanged)
    def template_path(self) -> str:
        return self._config.template_path

    @Property(str, notify=configChanged)
    def data_path(self) -> str:
        return self._config.data_path

    @Property(str, notify=configChanged)
    def printer_name(self) -> str:
        return self._config.printer_name

    @Property(int, notify=configChanged)
    def stamp_columns(self) -> int:
        return self._config.stamp_columns

    @Property(list, notify=printersChanged)
    def printers(self) -> list[str]:
        return self._printers

    @Property(str, notify=requestStatsChanged)
    def last_request_at(self) -> str:
        return self._last_request_at

    @Property(str, notify=requestStatsChanged)
    def last_request_status(self) -> str:
        return self._last_request_status

    @Property(int, notify=requestStatsChanged)
    def request_count(self) -> int:
        return self._request_count

    @Property(int, notify=requestStatsChanged)
    def failed_count(self) -> int:
        return self._failed_count

    @Property(list, notify=testDataChanged)
    def test_rows(self) -> list[dict[str, str]]:
        return self._test_rows

    @Property(str, notify=testDataChanged)
    def raw_zpl_preview(self) -> str:
        return self._raw_zpl_preview

    @Slot()
    def refresh_printers(self) -> None:
        printers = self._printer_discovery_service.installed_printers()
        if self._config.printer_name and self._config.printer_name not in printers:
            printers.insert(0, self._config.printer_name)
        self._printers = printers
        if not self._config.printer_name and self._printers:
            self._update_config(printer_name=self._printers[0])
        self.printersChanged.emit()
        self.set_status(f"Loaded {len(self._printers)} printer(s).")

    @Slot()
    def start_api(self) -> None:
        self._api_server_service.start(self._config.api_url)

    @Slot()
    def stop_api(self) -> None:
        self._api_server_service.stop()

    @Slot(str)
    def set_status(self, status: str) -> None:
        if status == self._status:
            return
        self._status = status
        self.statusChanged.emit()

    @Slot(str)
    def set_api_url(self, api_url: str) -> None:
        value = api_url.strip()
        if value and not value.endswith("/"):
            value += "/"
        self._update_config(api_url=value)

    @Slot(str)
    def set_template_path(self, template_path: str) -> None:
        self._update_config(template_path=self._clean_file_url(template_path))

    @Slot(str)
    def set_data_path(self, data_path: str) -> None:
        self._update_config(data_path=self._clean_file_url(data_path))

    @Slot(str)
    def set_printer_name(self, printer_name: str) -> None:
        self._update_config(printer_name=printer_name)

    @Slot(int)
    def set_stamp_columns(self, stamp_columns: int) -> None:
        if stamp_columns < 1:
            stamp_columns = 1
        self._update_config(stamp_columns=stamp_columns)

    @Slot()
    def print_test(self) -> None:
        request = PrintRequest(labels=self._test_labels())
        self._print_workflow_service.submit_test(request)

    @Slot()
    def reload_format(self) -> None:
        self.set_status("Format reload workflow is not implemented yet.")

    @Slot(int, str, str)
    def update_test_value(self, row_index: int, column_key: str, value: str) -> None:
        if row_index < 0 or row_index >= len(self._test_rows):
            return
        if column_key not in {"label1", "label2"}:
            return
        row = dict(self._test_rows[row_index])
        if row.get(column_key) == value:
            return
        row[column_key] = value
        self._test_rows[row_index] = row
        self.testDataChanged.emit()

    @Slot(str, str, str)
    def update_test_cell(self, field: str, column_key: str, value: str) -> None:
        if column_key not in {"label1", "label2"}:
            return
        for row_index, row_data in enumerate(self._test_rows):
            if row_data.get("field") == field:
                self.update_test_value(row_index, column_key, value)
                return

    def _on_api_started(self, url: str) -> None:
        self._api_running = True
        self.apiRunningChanged.emit()
        self.set_status(f"API server started at {url}")

    def _on_api_stopped(self) -> None:
        self._api_running = False
        self.apiRunningChanged.emit()
        self.set_status("API server stopped")

    def _on_api_failed(self, message: str) -> None:
        self._api_running = False
        self.apiRunningChanged.emit()
        self.set_status(message)

    def _on_request_processed(self, status: str, success: bool) -> None:
        self._last_request_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._last_request_status = status
        self._request_count += 1
        if not success:
            self._failed_count += 1
        self.requestStatsChanged.emit()

    def _on_print_started(self, payload: object) -> None:
        label_count = len(payload.get("labels", [])) if isinstance(payload, dict) else 0
        self.set_status(f"Printing {label_count} test label(s)...")

    def _on_print_finished(self, payload: object) -> None:
        if isinstance(payload, dict):
            self.set_status(
                "Print completed: "
                f"{payload.get('label_count', 0)} label(s), "
                f"{payload.get('page_count', 0)} page(s)."
            )
            return
        self.set_status("Print completed.")

    def _on_print_failed(self, message: str) -> None:
        self.set_status(f"Print failed: {message}")

    def _update_config(self, **changes: object) -> None:
        next_config = replace(self._config, **changes)
        if next_config == self._config:
            return
        self._config = next_config
        try:
            self._settings_repository.save(self._config)
        except OSError as exc:
            self.set_status(f"Could not save settings: {exc}")
            return
        self.configChanged.emit()

    def _clean_file_url(self, value: str) -> str:
        if not value:
            return ""
        parsed = urlparse(value)
        if parsed.scheme != "file":
            return value
        path = unquote(parsed.path)
        if parsed.netloc:
            path = f"//{parsed.netloc}{path}"
        if len(path) > 3 and path[0] == "/" and path[2] == ":":
            path = path[1:]
        return str(Path(path))

    def _test_labels(self) -> list[dict[str, str]]:
        label_count = max(1, self._config.stamp_columns)
        labels = [dict() for _ in range(label_count)]
        for row in self._test_rows:
            field_name = str(row.get("field", "")).strip()
            if not field_name:
                continue
            for index in range(label_count):
                value_key = f"label{index + 1}"
                labels[index][field_name] = str(row.get(value_key, ""))
        return labels
