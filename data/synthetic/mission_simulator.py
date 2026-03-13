"""
ELARA — Synthetic Mission Data Generator
Based on NASA HI-SEAS and ISS published research parameters.
Generates 180-day psychological behavioral signal data for 3 astronauts.
"""

import numpy as np
import pandas as pd
from pathlib import Path
import json
import random

# ── Reproducibility ──────────────────────────────────────────────────────────
np.random.seed(42)
random.seed(42)

# ── Mission Configuration ─────────────────────────────────────────────────────
MISSION_DAYS        = 180
CREW_SIZE           = 3
BASELINE_DAYS       = 14       # First 14 days = calibration phase
TQS_START           = 120      # Third-Quarter Syndrome window start
TQS_PEAK            = 135      # Peak risk day
TQS_END             = 150      # Window end
OUTPUT_DIR          = Path("data/raw")

# ── Astronaut Profiles ────────────────────────────────────────────────────────
# Each astronaut has unique baseline characteristics
ASTRONAUT_PROFILES = {
    "GAGANYAAN_01": {
        "name"              : "Arjun Sharma",
        "voice_pitch_base"  : 145.0,   # Hz — male voice baseline
        "sleep_base"        : 7.2,     # hours
        "latency_base"      : 1.4,     # seconds
        "resilience_factor" : 0.85,    # High resilience
        "tqs_vulnerability" : 0.6,     # Moderate TQS risk
    },
    "GAGANYAAN_02": {
        "name"              : "Priya Nair",
        "voice_pitch_base"  : 210.0,   # Hz — female voice baseline
        "sleep_base"        : 7.5,
        "latency_base"      : 1.2,
        "resilience_factor" : 0.78,
        "tqs_vulnerability" : 0.8,     # Higher TQS risk
    },
    "GAGANYAAN_03": {
        "name"              : "Vikram Rao",
        "voice_pitch_base"  : 130.0,
        "sleep_base"        : 6.9,
        "latency_base"      : 1.8,
        "resilience_factor" : 0.92,    # Very high resilience
        "tqs_vulnerability" : 0.4,     # Low TQS risk
    },
}


def mission_stress_curve(day: int, tqs_vulnerability: float) -> float:
    """
    Returns a stress multiplier for a given mission day.
    Models real mission phases:
      - Days 01-14  : Adaptation (mild stress)
      - Days 15-60  : Operational baseline (stable)
      - Days 61-119 : Mid-mission fatigue (gradual increase)
      - Days 120-150: Third-Quarter Syndrome (peak stress)
      - Days 151-180: Return anticipation (mixed recovery)
    """
    if day <= 14:
        return 0.3 + (day / 14) * 0.2                          # Adapting

    elif day <= 60:
        return 0.5 + np.random.normal(0, 0.05)                 # Stable baseline

    elif day <= 119:
        fatigue = 0.5 + ((day - 60) / 60) * 0.3               # Gradual fatigue
        return fatigue + np.random.normal(0, 0.08)

    elif day <= 150:
        # Third-Quarter Syndrome peak
        tqs_intensity = ((day - 120) / 30) * tqs_vulnerability
        return 0.8 + tqs_intensity + np.random.normal(0, 0.1)

    else:
        # Return phase — anticipation reduces stress slightly
        recovery = ((day - 150) / 30) * 0.2
        return max(0.6, 0.85 - recovery + np.random.normal(0, 0.07))


def generate_voice_features(day: int, profile: dict) -> dict:
    """
    Generates daily voice features based on stress level.
    Higher stress = lower pitch, lower energy, slower speech.
    """
    stress      = mission_stress_curve(day, profile["tqs_vulnerability"])
    base_pitch  = profile["voice_pitch_base"]

    return {
        "pitch_mean"    : round(base_pitch - (stress * 18) + np.random.normal(0, 3), 2),
        "pitch_std"     : round(12 + stress * 8 + np.random.normal(0, 1), 2),
        "energy_mean"   : round(max(0.1, 0.75 - stress * 0.3 + np.random.normal(0, 0.05)), 3),
        "speech_rate"   : round(max(80, 148 - stress * 25 + np.random.normal(0, 5)), 1),
        "jitter"        : round(0.02 + stress * 0.03 + np.random.normal(0, 0.005), 4),
        "shimmer"       : round(0.05 + stress * 0.06 + np.random.normal(0, 0.008), 4),
    }


def generate_sleep_features(day: int, profile: dict) -> dict:
    """
    Generates nightly sleep data.
    Higher stress = shorter sleep, more fragmentation, less REM.
    """
    stress          = mission_stress_curve(day, profile["tqs_vulnerability"])
    base_sleep      = profile["sleep_base"]

    return {
        "duration_hrs"      : round(max(3.5, base_sleep - stress * 1.8 + np.random.normal(0, 0.3)), 2),
        "fragmentation_idx" : round(min(1.0, 0.1 + stress * 0.5 + np.random.normal(0, 0.05)), 3),
        "rem_ratio"         : round(max(0.05, 0.21 - stress * 0.08 + np.random.normal(0, 0.02)), 3),
        "sleep_efficiency"  : round(max(0.5, 0.92 - stress * 0.25 + np.random.normal(0, 0.03)), 3),
    }


def generate_latency_features(day: int, profile: dict) -> dict:
    """
    Generates interaction response latency data.
    Higher stress / fatigue = slower responses, higher variance.
    """
    stress          = mission_stress_curve(day, profile["tqs_vulnerability"])
    base_latency    = profile["latency_base"]

    return {
        "mean_latency_sec"  : round(base_latency + stress * 1.2 + np.random.normal(0, 0.15), 3),
        "latency_std"       : round(0.2 + stress * 0.4 + np.random.normal(0, 0.05), 3),
        "max_latency_sec"   : round(base_latency + stress * 2.5 + np.random.normal(0, 0.3), 3),
        "missed_prompts"    : int(max(0, round(stress * 3 + np.random.normal(0, 0.5)))),
    }


