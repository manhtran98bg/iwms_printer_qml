from __future__ import annotations

from datetime import datetime
import json
from json import JSONDecodeError
from pathlib import Path
import re
import string
from typing import Any

from PySide6.QtCore import QObject

from src.core.errors import TemplateError
from src.models.print_format import PrintFormat


class PrintTemplateService(QObject):
    """Loads print format JSON, reads ZPL templates, and renders placeholders."""

    CURRENT_DATETIME_TOKEN = "{{current_datetime}}"
    MARGIN_LEFT_TOKEN = "{{margin_left}}"
    MARGIN_TOP_TOKEN = "{{margin_top}}"
    MIN_MARGIN = -20
    MAX_MARGIN = 20
    _template_keys = ("template", "templatePath", "templateFile")
    _preview_keys = ("preview", "previewPath", "previewFile", "image", "imagePath", "imageFile")
    _placeholder_pattern = re.compile(r"(?<=\^FD)(.+?)_(\d+)(?=\^FS)")
    _computed_token_pattern = re.compile(r"\{([A-Za-z_][A-Za-z0-9_.]*)\}")

    def load_format(self, path: str) -> PrintFormat:
        format_path = Path(path)
        if not format_path.exists():
            raise TemplateError(f"Format file does not exist: {path}")
        payload = self._load_schema_payload(format_path)

        required_fields = self._required_fields(payload)
        template_path = self._template_path(payload, format_path.parent)
        preview_path = self._optional_path(payload, format_path.parent, self._preview_keys)
        margin_left, margin_top = self._print_settings(payload)
        routing = self._routing(payload)
        variables = self._variables(payload)
        computed_fields = self._computed_fields(payload)
        default_values = self._default_values(payload, required_fields)
        return PrintFormat(
            schema_path=str(format_path.resolve()),
            required_fields=required_fields,
            template_path=template_path,
            preview_path=preview_path,
            margin_left=margin_left,
            margin_top=margin_top,
            routing=routing,
            variables=variables,
            computed_fields=computed_fields,
            default_values=default_values,
        )

    def load_routed_formats(self, root_path: str | Path) -> list[PrintFormat]:
        root = Path(root_path)
        if not root.exists():
            return []

        routed_formats: list[PrintFormat] = []
        for schema_path in sorted(root.rglob("*_schema.json")):
            print_format = self.load_format(str(schema_path))
            if print_format.routing:
                routed_formats.append(print_format)
        return sorted(
            routed_formats,
            key=lambda print_format: (
                int(print_format.routing.get("priority", 0)),
                print_format.schema_path,
            ),
            reverse=True,
        )

    def matching_format(
        self,
        label: dict[str, Any],
        formats: list[PrintFormat],
    ) -> PrintFormat | None:
        for print_format in formats:
            if self._matches_routing(label, print_format.routing):
                return print_format
        return None

    def save_print_settings(self, path: str, margin_left: int, margin_top: int) -> None:
        format_path = Path(path)
        payload = self._load_schema_payload(format_path)
        payload["printSettings"] = {
            "margin_left": self._validate_margin(margin_left, "margin_left"),
            "margin_top": self._validate_margin(margin_top, "margin_top"),
        }
        try:
            format_path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        except OSError as exc:
            raise TemplateError(f"Kh\u00f4ng th\u1ec3 l\u01b0u printSettings: {exc}") from exc

    def load_template(self, path: str) -> str:
        template_path = Path(path)
        if not template_path.exists():
            raise TemplateError(f"File template kh\u00f4ng t\u1ed3n t\u1ea1i: {path}")
        return template_path.read_text(encoding="utf-8")

    def discover_fields(self, template_text: str) -> list[str]:
        fields = {match.group(1) for match in self._placeholder_pattern.finditer(template_text)}
        if any(field.startswith("Customer ") for field in fields):
            fields.add("Customer")
        fields.update(self._to_snake_case(field) for field in list(fields))
        return sorted(fields)

    def discover_column_count(self, template_text: str) -> int:
        indexes = [
            int(match.group(2))
            for match in self._placeholder_pattern.finditer(template_text)
        ]
        if not indexes:
            return 1
        return max(indexes) + 1

    def computation_source_fields(
        self,
        variables: dict[str, dict[str, Any]],
        computed_fields: dict[str, dict[str, Any]],
    ) -> list[str]:
        sources = {definition["source"] for definition in variables.values()}
        sources.update(
            definition["fallbackSource"]
            for definition in variables.values()
            if definition.get("fallbackSource")
        )
        for definition in computed_fields.values():
            for token in self._computed_token_pattern.findall(definition["template"]):
                if token in variables:
                    sources.add(variables[token]["source"])
                else:
                    sources.add(token)
        return sorted(sources)

    def render(
        self,
        template_text: str,
        labels: list[dict[str, Any]],
        columns: int,
        margin_left: int = 0,
        margin_top: int = 0,
        variables: dict[str, dict[str, Any]] | None = None,
        computed_fields: dict[str, dict[str, Any]] | None = None,
    ) -> list[str]:
        if not template_text:
            raise TemplateError("N\u1ed9i dung template \u0111ang tr\u1ed1ng.")
        if columns < 1:
            raise TemplateError("S\u1ed1 c\u1ed9t template ph\u1ea3i l\u1edbn h\u01a1n 0.")
        if not labels:
            raise TemplateError("D\u1eef li\u1ec7u in \u0111ang tr\u1ed1ng.")

        pages: list[str] = []
        row_count = (len(labels) + columns - 1) // columns
        normalized_margin_left = self._validate_margin(margin_left, "margin_left")
        normalized_margin_top = self._validate_margin(margin_top, "margin_top")
        for row_index in range(row_count):
            row_labels = labels[row_index * columns : (row_index + 1) * columns]
            pages.append(
                self._render_page(
                    template_text,
                    row_labels,
                    columns,
                    normalized_margin_left,
                    normalized_margin_top,
                    variables or {},
                    computed_fields or {},
                )
            )
        return pages

    def _load_schema_payload(self, format_path: Path) -> dict[str, Any]:
        try:
            payload = json.loads(format_path.read_text(encoding="utf-8"))
        except (OSError, JSONDecodeError) as exc:
            raise TemplateError(f"Kh\u00f4ng th\u1ec3 \u0111\u1ecdc JSON schema: {exc}") from exc
        if not isinstance(payload, dict):
            raise TemplateError("JSON schema ph\u1ea3i l\u00e0 object.")
        return payload

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

    def _optional_path(
        self,
        payload: dict[str, Any],
        base_dir: Path,
        keys: tuple[str, ...],
    ) -> str:
        raw_path = ""
        for key in keys:
            value = payload.get(key)
            if value:
                raw_path = str(value).strip()
                break
        if not raw_path:
            return ""

        path = Path(raw_path)
        if not path.is_absolute():
            path = base_dir / path
        return str(path.resolve())

    def _print_settings(self, payload: dict[str, Any]) -> tuple[int, int]:
        raw_settings = payload.get("printSettings", {})
        if raw_settings is None:
            raw_settings = {}
        if not isinstance(raw_settings, dict):
            raise TemplateError("Key 'printSettings' trong JSON schema ph\u1ea3i l\u00e0 object.")
        return (
            self._validate_margin(raw_settings.get("margin_left", 0), "margin_left"),
            self._validate_margin(raw_settings.get("margin_top", 0), "margin_top"),
        )

    def _variables(self, payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
        raw_variables = payload.get("variables", {})
        if raw_variables is None:
            return {}
        if not isinstance(raw_variables, dict):
            raise TemplateError("Key 'variables' trong JSON schema ph\u1ea3i l\u00e0 object.")

        variables: dict[str, dict[str, Any]] = {}
        for raw_name, raw_definition in raw_variables.items():
            name = str(raw_name).strip()
            if not name or not isinstance(raw_definition, dict):
                raise TemplateError("M\u1ed7i variable ph\u1ea3i c\u00f3 t\u00ean v\u00e0 definition object.")
            source = str(raw_definition.get("source", "")).strip()
            if not source:
                raise TemplateError(f"Variable '{name}' ph\u1ea3i c\u00f3 source.")
            definition: dict[str, Any] = {"source": source}
            fallback_source = str(raw_definition.get("fallbackSource", "")).strip()
            if fallback_source:
                definition["fallbackSource"] = fallback_source
            raw_transform = raw_definition.get("transform")
            if raw_transform is not None:
                definition["transform"] = self._normalize_variable_transform(
                    name,
                    raw_transform,
                )
            raw_fallback_transform = raw_definition.get("fallbackTransform")
            if raw_fallback_transform is not None:
                if not fallback_source:
                    raise TemplateError(
                        f"Variable '{name}' c\u00f3 fallbackTransform nh\u01b0ng thi\u1ebfu fallbackSource."
                    )
                definition["fallbackTransform"] = self._normalize_variable_transform(
                    name,
                    raw_fallback_transform,
                )
            variables[name] = definition
        return variables

    def _normalize_variable_transform(
        self,
        variable_name: str,
        raw_transform: Any,
    ) -> dict[str, Any]:
        if not isinstance(raw_transform, dict):
            raise TemplateError(f"Transform c\u1ee7a variable '{variable_name}' ph\u1ea3i l\u00e0 object.")
        transform_type = str(raw_transform.get("type", "")).strip()
        if transform_type == "date":
            input_format = str(raw_transform.get("inputFormat", "")).strip()
            output_format = str(raw_transform.get("outputFormat", "")).strip()
            if not input_format or not output_format:
                raise TemplateError(
                    f"Date transform c\u1ee7a variable '{variable_name}' ph\u1ea3i c\u00f3 inputFormat v\u00e0 outputFormat."
                )
            return {
                "type": transform_type,
                "inputFormat": input_format,
                "outputFormat": output_format,
            }
        if transform_type == "padNumericSuffix":
            
            try:
                length = int(raw_transform.get("length", 0))
            except (TypeError, ValueError) as exc:
                raise TemplateError(
                    f"padNumericSuffix c\u1ee7a variable '{variable_name}' ph\u1ea3i c\u00f3 length s\u1ed1 nguy\u00ean."
                ) from exc
            character = str(raw_transform.get("character", "0"))
            if length < 1 or len(character) != 1:
                raise TemplateError(
                    f"padNumericSuffix c\u1ee7a variable '{variable_name}' c\u00f3 c\u1ea5u h\u00ecnh kh\u00f4ng h\u1ee3p l\u1ec7."
                )
            return {
                "type": transform_type,
                "length": length,
                "character": character,
            }
        if transform_type == "truncate":
            try:
                max_length = int(raw_transform.get("maxLength", 0))
            except (TypeError, ValueError) as exc:
                raise TemplateError(
                    f"truncate của variable '{variable_name}' phải có maxLength số nguyên."
                ) from exc
            suffix = str(raw_transform.get("suffix", "..."))
            if max_length < 1:
                raise TemplateError(
                    f"truncate của variable '{variable_name}' phải có maxLength lớn hơn 0."
                )
            if len(suffix) > max_length:
                raise TemplateError(
                    f"truncate của variable '{variable_name}' có suffix dài hơn maxLength."
                )
            return {
                "type": transform_type,
                "maxLength": max_length,
                "suffix": suffix,
            }
        raise TemplateError(
            f"Variable '{variable_name}' c\u00f3 transform kh\u00f4ng h\u1ed7 tr\u1ee3: {transform_type}."
        )

    def _computed_fields(self, payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
        raw_fields = payload.get("computedFields", {})
        if raw_fields is None:
            return {}
        if not isinstance(raw_fields, dict):
            raise TemplateError("Key 'computedFields' trong JSON schema ph\u1ea3i l\u00e0 object.")

        computed_fields: dict[str, dict[str, Any]] = {}
        for raw_name, raw_definition in raw_fields.items():
            name = str(raw_name).strip()
            if not name or not isinstance(raw_definition, dict):
                raise TemplateError("M\u1ed7i computed field ph\u1ea3i c\u00f3 t\u00ean v\u00e0 definition object.")
            template = raw_definition.get("template")
            if not isinstance(template, str):
                raise TemplateError(f"Computed field '{name}' ph\u1ea3i c\u00f3 template string.")
            computed_fields[name] = {"template": template}
        return computed_fields

    def _routing(self, payload: dict[str, Any]) -> dict[str, Any]:
        raw_routing = payload.get("routing", {})
        if raw_routing is None:
            return {}
        if not isinstance(raw_routing, dict):
            raise TemplateError("Key 'routing' trong JSON schema phải là object.")

        raw_match = raw_routing.get("match", {})
        if not isinstance(raw_match, dict):
            raise TemplateError("Key 'routing.match' trong JSON schema phải là object.")

        field = str(raw_match.get("field", "")).strip()
        regex = str(raw_match.get("regex", "")).strip()
        if not field or not regex:
            return {}

        flags = str(raw_match.get("flags", "")).strip()
        regex_flags = self._regex_flags(flags)
        try:
            re.compile(regex, regex_flags)
        except re.error as exc:
            raise TemplateError(f"Regex routing không hợp lệ: {regex}") from exc

        try:
            priority = int(raw_routing.get("priority", 0))
        except (TypeError, ValueError) as exc:
            raise TemplateError("Key 'routing.priority' phải là số nguyên.") from exc

        return {
            "priority": priority,
            "match": {
                "field": field,
                "regex": regex,
                "flags": flags,
            },
        }

    def _matches_routing(self, label: dict[str, Any], routing: dict[str, Any]) -> bool:
        raw_match = routing.get("match", {})
        if not isinstance(raw_match, dict):
            return False
        field = str(raw_match.get("field", "")).strip()
        regex = str(raw_match.get("regex", "")).strip()
        if not field or not regex:
            return False

        flags = str(raw_match.get("flags", "")).strip()
        value = self._resolve_field_value(label, field)
        return (
            re.search(regex, "" if value is None else str(value), self._regex_flags(flags))
            is not None
        )

    def _regex_flags(self, flags: str) -> int:
        regex_flags = 0
        if "i" in flags:
            regex_flags |= re.IGNORECASE
        if "m" in flags:
            regex_flags |= re.MULTILINE
        return regex_flags

    def _validate_margin(self, value: Any, field_name: str) -> int:
        if isinstance(value, bool):
            raise TemplateError(f"{field_name} ph\u1ea3i l\u00e0 s\u1ed1 nguy\u00ean.")
        try:
            normalized = int(value)
        except (TypeError, ValueError) as exc:
            raise TemplateError(f"{field_name} ph\u1ea3i l\u00e0 s\u1ed1 nguy\u00ean.") from exc
        if normalized < self.MIN_MARGIN or normalized > self.MAX_MARGIN:
            raise TemplateError(
                f"{field_name} ph\u1ea3i trong kho\u1ea3ng {self.MIN_MARGIN}..{self.MAX_MARGIN}."
            )
        return normalized

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
        row_labels: list[dict[str, Any]],
        columns: int,
        margin_left: int,
        margin_top: int,
        variables: dict[str, dict[str, Any]],
        computed_fields: dict[str, dict[str, Any]],
    ) -> str:
        normalized_labels = [
            self._expand_label_fields(label, variables, computed_fields)
            for label in row_labels
        ]

        def replace_placeholder(match: re.Match[str]) -> str:
            field_name = match.group(1)
            column_index = int(match.group(2))
            if column_index >= columns or column_index >= len(normalized_labels):
                return ""
            value = self._resolve_field_value(normalized_labels[column_index], field_name)
            return "" if value is None else str(value)

        rendered_text = template_text.replace(
            self.CURRENT_DATETIME_TOKEN,
            datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        )
        rendered_text = rendered_text.replace(self.MARGIN_LEFT_TOKEN, str(margin_left))
        rendered_text = rendered_text.replace(self.MARGIN_TOP_TOKEN, str(margin_top))
        return self._placeholder_pattern.sub(replace_placeholder, rendered_text)

    def _resolve_field_value(self, label: dict[str, Any], field_name: str) -> Any:
        if field_name in label:
            return label[field_name]

        value: Any = label
        for path_part in field_name.split("."):
            if not isinstance(value, dict) or path_part not in value:
                return ""
            value = value[path_part]
        return value

    def _expand_label_fields(
        self,
        label: dict[str, Any],
        variables: dict[str, dict[str, Any]],
        computed_fields: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        expanded = dict(label)
        self._expand_snake_case_aliases(expanded)
        self._expand_parts_no(expanded)
        self._expand_customer(expanded)
        for name, definition in variables.items():
            value = self._resolve_field_value(expanded, definition["source"])
            selected_transform = definition.get("transform")
            if value in (None, "") and definition.get("fallbackSource"):
                value = self._resolve_field_value(
                    expanded,
                    definition["fallbackSource"],
                )
                selected_transform = definition.get(
                    "fallbackTransform",
                    selected_transform,
                )
            expanded[name] = self._apply_variable_transform(
                name,
                value,
                selected_transform,
            )
        for name, definition in computed_fields.items():
            expanded[name] = self._render_computed_template(
                definition["template"],
                expanded,
            )
        return expanded

    def _apply_variable_transform(
        self,
        variable_name: str,
        value: Any,
        transform: dict[str, Any] | None,
    ) -> Any:
        if transform is None or value in (None, ""):
            return value
        if transform["type"] == "date":
            try:
                return datetime.strptime(
                    str(value),
                    transform["inputFormat"],
                ).strftime(transform["outputFormat"])
            except ValueError as exc:
                raise TemplateError(
                    f"Variable '{variable_name}' kh\u00f4ng \u0111\u00fang format ng\u00e0y "
                    f"{transform['inputFormat']}: {value}"
                ) from exc
        if transform["type"] == "padNumericSuffix":
            match = re.fullmatch(r"(.*?)(\d+)", str(value).strip())
            if match is None:
                raise TemplateError(
                    f"Variable '{variable_name}' kh\u00f4ng c\u00f3 numeric suffix: {value}"
                )
            prefix, numeric_suffix = match.groups()
            padded_suffix = numeric_suffix.rjust(
                transform["length"],
                transform["character"],
            )
            return f"{prefix}{padded_suffix}"
        if transform["type"] == "truncate":
            text = str(value)
            max_length = transform["maxLength"]
            if len(text) <= max_length:
                return text
            keep_length = max_length - len(transform["suffix"])
            return f"{text[:keep_length].rstrip()}{transform['suffix']}"
        return value

    def _render_computed_template(self, template: str, label: dict[str, Any]) -> str:
        def replace_token(match: re.Match[str]) -> str:
            value = self._resolve_field_value(label, match.group(1))
            return "" if value is None else str(value)

        return self._computed_token_pattern.sub(replace_token, template)

    def _expand_snake_case_aliases(self, label: dict[str, Any]) -> None:
        for key, value in list(label.items()):
            snake_key = self._to_snake_case(str(key))
            if snake_key:
                label.setdefault(snake_key, value)
        aliases = {
            "mold_no": "Mold No",
            "parts_no": "Parts No",
            "parts_name": "Parts Name",
            "qty_unit_barcode": "Qty unit barcode",
            "kind_of_unit": "Kind of unit",
            "qty_unit": "Qty unit",
            "rev_his": "Rev His",
            "unit_box": "Unit Box",
            "total_qty": "Total Qty",
            "production_date": "Production date",
            "im_box": "IM Box",
            "shift": "Shift",
            "customer": "Customer",
            "qty_box_barcode": "Qty box barcode",
            "parts_suffix": "Parts Suffix",
            "customer_1": "Customer 1",
            "customer_2": "Customer 2",
            "customer_3": "Customer 3",
        }
        for snake_key, placeholder_key in aliases.items():
            if snake_key in label:
                label.setdefault(placeholder_key, label[snake_key])

    def _expand_parts_no(self, label: dict[str, Any]) -> None:
        raw_parts_no = str(label.get("Parts No", "")).strip()
        if not raw_parts_no or label.get("Parts Suffix"):
            return
        parts = [part for part in raw_parts_no.split("-") if part]
        if len(parts) < 3:
            return
        label["Parts No"] = "-".join(parts[:-1])
        label["Parts Suffix"] = parts[-1]

    def _expand_customer(self, label: dict[str, Any]) -> None:
        raw_customer = str(label.get("Customer", "")).strip()
        if not raw_customer:
            return
        parts = [
            value.strip(string.whitespace + "-")
            for value in raw_customer.split("-")
            if value.strip(string.whitespace + "-")
        ]
        for index, value in enumerate(parts, start=1):
            label.setdefault(f"Customer {index}", value)

    def _to_snake_case(self, value: str) -> str:
        normalized = re.sub(r"[^A-Za-z0-9]+", "_", value.strip())
        normalized = re.sub(r"_+", "_", normalized).strip("_")
        return normalized.lower()
