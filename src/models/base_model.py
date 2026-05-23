from __future__ import annotations

from dataclasses import asdict, fields, is_dataclass
from typing import Any, Self


class BaseModel:
    """Base dataclass model with dict serialization helpers."""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        if not is_dataclass(cls):
            raise TypeError(f"{cls.__name__} must be a dataclass")
        field_names = {field.name for field in fields(cls)}
        payload = {key: value for key, value in data.items() if key in field_names}
        return cls(**payload)

    def to_dict(self) -> dict[str, Any]:
        if not is_dataclass(self):
            raise TypeError(f"{type(self).__name__} must be a dataclass")
        return asdict(self)
