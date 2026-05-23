from __future__ import annotations

from PySide6.QtCore import QObject, QMetaObject, QThread, Qt


class ThreadManager:
    """Owns QThreads used by long-running QObject services."""

    def __init__(self) -> None:
        self._threads: list[QThread] = []
        self._workers: list[QObject] = []

    def move_to_thread(
        self,
        worker: QObject,
        name: str,
        start_method: str | None = None,
        stop_method: str = "stop",
    ) -> QThread:
        thread = QThread()
        thread.setObjectName(name)
        worker.moveToThread(thread)
        if start_method:
            thread.started.connect(getattr(worker, start_method))
        worker.setProperty("_thread_manager_stop_method", stop_method)
        self._workers.append(worker)
        self._threads.append(thread)
        return thread

    def start_all(self) -> None:
        for thread in self._threads:
            if not thread.isRunning():
                thread.start()

    def stop_all(self) -> None:
        for worker in self._workers:
            self._request_worker_stop(worker)
        for worker in self._workers:
            self._stop_worker(worker)
        for thread in self._threads:
            thread.quit()
        for thread in self._threads:
            thread.wait(1500)

    def _request_worker_stop(self, worker: QObject) -> None:
        if hasattr(worker, "request_stop"):
            getattr(worker, "request_stop")()

    def _stop_worker(self, worker: QObject) -> None:
        stop_method = worker.property("_thread_manager_stop_method") or "stop"
        if not hasattr(worker, stop_method):
            return
        worker_thread = worker.thread()
        if worker_thread == QThread.currentThread() or not worker_thread.isRunning():
            getattr(worker, stop_method)()
            return
        QMetaObject.invokeMethod(worker, stop_method, Qt.ConnectionType.QueuedConnection)
