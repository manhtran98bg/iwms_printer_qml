from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.models.base_model import BaseModel


@dataclass(frozen=True)
class PrintFormat(BaseModel):
    schema_path: str = ""
    required_fields: list[str] = field(default_factory=list)
    template_path: str = ""
    preview_path: str = ""
    margin_left: int = 0
    margin_top: int = 0
    routing: dict[str, Any] = field(default_factory=dict)
    variables: dict[str, dict[str, Any]] = field(default_factory=dict)
    computed_fields: dict[str, dict[str, Any]] = field(default_factory=dict)
    default_values: dict[str, str] = field(default_factory=dict)
