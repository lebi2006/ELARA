"""
ELARA — Multimodal Fusion Model
Combines all signal streams into a single
Unified Psychological Health Index (0-100).
This is the master score mission control monitors.
"""

import numpy as np
import pandas as pd
import pickle
import shap
from pathlib import Path
from sklearn.ensemble         import GradientBoostingRegressor
from sklearn.model_selection  import train_test_split, cross_val_score
from sklearn.preprocessing    import StandardScaler
from sklearn.metrics          import mean_absolute_error, r2_score
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from signals.feature_engineering import FUSION_FEATURES

MODEL_DIR = Path("models/fusion")


class FusionModel:
    """
    Fuses all behavioral signal scores into a
    Unified Psychological Health Index (0-100).
    Higher = healthier. Below 45 = intervention required.
    """

    def __init__(self):
        self.model = GradientBoostingRegressor(
            n_estimators    = 250,
            max_depth       = 4,
            learning_rate   = 0.04,
            subsample       = 0.85,
            random_state    = 42
        )
        self.scaler     = StandardScaler()
        self.explainer  = None
        self.features   = FUSION_FEATURES
        self.is_trained = False

    def train(self, df: pd.DataFrame) -> dict:
        train_df = df[df["mission_day"] > 14].copy()

        X = train_df[self.features].fillna(0)
        y = train_df["health_index"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        X_train_scaled  = self.scaler.fit_transform(X_train)
        X_test_scaled   = self.scaler.transform(X_test)

        print("  Training Fusion Model...")
        self.model.fit(X_train_scaled, y_train)

        y_pred  = self.model.predict(X_test_scaled)
        mae     = mean_absolute_error(y_test, y_pred)
        r2      = r2_score(y_test, y_pred)

        cv_scores = cross_val_score(
            self.model,
            self.scaler.transform(X),
            y,
            cv=5,
            scoring="r2"
        )

        print("  Building SHAP explainer...")
        self.explainer = shap.Explainer(
            self.model.predict,
            self.scaler.transform(X_train),
            feature_names=self.features
        )

        self.is_trained = True

        metrics = {
            "mae"        : round(mae, 3),
            "r2"         : round(r2, 3),
            "cv_r2_mean" : round(cv_scores.mean(), 3),
            "cv_r2_std"  : round(cv_scores.std(), 3),
        }

        print(f"  MAE: {metrics['mae']}  |  R²: {metrics['r2']}  |  CV R²: {metrics['cv_r2_mean']} ± {metrics['cv_r2_std']}")
        return metrics

    def predict(self, features: dict) -> dict:
        if not self.is_trained:
            raise RuntimeError("Model not trained.")

        X           = pd.DataFrame([features])[self.features].fillna(0)
        X_scaled    = self.scaler.transform(X)
        score       = float(self.model.predict(X_scaled)[0])
        score       = round(min(100, max(0, score)), 2)

        shap_values = self.explainer(X_scaled)
        explanation = {
            feat: round(float(shap_values.values[0][i]), 3)
            for i, feat in enumerate(self.features)
        }

        # Health status label
        if score >= 70:
            status = "STABLE"
        elif score >= 45:
            status = "MONITOR"
        elif score >= 25:
            status = "AT_RISK"
        else:
            status = "CRITICAL"

        return {
            "health_index"      : score,
            "status"            : status,
            "explanation"       : explanation,
            "top_contributors"  : sorted(
                explanation.items(),
                key=lambda x: abs(x[1]),
                reverse=True
            )[:3],
        }

    def save(self):
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        with open(MODEL_DIR / "fusion_model.pkl", "wb") as f:
            pickle.dump({
                "model": self.model, "scaler": self.scaler,
                "features": self.features
            }, f)
        print(f"  Saved: models/fusion/fusion_model.pkl")

    def load(self):
        with open(MODEL_DIR / "fusion_model.pkl", "rb") as f:
            data = pickle.load(f)
        self.model      = data["model"]
        self.scaler     = data["scaler"]
        self.features   = data["features"]
        self.is_trained = True


if __name__ == "__main__":
    from signals.feature_engineering import build_feature_matrix
    print("=" * 50)
    print("Training Fusion Model")
    print("=" * 50)
    df      = build_feature_matrix()
    model   = FusionModel()
    metrics = model.train(df)
    model.save()