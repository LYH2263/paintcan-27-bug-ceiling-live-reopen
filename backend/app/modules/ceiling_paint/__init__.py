"""Ceiling paint module.

Adds ceiling paint estimation on top of the wall net-area flow:
- ceiling area is derived from room length x width (openings never bite a ceiling);
- ceiling paint uses its OWN coverage (m2/L) and coat count, independent of walls.
"""

CEILING_DEFAULT_COVERAGE = 8.0
CEILING_DEFAULT_COATS = 2


def ceiling_area(length: float, width: float) -> dict:
    m2 = float(length) * float(width)
    return {"ceiling_m2": round(m2, 2)}


def ceiling_paint(length: float, width: float, coverage_m2_per_l: float, coats: int) -> dict:
    if coverage_m2_per_l <= 0 or coats <= 0:
        raise ValueError("ceiling coverage and coats must be positive")
    area = ceiling_area(length, width)
    need = area["ceiling_m2"] * int(coats) / float(coverage_m2_per_l)
    return {
        **area,
        "ceiling_liters": round(need, 2),
        "ceiling_coats": int(coats),
        "ceiling_coverage": float(coverage_m2_per_l),
    }
