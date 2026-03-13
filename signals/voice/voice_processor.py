"""
ELARA — Voice Signal Processor
Extracts psychological stress indicators from voice feature data.
In production: processes real audio via librosa.
In prototype: processes pre-extracted voice features from synthetic data.
"""

import numpy as np
import pandas as pd
from pathlib import Path


class VoiceProcessor:
    """
    Processes daily voice features and computes normalized
    stress indicators relative to each astronaut's personal baseline.
    """

    def __init__(self, baseline_days: int = 14):
        self.baseline_days  = baseline_days
        self.baselines      = {}  # Per-astronaut baselines

    def establish_baseline(self, df: pd.DataFrame, astronaut_id: str) -> dict:
        """
        Computes personal voice baseline from first 14 days.
        All future anomalies measured against THIS individual's baseline.
        """
        baseline_df = df[
            (df["astronaut_id"] == astronaut_id) &
            (df["mission_day"] <= self.baseline_days)
        ]

        baseline = {
            "pitch_mean_avg"    : baseline_df["pitch_mean"].mean(),
            "pitch_mean_std"    : baseline_df["pitch_mean"].std(),
            "energy_mean_avg"   : baseline_df["energy_mean"].mean(),
            "energy_mean_std"   : baseline_df["energy_mean"].std(),
            "speech_rate_avg"   : baseline_df["speech_rate"].mean(),
            "speech_rate_std"   : baseline_df["speech_rate"].std(),
            "jitter_avg"        : baseline_df["jitter"].mean(),
            "shimmer_avg"       : baseline_df["shimmer"].mean(),
        }

        self.baselines[astronaut_id] = baseline
        return baseline

    def compute_voice_stress_score(self, row: pd.Series, astronaut_id: str) -> float:
        """
        Computes a normalized voice stress score (0-100) for a single day.
        Compares current readings against personal baseline.
        Higher score = more stress detected in voice.
        """
        if astronaut_id not in self.baselines:
            raise ValueError(f"No baseline established for {astronaut_id}")

        baseline = self.baselines[astronaut_id]

        # Pitch drop from baseline (stress lowers pitch)
        pitch_drop = max(0, (baseline["pitch_mean_avg"] - row["pitch_mean"]) /
                         max(baseline["pitch_mean_std"], 1e-6))

        # Energy drop from baseline (stress reduces vocal energy)
        energy_drop = max(0, (baseline["energy_mean_avg"] - row["energy_mean"]) /
                          max(baseline["energy_mean_std"], 1e-6))

        # Speech rate drop (stress slows speech)
        rate_drop = max(0, (baseline["speech_rate_avg"] - row["speech_rate"]) /
                        max(baseline["speech_rate_std"], 1e-6))

        # Jitter and shimmer increase (voice instability)
        jitter_rise     = max(0, (row["jitter"] - baseline["jitter_avg"]) /
                              max(baseline["jitter_avg"], 1e-6))
        shimmer_rise    = max(0, (row["shimmer"] - baseline["shimmer_avg"]) /
                              max(baseline["shimmer_avg"], 1e-6))

        # Weighted combination
        raw_score = (
            pitch_drop   * 0.25 +
            energy_drop  * 0.30 +
            rate_drop    * 0.20 +
            jitter_rise  * 0.15 +
            shimmer_rise * 0.10
        )

        # Normalize to 0-100
        return round(min(100, raw_score * 35), 2)

    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Main processing function.
        Returns dataframe with voice stress scores for all astronauts.
        """
        results = []

        for astronaut_id in df["astronaut_id"].unique():
            astronaut_df = df[df["astronaut_id"] == astronaut_id].copy()

            # Establish personal baseline
            self.establish_baseline(df, astronaut_id)

            # Compute daily voice stress scores
            astronaut_df["voice_stress_score"] = astronaut_df.apply(
                lambda row: self.compute_voice_stress_score(row, astronaut_id), axis=1
            )

            results.append(astronaut_df)

        return pd.concat(results, ignore_index=True)


if __name__ == "__main__":
    df      = pd.read_csv("data/raw/mission_data_full.csv")
    proc    = VoiceProcessor(baseline_days=14)
    result  = proc.process(df)

    print("Voice Processing Complete")
    print(result[["astronaut_name", "mission_day", "mission_phase",
                  "voice_stress_score"]].groupby(
        ["astronaut_name", "mission_phase"])["voice_stress_score"].mean().round(2)
    )