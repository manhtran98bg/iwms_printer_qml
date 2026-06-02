from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Slot

from src.core.errors import PrintRequestError
from src.models.printer_config import PrinterConfig
from src.models.print_request import PrintRequest
from src.services.print_spooler_service import PrintSpoolerService
from src.services.settings_repository_service import SettingsRepositoryService
from src.services.template_service import TemplateService


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
        template_service: TemplateService,
        spooler_service: PrintSpoolerService,
    ) -> None:
        super().__init__()
        self._settings_repository = settings_repository
        self._template_service = template_service
        self._spooler_service = spooler_service

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
            if self._is_zpl_printer(config.printer_name):
                rendered_pages = self._print_raw(config, request)
                page_count = len(rendered_pages)
                print_mode = "raw"
            else:
                self._spooler_service.print_test_document(config.printer_name, request.labels)
                page_count = 1
                print_mode = "document"
        except Exception as exc:
            self.print_failed.emit(str(exc))
            return
        self.print_finished.emit(
            {
                "label_count": len(request.labels),
                "page_count": page_count,
                "printer_name": config.printer_name,
                "print_mode": print_mode,
            }
        )

    def _validate_config(self, config: object) -> None:
        if not getattr(config, "printer_name", ""):
            raise PrintRequestError("Printer is not selected.")
        if not getattr(config, "template_path", ""):
            raise PrintRequestError("Template file is not selected.")
        if getattr(config, "stamp_columns", 0) < 1:
            raise PrintRequestError("Stamp columns must be greater than zero.")

    def _validate_test_config(self, config: object) -> None:
        if not getattr(config, "printer_name", ""):
            raise PrintRequestError("Printer is not selected.")
        if getattr(config, "stamp_columns", 0) < 1:
            raise PrintRequestError("Stamp columns must be greater than zero.")
        if self._is_zpl_printer(getattr(config, "printer_name", "")):
            self._validate_config(config)

    def _validate_request(self, request: PrintRequest) -> None:
        if not request.labels:
            raise PrintRequestError("Print request has no labels.")
        for index, label in enumerate(request.labels):
            if not isinstance(label, dict):
                raise PrintRequestError(f"Label at index {index} must be an object.")

    def _print_raw(self, config: PrinterConfig, request: PrintRequest) -> list[str]:
        template_text = self._template_service.load_template(config.template_path)
        rendered_pages = self._template_service.render(
            template_text,
            request.labels,
            config.stamp_columns,
        )
        self._spooler_service.print_raw(config.printer_name, rendered_pages)
        return rendered_pages

    def _is_zpl_printer(self, printer_name: str) -> bool:
        normalized_name = f" {printer_name.strip().casefold()} "
        return any(token in normalized_name for token in self._zpl_printer_tokens)
