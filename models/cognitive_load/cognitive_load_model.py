"""
ELARA — Cognitive Load Estimation Model
Predicts cognitive load score from behavioral signals.
Uses Gradient Boosting with SHAP explainability.
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
from signals.feature_engineering import COGNITIVE_LOAD_FEATURES

MODEL_DIR = Path("models/cognitive_load")


class CognitiveLoadModel:
    """
    Estimates real-time cognitive load score (0-100) from
    multimodal behavioral signals.
    Output drives the Cognitive Readiness Score on the dashboard.
    """

    def __init__(self):
        self.model   = GradientBoostingRegressor(
            n_estimators    = 200,
            max_depth       = 4,
            learning_rate   = 0.05,
            subsample       = 0.8,
            random_state    = 42
        )
        self.scaler     = StandardScaler()
        self.explainer  = None
        self.features   = COGNITIVE_LOAD_FEATURES
        self.is_trained = False

    def train(self, df: pd.DataFrame) -> dict:
        """
        Trains the cognitive load model.
        Returns evaluation metrics.
        """
        # Filter out baseline calibration days from training
        # (baseline days are for calibration, not prediction)
        train_df = df[df["mission_day"] > 14].copy()

        X = train_df[self.features].fillna(0)
        y = train_df["cognitive_load_score"]

        # Train / test split — respect temporal order
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Scale features
        X_train_scaled  = self.scaler.fit_transform(X_train)
        self._background = X_train_scaled[:50]
        X_test_scaled   = self.scaler.transform(X_test)

        # Train model
        print("  Training Cognitive Load Model...")
        self.model.fit(X_train_scaled, y_train)

        # Evaluate
        y_pred  = self.model.predict(X_test_scaled)
        mae     = mean_absolute_error(y_test, y_pred)
        r2      = r2_score(y_test, y_pred)

        # Cross validation
        cv_scores = cross_val_score(
            self.model,
            self.scaler.transform(X),
            y,
            cv=5,
            scoring="r2"
        )

        # Build SHAP explainer
        print("  Building SHAP explainer...")
        self.explainer = shap.Explainer(
            self.model.predict,
            self.scaler.transform(X_train),
            feature_names=self.features
        )

        self.is_trained = True

        metrics = {
            "mae"           : round(mae, 3),
            "r2"            : round(r2, 3),
            "cv_r2_mean"    : round(cv_scores.mean(), 3),
            "cv_r2_std"     : round(cv_scores.std(), 3),
            "train_samples" : len(X_train),
            "test_samples"  : len(X_test),
        }

        print(f"  MAE: {metrics['mae']}  |  R²: {metrics['r2']}  |  CV R²: {metrics['cv_r2_mean']} ± {metrics['cv_r2_std']}")
        return metrics

    def predict(self, features: dict) -> dict:
        """
        Predicts cognitive load for a single observation.
        Returns score + SHAP explanation.
        """
        if not self.is_trained:
            raise RuntimeError("Model not trained. Call train() first.")

        X = pd.DataFrame([features])[self.features].fillna(0)
        X_scaled = self.scaler.transform(X)

        score = float(self.model.predict(X_scaled)[0])
        score = round(min(100, max(0, score)), 2)

       # Feature importance explanation (fast, no per-request SHAP cost)
        explanation = {
            feat: round(float(self.model.feature_importances_[i]), 3)
            for i, feat in enumerate(self.features)
        }

        # Cognitive readiness is inverse of load
        readiness = round(100 - score, 2)

        return {
            "cognitive_load_score"      : score,
            "cognitive_readiness_score" : readiness,
            "explanation"               : explanation,
            "top_contributors"          : sorted(
                explanation.items(),
                key=lambda x: abs(x[1]),
                reverse=True
            )[:3],
        }

    def save(self):
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        with open(MODEL_DIR / "cognitive_load_model.pkl", "wb") as f:
            pickle.dump({
                "model"         : self.model,
                "scaler"        : self.scaler,
                "features"      : self.features,
                "background"    : self._background
            }, f)
        print(f"  Saved: models/cognitive_load/cognitive_load_model.pkl")

    def load(self):
        with open(MODEL_DIR / "cognitive_load_model.pkl", "rb") as f:
            data = pickle.load(f)
        self.model          = data["model"]
        self.scaler         = data["scaler"]
        self.features       = data["features"]
        self._background    = data["background"]
        self.is_trained     = True
        self.explainer      = shap.Explainer(
            self.model.predict,
            self._background,
            feature_names=self.features
        )


if __name__ == "__main__":
    from signals.feature_engineering import build_feature_matrix
    print("=" * 50)
    print("Training Cognitive Load Model")
    print("=" * 50)
    df      = build_feature_matrix()
    model   = CognitiveLoadModel()
    metrics = model.train(df)
    model.save()
    print("\nMetrics:", metrics)