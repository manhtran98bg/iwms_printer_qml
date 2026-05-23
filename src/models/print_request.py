from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.models.base_model import BaseModel


LabelPayload = dict[str, str]


@dataclass(frozen=True)
class PrintRequest(BaseModel):
    labels: list[LabelPayload] = field(default_factory=list)

    @classmethod
    def from_compatible_body(cls, body: Any) -> "PrintRequest":
        if isinstance(body, list):
            return cls(labels=body)
        if isinstance(body, dict) and isinstance(body.get("labels"), list):
            return cls(labels=body["labels"])
        return cls(labels=[])
