"""
ELARA — Sleep Signal Processor
Detects sleep quality degradation relative to personal baseline.
Poor sleep is one of the earliest indicators of psychological stress.
"""

import numpy as np
import pandas as pd


class SleepProcessor:
    """
    Processes nightly sleep data and computes a sleep disruption score
    relative to each astronaut's personal baseline.
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
            "duration_avg"          : baseline_df["duration_hrs"].mean(),
            "duration_std"          : baseline_df["duration_hrs"].std(),
            "fragmentation_avg"     : baseline_df["fragmentation_idx"].mean(),
            "rem_ratio_avg"         : baseline_df["rem_ratio"].mean(),
            "sleep_efficiency_avg"  : baseline_df["sleep_efficiency"].mean(),
        }

        self.baselines[astronaut_id] = baseline
        return baseline

    def compute_sleep_disruption_score(self, row: pd.Series, astronaut_id: str) -> float:
        """
        Computes sleep disruption score (0-100).
        Higher = more disrupted sleep = higher psychological risk signal.
        """
        baseline = self.baselines[astronaut_id]

        # Sleep duration deficit
        duration_deficit = max(0, (baseline["duration_avg"] - row["duration_hrs"]) /
                               max(baseline["duration_std"], 0.1))

        # Fragmentation increase
        frag_increase = max(0, (row["fragmentation_idx"] - baseline["fragmentation_avg"]) /
                            max(baseline["fragmentation_avg"], 1e-6))

        # REM ratio drop
        rem_drop = max(0, (baseline["rem_ratio_avg"] - row["rem_ratio"]) /
                       max(baseline["rem_ratio_avg"], 1e-6))

        # Sleep efficiency drop
        efficiency_drop = max(0, (baseline["sleep_efficiency_avg"] - row["sleep_efficiency"]) /
                              max(baseline["sleep_efficiency_avg"], 1e-6))

        raw_score = (
            duration_deficit    * 0.35 +
            frag_increase       * 0.25 +
            rem_drop            * 0.25 +
            efficiency_drop     * 0.15
        )

        return round(min(100, raw_score * 40), 2)

    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        results = []

        for astronaut_id in df["astronaut_id"].unique():
            astronaut_df = df[df["astronaut_id"] == astronaut_id].copy()
            self.establish_baseline(df, astronaut_id)

            astronaut_df["sleep_disruption_score"] = astronaut_df.apply(
                lambda row: self.compute_sleep_disruption_score(row, astronaut_id), axis=1
            )

            results.append(astronaut_df)

        return pd.concat(results, ignore_index=True)


if __name__ == "__main__":
    df      = pd.read_csv("data/raw/mission_data_full.csv")
    proc    = SleepProcessor(baseline_days=14)
    result  = proc.process(df)

    print("Sleep Processing Complete")
    print(result[["astronaut_name", "mission_phase",
                  "sleep_disruption_score"]].groupby(
        ["astronaut_name", "mission_phase"])["sleep_disruption_score"].mean().round(2)
    )