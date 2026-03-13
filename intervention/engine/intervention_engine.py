"""
ELARA — Adaptive Intervention Engine
Selects and personalizes micro-interventions based on
the astronaut's current assessment and historical response profile.
Tracks intervention effectiveness and adapts over time.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import json
import random
from pathlib import Path
from datetime import datetime
from intervention.library.intervention_library import (
    get_interventions_for_condition,
    get_intervention_by_id,
)

HISTORY_DIR = Path("data/processed/intervention_history")


class InterventionEngine:
    """
    Adaptive intervention recommender.
    Selects the most appropriate intervention based on:
    - Current assessment results
    - Astronaut's personal history
    - Previously effective interventions
    - Mission phase context
    """

    def __init__(self):
        HISTORY_DIR.mkdir(parents=True, exist_ok=True)
        self.history = {}       # astronaut_id -> list of past interventions

    def _load_history(self, astronaut_id: str) -> list:
        path = HISTORY_DIR / f"{astronaut_id}_history.json"
        if path.exists():
            with open(path) as f:
                return json.load(f)
        return []

    def _save_history(self, astronaut_id: str):
        path = HISTORY_DIR / f"{astronaut_id}_history.json"
        with open(path, "w") as f:
            json.dump(self.history.get(astronaut_id, []), f, indent=2)

    def _get_effective_interventions(self, astronaut_id: str) -> list:
        """Returns IDs of interventions that previously improved this astronaut's scores."""
        history = self.history.get(astronaut_id, [])
        return [
            h["intervention_id"]
            for h in history
            if h.get("effectiveness") == "IMPROVED"
        ]

    def _select_intervention(self, candidates: list, astronaut_id: str) -> dict:
        """
        Selects best intervention from candidates.
        Prefers previously effective interventions for this astronaut.
        """
        if not candidates:
            return {}

        effective = self._get_effective_interventions(astronaut_id)

        # Prioritize previously effective interventions
        preferred = [c for c in candidates if c["id"] in effective]
        if preferred:
            return preferred[0]

        # Otherwise pick randomly from candidates
        return random.choice(candidates)

    def _determine_conditions(self, assessment: dict) -> list:
        """
        Maps assessment results to intervention conditions.
        """
        conditions  = []
        a           = assessment.get("assessment", {})
        alerts      = assessment.get("alerts", [])

        health_index        = a.get("health_index", 100)
        readiness           = a.get("cognitive_readiness_score", 100)
        risk_level          = a.get("risk_level", "LOW")
        tqs_prob            = a.get("tqs_probability", 0)
        signal_scores       = assessment.get("signal_scores", {})
        sleep_disruption    = signal_scores.get("sleep_disruption", 0)

        # Map conditions in priority order
        if health_index < 25:
            conditions.append("CRITICAL_ALERT")

        if readiness < 40:
            conditions.append("COGNITIVE_OVERLOAD")

        if risk_level in ["HIGH", "CRITICAL"] or tqs_prob > 0.7:
            conditions.append("PSYCHOLOGICAL_DRIFT")

        if tqs_prob > 0.5:
            conditions.append("TQS_PREVENTION")

        if sleep_disruption > 50:
            conditions.append("SLEEP_DISRUPTION")

        return conditions

    def recommend(self, assessment: dict) -> dict:
        """
        Main recommendation function.
        Returns a prioritized list of interventions for this astronaut today.
        """
        astronaut_id    = assessment["astronaut_id"]
        mission_day     = assessment["mission_day"]
        total_days      = 180
        days_remaining  = total_days - mission_day

        # Load history
        if astronaut_id not in self.history:
            self.history[astronaut_id] = self._load_history(astronaut_id)

        # Determine what conditions need intervention
        conditions = self._determine_conditions(assessment)

        if not conditions:
            return {
                "astronaut_id"  : astronaut_id,
                "mission_day"   : mission_day,
                "status"        : "NO_INTERVENTION_NEEDED",
                "interventions" : [],
                "message"       : "Psychological indicators within normal range. No intervention required today.",
            }

        # Select one intervention per condition (max 3 total)
        selected_interventions = []
        for condition in conditions[:3]:
            candidates  = get_interventions_for_condition(condition)
            selected    = self._select_intervention(candidates, astronaut_id)

            if selected:
                # Personalize dynamic fields
                personalized = selected.copy()
                personalized["description"] = personalized["description"].format(
                    mission_day     = mission_day,
                    total_days      = total_days,
                    days_remaining  = days_remaining,
                )

                selected_interventions.append({
                    "condition"     : condition,
                    "intervention"  : personalized,
                    "priority"      : conditions.index(condition) + 1,
                })

                # Log to history
                self.history[astronaut_id].append({
                    "mission_day"       : mission_day,
                    "condition"         : condition,
                    "intervention_id"   : selected["id"],
                    "timestamp"         : datetime.now().isoformat(),
                    "effectiveness"     : "PENDING",
                })

        # Save updated history
        self._save_history(astronaut_id)

        return {
            "astronaut_id"  : astronaut_id,
            "mission_day"   : mission_day,
            "status"        : "INTERVENTIONS_RECOMMENDED",
            "conditions"    : conditions,
            "interventions" : selected_interventions,
            "message"       : f"{len(selected_interventions)} intervention(s) recommended based on current assessment.",
        }

    def record_effectiveness(self, astronaut_id: str,
                              intervention_id: str,
                              effectiveness: str):
        """
        Records whether an intervention improved the astronaut's state.
        effectiveness: 'IMPROVED' | 'NO_CHANGE' | 'WORSENED'
        This is the feedback loop that makes ELARA adaptive.
        """
        if astronaut_id not in self.history:
            self.history[astronaut_id] = self._load_history(astronaut_id)

        for entry in reversed(self.history[astronaut_id]):
            if entry["intervention_id"] == intervention_id and \
               entry["effectiveness"] == "PENDING":
                entry["effectiveness"] = effectiveness
                break

        self._save_history(astronaut_id)


if __name__ == "__main__":
    from models.elara_pipeline  import ELARAPipeline
    from signals.feature_engineering import build_feature_matrix

    print("=" * 55)
    print("ELARA Intervention Engine — Test")
    print("=" * 55)

    df          = build_feature_matrix()
    pipeline    = ELARAPipeline()
    pipeline.load(df)
    engine      = InterventionEngine()

    for day in [60, 137]:
        print(f"\n{'='*55}")
        print(f"Mission Day {day} Interventions")
        print(f"{'='*55}")

        assessments = pipeline.assess_crew(day)
        for assessment in assessments:
            result = engine.recommend(assessment)
            print(f"\n{assessment['astronaut_name']}:")
            print(f"  Status: {result['status']}")
            if result["interventions"]:
                for item in result["interventions"]:
                    iv = item["intervention"]
                    print(f"  [{item['condition']}] {iv['title']}")
                    print(f"    → {iv['description']}")
                    print(f"    → Duration: {iv['duration_min']} min | Type: {iv['type']}")