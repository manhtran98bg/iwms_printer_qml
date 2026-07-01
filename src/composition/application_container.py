from __future__ import annotations

import logging

from src.services.printer_service import PrinterService
from src.services.print_template_service import PrintTemplateService
from src.services.print_workflow_service import PrintWorkflowService
from src.services.server_handler_service import ServerHandlerService
from src.services.settings_repository_service import SettingsRepositoryService
from src.viewmodels.main_viewmodel import MainViewModel


logger = logging.getLogger(__name__)


class ApplicationContainer:
    """Composition root for services and ViewModels."""

    def __init__(self) -> None:
        logger.info("Initializing application container")
        self.settings_repository_service = SettingsRepositoryService()
        self.printer_service = PrinterService()
        self.print_template_service = PrintTemplateService()
        self.server_handler_service = ServerHandlerService()
        self.print_workflow_service = PrintWorkflowService(
            settings_repository=self.settings_repository_service,
            print_template_service=self.print_template_service,
            printer_service=self.printer_service,
        )
        self.main_viewmodel = MainViewModel(
            settings_repository=self.settings_repository_service,
            printer_service=self.printer_service,
            server_handler_service=self.server_handler_service,
            print_workflow_service=self.print_workflow_service,
            print_template_service=self.print_template_service,
        )
        self.server_handler_service.print_request_received.connect(
            self.print_workflow_service.submit
        )
        logger.info("Application container initialized")

    def start(self) -> None:
        logger.info("Starting application services")
        self.main_viewmodel.refresh_printers()
        self.main_viewmodel.start_api()

    def shutdown(self) -> None:
        logger.info("Shutting down application services")
        self.server_handler_service.stop()
