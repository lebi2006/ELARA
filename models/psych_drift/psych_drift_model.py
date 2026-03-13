"""
ELARA — Psychological Drift Detection Model
Detects long-term emotional baseline shifts and
predicts Third-Quarter Syndrome risk.
"""

import numpy as np
import pandas as pd
import pickle
import shap
from pathlib import Path
from sklearn.ensemble         import RandomForestClassifier
from sklearn.model_selection  import train_test_split, cross_val_score
from sklearn.preprocessing    import StandardScaler, LabelEncoder
from sklearn.metrics          import classification_report, accuracy_score
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from signals.feature_engineering import PSYCH_DRIFT_FEATURES

MODEL_DIR = Path("models/psych_drift")


class PsychDriftModel:
    """
    Classifies astronaut psychological risk level:
    LOW / MODERATE / HIGH / CRITICAL
    and detects Third-Quarter Syndrome onset early.
    """

    def __init__(self):
        self.model  = RandomForestClassifier(
            n_estimators    = 300,
            max_depth       = 6,
            min_samples_leaf= 3,
            random_state    = 42,
            class_weight    = "balanced"
        )
        self.scaler     = StandardScaler()
        self.encoder    = LabelEncoder()
        self.explainer  = None
        self.features   = PSYCH_DRIFT_FEATURES
        self.is_trained = False

    def train(self, df: pd.DataFrame) -> dict:
        train_df = df[df["mission_day"] > 14].copy()

        X = train_df[self.features].fillna(0)
        y = self.encoder.fit_transform(train_df["risk_level"])

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        X_train_scaled  = self.scaler.fit_transform(X_train)
        self._background = X_train_scaled[:50]
        X_test_scaled   = self.scaler.transform(X_test)

        print("  Training Psychological Drift Model...")
        self.model.fit(X_train_scaled, y_train)

        y_pred      = self.model.predict(X_test_scaled)
        accuracy    = accuracy_score(y_test, y_pred)

        cv_scores = cross_val_score(
            self.model,
            self.scaler.transform(X),
            y,
            cv=5,
            scoring="accuracy"
        )

        print("  Building SHAP explainer...")
        self.explainer = shap.Explainer(
            self.model,
            self.scaler.transform(X_train),
            feature_names=self.features
        )

        self.is_trained = True

        print(f"  Accuracy: {round(accuracy, 3)}  |  CV Accuracy: {round(cv_scores.mean(), 3)} ± {round(cv_scores.std(), 3)}")
        print()
        print(classification_report(
            y_test, y_pred,
            target_names=self.encoder.classes_
        ))

        return {
            "accuracy"      : round(accuracy, 3),
            "cv_mean"       : round(cv_scores.mean(), 3),
            "cv_std"        : round(cv_scores.std(), 3),
            "classes"       : list(self.encoder.classes_),
        }

    def predict(self, features: dict) -> dict:
        if not self.is_trained:
            raise RuntimeError("Model not trained.")

        X           = pd.DataFrame([features])[self.features].fillna(0)
        X_scaled    = self.scaler.transform(X)

        pred_encoded    = self.model.predict(X_scaled)[0]
        risk_level      = self.encoder.inverse_transform([pred_encoded])[0]
        probabilities   = self.model.predict_proba(X_scaled)[0]

        prob_dict = {
            cls: round(float(prob), 3)
            for cls, prob in zip(self.encoder.classes_, probabilities)
        }

        # Feature importance explanation (fast, no per-request SHAP cost)
        explanation = {
            feat: round(float(self.model.feature_importances_[i]), 3)
            for i, feat in enumerate(self.features)
        }

        return {
            "risk_level"        : risk_level,
            "probabilities"     : prob_dict,
            "explanation"       : explanation,
            "top_contributors"  : sorted(
                explanation.items(),
                key=lambda x: abs(x[1]),
                reverse=True
            )[:3],
            "tqs_probability"   : round(
                prob_dict.get("HIGH", 0) + prob_dict.get("CRITICAL", 0), 3
            ),
        }

    def save(self):
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        with open(MODEL_DIR / "psych_drift_model.pkl", "wb") as f:
            pickle.dump({
                "model"         : self.model,
                "scaler"        : self.scaler,
                "encoder"       : self.encoder,
                "features"      : self.features,
                "background"    : self._background
            }, f)
        print(f"  Saved: models/psych_drift/psych_drift_model.pkl")

    def load(self):
        with open(MODEL_DIR / "psych_drift_model.pkl", "rb") as f:
            data = pickle.load(f)
        self.model          = data["model"]
        self.scaler         = data["scaler"]
        self.encoder        = data["encoder"]
        self.features       = data["features"]
        self._background    = data["background"]
        self.is_trained     = True
        self.explainer      = shap.Explainer(
            self.model,
            self._background,
            feature_names=self.features
        )


if __name__ == "__main__":
    from signals.feature_engineering import build_feature_matrix
    print("=" * 50)
    print("Training Psychological Drift Model")
    print("=" * 50)
    df      = build_feature_matrix()
    model   = PsychDriftModel()
    metrics = model.train(df)
    model.save()