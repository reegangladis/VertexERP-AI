from datetime import UTC, datetime


def utc_now() -> datetime:
    """Returns the current timezone-aware UTC datetime."""
    return datetime.now(UTC)


def format_iso(dt: datetime) -> str:
    """Formats a datetime as an ISO-8601 string in UTC."""
    # Ensure it is timezone-aware
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC).isoformat()


def parse_iso(val: str) -> datetime:
    """Parses an ISO-8601 string to a timezone-aware UTC datetime."""
    dt = datetime.fromisoformat(val)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def days_between(dt1: datetime, dt2: datetime) -> int:
    """Calculates the absolute difference in days between two datetimes."""
    return abs((dt1 - dt2).days)
