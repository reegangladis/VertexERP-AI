"""Enterprise-Grade Prometheus & OpenTelemetry Compatible Metrics Registry for VertexERP AI V2."""

from __future__ import annotations

import threading
import time
from collections import defaultdict
from typing import Any

from app.core.config import settings


class MetricLabelKey:
    """Helper to serialize label dictionaries to deterministic string tuples."""

    @staticmethod
    def to_key(labels: dict[str, str] | None) -> tuple[tuple[str, str], ...]:
        if not labels:
            return ()
        return tuple(sorted((str(k), str(v)) for k, v in labels.items()))

    @staticmethod
    def format_labels(labels_tuple: tuple[tuple[str, str], ...]) -> str:
        if not labels_tuple:
            return ""
        items = [f'{k}="{v}"' for k, v in labels_tuple]
        return "{" + ",".join(items) + "}"


class Counter:
    """Thread-safe monotonic counter metric."""

    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description
        self._values: dict[tuple[tuple[str, str], ...], float] = defaultdict(float)
        self._lock = threading.Lock()

    def inc(self, amount: float = 1.0, labels: dict[str, str] | None = None) -> None:
        if amount < 0:
            raise ValueError("Counter increments must be non-negative.")
        key = MetricLabelKey.to_key(labels)
        with self._lock:
            self._values[key] += amount

    def get_value(self, labels: dict[str, str] | None = None) -> float:
        key = MetricLabelKey.to_key(labels)
        with self._lock:
            return self._values.get(key, 0.0)

    def to_prometheus_lines(self) -> list[str]:
        lines = [
            f"# HELP {self.name} {self.description}",
            f"# TYPE {self.name} counter",
        ]
        with self._lock:
            if not self._values:
                lines.append(f"{self.name} 0")
            for labels_tuple, val in sorted(self._values.items()):
                label_str = MetricLabelKey.format_labels(labels_tuple)
                lines.append(f"{self.name}{label_str} {val}")
        return lines


class Gauge:
    """Thread-safe gauge representing an instantaneous value."""

    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description
        self._values: dict[tuple[tuple[str, str], ...], float] = defaultdict(float)
        self._lock = threading.Lock()

    def set(self, value: float, labels: dict[str, str] | None = None) -> None:
        key = MetricLabelKey.to_key(labels)
        with self._lock:
            self._values[key] = float(value)

    def inc(self, amount: float = 1.0, labels: dict[str, str] | None = None) -> None:
        key = MetricLabelKey.to_key(labels)
        with self._lock:
            self._values[key] += amount

    def dec(self, amount: float = 1.0, labels: dict[str, str] | None = None) -> None:
        key = MetricLabelKey.to_key(labels)
        with self._lock:
            self._values[key] -= amount

    def get_value(self, labels: dict[str, str] | None = None) -> float:
        key = MetricLabelKey.to_key(labels)
        with self._lock:
            return self._values.get(key, 0.0)

    def to_prometheus_lines(self) -> list[str]:
        lines = [
            f"# HELP {self.name} {self.description}",
            f"# TYPE {self.name} gauge",
        ]
        with self._lock:
            if not self._values:
                lines.append(f"{self.name} 0")
            for labels_tuple, val in sorted(self._values.items()):
                label_str = MetricLabelKey.format_labels(labels_tuple)
                lines.append(f"{self.name}{label_str} {val}")
        return lines


class Histogram:
    """Thread-safe histogram tracking value distribution into cumulative buckets."""

    DEFAULT_BUCKETS = (0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 10.0)

    def __init__(
        self,
        name: str,
        description: str,
        buckets: tuple[float, ...] = DEFAULT_BUCKETS,
    ) -> None:
        self.name = name
        self.description = description
        self.buckets = sorted(buckets) + [float("inf")]
        self._counts: dict[tuple[tuple[str, str], ...], int] = defaultdict(int)
        self._sums: dict[tuple[tuple[str, str], ...], float] = defaultdict(float)
        self._bucket_counts: dict[tuple[tuple[str, str], ...], dict[float, int]] = defaultdict(
            lambda: dict.fromkeys(self.buckets, 0)
        )
        self._lock = threading.Lock()

    def observe(self, value: float, labels: dict[str, str] | None = None) -> None:
        key = MetricLabelKey.to_key(labels)
        with self._lock:
            self._counts[key] += 1
            self._sums[key] += value
            b_map = self._bucket_counts[key]
            for b in self.buckets:
                if value <= b:
                    b_map[b] += 1

    def to_prometheus_lines(self) -> list[str]:
        lines = [
            f"# HELP {self.name} {self.description}",
            f"# TYPE {self.name} histogram",
        ]
        with self._lock:
            for key, b_map in sorted(self._bucket_counts.items()):
                base_labels = dict(key)
                for b in self.buckets:
                    le_str = "+Inf" if b == float("inf") else str(b)
                    b_labels = dict(base_labels)
                    b_labels["le"] = le_str
                    label_str = MetricLabelKey.format_labels(MetricLabelKey.to_key(b_labels))
                    lines.append(f"{self.name}_bucket{label_str} {b_map[b]}")

                base_label_str = MetricLabelKey.format_labels(key)
                lines.append(f"{self.name}_sum{base_label_str} {self._sums[key]}")
                lines.append(f"{self.name}_count{base_label_str} {self._counts[key]}")
        return lines


