"""
ELARA — Unified Prediction Pipeline
Single entry point that runs all signal processors
and all AI models for one astronaut on one mission day.
Returns a complete psychological assessment.
"""

import pandas as pd
import numpy as np
import sys, os
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from signals.voice.voice_processor              import VoiceProcessor
from signals.sleep.sleep_processor              import SleepProcessor
from signals.latency.latency_processor          import LatencyProcessor
from signals.linguistic.linguistic_processor    import LinguisticProcessor
from signals.feature_engineering                import (
    COGNITIVE_LOAD_FEATURES,
    PSYCH_DRIFT_FEATURES,
    FUSION_FEATURES
)
from models.cognitive_load.cognitive_load_model import CognitiveLoadModel
from models.psych_drift.psych_drift_model       import PsychDriftModel
from models.fusion.fusion_model                 import FusionModel


class ELARAPipeline:
    """
    Master pipeline that coordinates all ELARA components.
    Takes raw mission dataframe + astronaut ID + mission day.
    Returns complete psychological assessment with explanations.
    """

    def __init__(self):
        # Signal processors
        self.voice_proc     = VoiceProcessor(baseline_days=14)
        self.sleep_proc     = SleepProcessor(baseline_days=14)
        self.latency_proc   = LatencyProcessor(baseline_days=14)
        self.ling_proc      = LinguisticProcessor(baseline_days=14)

        # AI models
        self.cognitive_model    = CognitiveLoadModel()
        self.drift_model        = PsychDriftModel()
        self.fusion_model       = FusionModel()

        self.is_ready = False

    def load(self, df: pd.DataFrame):
        """
        Initializes pipeline with full mission data.
        Establishes personal baselines for all astronauts.
        Loads all trained models from disk.
        """
        print("Initializing ELARA Pipeline...")

        # Process all signals to establish baselines
        print("  Establishing personal baselines...")
        df = self.voice_proc.process(df)
        df = self.sleep_proc.process(df)
        df = self.latency_proc.process(df)
        df = self.ling_proc.process(df)
        self.processed_df = df

        # Load trained models
        print("  Loading trained models...")
        self.cognitive_model.load()
        self.drift_model.load()
        self.fusion_model.load()

        self.is_ready = True
        print("  ELARA Pipeline ready.")
        return self

    def assess(self, astronaut_id: str, mission_day: int) -> dict:
        """
        Runs complete psychological assessment for one astronaut
        on one mission day.
        """
        if not self.is_ready:
            raise RuntimeError("Pipeline not loaded. Call load() first.")

        # Get processed row for this astronaut and day
        row = self.processed_df[
            (self.processed_df["astronaut_id"]  == astronaut_id) &
            (self.processed_df["mission_day"]   == mission_day)
        ]

        if row.empty:
            raise ValueError(f"No data for {astronaut_id} on day {mission_day}")

        row_dict = row.iloc[0].to_dict()

        # Run all 3 models
        cognitive   = self.cognitive_model.predict(row_dict)
        drift       = self.drift_model.predict(row_dict)
        fusion      = self.fusion_model.predict(row_dict)

        # Build mission phase context
        phase       = row_dict.get("mission_phase", "UNKNOWN")
        is_tqs      = bool(row_dict.get("is_tqs_window", 0))

        # Composite alert logic
        alerts = []
        if cognitive["cognitive_readiness_score"] < 40:
            alerts.append({
                "type"      : "COGNITIVE_READINESS",
                "severity"  : "HIGH",
                "message"   : f"Cognitive readiness critically low ({cognitive['cognitive_readiness_score']}). Recommend delaying high-risk tasks.",
            })

        if drift["risk_level"] in ["HIGH", "CRITICAL"]:
            alerts.append({
                "type"      : "PSYCHOLOGICAL_DRIFT",
                "severity"  : drift["risk_level"],
                "message"   : f"Psychological drift detected. Risk level: {drift['risk_level']}. TQS probability: {drift['tqs_probability']}",
            })

        if is_tqs:
            alerts.append({
                "type"      : "TQS_WINDOW",
                "severity"  : "MONITOR",
                "message"   : "Astronaut is within Third-Quarter Syndrome risk window (Days 120-150). Heightened monitoring active.",
            })

        if fusion["health_index"] < 45:
            alerts.append({
                "type"      : "HEALTH_INDEX",
                "severity"  : fusion["status"],
                "message"   : f"Unified Health Index critically low ({fusion['health_index']}). Immediate review recommended.",
            })

        return {
            "astronaut_id"  : astronaut_id,
            "astronaut_name": row_dict.get("astronaut_name", astronaut_id),
            "mission_day"   : mission_day,
            "mission_phase" : phase,
            "assessment"    : {
                "cognitive_load_score"      : cognitive["cognitive_load_score"],
                "cognitive_readiness_score" : cognitive["cognitive_readiness_score"],
                "risk_level"                : drift["risk_level"],
                "tqs_probability"           : drift["tqs_probability"],
                "health_index"              : fusion["health_index"],
                "health_status"             : fusion["status"],
            },
            "explanations"  : {
                "cognitive_load"    : cognitive["top_contributors"],
                "psych_drift"       : drift["top_contributors"],
                "health_index"      : fusion["top_contributors"],
            },
            "alerts"        : alerts,
            "signal_scores" : {
                "voice_stress"      : round(row_dict.get("voice_stress_score", 0), 2),
                "sleep_disruption"  : round(row_dict.get("sleep_disruption_score", 0), 2),
                "cognitive_latency" : round(row_dict.get("cognitive_latency_score", 0), 2),
                "linguistic_drift"  : round(row_dict.get("linguistic_drift_score", 0), 2),
            },
        }

    def assess_crew(self, mission_day: int) -> list:
        """
        Runs assessment for all crew members on a given day.
        Used by mission control dashboard.
        """
        crew_ids = self.processed_df["astronaut_id"].unique()
        return [self.assess(astronaut_id, mission_day) for astronaut_id in crew_ids]


if __name__ == "__main__":
    from signals.feature_engineering import build_feature_matrix

    print("=" * 55)
    print("ELARA Pipeline — Full Assessment Test")
    print("=" * 55)

    df          = build_feature_matrix()
    pipeline    = ELARAPipeline()
    pipeline.load(df)

    # Test Day 10 (baseline) vs Day 137 (TQS peak)
    for day in [10, 60, 137]:
        print(f"\n{'='*55}")
        print(f"Mission Day {day} — Crew Assessment")
        print(f"{'='*55}")
        results = pipeline.assess_crew(day)

        for r in results:
            a = r["assessment"]
            print(f"\n{r['astronaut_name']} ({r['mission_phase']})")
            print(f"  Health Index      : {a['health_index']} [{a['health_status']}]")
            print(f"  Cognitive Load    : {a['cognitive_load_score']} | Readiness: {a['cognitive_readiness_score']}")
            print(f"  Risk Level        : {a['risk_level']} | TQS Prob: {a['tqs_probability']}")
            print(f"  Signal Scores     : {r['signal_scores']}")
            if r["alerts"]:
                print(f"  ⚠ ALERTS:")
                for alert in r["alerts"]:
                    print(f"    [{alert['severity']}] {alert['message']}")