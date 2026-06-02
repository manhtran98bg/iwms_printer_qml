from __future__ import annotations

from datetime import datetime
import json
from json import JSONDecodeError
from pathlib import Path
import re
from typing import Any

from PySide6.QtCore import QObject

from src.core.errors import TemplateError
from src.models.print_format import PrintFormat


class PrintTemplateService(QObject):
    """Loads print format JSON, reads ZPL templates, and renders placeholders."""

    CURRENT_DATETIME_TOKEN = "{{current_datetime}}"
    _template_keys = ("template", "templatePath", "templateFile")
    _placeholder_pattern = re.compile(r"(?<=\^FD)(.+?)_(\d+)(?=\^FS)")

    def load_format(self, path: str) -> PrintFormat:
        format_path = Path(path)
        if not format_path.exists():
            raise TemplateError(f"Format file does not exist: {path}")
        try:
            payload = json.loads(format_path.read_text(encoding="utf-8"))
        except (OSError, JSONDecodeError) as exc:
            raise TemplateError(f"Kh\u00f4ng th\u1ec3 \u0111\u1ecdc JSON schema: {exc}") from exc
        if not isinstance(payload, dict):
            raise TemplateError("JSON schema ph\u1ea3i l\u00e0 object.")

        required_fields = self._required_fields(payload)
        template_path = self._template_path(payload, format_path.parent)
        default_values = self._default_values(payload, required_fields)
        return PrintFormat(
            required_fields=required_fields,
            template_path=template_path,
            default_values=default_values,
        )

    def load_template(self, path: str) -> str:
        template_path = Path(path)
        if not template_path.exists():
            raise TemplateError(f"File template kh\u00f4ng t\u1ed3n t\u1ea1i: {path}")
        return template_path.read_text(encoding="utf-8")

    def discover_fields(self, template_text: str) -> list[str]:
        fields = {match.group(1) for match in self._placeholder_pattern.finditer(template_text)}
        return sorted(fields)

    def discover_column_count(self, template_text: str) -> int:
        indexes = [
            int(match.group(2))
            for match in self._placeholder_pattern.finditer(template_text)
        ]
        if not indexes:
            return 1
        return max(indexes) + 1

    def render(self, template_text: str, labels: list[dict[str, str]], columns: int) -> list[str]:
        if not template_text:
            raise TemplateError("N\u1ed9i dung template \u0111ang tr\u1ed1ng.")
        if columns < 1:
            raise TemplateError("S\u1ed1 c\u1ed9t template ph\u1ea3i l\u1edbn h\u01a1n 0.")
        if not labels:
            raise TemplateError("D\u1eef li\u1ec7u in \u0111ang tr\u1ed1ng.")

        pages: list[str] = []
        row_count = (len(labels) + columns - 1) // columns
        for row_index in range(row_count):
            row_labels = labels[row_index * columns : (row_index + 1) * columns]
            pages.append(self._render_page(template_text, row_labels, columns))
        return pages

    def _required_fields(self, payload: dict[str, Any]) -> list[str]:
        raw_fields = payload.get("require", payload.get("requiredFields", []))
        if not isinstance(raw_fields, list):
            raise TemplateError("Key 'require' trong JSON schema ph\u1ea3i l\u00e0 array.")

        fields: list[str] = []
        seen: set[str] = set()
        for raw_field in raw_fields:
            field = str(raw_field).strip()
            if not field or field in seen:
                continue
            seen.add(field)
            fields.append(field)
        if not fields:
            raise TemplateError("JSON schema ph\u1ea3i c\u00f3 \u00edt nh\u1ea5t m\u1ed9t field b\u1eaft bu\u1ed9c.")
        return fields

    def _template_path(self, payload: dict[str, Any], base_dir: Path) -> str:
        raw_template_path = ""
        for key in self._template_keys:
            value = payload.get(key)
            if value:
                raw_template_path = str(value).strip()
                break
        if not raw_template_path:
            raise TemplateError(
                "JSON schema ph\u1ea3i c\u00f3 key \u0111\u01b0\u1eddng d\u1eabn template: template, templatePath, ho\u1eb7c templateFile."
            )

        template_path = Path(raw_template_path)
        if not template_path.is_absolute():
            template_path = base_dir / template_path
        return str(template_path.resolve())

    def _default_values(
        self,
        payload: dict[str, Any],
        required_fields: list[str],
    ) -> dict[str, str]:
        raw_defaults = payload.get("defaults", {})
        if raw_defaults is None:
            return {}
        if not isinstance(raw_defaults, dict):
            raise TemplateError("Key 'defaults' trong JSON schema ph\u1ea3i l\u00e0 object.")

        required_field_set = set(required_fields)
        defaults: dict[str, str] = {}
        for key, value in raw_defaults.items():
            field_name = str(key).strip()
            if not field_name or field_name not in required_field_set:
                continue
            defaults[field_name] = "" if value is None else str(value)
        return defaults

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

        rendered_text = template_text.replace(
            self.CURRENT_DATETIME_TOKEN,
            datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        )
        return self._placeholder_pattern.sub(replace_placeholder, rendered_text)
