from __future__ import annotations

from pathlib import Path
import re

from PySide6.QtCore import QObject

from src.core.errors import TemplateError


class TemplateService(QObject):
    """Loads ZPL templates and discovers placeholders."""

    _placeholder_pattern = re.compile(
        r"(?:(?<=\^FD)|(?<![\^A-Za-z0-9_]))([A-Za-z][A-Za-z0-9_]*)_(\d+)\b"
    )

    def load_template(self, path: str) -> str:
        template_path = Path(path)
        if not template_path.exists():
            raise TemplateError(f"Template file does not exist: {path}")
        return template_path.read_text(encoding="utf-8")

    def discover_fields(self, template_text: str) -> list[str]:
        fields = {match.group(1) for match in self._placeholder_pattern.finditer(template_text)}
        return sorted(fields)

    def render(self, template_text: str, labels: list[dict[str, str]], columns: int) -> list[str]:
        if not template_text:
            raise TemplateError("Template content is empty.")
        if columns < 1:
            raise TemplateError("Stamp columns must be greater than zero.")
        if not labels:
            raise TemplateError("Print data is empty.")

        pages: list[str] = []
        row_count = (len(labels) + columns - 1) // columns
        for row_index in range(row_count):
            row_labels = labels[row_index * columns : (row_index + 1) * columns]
            pages.append(self._render_page(template_text, row_labels, columns))
        return pages

    def _render_page(
        self,
        template_text: str,
        row_labels: list[dict[str, str]],
        columns: int,
    ) -> str:
        def replace_placeholder(match: re.Match[str]) -> str:
            field_name = match.group(1)
            column_index = int(match.group(2))
            if column_index >= columns or column_index >= len(row_labels):
                return ""
            value = row_labels[column_index].get(field_name, "")
            return "" if value is None else str(value)

        return self._placeholder_pattern.sub(replace_placeholder, template_text)