def generate_linguistic_features(day: int, profile: dict) -> dict:
    """
    Generates linguistic pattern features from mission logs.
    Higher stress = negative sentiment, simpler language, fewer self-references.
    Based on published research on astronaut communication patterns.
    """
    stress = mission_stress_curve(day, profile["tqs_vulnerability"])

    return {
        "sentiment_score"       : round(max(-1.0, 0.6 - stress * 0.9 + np.random.normal(0, 0.1)), 3),
        "pronoun_i_ratio"       : round(max(0.0, 0.18 - stress * 0.12 + np.random.normal(0, 0.02)), 3),
        "emotional_word_ratio"  : round(max(0.0, 0.12 - stress * 0.08 + np.random.normal(0, 0.015)), 3),
        "vocabulary_complexity" : round(max(0.1, 0.72 - stress * 0.3 + np.random.normal(0, 0.05)), 3),
        "log_word_count"        : int(max(20, round(280 - stress * 120 + np.random.normal(0, 20)))),
        "negative_word_ratio"   : round(min(1.0, 0.05 + stress * 0.2 + np.random.normal(0, 0.02)), 3),
    }


def compute_ground_truth_label(day: int, profile: dict) -> dict:
    """
    Computes ground truth psychological health scores for model training.
    These are the TARGET LABELS our AI models will learn to predict.
    """
    stress              = mission_stress_curve(day, profile["tqs_vulnerability"])
    resilience          = profile["resilience_factor"]

    cognitive_load      = round(min(100, max(0, stress * 85 + np.random.normal(0, 5))), 1)
    psych_drift         = round(min(100, max(0, stress * 78 * (1 - resilience * 0.3) + np.random.normal(0, 4))), 1)
    health_index        = round(max(0, 100 - (cognitive_load * 0.4 + psych_drift * 0.6)), 1)

    # Risk level thresholds based on NASA flight surgeon protocols
    if health_index >= 70:
        risk_level = "LOW"
    elif health_index >= 45:
        risk_level = "MODERATE"
    elif health_index >= 25:
        risk_level = "HIGH"
    else:
        risk_level = "CRITICAL"

    return {
        "cognitive_load_score"  : cognitive_load,
        "psych_drift_score"     : psych_drift,
        "health_index"          : health_index,
        "risk_level"            : risk_level,
        "is_tqs_window"         : int(TQS_START <= day <= TQS_END),
        "stress_raw"            : round(stress, 4),
    }


def generate_mission_data() -> pd.DataFrame:
    """
    Master function — generates complete 180-day mission dataset
    for all 3 crew members.
    """
    records = []

    for astronaut_id, profile in ASTRONAUT_PROFILES.items():
        print(f"  Generating data for {profile['name']} ({astronaut_id})...")

        for day in range(1, MISSION_DAYS + 1):
            record = {
                "astronaut_id"  : astronaut_id,
                "astronaut_name": profile["name"],
                "mission_day"   : day,
                "mission_phase" : get_mission_phase(day),
            }

            # Add all signal features
            record.update(generate_voice_features(day, profile))
            record.update(generate_sleep_features(day, profile))
            record.update(generate_latency_features(day, profile))
            record.update(generate_linguistic_features(day, profile))
            record.update(compute_ground_truth_label(day, profile))

            records.append(record)

    return pd.DataFrame(records)


def get_mission_phase(day: int) -> str:
    if day <= 14:
        return "BASELINE_CALIBRATION"
    elif day <= 60:
        return "OPERATIONAL_STABLE"
    elif day <= 119:
        return "MID_MISSION_FATIGUE"
    elif day <= 150:
        return "THIRD_QUARTER_SYNDROME"
    else:
        return "RETURN_ANTICIPATION"


def save_data(df: pd.DataFrame):
    """Saves generated data in multiple formats for different pipeline stages."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Full dataset
    df.to_csv(OUTPUT_DIR / "mission_data_full.csv", index=False)
    print(f"  Saved: data/raw/mission_data_full.csv ({len(df)} records)")

    # Per-astronaut files
    for astronaut_id in df["astronaut_id"].unique():
        sub = df[df["astronaut_id"] == astronaut_id]
        sub.to_csv(OUTPUT_DIR / f"{astronaut_id}_mission_data.csv", index=False)
        print(f"  Saved: data/raw/{astronaut_id}_mission_data.csv")

    # Mission metadata
    metadata = {
        "mission_duration_days" : MISSION_DAYS,
        "crew_size"             : CREW_SIZE,
        "baseline_days"         : BASELINE_DAYS,
        "tqs_window"            : {"start": TQS_START, "peak": TQS_PEAK, "end": TQS_END},
        "astronauts"            : list(ASTRONAUT_PROFILES.keys()),
        "total_records"         : len(df),
        "features"              : list(df.columns),
        "data_source"           : "Synthetic — generated from NASA HI-SEAS & ISS research parameters",
    }

    with open(OUTPUT_DIR / "mission_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"  Saved: data/raw/mission_metadata.json")


if __name__ == "__main__":
    print("=" * 60)
    print("ELARA — Synthetic Mission Data Generator")
    print("Generating 180-day Gaganyaan mission simulation...")
    print("=" * 60)

    df = generate_mission_data()
    save_data(df)

    print("=" * 60)
    print(f"Generation complete. {len(df)} total daily records created.")
    print(f"Mission phases breakdown:")
    print(df["mission_phase"].value_counts().to_string())
    print("=" * 60)