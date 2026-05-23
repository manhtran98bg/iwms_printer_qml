from __future__ import annotations

from PySide6.QtCore import Property, Signal, Slot

from src.core.constants import APP_TITLE
from src.models.printer_config import PrinterConfig
from src.services.api_server_service import ApiServerService
from src.services.printer_discovery_service import PrinterDiscoveryService
from src.services.settings_repository_service import SettingsRepositoryService
from src.viewmodels.base_viewmodel import BaseViewModel


class MainViewModel(BaseViewModel):
    statusChanged = Signal()
    apiRunningChanged = Signal()
    configChanged = Signal()
    printersChanged = Signal()

    def __init__(
        self,
        settings_repository: SettingsRepositoryService,
        printer_discovery_service: PrinterDiscoveryService,
        api_server_service: ApiServerService,
    ) -> None:
        super().__init__()
        self._settings_repository = settings_repository
        self._printer_discovery_service = printer_discovery_service
        self._api_server_service = api_server_service
        self._config = self._settings_repository.load()
        self._status = "Initialized"
        self._api_running = False
        self._printers: list[str] = []

        self._api_server_service.started.connect(self._on_api_started)
        self._api_server_service.stopped.connect(self._on_api_stopped)
        self._api_server_service.failed.connect(self._on_api_failed)

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

    @Property(list, notify=printersChanged)
    def printers(self) -> list[str]:
        return self._printers

    @Slot()
    def refresh_printers(self) -> None:
        self._printers = self._printer_discovery_service.installed_printers()
        self.printersChanged.emit()

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
