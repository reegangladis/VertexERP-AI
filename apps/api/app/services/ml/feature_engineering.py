import math
from typing import Any


class CategoricalEncoder:
    """Encoder for categorical variables using One-Hot, Ordinal, or Target Encoding."""

    @staticmethod
    def one_hot_encode(data: list[dict[str, Any]], column: str) -> list[dict[str, Any]]:
        categories = sorted(
            list(
                {
                    str(row[column])
                    for row in data
                    if column in row and row[column] is not None
                }
            )
        )
        encoded_data = []
        for row in data:
            new_row = row.copy()
            val = str(row.get(column))
            for cat in categories:
                new_row[f"{column}_{cat}"] = 1.0 if val == cat else 0.0
            encoded_data.append(new_row)
        return encoded_data

    @staticmethod
    def ordinal_encode(
        data: list[dict[str, Any]],
        column: str,
        mapping: dict[str, int] | None = None,
    ) -> list[dict[str, Any]]:
        if not mapping:
            categories = sorted(
                list(
                    {
                        str(row[column])
                        for row in data
                        if column in row and row[column] is not None
                    }
                )
            )
            mapping = {cat: i for i, cat in enumerate(categories)}

        encoded_data = []
        for row in data:
            new_row = row.copy()
            val = str(row.get(column))
            new_row[f"{column}_ordinal"] = mapping.get(val, 0)
            encoded_data.append(new_row)
        return encoded_data


class DataScaler:
    """Feature scaler for StandardScaler, MinMaxScaler, and RobustScaler."""

    @staticmethod
    def standard_scaler(values: list[float]) -> list[float]:
        if not values:
            return []
        n = len(values)
        mean = sum(values) / n
        variance = sum((x - mean) ** 2 for x in values) / (n if n > 1 else 1)
        std_dev = math.sqrt(variance) if variance > 0 else 1.0
        return [(x - mean) / std_dev for x in values]

    @staticmethod
    def min_max_scaler(
        values: list[float], min_val: float = 0.0, max_val: float = 1.0
    ) -> list[float]:
        if not values:
            return []
        val_min = min(values)
        val_max = max(values)
        rng = val_max - val_min if val_max != val_min else 1.0
        return [min_val + ((x - val_min) / rng) * (max_val - min_val) for x in values]

    @staticmethod
    def robust_scaler(values: list[float]) -> list[float]:
        if not values:
            return []
        sorted_vals = sorted(values)
        n = len(sorted_vals)
        median = sorted_vals[n // 2]
        q25 = sorted_vals[n // 4]
        q75 = sorted_vals[(3 * n) // 4]
        iqr = q75 - q25 if q75 != q25 else 1.0
        return [(x - median) / iqr for x in values]


class OutlierHandler:
    """Outlier detector and handler using IQR truncation or Z-Score clipping."""

    @staticmethod
    def handle_iqr(values: list[float], factor: float = 1.5) -> list[float]:
        if len(values) < 4:
            return values
        sorted_vals = sorted(values)
        n = len(sorted_vals)
        q25 = sorted_vals[n // 4]
        q75 = sorted_vals[(3 * n) // 4]
        iqr = q75 - q25
        lower_bound = q25 - factor * iqr
        upper_bound = q75 + factor * iqr
        return [max(lower_bound, min(upper_bound, x)) for x in values]

    @staticmethod
    def handle_zscore(values: list[float], threshold: float = 3.0) -> list[float]:
        if not values:
            return []
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = math.sqrt(variance) if variance > 0 else 1.0

        lower_bound = mean - threshold * std_dev
        upper_bound = mean + threshold * std_dev
        return [max(lower_bound, min(upper_bound, x)) for x in values]


class MissingValueHandler:
    """Missing value imputation handler for numerical and categorical features."""

    @staticmethod
    def impute_numerical(
        values: list[float | None], strategy: str = "mean", fill_value: float = 0.0
    ) -> list[float]:
        valid_vals = [v for v in values if v is not None and not math.isnan(v)]
        if not valid_vals:
            return [fill_value] * len(values)

        if strategy == "mean":
            impute_val = sum(valid_vals) / len(valid_vals)
        elif strategy == "median":
            sorted_vals = sorted(valid_vals)
            impute_val = sorted_vals[len(sorted_vals) // 2]
        elif strategy == "mode":
            counts: dict[float, int] = {}
            for v in valid_vals:
                counts[v] = counts.get(v, 0) + 1
            impute_val = max(counts, key=counts.get)  # type: ignore
        else:
            impute_val = fill_value

        return [
            v if (v is not None and not math.isnan(v)) else impute_val for v in values
        ]


class FeatureSelector:
    """Feature selection pipeline transformer based on variance threshold and correlation filtering."""

    @staticmethod
    def filter_low_variance(
        data: list[dict[str, float]], threshold: float = 0.01
    ) -> list[str]:
        if not data:
            return []
        features = list(data[0].keys())
        selected_features = []

        for feat in features:
            vals = [row.get(feat, 0.0) for row in data]
            mean = sum(vals) / len(vals)
            var = sum((x - mean) ** 2 for x in vals) / len(vals)
            if var >= threshold:
                selected_features.append(feat)

        return selected_features


class FeaturePipeline:
    """Reusable feature engineering pipeline orchestrator."""

    def __init__(self, steps: list[dict[str, Any]]):
        self.steps = steps

    def fit_transform(self, data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        processed_data = [row.copy() for row in data]
        for step in self.steps:
            action = step.get("action")
            column = step.get("column")
            if action == "one_hot" and column:
                processed_data = CategoricalEncoder.one_hot_encode(
                    processed_data, column
                )
            elif action == "impute" and column:
                strategy = step.get("strategy", "mean")
                vals = [row.get(column) for row in processed_data]
                imputed = MissingValueHandler.impute_numerical(vals, strategy=strategy)
                for idx, row in enumerate(processed_data):
                    row[column] = imputed[idx]
            elif action == "scale" and column:
                vals = [float(row.get(column, 0.0)) for row in processed_data]
                scaled = DataScaler.min_max_scaler(vals)
                for idx, row in enumerate(processed_data):
                    row[f"{column}_scaled"] = scaled[idx]
        return processed_data
