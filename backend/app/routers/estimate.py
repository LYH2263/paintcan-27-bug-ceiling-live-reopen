from fastapi import APIRouter, HTTPException
from app.schemas.estimate import EstimateRequest
from app.services.paint_service import PaintService
router = APIRouter()
@router.post("/estimate")
def post_estimate(body: EstimateRequest):
    with PaintService() as s:
        try:
            r = s.estimate(
                body.room_id, body.persist, body.coats, body.coverage,
                ceiling_enabled=body.ceiling_enabled,
                ceiling_coverage=body.ceiling_coverage,
                ceiling_coats=body.ceiling_coats,
            )
        except ValueError as e:
            # Defensive: schema validation already rejects non-positive values with 422.
            raise HTTPException(status_code=422, detail=str(e))
        if not r: raise HTTPException(404)
        return r
