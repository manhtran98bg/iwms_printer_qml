from __future__ import annotations

from pathlib import Path
import re

from PySide6.QtCore import QObject


class TemplateService(QObject):
    """Loads ZPL templates and discovers placeholders."""

    _placeholder_pattern = re.compile(r"\b([A-Za-z][A-Za-z0-9_]*)_(\d+)\b")

    def load_template(self, path: str) -> str:
        return Path(path).read_text(encoding="utf-8")

    def discover_fields(self, template_text: str) -> list[str]:
        fields = {match.group(1) for match in self._placeholder_pattern.finditer(template_text)}
        return sorted(fields)

    def render(self, template_text: str, labels: list[dict[str, str]], columns: int) -> list[str]:
        return []
