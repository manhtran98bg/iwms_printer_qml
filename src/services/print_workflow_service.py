from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import QObject, Signal, Slot

from src.core.errors import PrintRequestError
from src.core.runtime_paths import APP_ENVIRONMENT_ROOT, ASSETS_TEMPLATE_ROOT
from src.models.print_format import PrintFormat
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
        self._routed_formats: list[PrintFormat] | None = None

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
            rendered_pages = self._render_pages(config, request, auto_route=False)
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
        print_format = self._render_format(config)
        template_text = self._print_template_service.load_template(print_format.template_path)
        columns = self._print_template_service.discover_column_count(template_text)
        rendered_pages = self._print_template_service.render(
            template_text,
            request.labels,
            columns,
            print_format.margin_left,
            print_format.margin_top,
            print_format.variables,
            print_format.computed_fields,
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
        rendered_pages = self._render_pages(config, request, auto_route=True)
        self._printer_service.print_raw(config.printer_name, rendered_pages)
        return rendered_pages

    def _render_pages(
        self,
        config: PrinterConfig,
        request: PrintRequest,
        auto_route: bool = False,
    ) -> list[str]:
        if auto_route:
            return self._render_routed_pages(config, request)

        print_format = self._render_format(config)
        return self._render_labels(print_format, request.labels)

    def _render_routed_pages(
        self,
        config: PrinterConfig,
        request: PrintRequest,
    ) -> list[str]:
        fallback_format = self._render_format(config)
        routed_formats = self._load_routed_formats()
        rendered_pages: list[str] = []
        current_format: PrintFormat | None = None
        current_labels: list[dict] = []

        def flush_current_labels() -> None:
            nonlocal current_format, current_labels
            if current_format is None or not current_labels:
                return
            rendered_pages.extend(self._render_labels(current_format, current_labels))
            current_format = None
            current_labels = []

        for label in request.labels:
            matched_format = (
                self._print_template_service.matching_format(label, routed_formats)
                or fallback_format
            )
            if current_format is None:
                current_format = matched_format
            elif self._format_key(current_format) != self._format_key(matched_format):
                flush_current_labels()
                current_format = matched_format
            current_labels.append(label)

        flush_current_labels()
        return rendered_pages

    def _render_labels(
        self,
        print_format: PrintFormat,
        labels: list[dict],
    ) -> list[str]:
        template_text = self._print_template_service.load_template(print_format.template_path)
        columns = self._print_template_service.discover_column_count(template_text)
        return self._print_template_service.render(
            template_text,
            labels,
            columns,
            print_format.margin_left,
            print_format.margin_top,
            print_format.variables,
            print_format.computed_fields,
        )

    def _render_format(self, config: PrinterConfig) -> PrintFormat:
        if config.data_path:
            return self._print_template_service.load_format(config.data_path)
        return PrintFormat(template_path=config.template_path)

    def _load_routed_formats(self) -> list[PrintFormat]:
        if self._routed_formats is None:
            self._routed_formats = self._print_template_service.load_routed_formats(
                ASSETS_TEMPLATE_ROOT
            )
        return self._routed_formats

    def _format_key(self, print_format: PrintFormat) -> str:
        return print_format.schema_path or print_format.template_path

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