class AppMetricsRegistry:
    """Central registry maintaining all domain metric collectors."""

    def __init__(self) -> None:
        # 1. HTTP Server Metrics
        self.http_requests_total = Counter(
            "http_requests_total",
            "Total count of HTTP requests processed by the application.",
        )
        self.http_request_duration_seconds = Histogram(
            "http_request_duration_seconds",
            "HTTP request latency execution duration in seconds.",
        )
        self.http_requests_in_progress = Gauge(
            "http_requests_in_progress",
            "Current count of active in-flight HTTP requests.",
        )

        # 2. Database Connection & Query Metrics
        self.db_query_duration_seconds = Histogram(
            "db_query_duration_seconds",
            "Database query execution latency in seconds.",
            buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5),
        )
        self.db_pool_size = Gauge("db_pool_size", "Configured database connection pool size.")
        self.db_pool_checked_out = Gauge(
            "db_pool_checked_out", "Number of database connections currently in use."
        )
        self.db_pool_overflow = Gauge(
            "db_pool_overflow", "Number of database connections opened beyond base pool."
        )
        self.db_query_errors_total = Counter(
            "db_query_errors_total", "Total database query failures and timeout exceptions."
        )

        # 3. Background Job & Worker Metrics
        self.worker_jobs_processed_total = Counter(
            "worker_jobs_processed_total", "Total background jobs processed by workers."
        )
        self.worker_job_duration_seconds = Histogram(
            "worker_job_duration_seconds",
            "Background job processing execution duration in seconds.",
            buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, 15.0, 30.0, 60.0),
        )
        self.worker_queue_depth = Gauge(
            "worker_queue_depth", "Instantaneous depth of background job queue."
        )
        self.worker_active_threads = Gauge(
            "worker_active_threads", "Count of actively executing background worker threads."
        )
        self.worker_job_retries_total = Counter(
            "worker_job_retries_total", "Total count of background job retries triggered."
        )
        self.worker_dead_letter_total = Counter(
            "worker_dead_letter_total", "Total jobs routed to Dead Letter Queue (DLQ)."
        )

        # 4. AI Copilot & Gateway Telemetry
        self.ai_requests_total = Counter(
            "ai_requests_total", "Total AI completion and embedding requests."
        )
        self.ai_request_duration_seconds = Histogram(
            "ai_request_duration_seconds",
            "AI gateway inference latency in seconds.",
            buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0),
        )
        self.ai_tokens_consumed_total = Counter(
            "ai_tokens_consumed_total", "Total LLM tokens consumed."
        )
        self.ai_cost_estimated_usd_total = Counter(
            "ai_cost_estimated_usd_total", "Estimated cumulative AI API spend in USD."
        )
        self.ai_guardrail_blocks_total = Counter(
            "ai_guardrail_blocks_total",
            "Total prompt injection or security guardrail violations blocked.",
        )
        self.ai_rag_retrieval_duration_seconds = Histogram(
            "ai_rag_retrieval_duration_seconds",
            "RAG hybrid document vector retrieval latency in seconds.",
        )

        # 5. Application Errors & Invariants
        self.app_errors_total = Counter(
            "app_errors_total", "Total application exceptions and RFC 7807 problem responses."
        )

    def generate_prometheus_text(self) -> str:
        """Renders complete Prometheus exposition text format (0.0.4)."""
        lines: list[str] = [
            "# VertexERP AI V2 Prometheus Metrics Export",
            f"# Environment: {settings.APP_ENV.value} | Version: {settings.APP_VERSION}",
            "",
        ]

        collectors = [
            self.http_requests_total,
            self.http_request_duration_seconds,
            self.http_requests_in_progress,
            self.db_query_duration_seconds,
            self.db_pool_size,
            self.db_pool_checked_out,
            self.db_pool_overflow,
            self.db_query_errors_total,
            self.worker_jobs_processed_total,
            self.worker_job_duration_seconds,
            self.worker_queue_depth,
            self.worker_active_threads,
            self.worker_job_retries_total,
            self.worker_dead_letter_total,
            self.ai_requests_total,
            self.ai_request_duration_seconds,
            self.ai_tokens_consumed_total,
            self.ai_cost_estimated_usd_total,
            self.ai_guardrail_blocks_total,
            self.ai_rag_retrieval_duration_seconds,
            self.app_errors_total,
        ]

        for collector in collectors:
            lines.extend(collector.to_prometheus_lines())
            lines.append("")

        return "\n".join(lines) + "\n"

    def get_snapshot_json(self) -> dict[str, Any]:
        """Provides a structured JSON summary snapshot of key metrics."""
        return {
            "app_version": settings.APP_VERSION,
            "environment": settings.APP_ENV.value,
            "timestamp": time.time(),
            "http": {
                "active_requests": self.http_requests_in_progress.get_value(),
            },
            "database": {
                "pool_size": self.db_pool_size.get_value(),
                "checked_out": self.db_pool_checked_out.get_value(),
                "overflow": self.db_pool_overflow.get_value(),
            },
            "workers": {
                "queue_depth": self.worker_queue_depth.get_value(),
                "active_workers": self.worker_active_threads.get_value(),
            },
        }


# Global Metrics Registry Singleton
metrics_registry = AppMetricsRegistry()
