"""Grandfather-Father-Son (GFS) Backup Retention Pruner for VertexERP AI V2."""

from __future__ import annotations

import argparse
import json
import logging
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("vertexerp.retention")


def parse_manifest_date(manifest: dict[str, Any]) -> datetime:
    """Parses ISO 8601 UTC creation date from manifest."""
    dt_str = manifest.get("created_at")
    if not dt_str:
        return datetime.fromtimestamp(0, UTC)
    # Support 'Z' or '+00:00'
    dt_str = dt_str.replace("Z", "+00:00")
    return datetime.fromisoformat(dt_str)


def evaluate_gfs_retention(
    manifests: list[tuple[Path, dict[str, Any]]],
    now: datetime | None = None,
    keep_recent_hours: int = 24,
    keep_daily_days: int = 7,
    keep_weekly_weeks: int = 4,
    keep_monthly_months: int = 12,
    keep_yearly_years: int = 7,
) -> tuple[set[Path], set[Path]]:
    """
    Evaluates GFS retention rules across manifests.
    Returns: (retained_manifest_paths, expired_manifest_paths)
    """
    current_time = now or datetime.now(UTC)
    retained: set[Path] = set()

    # Sort manifests chronologically newest to oldest
    sorted_manifests = sorted(
        manifests, key=lambda item: parse_manifest_date(item[1]), reverse=True
    )

    daily_buckets: set[str] = set()
    weekly_buckets: set[str] = set()
    monthly_buckets: set[str] = set()
    yearly_buckets: set[str] = set()

    recent_cutoff = current_time - timedelta(hours=keep_recent_hours)
    daily_cutoff = current_time - timedelta(days=keep_daily_days)
    weekly_cutoff = current_time - timedelta(weeks=keep_weekly_weeks)
    monthly_cutoff = current_time - timedelta(days=keep_monthly_months * 30)
    yearly_cutoff = current_time - timedelta(days=keep_yearly_years * 365)

    for m_path, m_data in sorted_manifests:
        m_time = parse_manifest_date(m_data)

        # 1. Recent 24 hours: retain everything
        if m_time >= recent_cutoff:
            retained.add(m_path)
            continue

        # 2. Daily tier (last 7 days)
        day_key = m_time.strftime("%Y-%m-%d")
        if m_time >= daily_cutoff and day_key not in daily_buckets:
            daily_buckets.add(day_key)
            retained.add(m_path)
            continue

        # 3. Weekly tier (last 4 weeks)
        week_key = m_time.strftime("%Y-W%W")
        if m_time >= weekly_cutoff and week_key not in weekly_buckets:
            weekly_buckets.add(week_key)
            retained.add(m_path)
            continue

        # 4. Monthly tier (last 12 months)
        month_key = m_time.strftime("%Y-%m")
        if m_time >= monthly_cutoff and month_key not in monthly_buckets:
            monthly_buckets.add(month_key)
            retained.add(m_path)
            continue

        # 5. Yearly tier (up to 7 years)
        year_key = m_time.strftime("%Y")
        if m_time >= yearly_cutoff and year_key not in yearly_buckets:
            yearly_buckets.add(year_key)
            retained.add(m_path)
            continue

    all_paths = {p for p, _ in manifests}
    expired = all_paths - retained
    return retained, expired


def prune_backup_directory(
    backup_dir: Path,
    dry_run: bool = True,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Scans backup directory and prunes expired archives according to GFS retention."""
    manifest_files = list(backup_dir.glob("*.manifest.json"))
    manifests: list[tuple[Path, dict[str, Any]]] = []

    for mf in manifest_files:
        try:
            data = json.loads(mf.read_text(encoding="utf-8"))
            manifests.append((mf, data))
        except Exception as e:
            logger.warning("Skipping invalid manifest %s: %s", mf, e)

    retained, expired = evaluate_gfs_retention(manifests, now=now)

    deleted_files: list[str] = []
    for exp_manifest in expired:
        try:
            data = json.loads(exp_manifest.read_text(encoding="utf-8"))
            archive_name = data.get("archive_file")
            if archive_name:
                archive_path = backup_dir / archive_name
                if archive_path.exists():
                    if not dry_run:
                        archive_path.unlink()
                    deleted_files.append(str(archive_path))

            if not dry_run:
                exp_manifest.unlink()
            deleted_files.append(str(exp_manifest))
        except Exception as e:
            logger.error("Error pruning backup %s: %s", exp_manifest, e)

    logger.info(
        "Pruning complete (dry_run=%s): %d total, %d retained, %d expired/deleted",
        dry_run,
        len(manifests),
        len(retained),
        len(expired),
    )
    return {
        "total_backups": len(manifests),
        "retained_count": len(retained),
        "expired_count": len(expired),
        "deleted_files": deleted_files,
        "dry_run": dry_run,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="VertexERP GFS Backup Retention Pruner")
    parser.add_argument(
        "--backup-dir", default="backups", help="Directory containing backup archives"
    )
    parser.add_argument(
        "--apply", action="store_true", help="Actually delete expired files (default is dry-run)"
    )

    args = parser.parse_args()
    backup_path = Path(args.backup_dir)
    prune_backup_directory(backup_path, dry_run=not args.apply)


if __name__ == "__main__":
    main()
