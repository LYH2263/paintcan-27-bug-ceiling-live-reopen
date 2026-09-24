"""Reopen a past run read-only: serve the snapshot pinned at write time.

A stored run's wall liters, ceiling liters and the ceiling-enabled switch are
all part of the result that was calculated when the run was written. Opening
that run later must never feed current coverage/coat settings back into it —
changing (or even removing) today's ceiling default leaves old records
untouched. Brand-new estimates are the only place live defaults apply, and
that happens in PaintService.estimate.
"""
import json


def _load_json(raw):
    if raw is None:
        return {}
    if isinstance(raw, (dict, list)):
        return raw
    try:
        return json.loads(raw or "{}")
    except (TypeError, ValueError, json.JSONDecodeError):
        return {}


def pinned_run_result(row):
    """Return a calc_runs row's write-time result_json, byte-for-byte values."""
    raw = row.get("result_json") if "result_json" in row else row.get("result")
    result = _load_json(raw)
    if not isinstance(result, dict):
        return {}
    # The switch is pinned as well. Rows written before the result carried
    # ceiling_enabled still record it in input_json; restore it from there,
    # never from live settings.
    if "ceiling_enabled" not in result:
        payload = _load_json(
            row.get("input_json") if "input_json" in row else row.get("input")
        )
        if isinstance(payload, dict) and "ceiling_enabled" in payload:
            result = dict(result)
            result["ceiling_enabled"] = bool(payload["ceiling_enabled"])
    return result
