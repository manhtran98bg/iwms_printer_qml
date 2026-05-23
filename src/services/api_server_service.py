from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Slot


class ApiServerService(QObject):
    """Local HTTP server facade. FastAPI/uvicorn implementation comes next."""

    started = Signal(str)
    stopped = Signal()
    failed = Signal(str)
    print_request_received = Signal(object)

    def __init__(self) -> None:
        super().__init__()
        self._running = False
        self._url = ""

    @Slot(str)
    def start(self, url: str) -> None:
        self._url = url
        self._running = True
        self.started.emit(url)

    @Slot()
    def stop(self) -> None:
        if not self._running:
            return
        self._running = False
        self.stopped.emit()

    def request_stop(self) -> None:
        self.stop()
