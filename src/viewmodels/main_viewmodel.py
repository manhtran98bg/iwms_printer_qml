from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote, urlparse

from PySide6.QtCore import Property, Signal, Slot

from src.core.constants import APP_TITLE
from src.core.runtime_paths import DEFAULT_TEMPLATE_DIR
from src.models.printer_config import PrinterConfig
from src.models.print_request import PrintRequest
from src.services.printer_service import PrinterService
from src.services.print_template_service import PrintTemplateService
from src.services.print_workflow_service import PrintWorkflowService
from src.services.server_handler_service import ServerHandlerService
from src.services.settings_repository_service import SettingsRepositoryService
from src.viewmodels.base_viewmodel import BaseViewModel


class MainViewModel(BaseViewModel):
    statusChanged = Signal()
    apiRunningChanged = Signal()
    configChanged = Signal()
    printersChanged = Signal()
    requestStatsChanged = Signal()
    testDataChanged = Signal()
    templatePreviewChanged = Signal()

    def __init__(
        self,
        settings_repository: SettingsRepositoryService,
        printer_service: PrinterService,
        server_handler_service: ServerHandlerService,
        print_workflow_service: PrintWorkflowService,
        print_template_service: PrintTemplateService,
    ) -> None:
        super().__init__()
        self._settings_repository = settings_repository
        self._printer_service = printer_service
        self._server_handler_service = server_handler_service
        self._print_workflow_service = print_workflow_service
        self._print_template_service = print_template_service
        self._config = self._settings_repository.load()
        self._status = "\u0110\u00e3 kh\u1edfi t\u1ea1o"
        self._api_running = False
        self._printers: list[str] = []
        self._last_request_at = "-"
        self._last_request_status = "-"
        self._request_count = 0
        self._failed_count = 0
        self._required_fields = list(self._config.required_fields or [])
        self._default_values: dict[str, str] = {}
        self._test_rows: list[dict[str, str]] = []
        self._raw_zpl_preview = ""
        self._template_preview_path = ""

        self._server_handler_service.started.connect(self._on_api_started)
        self._server_handler_service.stopped.connect(self._on_api_stopped)
        self._server_handler_service.failed.connect(self._on_api_failed)
        self._server_handler_service.request_processed.connect(self._on_request_processed)
        self._print_workflow_service.print_started.connect(self._on_print_started)
        self._print_workflow_service.print_finished.connect(self._on_print_finished)
        self._print_workflow_service.print_failed.connect(self._on_print_failed)
        if self._config.data_path:
            self._load_format_file(self._config.data_path, reset_rows=False)
        else:
            self._refresh_raw_zpl_preview()

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

    @Property(str, constant=True)
    def template_folder_url(self) -> str:
        return DEFAULT_TEMPLATE_DIR.as_uri()

    @Property(str, notify=configChanged)
    def schema_folder_url(self) -> str:
        data_path = Path(self._config.data_path) if self._config.data_path else None
        if data_path is not None and data_path.is_file():
            return data_path.parent.as_uri()
        return DEFAULT_TEMPLATE_DIR.as_uri()

    @Property(str, notify=templatePreviewChanged)
    def template_preview_url(self) -> str:
        preview_path = Path(self._template_preview_path) if self._template_preview_path else None
        if preview_path is None or not preview_path.is_file():
            return ""
        return preview_path.as_uri()

    @Property(bool, notify=templatePreviewChanged)
    def template_preview_available(self) -> bool:
        preview_path = Path(self._template_preview_path) if self._template_preview_path else None
        return preview_path is not None and preview_path.is_file()

    @Property(str, notify=configChanged)
    def printer_name(self) -> str:
        return self._config.printer_name

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

    @Property(list, notify=testDataChanged)
    def required_fields(self) -> list[str]:
        return self._required_fields

    @Property(str, notify=testDataChanged)
    def raw_zpl_preview(self) -> str:
        return self._raw_zpl_preview

    @Slot()
    def refresh_printers(self) -> None:
        printers = self._printer_service.installed_printers()
        if self._config.printer_name and self._config.printer_name not in printers:
            printers.insert(0, self._config.printer_name)
        self._printers = printers
        if not self._config.printer_name and self._printers:
            self._update_config(printer_name=self._printers[0])
        self.printersChanged.emit()
        self.set_status(f"\u0110\u00e3 t\u1ea3i {len(self._printers)} m\u00e1y in.")

    @Slot()
    def start_api(self) -> None:
        self._server_handler_service.start(self._config.api_url)

    @Slot()
    def stop_api(self) -> None:
        self._server_handler_service.stop()

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
        self._refresh_raw_zpl_preview()

    @Slot(str)
    def set_data_path(self, data_path: str) -> None:
        cleaned_path = self._clean_file_url(data_path)
        self._update_config(data_path=cleaned_path)
        self._load_format_file(cleaned_path, reset_rows=True)

    @Slot(str)
    def set_printer_name(self, printer_name: str) -> None:
        self._update_config(printer_name=printer_name)

    @Slot()
    def print_test(self) -> None:
        request = PrintRequest(labels=self._test_labels())
        self._print_workflow_service.submit_test(request)

    @Slot()
    def reload_format(self) -> None:
        self.reload_schema()

    @Slot()
    def reload_schema(self) -> None:
        if not self._config.data_path:
            self.set_status("Ch\u01b0a ch\u1ecdn file schema.")
            return
        self._load_format_file(self._config.data_path, reset_rows=True)

    @Slot(int, str, str)
    def update_test_value(self, row_index: int, column_key: str, value: str) -> None:
        if row_index < 0 or row_index >= len(self._test_rows):
            return
        if column_key != "value":
            return
        row = dict(self._test_rows[row_index])
        if row.get(column_key) == value:
            return
        row[column_key] = value
        self._test_rows[row_index] = row
        self.testDataChanged.emit()
        self._refresh_raw_zpl_preview()

    @Slot(str, str, str)
    def update_test_cell(self, field: str, column_key: str, value: str) -> None:
        if column_key != "value":
            return
        for row_index, row_data in enumerate(self._test_rows):
            if row_data.get("key") == field:
                self.update_test_value(row_index, column_key, value)
                return

    def _on_api_started(self, url: str) -> None:
        self._api_running = True
        self.apiRunningChanged.emit()
        self.set_status(f"M\u00e1y ch\u1ee7 API \u0111\u00e3 kh\u1edfi \u0111\u1ed9ng t\u1ea1i {url}")

    def _on_api_stopped(self) -> None:
        self._api_running = False
        self.apiRunningChanged.emit()
        self.set_status("M\u00e1y ch\u1ee7 API \u0111\u00e3 d\u1eebng")

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
        self.set_status(f"\u0110ang x\u1eed l\u00fd {label_count} tem...")

    def _on_print_finished(self, payload: object) -> None:
        if isinstance(payload, dict):
            output_path = payload.get("output_path")
            self.set_status(
                "\u0110\u00e3 in xong: "
                f"{payload.get('label_count', 0)} tem, "
                f"{payload.get('page_count', 0)} trang, "
                f"m\u00e1y in {payload.get('printer_name', '-')}."
                + (f" File ZPL: {output_path}" if output_path else "")
            )
            return
        self.set_status("\u0110\u00e3 in xong.")

    def _on_print_failed(self, message: str) -> None:
        self.set_status(f"In th\u1ea5t b\u1ea1i: {message}")

    def _update_config(self, **changes: object) -> None:
        next_config = replace(self._config, **changes)
        if next_config == self._config:
            return
        self._config = next_config
        try:
            self._settings_repository.save(self._config)
        except OSError as exc:
            self.set_status(f"Kh\u00f4ng th\u1ec3 l\u01b0u c\u00e0i \u0111\u1eb7t: {exc}")
            return
        self.configChanged.emit()

    def _load_format_file(self, data_path: str, reset_rows: bool) -> None:
        if not data_path:
            return
        try:
            print_format = self._print_template_service.load_format(data_path)
            template_fields = self._print_workflow_service.template_fields(
                print_format.template_path
            )
        except Exception as exc:
            self._set_template_preview_path("")
            self.set_status(f"Kh\u00f4ng th\u1ec3 t\u1ea3i schema: {exc}")
            return

        self._required_fields = print_format.required_fields
        self._default_values = dict(print_format.default_values or {})
        self._set_template_preview_path(print_format.preview_path)
        self._test_rows = self._build_required_test_rows(reset_rows=reset_rows)
        self._update_config(
            data_path=data_path,
            template_path=print_format.template_path,
            required_fields=self._required_fields,
        )
        self.testDataChanged.emit()
        self._refresh_raw_zpl_preview()
        missing_fields = [
            field for field in self._required_fields if field not in template_fields
        ]
        if missing_fields:
            self.set_status(
                "\u0110\u00e3 t\u1ea3i schema, nh\u01b0ng template thi\u1ebfu: "
                + ", ".join(missing_fields)
            )
            return
        self.set_status(f"\u0110\u00e3 t\u1ea3i schema: {len(self._required_fields)} tr\u01b0\u1eddng.")

    def _set_template_preview_path(self, preview_path: str) -> None:
        if preview_path == self._template_preview_path:
            return
        self._template_preview_path = preview_path
        self.templatePreviewChanged.emit()

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
        label_count = self._template_column_count()
        values = {
            str(row.get("key", "")).strip(): str(row.get("value", ""))
            for row in self._test_rows
            if str(row.get("key", "")).strip()
        }
        return [dict(values) for _ in range(label_count)]

    def _build_required_test_rows(self, reset_rows: bool) -> list[dict[str, str]]:
        existing_values = {}
        if not reset_rows:
            existing_values = {
                str(row.get("key", "")).strip(): str(row.get("value", ""))
                for row in self._test_rows
                if str(row.get("key", "")).strip()
            }
        return [
            {
                "key": field,
                "value": existing_values.get(
                    field,
                    self._default_values.get(field, ""),
                ),
            }
            for field in self._required_fields
        ]

    def _template_column_count(self) -> int:
        if not self._config.template_path:
            return 1
        try:
            return max(1, self._print_workflow_service.template_column_count(
                self._config.template_path
            ))
        except Exception:
            return 1

    def _refresh_raw_zpl_preview(self) -> None:
        if not self._config.template_path:
            self._raw_zpl_preview = ""
            self.testDataChanged.emit()
            return
        try:
            template_text = self._print_workflow_service.preview(
                PrintRequest(labels=self._test_labels())
            )
        except Exception:
            try:
                self._raw_zpl_preview = Path(self._config.template_path).read_text(encoding="utf-8")
            except Exception:
                self._raw_zpl_preview = ""
        else:
            self._raw_zpl_preview = template_text
        self.testDataChanged.emit()
