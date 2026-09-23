import pytest
from fastapi.testclient import TestClient

from app import seed
from app.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Redirect the connection at a fresh per-test database; startup then seeds it.
    import app.db as db
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "app.db")
    seed.init_db()
    with TestClient(app) as c:
        yield c


def test_default_estimate_is_wall_only_backward_compatible(client):
    r = client.post("/api/estimate", json={"room_id": 1, "persist": False})
    assert r.status_code == 200
    j = r.json()
    assert set(j) == {"run_id", "room_id", "gross_m2", "openings_m2",
                      "net_m2", "liters", "coats", "coverage"}
    assert j["liters"] == 11.6 and j["run_id"] is None


def test_ceiling_enabled_with_defaults(client):
    j = client.post("/api/estimate",
                    json={"room_id": 1, "persist": False, "ceiling_enabled": True}).json()
    assert j["ceiling_enabled"] is True
    assert j["ceiling_m2"] == 20.0 and j["ceiling_liters"] == 5.0
    assert j["liters"] == 11.6 and j["total_liters"] == 16.6


def test_ceiling_overrides_independent(client):
    j = client.post("/api/estimate", json={
        "room_id": 1, "persist": False, "ceiling_enabled": True,
        "ceiling_coverage": 10, "ceiling_coats": 1}).json()
    assert j["ceiling_liters"] == 2.0 and j["total_liters"] == 13.6
    assert j["ceiling_coverage"] == 10.0 and j["ceiling_coats"] == 1


@pytest.mark.parametrize("body", [
    {"room_id": 1, "ceiling_enabled": True, "ceiling_coverage": 0},
    {"room_id": 1, "ceiling_enabled": True, "ceiling_coverage": -2},
    {"room_id": 1, "ceiling_enabled": True, "ceiling_coats": 0},
    {"room_id": 1, "ceiling_enabled": True, "ceiling_coats": -1},
    {"room_id": 1, "ceiling_enabled": True, "ceiling_coats": 2.5},
    {"room_id": 1, "coats": 2.5},
    {"room_id": 1, "coverage": 0},
])
def test_invalid_orders_rejected_without_writing(client, body):
    before = len(client.get("/api/history").json()["items"])
    r = client.post("/api/estimate", json=body)
    assert r.status_code == 422
    after = len(client.get("/api/history").json()["items"])
    assert before == after


def test_settings_invalid_rejected(client):
    assert client.post("/api/settings", json={"ceiling_coats": 0}).status_code == 422
    assert client.post("/api/settings", json={"ceiling_coverage": -1}).status_code == 422


def test_persist_pins_snapshot_and_history(client):
    j = client.post("/api/estimate",
                    json={"room_id": 1, "persist": True, "ceiling_enabled": True}).json()
    rid = j["run_id"]
    assert isinstance(rid, int)

    detail = client.get(f"/api/history/{rid}").json()
    res = detail["result"]
    # History by id carries the write-time wall liters, ceiling liters and switch.
    assert res["liters"] == 11.6
    assert res["ceiling_liters"] == 5.0
    assert res["ceiling_enabled"] is True
    assert detail["input"]["ceiling_enabled"] is True

    # Tighten the ceiling default coverage; the pinned record must not follow.
    client.post("/api/settings", json={"ceiling_coverage": 6})
    pinned = client.get(f"/api/history/{rid}").json()["result"]
    assert pinned["ceiling_liters"] == 5.0 and pinned["liters"] == 11.6

    # A fresh estimate uses the new default.
    fresh = client.post("/api/estimate",
                        json={"room_id": 1, "persist": False, "ceiling_enabled": True}).json()
    assert fresh["ceiling_liters"] == 6.67


def test_history_unknown_id_404(client):
    assert client.get("/api/history/999999").status_code == 404


def test_ceiling_default_settings_exist(client):
    s = client.get("/api/settings").json()
    assert s["ceiling_coverage"] == 8.0 and s["ceiling_coats"] == 2
