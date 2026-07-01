from __future__ import annotations

import logging
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
from src.core.logging_config import configure_logging

try:
    from src import resources_rc  # noqa: F401
except ImportError:
    resources_rc = None


logger = logging.getLogger(__name__)


def run() -> int:
    configure_logging()
    logger.info("Starting %s", APP_NAME)
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
        logger.error("Failed to load QML root from %s", qml_root / "Main.qml")
        return 1
    logger.info("Loaded QML root from %s", qml_root / "Main.qml")

    container.start()
    exit_code = app.exec()
    logger.info("Application exited with code %s", exit_code)
    return exit_code
