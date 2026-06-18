from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import QObject, Signal, Slot

from src.core.errors import PrintRequestError
from src.core.runtime_paths import APP_ENVIRONMENT_ROOT
from src.models.printer_config import PrinterConfig
from src.models.print_request import PrintRequest
from src.services.printer_service import PrinterService
from src.services.print_template_service import PrintTemplateService
from src.services.settings_repository_service import SettingsRepositoryService


class PrintWorkflowService(QObject):
    """Coordinates validation, template rendering, and printing."""

    _zpl_printer_tokens = (
        "zebra",
        "zdesigner",
        " zpl",
        "zpl ",
        "zd220",
        "zd230",
        "zd410",
        "zd411",
        "zd420",
        "zd421",
        "zd500",
        "zd510",
        "zd611",
        "zd621",
        "zt111",
        "zt220",
        "zt230",
        "zt231",
        "zt410",
        "zt411",
        "zt420",
        "zt421",
        "gx420",
        "gx430",
        "gk420",
    )

    print_started = Signal(object)
    print_finished = Signal(object)
    print_failed = Signal(str)

    def __init__(
        self,
        settings_repository: SettingsRepositoryService,
        print_template_service: PrintTemplateService,
        printer_service: PrinterService,
    ) -> None:
        super().__init__()
        self._settings_repository = settings_repository
        self._print_template_service = print_template_service
        self._printer_service = printer_service

    @Slot(object)
    def submit(self, request: PrintRequest) -> None:
        self.print_started.emit(request.to_dict())
        try:
            config = self._settings_repository.load()
            self._validate_config(config)
            self._validate_request(request)
            rendered_pages = self._print_raw(config, request)
        except Exception as exc:
            self.print_failed.emit(str(exc))
            return
        self.print_finished.emit(
            {
                "label_count": len(request.labels),
                "page_count": len(rendered_pages),
                "printer_name": config.printer_name,
            }
        )

    @Slot(object)
    def submit_test(self, request: PrintRequest) -> None:
        self.print_started.emit(request.to_dict())
        try:
            config = self._settings_repository.load()
            self._validate_test_config(config)
            self._validate_request(request)
            rendered_pages = self._render_pages(config, request)
            output_path = self._write_test_output(rendered_pages)
            self._printer_service.print_raw(config.printer_name, rendered_pages)
        except Exception as exc:
            self.print_failed.emit(str(exc))
            return
        self.print_finished.emit(
            {
                "label_count": len(request.labels),
                "page_count": len(rendered_pages),
                "printer_name": config.printer_name,
                "print_mode": "raw",
                "output_path": str(output_path),
            }
        )

    def preview(self, request: PrintRequest) -> str:
        config = self._settings_repository.load()
        if not getattr(config, "template_path", ""):
            return ""
        template_path, margin_left, margin_top = self._render_settings(config)
        template_text = self._print_template_service.load_template(template_path)
        columns = self._print_template_service.discover_column_count(template_text)
        rendered_pages = self._print_template_service.render(
            template_text,
            request.labels,
            columns,
            margin_left,
            margin_top,
        )
        return "\n".join(rendered_pages)

    def template_column_count(self, template_path: str) -> int:
        template_text = self._print_template_service.load_template(template_path)
        return self._print_template_service.discover_column_count(template_text)

    def template_fields(self, template_path: str) -> list[str]:
        template_text = self._print_template_service.load_template(template_path)
        return self._print_template_service.discover_fields(template_text)

    def _validate_config(self, config: object) -> None:
        if not getattr(config, "printer_name", ""):
            raise PrintRequestError("Ch\u01b0a ch\u1ecdn m\u00e1y in.")
        if not getattr(config, "template_path", ""):
            raise PrintRequestError("Ch\u01b0a ch\u1ecdn file template.")

    def _validate_test_config(self, config: object) -> None:
        if not getattr(config, "printer_name", ""):
            raise PrintRequestError("Ch\u01b0a ch\u1ecdn m\u00e1y in.")
        if not getattr(config, "template_path", ""):
            raise PrintRequestError("Ch\u01b0a ch\u1ecdn file template.")

    def _validate_request(self, request: PrintRequest) -> None:
        if not request.labels:
            raise PrintRequestError("Request in kh\u00f4ng c\u00f3 tem.")
        for index, label in enumerate(request.labels):
            if not isinstance(label, dict):
                raise PrintRequestError(f"Tem t\u1ea1i index {index} ph\u1ea3i l\u00e0 object.")

    def _print_raw(self, config: PrinterConfig, request: PrintRequest) -> list[str]:
        rendered_pages = self._render_pages(config, request)
        self._printer_service.print_raw(config.printer_name, rendered_pages)
        return rendered_pages

    def _render_pages(self, config: PrinterConfig, request: PrintRequest) -> list[str]:
        template_path, margin_left, margin_top = self._render_settings(config)
        template_text = self._print_template_service.load_template(template_path)
        columns = self._print_template_service.discover_column_count(template_text)
        return self._print_template_service.render(
            template_text,
            request.labels,
            columns,
            margin_left,
            margin_top,
        )

    def _render_settings(self, config: PrinterConfig) -> tuple[str, int, int]:
        if config.data_path:
            print_format = self._print_template_service.load_format(config.data_path)
            return (
                print_format.template_path,
                print_format.margin_left,
                print_format.margin_top,
            )
        return config.template_path, 0, 0

    def _write_test_output(self, rendered_pages: list[str]):
        output_dir = APP_ENVIRONMENT_ROOT / "test_output"
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"test_print_{timestamp}.txt"
        output_path.write_text("\n".join(rendered_pages), encoding="utf-8")
        return output_path

    def _is_zpl_printer(self, printer_name: str) -> bool:
        normalized_name = f" {printer_name.strip().casefold()} "
        return any(token in normalized_name for token in self._zpl_printer_tokens)
