import math
from typing import Optional

from pydantic import BaseModel, Field, StrictInt, field_validator


def _positive_finish(v):
    if v is None:
        return v
    if not math.isfinite(v) or v <= 0:
        raise ValueError("must be a positive number")
    return v


class EstimateRequest(BaseModel):
    room_id: int
    persist: bool = True

    # Wall-side overrides (fall back to global settings when omitted).
    coats: Optional[StrictInt] = Field(default=None, gt=0)
    coverage: Optional[float] = None

    # Ceiling module — disabled by default so a bare request reproduces the
    # original wall-only estimate. When enabled, ceiling coverage/coats are
    # independent and fall back to the ceiling defaults (then to wall values).
    ceiling_enabled: bool = False
    ceiling_coverage: Optional[float] = None
    ceiling_coats: Optional[StrictInt] = Field(default=None, gt=0)

    @field_validator("coverage", "ceiling_coverage")
    @classmethod
    def _positive_coverage(cls, v):
        return _positive_finish(v)
