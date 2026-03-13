"""
ELARA — Interaction Latency Processor
Detects cognitive slowing through response time analysis.
Increasing latency indicates mental fatigue and emotional withdrawal.
"""

import numpy as np
import pandas as pd


class LatencyProcessor:
    """
    Processes interaction response latency data.
    Slowed responses to onboard system prompts signal cognitive fatigue.
    """

    def __init__(self, baseline_days: int = 14):
        self.baseline_days  = baseline_days
        self.baselines      = {}

    def establish_baseline(self, df: pd.DataFrame, astronaut_id: str) -> dict:
        baseline_df = df[
            (df["astronaut_id"] == astronaut_id) &
            (df["mission_day"] <= self.baseline_days)
        ]

        baseline = {
            "mean_latency_avg"  : baseline_df["mean_latency_sec"].mean(),
            "mean_latency_std"  : baseline_df["mean_latency_sec"].std(),
            "latency_std_avg"   : baseline_df["latency_std"].mean(),
            "missed_avg"        : baseline_df["missed_prompts"].mean(),
        }

        self.baselines[astronaut_id] = baseline
        return baseline

    def compute_cognitive_latency_score(self, row: pd.Series, astronaut_id: str) -> float:
        """
        Computes cognitive latency score (0-100).
        Higher = more cognitive slowing detected.
        """
        baseline = self.baselines[astronaut_id]

        # Mean latency increase
        latency_increase = max(0, (row["mean_latency_sec"] - baseline["mean_latency_avg"]) /
                               max(baseline["mean_latency_std"], 0.1))

        # Latency variance increase (inconsistent responses)
        variance_increase = max(0, (row["latency_std"] - baseline["latency_std_avg"]) /
                                max(baseline["latency_std_avg"], 1e-6))

        # Missed prompts (most serious signal)
        missed_ratio = row["missed_prompts"] / max(baseline["missed_avg"] + 1, 1)

        raw_score = (
            latency_increase    * 0.45 +
            variance_increase   * 0.30 +
            missed_ratio        * 0.25
        )

        return round(min(100, raw_score * 30), 2)

    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        results = []

        for astronaut_id in df["astronaut_id"].unique():
            astronaut_df = df[df["astronaut_id"] == astronaut_id].copy()
            self.establish_baseline(df, astronaut_id)

            astronaut_df["cognitive_latency_score"] = astronaut_df.apply(
                lambda row: self.compute_cognitive_latency_score(row, astronaut_id), axis=1
            )

            results.append(astronaut_df)

        return pd.concat(results, ignore_index=True)


if __name__ == "__main__":
    df      = pd.read_csv("data/raw/mission_data_full.csv")
    proc    = LatencyProcessor(baseline_days=14)
    result  = proc.process(df)

    print("Latency Processing Complete")
    print(result[["astronaut_name", "mission_phase",
                  "cognitive_latency_score"]].groupby(
        ["astronaut_name", "mission_phase"])["cognitive_latency_score"].mean().round(2)
    )