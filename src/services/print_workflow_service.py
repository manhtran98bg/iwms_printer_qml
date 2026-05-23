from __future__ import annotations

from PySide6.QtCore import QObject, Signal

from src.models.print_request import PrintRequest
from src.services.print_spooler_service import PrintSpoolerService
from src.services.settings_repository_service import SettingsRepositoryService
from src.services.template_service import TemplateService


class PrintWorkflowService(QObject):
    """Coordinates validation, template rendering, and RAW printing."""

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

    def submit(self, request: PrintRequest) -> None:
        self.print_started.emit(request.to_dict())
        self.print_failed.emit("Print workflow is scaffolded but not implemented.")
