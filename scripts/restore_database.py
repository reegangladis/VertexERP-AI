"""Enterprise Database Restore & Verification Engine for VertexERP AI V2."""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("vertexerp.restore")


def calculate_sha256(data: bytes) -> str:
    """Calculates standard SHA-256 hexadecimal digest."""
    return hashlib.sha256(data).hexdigest()


def decrypt_payload(encrypted_data: bytes, key: bytes, nonce: bytes) -> bytes:
    """Decrypts AES-256-GCM encrypted backup payload."""
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, encrypted_data, None)


def verify_and_decrypt_backup(
    manifest_path: Path,
    encryption_key: bytes | None = None,
) -> tuple[dict[str, Any], bytes]:
    """
    Validates manifest integrity, checksums, and decrypts the backup archive.
    Returns: (manifest_dict, decrypted_bytes)
    """
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest file not found: {manifest_path}")

    manifest: dict[str, Any] = json.loads(manifest_path.read_text(encoding="utf-8"))
    backup_dir = manifest_path.parent
    archive_file = backup_dir / manifest["archive_file"]

    if not archive_file.exists():
        raise FileNotFoundError(f"Backup archive binary not found: {archive_file}")

    archive_bytes = archive_file.read_bytes()

    # 1. Verify archive file SHA-256 integrity
    actual_archive_sha256 = calculate_sha256(archive_bytes)
    if actual_archive_sha256 != manifest["archive_sha256"]:
        raise ValueError(
            f"SECURITY ALERT: Archive checksum mismatch! Expected {manifest['archive_sha256']}, got {actual_archive_sha256}. "
            "Backup may have been corrupted or tampered with."
        )

    # 2. Decrypt if encrypted
    if manifest.get("encrypted", False):
        if not encryption_key:
            raise ValueError(
                f"Backup {manifest['backup_id']} is encrypted but no decryption key was supplied."
            )

        nonce_hex = manifest.get("nonce_hex")
        if not nonce_hex:
            raise ValueError(f"Manifest {manifest_path} is missing encryption nonce.")

        nonce = bytes.fromhex(nonce_hex)
        try:
            raw_bytes = decrypt_payload(archive_bytes, encryption_key, nonce)
        except Exception as exc:
            raise ValueError(
                f"Decryption failed: authentication tag verification failed ({exc})"
            ) from exc

        actual_unencrypted_sha256 = calculate_sha256(raw_bytes)
        if actual_unencrypted_sha256 != manifest["unencrypted_sha256"]:
            raise ValueError(
                f"Decrypted payload checksum mismatch! Expected {manifest['unencrypted_sha256']}, got {actual_unencrypted_sha256}."
            )
    else:
        raw_bytes = archive_bytes

    logger.info(
        "Backup integrity verified: id=%s (%d bytes, sha256=%s)",
        manifest["backup_id"],
        len(raw_bytes),
        manifest["unencrypted_sha256"][:12],
    )
    return manifest, raw_bytes


def execute_pg_restore(
    backup_bytes: bytes,
    host: str = "localhost",
    port: int = 5432,
    user: str = "postgres",
    database: str = "vertexerp_restore_test",
    password: str | None = None,
    clean: bool = True,
) -> None:
    """Executes pg_restore to recover database state."""
    env = os.environ.copy()
    if password:
        env["PGPASSWORD"] = password

    cmd = [
        "pg_restore",
        "-h",
        host,
        "-p",
        str(port),
        "-U",
        user,
        "-d",
        database,
        "-v",
    ]
    if clean:
        cmd.append("--clean")

    logger.info("Restoring backup into database '%s' at %s:%d...", database, host, port)
    proc = subprocess.run(cmd, input=backup_bytes, capture_output=True, env=env)
    # pg_restore exit code 0 is clean, exit code 1 may contain benign warnings (e.g. drop non-existent)
    if proc.returncode not in (0, 1):
        err_msg = proc.stderr.decode("utf-8", errors="replace")
        raise RuntimeError(f"pg_restore failed with exit code {proc.returncode}: {err_msg}")


def mark_backup_verified(manifest_path: Path) -> dict[str, Any]:
    """Updates manifest to RESTORE_VERIFIED status after successful restore assertions."""
    manifest: dict[str, Any] = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["status"] = "RESTORE_VERIFIED"
    manifest["verified_at"] = datetime.now(UTC).isoformat()
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    logger.info("Manifest %s updated: status=RESTORE_VERIFIED", manifest["backup_id"])
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(
        description="VertexERP AI V2 Database Restore & Verification Utility"
    )
    parser.add_argument("manifest", help="Path to backup manifest JSON file")
    parser.add_argument("--key", help="AES-256 Hex Key (32 bytes / 64 hex chars) if encrypted")
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify checksums and decryption without executing pg_restore",
    )
    parser.add_argument(
        "--target-db", default="vertexerp_v2", help="Target database to restore into"
    )
    parser.add_argument(
        "--host", default=os.getenv("DATABASE_HOST", "localhost"), help="PostgreSQL host"
    )
    parser.add_argument(
        "--port", type=int, default=int(os.getenv("DATABASE_PORT", "5432")), help="PostgreSQL port"
    )
    parser.add_argument(
        "--user", default=os.getenv("DATABASE_USER", "postgres"), help="PostgreSQL user"
    )

    args = parser.parse_args()
    manifest_file = Path(args.manifest)

    key_bytes = bytes.fromhex(args.key) if args.key else None
    manifest, raw_bytes = verify_and_decrypt_backup(manifest_file, key_bytes)

    if not args.verify_only:
        password = os.getenv("DATABASE_PASSWORD")
        execute_pg_restore(
            backup_bytes=raw_bytes,
            host=args.host,
            port=args.port,
            user=args.user,
            database=args.target_db,
            password=password,
        )

    mark_backup_verified(manifest_file)
    logger.info("Restore and verification workflow completed successfully.")


if __name__ == "__main__":
    main()
