from __future__ import annotations

from src.services.api_server_service import ApiServerService
from src.services.printer_discovery_service import PrinterDiscoveryService
from src.services.print_spooler_service import PrintSpoolerService
from src.services.print_workflow_service import PrintWorkflowService
from src.services.settings_repository_service import SettingsRepositoryService
from src.services.template_service import TemplateService
from src.viewmodels.main_viewmodel import MainViewModel


class ApplicationContainer:
    """Composition root for services and ViewModels."""

    def __init__(self) -> None:
        self.settings_repository_service = SettingsRepositoryService()
        self.printer_discovery_service = PrinterDiscoveryService()
        self.template_service = TemplateService()
        self.print_spooler_service = PrintSpoolerService()
        self.api_server_service = ApiServerService()
        self.print_workflow_service = PrintWorkflowService(
            settings_repository=self.settings_repository_service,
            template_service=self.template_service,
            spooler_service=self.print_spooler_service,
        )
        self.main_viewmodel = MainViewModel(
            settings_repository=self.settings_repository_service,
            printer_discovery_service=self.printer_discovery_service,
            api_server_service=self.api_server_service,
        )
        self.api_server_service.print_request_received.connect(
            self.print_workflow_service.submit
        )

    def start(self) -> None:
        self.main_viewmodel.refresh_printers()

    def shutdown(self) -> None:
        self.api_server_service.stop()
