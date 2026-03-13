"""
ELARA — API Service Layer
Precomputes all assessments at startup and serves from cache.
Every request is instant — zero per-request computation.
"""

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import json
import pandas as pd
from signals.feature_engineering            import build_feature_matrix
from models.elara_pipeline                  import ELARAPipeline
from intervention.engine.intervention_engine import InterventionEngine


class ELARAService:
    _instance   = None
    _pipeline   = None
    _engine     = None
    _df         = None

    # ── Caches ────────────────────────────────────────────────
    _assessment_cache   = {}   # (astronaut_id, day) -> assessment
    _crew_cache         = {}   # day -> crew list
    _timeline_cache     = {}   # astronaut_id -> timeline list
    _intervention_cache = {}   # (astronaut_id, day) -> interventions

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def initialize(self):
        print("Initializing ELARA Service...")
        self._df        = build_feature_matrix()
        self._pipeline  = ELARAPipeline()
        self._pipeline.load(self._df)
        self._engine    = InterventionEngine()

        print("  Precomputing all 180 days for all crew members...")
        self._precompute_all()
        print("ELARA Service ready. All data cached.")

    def _precompute_all(self):
        """
        Runs all assessments and interventions for all astronauts
        across all 180 mission days at startup.
        Stores everything in memory for instant retrieval.
        """
        crew_ids = list(self._df["astronaut_id"].unique())

        for day in range(1, 181):
            crew_list = []
            for astronaut_id in crew_ids:
                try:
                    result      = self._pipeline.assess(astronaut_id, day)
                    formatted   = self._format_assessment(result)

                    # Cache individual assessment
                    self._assessment_cache[(astronaut_id, day)] = formatted

                    # Cache intervention
                    intervention = self._engine.recommend(result)
                    self._intervention_cache[(astronaut_id, day)] = intervention

                    crew_list.append(formatted)
                except Exception as e:
                    print(f"  Warning: Could not compute day {day} for {astronaut_id}: {e}")

            # Cache crew assessment for this day
            self._crew_cache[day] = {"mission_day": day, "crew": crew_list}

            if day % 30 == 0:
                print(f"  Precomputed day {day}/180...")

        # Precompute timelines
        for astronaut_id in crew_ids:
            timeline = []
            for day in range(1, 181):
                assessment = self._assessment_cache.get((astronaut_id, day))
                if assessment:
                    timeline.append({
                        "mission_day"           : day,
                        "mission_phase"         : assessment["mission_phase"],
                        "health_index"          : assessment["health_index"],
                        "cognitive_load_score"  : assessment["cognitive_load_score"],
                        "risk_level"            : assessment["risk_level"],
                        "tqs_probability"       : assessment["tqs_probability"],
                    })
            self._timeline_cache[astronaut_id] = timeline

        print(f"  Precomputation complete.")
        print(f"  Cached: {len(self._assessment_cache)} assessments")
        print(f"  Cached: {len(self._intervention_cache)} interventions")
        print(f"  Cached: {len(self._timeline_cache)} timelines")

    # ── Public API methods ────────────────────────────────────

    def get_crew_assessment(self, mission_day: int) -> dict:
        return self._crew_cache.get(
            mission_day,
            {"mission_day": mission_day, "crew": []}
        )

    def get_astronaut_assessment(self, astronaut_id: str, mission_day: int) -> dict:
        return self._assessment_cache.get(
            (astronaut_id, mission_day), {}
        )

    def get_interventions(self, astronaut_id: str, mission_day: int) -> dict:
        return self._intervention_cache.get(
            (astronaut_id, mission_day), {}
        )

    def get_mission_timeline(self, astronaut_id: str) -> list:
        return self._timeline_cache.get(astronaut_id, [])

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