"""
ELARA — Intervention Routes
"""

from fastapi                    import APIRouter
from api.services.elara_service import ELARAService
from api.schemas.schemas        import EffectivenessUpdate

router = APIRouter(prefix="/api/intervention", tags=["Intervention"])


@router.get("/{astronaut_id}/{mission_day}")
def get_interventions(astronaut_id: str, mission_day: int):
    """Get personalized interventions for an astronaut on a given day."""
    service = ELARAService.get_instance()
    return service.get_interventions(astronaut_id, mission_day)


@router.post("/effectiveness")
def record_effectiveness(update: EffectivenessUpdate):
    """Record whether an intervention was effective."""
    service = ELARAService.get_instance()
    service.record_effectiveness(
        update.astronaut_id,
        update.intervention_id,
        update.effectiveness
    )
    return {"status": "recorded"}