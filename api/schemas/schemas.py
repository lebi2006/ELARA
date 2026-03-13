"""
ELARA — Pydantic Schemas
Request and response models for all API endpoints.
"""

from pydantic   import BaseModel
from typing     import List, Optional, Dict, Any
from datetime   import datetime


class AssessmentResponse(BaseModel):
    astronaut_id                : str
    astronaut_name              : str
    mission_day                 : int
    mission_phase               : str
    health_index                : float
    health_status               : str
    cognitive_load_score        : float
    cognitive_readiness_score   : float
    risk_level                  : str
    tqs_probability             : float
    signal_scores               : Dict[str, float]
    alerts                      : List[Dict[str, Any]]
    explanations                : Dict[str, Any]


class CrewAssessmentResponse(BaseModel):
    mission_day : int
    crew        : List[AssessmentResponse]


class InterventionResponse(BaseModel):
    astronaut_id    : str
    mission_day     : int
    status          : str
    conditions      : Optional[List[str]]   = []
    interventions   : List[Dict[str, Any]]
    message         : str


class MissionTimelineEntry(BaseModel):
    mission_day                 : int
    mission_phase               : str
    health_index                : float
    cognitive_load_score        : float
    risk_level                  : str
    tqs_probability             : float


class EffectivenessUpdate(BaseModel):
    astronaut_id        : str
    intervention_id     : str
    effectiveness       : str   # IMPROVED | NO_CHANGE | WORSENED