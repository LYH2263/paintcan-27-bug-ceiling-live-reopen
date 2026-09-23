import math
from typing import Optional

from pydantic import BaseModel, Field, StrictInt, field_validator


class SettingsUpdate(BaseModel):
    coverage: Optional[float] = None
    coats: Optional[StrictInt] = Field(default=None, gt=0)
    ceiling_coverage: Optional[float] = None
    ceiling_coats: Optional[StrictInt] = Field(default=None, gt=0)

    @field_validator("coverage", "ceiling_coverage")
    @classmethod
    def _positive(cls, v):
        if v is None:
            return v
        if not math.isfinite(v) or v <= 0:
            raise ValueError("must be a positive number")
        return v
