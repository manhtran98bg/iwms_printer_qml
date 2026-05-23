from __future__ import annotations

import os
import sys
from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QUrl

from src.composition.application_container import ApplicationContainer
from src.composition.qml_context import bind_qml_context


def run() -> int:
    os.environ.setdefault("QT_QUICK_CONTROLS_STYLE", "Imagine")

    app = QGuiApplication(sys.argv)
    container = ApplicationContainer()
    app.aboutToQuit.connect(container.shutdown)

    engine = QQmlApplicationEngine()
    bind_qml_context(engine, container)

    qml_root = Path(__file__).resolve().parent / "views" / "qml"
    engine.addImportPath(str(qml_root))
    engine.load(QUrl.fromLocalFile(str(qml_root / "Main.qml")))
    if not engine.rootObjects():
        return 1

    container.start()
    return app.exec()
