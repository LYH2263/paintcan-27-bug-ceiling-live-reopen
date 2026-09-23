from app.engines.paint_volume import paint_liters
from app.engines.wall_area import wall_area
from app.modules.ceiling_paint import ceiling_paint

# Wall-side keys only — when the ceiling is disabled (the default) the response
# must stay byte-for-byte compatible with the pre-ceiling estimate.
WALL_KEYS = ("gross_m2", "openings_m2", "net_m2", "liters", "coats", "coverage")


def estimate_room(length, width, height, openings, coverage, coats,
                  ceiling_enabled=False, ceiling_coverage=None, ceiling_coats=None):
    area = wall_area(length, width, height, openings)
    vol = paint_liters(area["net_m2"], coverage, coats)
    wall = {**area, **vol}
    if not ceiling_enabled:
        # Disabled by default: identical payload to the original wall-only flow.
        return wall
    ccov = float(coverage if ceiling_coverage is None else ceiling_coverage)
    ccoats = int(coats if ceiling_coats is None else ceiling_coats)
    ceil = ceiling_paint(length, width, ccov, ccoats)
    return {
        **wall,
        "ceiling_enabled": True,
        **ceil,
        "total_liters": round(wall["liters"] + ceil["ceiling_liters"], 2),
    }
