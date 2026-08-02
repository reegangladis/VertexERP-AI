import random
import time
from collections.abc import Callable
from typing import Any


class CircuitBreakerOpenException(Exception):
    """Exception raised when Circuit Breaker is in OPEN state."""

    pass


class CircuitBreaker:
    """Enterprise Circuit Breaker pattern (Closed, Open, Half-Open states)."""

    def __init__(
        self, failure_threshold: int = 5, recovery_timeout_seconds: float = 30.0
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout_seconds = recovery_timeout_seconds
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.failure_count = 0
        self.last_failure_time = 0.0

    def call(self, func: Callable, *args, **kwargs) -> Any:
        now = time.time()

        if self.state == "OPEN":
            if now - self.last_failure_time > self.recovery_timeout_seconds:
                self.state = "HALF_OPEN"
            else:
                raise CircuitBreakerOpenException(
                    "Circuit Breaker is OPEN. Request rejected to prevent cascading failure."
                )

        try:
            result = func(*args, **kwargs)
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
            return result
        except Exception as ex:
            self.failure_count += 1
            self.last_failure_time = now
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
            raise ex


class Bulkhead:
    """Enterprise Bulkhead Pattern limiting max concurrent executions for a resource pool."""

    def __init__(self, max_concurrent_calls: int = 20):
        self.max_concurrent_calls = max_concurrent_calls
        self.current_calls = 0

    def __enter__(self):
        if self.current_calls >= self.max_concurrent_calls:
            raise RuntimeError(
                "Bulkhead capacity reached. Request rejected to isolate resource pool."
            )
        self.current_calls += 1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.current_calls = max(0, self.current_calls - 1)


class ResilienceEngine:
    """Unified High Availability Engine with Circuit Breakers, Bulkheads, Retries with Jitter, and Fallbacks."""

    def __init__(self):
        self.circuit_breakers: dict[str, CircuitBreaker] = {}
        self.bulkheads: dict[str, Bulkhead] = {}

    def get_circuit_breaker(self, resource_name: str) -> CircuitBreaker:
        if resource_name not in self.circuit_breakers:
            self.circuit_breakers[resource_name] = CircuitBreaker()
        return self.circuit_breakers[resource_name]

    def get_bulkhead(self, resource_name: str, capacity: int = 20) -> Bulkhead:
        if resource_name not in self.bulkheads:
            self.bulkheads[resource_name] = Bulkhead(max_concurrent_calls=capacity)
        return self.bulkheads[resource_name]

    @staticmethod
    def execute_retry_with_jitter(
        func: Callable,
        max_retries: int = 3,
        base_delay: float = 0.5,
        max_delay: float = 5.0,
    ) -> Any:
        """Executes function with exponential backoff and randomized full jitter."""
        for attempt in range(1, max_retries + 1):
            try:
                return func()
            except Exception as ex:
                if attempt == max_retries:
                    raise ex
                # Full jitter calculation
                backoff = min(max_delay, base_delay * (2 ** (attempt - 1)))
                jittered_delay = random.uniform(0, backoff)
                time.sleep(jittered_delay)

    @staticmethod
    def execute_with_fallback(
        func: Callable, fallback_func: Callable, *args, **kwargs
    ) -> Any:
        """Executes primary function and triggers fallback handler on failure."""
        try:
            return func(*args, **kwargs)
        except Exception:
            return fallback_func(*args, **kwargs)
