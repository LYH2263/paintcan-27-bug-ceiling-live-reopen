import json

from app.db import connect
from app.engines.estimate import estimate_room
from app.repositories import openings, rooms, runs, settings


def _serialize_run(row):
    """Parse a calc_runs row; result_json is the pinned snapshot from write time."""
    return {
        "id": row["id"],
        "kind": row["kind"],
        "room_id": row["room_id"],
        "created_at": row["created_at"],
        "input": json.loads(row["input_json"]) if row["input_json"] else None,
        "result": json.loads(row["result_json"]) if row["result_json"] else None,
    }


class PaintService:
    def __init__(self): self._c = connect()
    def close(self): self._c.close()
    def __enter__(self): return self
    def __exit__(self, *a): self.close()
    def list_rooms(self): return rooms.list_all(self._c)
    def room_detail(self, rid):
        r = rooms.get(self._c, rid)
        if not r: return None
        return {"room": r, "openings": openings.for_room(self._c, rid)}
    def settings(self):
        cov, ct = settings.coverage_coats(self._c)
        ccov, cct = settings.ceiling_coverage_coats(self._c)
        return {
            "coverage": cov,
            "coats": ct,
            "ceiling_coverage": ccov,
            "ceiling_coats": cct,
        }
    def save_settings(self, coverage=None, coats=None, ceiling_coverage=None, ceiling_coats=None):
        if coverage is not None:
            settings.upsert(self._c, settings.WALL_COVERAGE_KEY, float(coverage))
        if coats is not None:
            settings.upsert(self._c, settings.WALL_COATS_KEY, int(coats))
        if ceiling_coverage is not None:
            settings.upsert(self._c, settings.CEILING_COVERAGE_KEY, float(ceiling_coverage))
        if ceiling_coats is not None:
            settings.upsert(self._c, settings.CEILING_COATS_KEY, int(ceiling_coats))
        return self.settings()
    def history(self, limit=50):
        return [_serialize_run(r) for r in runs.list_recent(self._c, limit)]
    def run_detail(self, run_id):
        row = runs.get(self._c, run_id)
        if not row:
            return None
        # Read-only reopen: return the write-time pinned snapshot verbatim.
        # Live coverage/coat defaults only apply to freshly taken estimates and
        # must never rewrite — or even recompute in the response — a past run.
        return _serialize_run(row)
    def estimate(self, room_id, persist, coats=None, coverage=None,
                 ceiling_enabled=False, ceiling_coverage=None, ceiling_coats=None):
        detail = self.room_detail(room_id)
        if not detail: return None
        r = detail["room"]
        wall_cov, wall_ct = settings.coverage_coats(self._c)
        cov = float(coverage) if coverage is not None else wall_cov
        ct = int(coats) if coats is not None else wall_ct
        if ceiling_enabled:
            def_cov, def_ct = settings.ceiling_coverage_coats(self._c)
            ccov = float(ceiling_coverage) if ceiling_coverage is not None else def_cov
            cct = int(ceiling_coats) if ceiling_coats is not None else def_ct
        else:
            ccov, cct = None, None
        ops = [{"w": o["w"], "h": o["h"]} for o in detail["openings"]]
        # Compute first; a non-positive coverage/coats raises here, BEFORE any
        # insert, so an invalid order is rejected whole and leaves no record.
        result = estimate_room(
            r["length"], r["width"], r["height"], ops, cov, ct,
            ceiling_enabled=ceiling_enabled,
            ceiling_coverage=ccov,
            ceiling_coats=cct,
        )
        # Pin the effective parameters and the wall/ceiling liters at write time.
        payload = {
            "room_id": room_id,
            "coats": ct,
            "coverage": cov,
            "ceiling_enabled": bool(ceiling_enabled),
            "ceiling_coverage": ccov,
            "ceiling_coats": cct,
        }
        rid = runs.insert(self._c, "estimate", payload, result, room_id) if persist else None
        return {"run_id": rid, "room_id": room_id, **result}
    def dashboard(self):
        rs = rooms.list_all(self._c)
        return {"room_count": len(rs), "clean": len([x for x in rs if "种子" not in x["name"] and "多种" not in x["name"]]), "dirty": len([x for x in rs if "多种" in x["name"]])}
