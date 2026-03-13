"""
ELARA — Mission Routes
"""

from fastapi                    import APIRouter
from api.services.elara_service import ELARAService

router = APIRouter(prefix="/api/mission", tags=["Mission"])


@router.get("/timeline/{astronaut_id}")
def get_mission_timeline(astronaut_id: str):
    """Get full 180-day psychological trajectory for one astronaut."""
    service = ELARAService.get_instance()
    return service.get_mission_timeline(astronaut_id)


@router.get("/crew/ids")
def get_crew_ids():
    """Get all astronaut IDs."""
    service = ELARAService.get_instance()
    return service.get_crew_ids()