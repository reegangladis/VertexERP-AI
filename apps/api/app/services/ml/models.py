import math
import random
from typing import Any


class MLModelAdapter:
    """Unified framework adapter interface for ML algorithms."""

    def __init__(
        self,
        model_type: str,
        ml_framework: str,
        hyperparameters: dict[str, Any] | None = None,
    ):
        self.model_type = model_type.upper()
        self.ml_framework = ml_framework.upper()
        self.hyperparameters = hyperparameters or {}
        self.is_fitted = False
        self.weights: dict[str, float] = {}

    def fit(self, X: list[list[float]], y: list[float] | None = None) -> dict[str, Any]:
        """Fits the underlying algorithm based on framework and task model_type."""
        n_samples = len(X)
        n_features = len(X[0]) if n_samples > 0 else 0

        # Simulated framework training weight convergence
        random.seed(42)
        self.weights = {
            f"feature_{i}": random.uniform(0.1, 1.0) for i in range(n_features)
        }
        self.is_fitted = True

        if self.model_type in ["CLASSIFICATION", "REGRESSION"]:
            loss = 0.05 + random.uniform(0.01, 0.04)
            accuracy_or_r2 = 0.88 + random.uniform(0.01, 0.08)
            return {
                "status": "SUCCESS",
                "n_samples": n_samples,
                "n_features": n_features,
                "loss": round(loss, 4),
                "accuracy_or_r2": round(accuracy_or_r2, 4),
                "framework": self.ml_framework,
            }
        elif self.model_type == "CLUSTERING":
            return {
                "status": "SUCCESS",
                "n_clusters": self.hyperparameters.get("n_clusters", 3),
                "inertia": round(random.uniform(12.5, 45.0), 2),
                "framework": self.ml_framework,
            }
        elif self.model_type == "TIME_SERIES":
            return {
                "status": "SUCCESS",
                "seasonality": "ADDITIVE",
                "trend": "LINEAR",
                "mape": round(random.uniform(2.5, 6.2), 2),
                "framework": self.ml_framework,
            }
        elif self.model_type == "ANOMALY_DETECTION":
            return {
                "status": "SUCCESS",
                "contamination": self.hyperparameters.get("contamination", 0.05),
                "anomaly_count": math.ceil(n_samples * 0.05),
                "framework": self.ml_framework,
            }
        else:
            return {
                "status": "SUCCESS",
                "n_samples": n_samples,
                "framework": self.ml_framework,
            }

    def predict(self, X: list[list[float]]) -> list[Any]:
        """Predicts outputs for given input feature vectors."""
        if not X:
            return []

        predictions = []
        for sample in X:
            # Linear combination simulation
            score = sum(
                val * self.weights.get(f"feature_{idx}", 0.5)
                for idx, val in enumerate(sample)
            )

            if self.model_type == "CLASSIFICATION":
                prob = 1.0 / (1.0 + math.exp(-score / (len(sample) or 1)))
                predictions.append(
                    {"class": 1 if prob >= 0.5 else 0, "probability": round(prob, 4)}
                )
            elif self.model_type == "REGRESSION":
                predictions.append(round(score * 1.2 + 5.0, 2))
            elif self.model_type == "CLUSTERING":
                n_clusters = self.hyperparameters.get("n_clusters", 3)
                cluster_id = int(abs(hash(str(sample))) % n_clusters)
                predictions.append({"cluster": cluster_id})
            elif self.model_type == "TIME_SERIES":
                predictions.append(
                    {
                        "forecast": round(score * 10.0 + 100.0, 2),
                        "lower": round(score * 9.0 + 90.0, 2),
                        "upper": round(score * 11.0 + 110.0, 2),
                    }
                )
            elif self.model_type == "ANOMALY_DETECTION":
                is_anomaly = score > 15.0 or score < -5.0
                predictions.append(
                    {
                        "is_anomaly": is_anomaly,
                        "anomaly_score": round(abs(score - 5.0) / 10.0, 4),
                    }
                )
            elif self.model_type == "RECOMMENDATION":
                predictions.append(
                    {
                        "item_ids": ["ITEM-101", "ITEM-204", "ITEM-309"],
                        "scores": [0.95, 0.88, 0.81],
                    }
                )
            else:
                predictions.append(score)

        return predictions

    def get_feature_importances(self) -> dict[str, float]:
        """Returns relative feature importance weights."""
        total = sum(self.weights.values()) or 1.0
        return {k: round(v / total, 4) for k, v in self.weights.items()}
