"""Unit tests for Database Backup, Encryption, Checksum Verification, Restore, and GFS Retention."""

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from scripts.backup_database import create_backup, generate_encryption_key
from scripts.prune_backups import evaluate_gfs_retention, prune_backup_directory
from scripts.restore_database import mark_backup_verified, verify_and_decrypt_backup


@pytest.fixture
def backup_dir(tmp_path: Path) -> Path:
    b_dir = tmp_path / "backups_test"
    b_dir.mkdir(parents=True, exist_ok=True)
    return b_dir


def test_backup_creation_and_manifest_generation(backup_dir: Path):
    """Verify unencrypted backup creates archive and manifest with correct checksum."""
    sample_sql = b"-- VertexERP SQL Dump\nCREATE TABLE test (id INT);\nINSERT INTO test VALUES (1);"
    manifest = create_backup(
        output_dir=backup_dir,
        database_name="vertexerp_test",
        synthetic_payload=sample_sql,
    )

    assert manifest["status"] == "PENDING_VERIFICATION"
    assert manifest["encrypted"] is False
    assert manifest["unencrypted_size_bytes"] == len(sample_sql)

    manifest_file = backup_dir / f"{manifest['backup_id']}.manifest.json"
    assert manifest_file.exists()

    # Verify and decrypt
    verified_manifest, raw_bytes = verify_and_decrypt_backup(manifest_file)
    assert raw_bytes == sample_sql
    assert verified_manifest["backup_id"] == manifest["backup_id"]


def test_backup_aes256_encryption_and_decryption(backup_dir: Path):
    """Verify AES-256-GCM encryption and exact plaintext recovery."""
    sample_data = b"CRITICAL_FINANCIAL_LEDGER_DATA_DEBITS_259900_CREDITS_259900"
    enc_key = generate_encryption_key()

    manifest = create_backup(
        output_dir=backup_dir,
        database_name="vertexerp_prod",
        encryption_key=enc_key,
        synthetic_payload=sample_data,
    )

    assert manifest["encrypted"] is True
    assert manifest["nonce_hex"] is not None

    archive_file = backup_dir / manifest["archive_file"]
    assert archive_file.exists()
    encrypted_bytes = archive_file.read_bytes()
    assert encrypted_bytes != sample_data  # Ciphertext must differ from plaintext

    manifest_file = backup_dir / f"{manifest['backup_id']}.manifest.json"
    _, decrypted_bytes = verify_and_decrypt_backup(manifest_file, encryption_key=enc_key)
    assert decrypted_bytes == sample_data

    # Update to verified
    updated_manifest = mark_backup_verified(manifest_file)
    assert updated_manifest["status"] == "RESTORE_VERIFIED"
    assert updated_manifest["verified_at"] is not None


def test_backup_tamper_detection_fails_closed(backup_dir: Path):
    """Verify that any modification to backup file or manifest fails closed."""
    sample_data = b"INTEGRITY_SENSITIVE_DATA"
    enc_key = generate_encryption_key()

    manifest = create_backup(
        output_dir=backup_dir,
        encryption_key=enc_key,
        synthetic_payload=sample_data,
    )

    archive_file = backup_dir / manifest["archive_file"]
    manifest_file = backup_dir / f"{manifest['backup_id']}.manifest.json"

    # Corrupt one byte of the archive
    corrupted_bytes = bytearray(archive_file.read_bytes())
    corrupted_bytes[0] ^= 0xFF
    archive_file.write_bytes(bytes(corrupted_bytes))

    with pytest.raises(ValueError, match="SECURITY ALERT: Archive checksum mismatch"):
        verify_and_decrypt_backup(manifest_file, encryption_key=enc_key)


def test_gfs_retention_pruning_policy(backup_dir: Path):
    """Verify Grandfather-Father-Son retention correctly partitions retained vs expired archives."""
    base_time = datetime(2026, 9, 11, 12, 0, 0, tzinfo=UTC)
    manifests = []

    # Generate synthetic manifests spanning various ages:
    # 1. Very recent (2h, 6h ago) -> 2 kept
    # 2. Daily tier (2d, 4d, 6d ago) -> 3 kept
    # 3. Weekly tier (2w, 3w ago) -> 2 kept
    # 4. Monthly tier (2m, 6m ago) -> 2 kept
    # 5. Yearly tier (2y, 4y ago) -> 2 kept
    # 6. Ancient expired (8y ago) -> expired
    offsets = [
        timedelta(hours=2),
        timedelta(hours=6),
        timedelta(days=2),
        timedelta(days=4),
        timedelta(days=6),
        timedelta(weeks=2),
        timedelta(weeks=3),
        timedelta(days=60),  # ~2 months
        timedelta(days=180),  # ~6 months
        timedelta(days=730),  # ~2 years
        timedelta(days=1460),  # ~4 years
        timedelta(days=3000),  # ~8.2 years (expired)
    ]

    for idx, delta in enumerate(offsets):
        created_time = base_time - delta
        b_id = f"bkp_synth_{idx}"
        m_data = {
            "backup_id": b_id,
            "archive_file": f"{b_id}.dump",
            "created_at": created_time.isoformat(),
        }
        m_file = backup_dir / f"{b_id}.manifest.json"
        m_file.write_text(json.dumps(m_data), encoding="utf-8")
        (backup_dir / f"{b_id}.dump").write_text("dummy")
        manifests.append((m_file, m_data))

    retained, expired = evaluate_gfs_retention(manifests, now=base_time)

    # 11 within retention criteria, 1 expired (> 7 years)
    assert len(retained) == 11
    assert len(expired) == 1

    # Run pruning simulation
    res = prune_backup_directory(backup_dir, dry_run=False, now=base_time)
    assert res["retained_count"] == 11
    assert res["expired_count"] == 1
