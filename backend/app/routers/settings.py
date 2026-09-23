from fastapi import APIRouter
from app.schemas.settings import SettingsUpdate
from app.services.paint_service import PaintService
router = APIRouter()
@router.get("/settings")
def settings():
    with PaintService() as s: return s.settings()
@router.post("/settings")
def save_settings(body: SettingsUpdate):
    with PaintService() as s:
        return s.save_settings(
            coverage=body.coverage, coats=body.coats,
            ceiling_coverage=body.ceiling_coverage, ceiling_coats=body.ceiling_coats,
        )
