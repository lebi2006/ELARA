"""
ELARA — Assessment Routes
"""

from fastapi                    import APIRouter
from api.services.elara_service import ELARAService

router = APIRouter(prefix="/api/assessment", tags=["Assessment"])


@router.get("/crew/{mission_day}")
def get_crew_assessment(mission_day: int):
    """Get psychological assessment for all crew on a given mission day."""
    service = ELARAService.get_instance()
    return service.get_crew_assessment(mission_day)


@router.get("/{astronaut_id}/{mission_day}")
def get_astronaut_assessment(astronaut_id: str, mission_day: int):
    """Get psychological assessment for one astronaut on a given mission day."""
    service = ELARAService.get_instance()
    return service.get_astronaut_assessment(astronaut_id, mission_day)


@router.get("/crew/info/all")
def get_crew_info():
    """Get list of all astronauts in the mission."""
    service = ELARAService.get_instance()
    return service.get_astronaut_info()