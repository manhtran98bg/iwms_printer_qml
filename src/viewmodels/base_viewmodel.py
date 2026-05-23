from __future__ import annotations

from PySide6.QtCore import QObject, Signal


class BaseViewModel(QObject):
    error_occurred = Signal(str)

    def __init__(self) -> None:
        super().__init__()
