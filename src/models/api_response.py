from __future__ import annotations

from dataclasses import dataclass

from src.models.base_model import BaseModel


@dataclass(frozen=True)
class ApiResponse(BaseModel):
    success: bool
    message: str
