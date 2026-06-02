from __future__ import annotations

from dataclasses import dataclass, field

from src.models.base_model import BaseModel


@dataclass(frozen=True)
class PrintFormat(BaseModel):
    required_fields: list[str] = field(default_factory=list)
    template_path: str = ""
    default_values: dict[str, str] = field(default_factory=dict)
