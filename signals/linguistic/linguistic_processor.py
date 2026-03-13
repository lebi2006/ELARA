"""
ELARA — Linguistic Signal Processor
Detects psychological drift through language pattern analysis.
Based on published research on astronaut communication degradation.
Pronoun shifts, sentiment drops, vocabulary simplification are
documented early markers of psychological distress in isolation.
"""

import numpy as np
import pandas as pd


class LinguisticProcessor:
    """
    Processes daily mission log linguistic features.
    Tracks language degradation as a psychological drift indicator.
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
            "sentiment_avg"         : baseline_df["sentiment_score"].mean(),
            "sentiment_std"         : baseline_df["sentiment_score"].std(),
            "pronoun_i_avg"         : baseline_df["pronoun_i_ratio"].mean(),
            "emotional_word_avg"    : baseline_df["emotional_word_ratio"].mean(),
            "vocabulary_avg"        : baseline_df["vocabulary_complexity"].mean(),
            "word_count_avg"        : baseline_df["log_word_count"].mean(),
            "negative_word_avg"     : baseline_df["negative_word_ratio"].mean(),
        }

        self.baselines[astronaut_id] = baseline
        return baseline

    def compute_linguistic_drift_score(self, row: pd.Series, astronaut_id: str) -> float:
        """
        Computes linguistic drift score (0-100).
        Higher = more language degradation = stronger psychological drift signal.

        Key signals based on NASA/ESA isolation research:
        - Sentiment drop: astronaut writes more negatively
        - Pronoun shift: stops using 'I' — dissociation from self
        - Vocabulary simplification: cognitive load reducing language complexity
        - Word count drop: withdrawal, reduced communication
        - Negative word increase: pessimism, hopelessness markers
        """
        baseline = self.baselines[astronaut_id]

        # Sentiment drop
        sentiment_drop = max(0, (baseline["sentiment_avg"] - row["sentiment_score"]) /
                             max(baseline["sentiment_std"], 0.05))

        # Pronoun I ratio drop (dissociation marker)
        pronoun_drop = max(0, (baseline["pronoun_i_avg"] - row["pronoun_i_ratio"]) /
                           max(baseline["pronoun_i_avg"], 1e-6))

        # Vocabulary complexity drop
        vocab_drop = max(0, (baseline["vocabulary_avg"] - row["vocabulary_complexity"]) /
                         max(baseline["vocabulary_avg"], 1e-6))

        # Word count drop (withdrawal)
        wordcount_drop = max(0, (baseline["word_count_avg"] - row["log_word_count"]) /
                             max(baseline["word_count_avg"], 1))

        # Negative word increase
        negative_rise = max(0, (row["negative_word_ratio"] - baseline["negative_word_avg"]) /
                            max(baseline["negative_word_avg"], 1e-6))

        raw_score = (
            sentiment_drop  * 0.30 +
            pronoun_drop    * 0.20 +
            vocab_drop      * 0.20 +
            wordcount_drop  * 0.15 +
            negative_rise   * 0.15
        )

        return round(min(100, raw_score * 38), 2)

    def compute_rolling_drift_trend(self, df: pd.DataFrame,
                                     astronaut_id: str,
                                     window: int = 7) -> pd.Series:
        """
        Computes 7-day rolling average of linguistic drift score.
        Smooths daily noise to reveal genuine long-term trends.
        This is what catches Third-Quarter Syndrome early.
        """
        astronaut_df = df[df["astronaut_id"] == astronaut_id].copy()
        return astronaut_df["linguistic_drift_score"].rolling(window=window,
                                                               min_periods=1).mean()

    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        results = []

        for astronaut_id in df["astronaut_id"].unique():
            astronaut_df = df[df["astronaut_id"] == astronaut_id].copy()
            self.establish_baseline(df, astronaut_id)

            astronaut_df["linguistic_drift_score"] = astronaut_df.apply(
                lambda row: self.compute_linguistic_drift_score(row, astronaut_id), axis=1
            )

            # Add rolling trend
            astronaut_df["linguistic_drift_7day_avg"] = self.compute_rolling_drift_trend(
                astronaut_df, astronaut_id
            )

            results.append(astronaut_df)

        return pd.concat(results, ignore_index=True)


if __name__ == "__main__":
    df      = pd.read_csv("data/raw/mission_data_full.csv")
    proc    = LinguisticProcessor(baseline_days=14)
    result  = proc.process(df)

    print("Linguistic Processing Complete")
    print(result[["astronaut_name", "mission_phase",
                  "linguistic_drift_score"]].groupby(
        ["astronaut_name", "mission_phase"])["linguistic_drift_score"].mean().round(2)
    )