"""
ELARA — Feature Engineering Pipeline
Runs all 4 signal processors and merges outputs into
a single unified feature matrix for model training.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from signals.voice.voice_processor           import VoiceProcessor
from signals.sleep.sleep_processor           import SleepProcessor
from signals.latency.latency_processor       import LatencyProcessor
from signals.linguistic.linguistic_processor import LinguisticProcessor


# Features used for each model
COGNITIVE_LOAD_FEATURES = [
    "voice_stress_score",
    "cognitive_latency_score",
    "sleep_disruption_score",
    "energy_mean",
    "speech_rate",
    "mean_latency_sec",
    "missed_prompts",
    "duration_hrs",
    "mission_day",
]

PSYCH_DRIFT_FEATURES = [
    "linguistic_drift_score",
    "linguistic_drift_7day_avg",
    "sleep_disruption_score",
    "voice_stress_score",
    "sentiment_score",
    "pronoun_i_ratio",
    "negative_word_ratio",
    "vocabulary_complexity",
    "mission_day",
]

FUSION_FEATURES = [
    "voice_stress_score",
    "sleep_disruption_score",
    "cognitive_latency_score",
    "linguistic_drift_score",
    "linguistic_drift_7day_avg",
    "mission_day",
    "is_tqs_window",
]


def build_feature_matrix(raw_path: str = "data/raw/mission_data_full.csv") -> pd.DataFrame:
    """
    Runs all signal processors and returns unified feature matrix.
    """
    print("Loading raw mission data...")
    df = pd.read_csv(raw_path)

    print("Running Voice Processor...")
    voice_proc  = VoiceProcessor(baseline_days=14)
    df          = voice_proc.process(df)

    print("Running Sleep Processor...")
    sleep_proc  = SleepProcessor(baseline_days=14)
    df          = sleep_proc.process(df)

    print("Running Latency Processor...")
    latency_proc = LatencyProcessor(baseline_days=14)
    df           = latency_proc.process(df)

    print("Running Linguistic Processor...")
    ling_proc   = LinguisticProcessor(baseline_days=14)
    df          = ling_proc.process(df)

    # Save processed feature matrix
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    df.to_csv("data/processed/feature_matrix.csv", index=False)
    print(f"Feature matrix saved: {len(df)} records, {len(df.columns)} columns")

    return df


if __name__ == "__main__":
    df = build_feature_matrix()
    print("\nSample feature matrix:")
    print(df[["astronaut_name", "mission_day", "mission_phase",
              "voice_stress_score", "sleep_disruption_score",
              "cognitive_latency_score", "linguistic_drift_score",
              "health_index", "risk_level"]].head(10).to_string(index=False))