from __future__ import annotations

import os
import sys
from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtGui import QFont, QFontDatabase, QIcon
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QUrl

from src.composition.application_container import ApplicationContainer
from src.composition.qml_context import bind_qml_context
from src.core.constants import APP_NAME

try:
    from src import resources_rc  # noqa: F401
except ImportError:
    resources_rc = None


def run() -> int:
    os.environ.setdefault("QT_QUICK_CONTROLS_STYLE", "Basic")

    app = QGuiApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    icon_path = Path(__file__).resolve().parent / "assets" / "icon" / "icon.ico"
    app.setWindowIcon(QIcon(str(icon_path)))
    QFontDatabase.addApplicationFont(":/assets/font/Roboto-Regular.ttf")
    QFontDatabase.addApplicationFont(":/assets/font/Roboto-Medium.ttf")
    QFontDatabase.addApplicationFont(":/assets/font/Roboto-Bold.ttf")
    app.setFont(QFont("Roboto"))

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
