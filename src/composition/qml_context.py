from __future__ import annotations

from PySide6.QtQml import QQmlApplicationEngine

from src.composition.application_container import ApplicationContainer


def bind_qml_context(engine: QQmlApplicationEngine, container: ApplicationContainer) -> None:
    engine.rootContext().setContextProperty("mainViewModel", container.main_viewmodel)
