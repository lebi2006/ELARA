"""
ELARA — API Service Layer
Business logic connecting FastAPI routes to the ELARA pipeline.
"""

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import json
import pandas as pd
from signals.feature_engineering        import build_feature_matrix
from models.elara_pipeline              import ELARAPipeline
from intervention.engine.intervention_engine import InterventionEngine


class ELARAService:
    """
    Singleton service that holds the loaded pipeline and
    serves all API requests.
    """
    _instance   = None
    _pipeline   = None
    _engine     = None
    _df         = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def initialize(self):
        """Load pipeline and intervention engine on startup."""
        print("Initializing ELARA Service...")
        self._df        = build_feature_matrix()
        self._pipeline  = ELARAPipeline()
        self._pipeline.load(self._df)
        self._engine    = InterventionEngine()
        print("ELARA Service ready.")

    def get_crew_assessment(self, mission_day: int) -> dict:
        results = self._pipeline.assess_crew(mission_day)
        return {
            "mission_day"   : mission_day,
            "crew"          : [self._format_assessment(r) for r in results]
        }

    def get_astronaut_assessment(self, astronaut_id: str, mission_day: int) -> dict:
        result = self._pipeline.assess(astronaut_id, mission_day)
        return self._format_assessment(result)

    def get_interventions(self, astronaut_id: str, mission_day: int) -> dict:
        assessment  = self._pipeline.assess(astronaut_id, mission_day)
        return self._engine.recommend(assessment)

    def get_mission_timeline(self, astronaut_id: str) -> list:
        """Returns full 180-day psychological trajectory for one astronaut."""
        timeline = []
        for day in range(1, 181):
            try:
                result = self._pipeline.assess(astronaut_id, day)
                a      = result["assessment"]
                timeline.append({
                    "mission_day"           : day,
                    "mission_phase"         : result["mission_phase"],
                    "health_index"          : a["health_index"],
                    "cognitive_load_score"  : a["cognitive_load_score"],
                    "risk_level"            : a["risk_level"],
                    "tqs_probability"       : a["tqs_probability"],
                })
            except Exception:
                continue
        return timeline

    def get_crew_ids(self) -> list:
        return list(self._df["astronaut_id"].unique())

    def get_astronaut_info(self) -> list:
        return self._df[["astronaut_id", "astronaut_name"]]\
            .drop_duplicates()\
            .to_dict(orient="records")

    def record_effectiveness(self, astronaut_id: str,
                              intervention_id: str,
                              effectiveness: str):
        self._engine.record_effectiveness(
            astronaut_id, intervention_id, effectiveness
        )

    def _format_assessment(self, result: dict) -> dict:
        a = result["assessment"]
        return {
            "astronaut_id"              : result["astronaut_id"],
            "astronaut_name"            : result["astronaut_name"],
            "mission_day"               : result["mission_day"],
            "mission_phase"             : result["mission_phase"],
            "health_index"              : a["health_index"],
            "health_status"             : a["health_status"],
            "cognitive_load_score"      : a["cognitive_load_score"],
            "cognitive_readiness_score" : a["cognitive_readiness_score"],
            "risk_level"                : a["risk_level"],
            "tqs_probability"           : a["tqs_probability"],
            "signal_scores"             : result["signal_scores"],
            "alerts"                    : result["alerts"],
            "explanations"              : result["explanations"],
        }