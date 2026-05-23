from __future__ import annotations

from dataclasses import dataclass, field

from src.core.constants import DEFAULT_API_URL, DEFAULT_STAMP_COLUMNS
from src.models.base_model import BaseModel


@dataclass(frozen=True)
class PrinterConfig(BaseModel):
    api_url: str = DEFAULT_API_URL
    template_path: str = ""
    data_path: str = ""
    printer_name: str = ""
    stamp_columns: int = DEFAULT_STAMP_COLUMNS
    required_fields: list[str] = field(default_factory=list)
