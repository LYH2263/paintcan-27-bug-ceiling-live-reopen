import pytest
from app.engines.estimate import estimate_room
from app.engines.paint_volume import paint_liters
from app.engines.wall_area import wall_area
from app.modules.ceiling_paint import ceiling_area, ceiling_paint

OPS = [{"w": 0.9, "h": 2.1}, {"w": 1.5, "h": 1.4}]


def test_living_room_net():
    a = wall_area(5, 4, 2.8, OPS)
    assert a["gross_m2"] == 50.4
    assert a["net_m2"] == 46.41


def test_liters_two_coats():
    v = paint_liters(46.41, 8, 2)
    assert v["liters"] == 11.6


def test_estimate_combined():
    e = estimate_room(5, 4, 2.8, OPS, 8, 2)
    assert e["liters"] == 11.6


def test_bad_coverage():
    with pytest.raises(ValueError):
        paint_liters(10, 0, 2)


# --- ceiling module ---------------------------------------------------------

def test_ceiling_area_is_length_times_width():
    assert ceiling_area(5, 4)["ceiling_m2"] == 20.0
    # Openings never reduce a ceiling.
    assert estimate_room(5, 4, 2.8, OPS, 8, 2, ceiling_enabled=True)["ceiling_m2"] == 20.0


def test_ceiling_liters_uses_own_coverage_and_coats():
    c = ceiling_paint(5, 4, coverage_m2_per_l=10, coats=1)
    assert c["ceiling_m2"] == 20.0 and c["ceiling_liters"] == 2.0
    assert c["ceiling_coverage"] == 10.0 and c["ceiling_coats"] == 1


def test_ceiling_default_disabled_matches_wall_only_payload():
    # Same room + same wall params as test_estimate_combined: response must be
    # identical and contain no ceiling keys.
    disabled = estimate_room(5, 4, 2.8, OPS, 8, 2)
    enabled = estimate_room(5, 4, 2.8, OPS, 8, 2, ceiling_enabled=True)
    assert disabled == {"gross_m2": 50.4, "openings_m2": 3.99, "net_m2": 46.41,
                        "liters": 11.6, "coats": 2, "coverage": 8.0}
    assert all(k not in disabled for k in
               ("ceiling_enabled", "ceiling_m2", "ceiling_liters", "total_liters"))
    # Wall liters must not move when the ceiling is switched on.
    assert enabled["liters"] == disabled["liters"] == 11.6
    assert enabled["ceiling_liters"] == 5.0 and enabled["total_liters"] == 16.6


def test_ceiling_overrides_independent_of_wall():
    e = estimate_room(5, 4, 2.8, OPS, coverage=8, coats=2,
                      ceiling_enabled=True, ceiling_coverage=5, ceiling_coats=3)
    assert e["coats"] == 2 and e["coverage"] == 8.0          # walls untouched
    assert e["ceiling_coats"] == 3 and e["ceiling_coverage"] == 5.0
    assert e["ceiling_liters"] == 12.0 and e["total_liters"] == 23.6


def test_ceiling_enabled_false_ignores_overrides():
    e = estimate_room(5, 4, 2.8, OPS, 8, 2,
                      ceiling_enabled=False, ceiling_coverage=5, ceiling_coats=3)
    assert "ceiling_liters" not in e and e["liters"] == 11.6


def test_ceiling_falls_back_to_wall_params():
    e = estimate_room(5, 4, 2.8, OPS, coverage=10, coats=1, ceiling_enabled=True)
    assert e["ceiling_coverage"] == 10.0 and e["ceiling_coats"] == 1
    assert e["ceiling_liters"] == 2.0


@pytest.mark.parametrize("cov,coats", [(0, 2), (-3, 2), (8, 0), (8, -1)])
def test_ceiling_rejects_nonpositive(cov, coats):
    with pytest.raises(ValueError):
        ceiling_paint(5, 4, cov, coats)
