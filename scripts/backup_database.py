"""Enterprise Database Backup & Encryption Utility for VertexERP AI V2."""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import secrets
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("vertexerp.backup")


def get_default_backup_dir() -> Path:
    return Path(os.getenv("BACKUP_DIR", "backups")).resolve()


def generate_encryption_key() -> bytes:
    """Generates a secure 256-bit key for AES-GCM encryption."""
    return AESGCM.generate_key(bit_length=256)


def calculate_sha256(data: bytes) -> str:
    """Calculates standard SHA-256 hexadecimal digest."""
    return hashlib.sha256(data).hexdigest()


def encrypt_payload(data: bytes, key: bytes) -> tuple[bytes, bytes]:
    """
    Encrypts raw backup bytes using AES-256-GCM.
    Returns: (encrypted_data, nonce)
    """
    aesgcm = AESGCM(key)
    nonce = secrets.token_bytes(12)  # Standard 96-bit nonce for GCM
    encrypted_bytes = aesgcm.encrypt(nonce, data, None)
    return encrypted_bytes, nonce


def execute_pg_dump(
    host: str = "localhost",
    port: int = 5432,
    user: str = "postgres",
    database: str = "vertexerp_v2",
    password: str | None = None,
) -> bytes:
    """Executes pg_dump command and returns compressed custom-format binary stream."""
    env = os.environ.copy()
    if password:
        env["PGPASSWORD"] = password

    cmd = [
        "pg_dump",
        "-h",
        host,
        "-p",
        str(port),
        "-U",
        user,
        "-F",
        "c",  # Custom format (compressed and suitable for pg_restore)
        "-b",  # Include large objects
        "-v",  # Verbose
        database,
    ]

    logger.info("Executing pg_dump for database '%s' at %s:%d...", database, host, port)
    proc = subprocess.run(cmd, capture_output=True, env=env)
    if proc.returncode != 0:
        err_msg = proc.stderr.decode("utf-8", errors="replace")
        raise RuntimeError(f"pg_dump failed with exit code {proc.returncode}: {err_msg}")

    return proc.stdout


def create_backup(
    output_dir: Path,
    database_name: str = "vertexerp_v2",
    host: str = "localhost",
    port: int = 5432,
    user: str = "postgres",
    password: str | None = None,
    encryption_key: bytes | None = None,
    synthetic_payload: bytes | None = None,
) -> dict[str, Any]:
    """
    Orchestrates backup generation, compression, integrity hashing, AES-256 encryption, and manifest writing.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp_str = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    backup_id = f"bkp_{timestamp_str}_{secrets.token_hex(4)}"

    # 1. Acquire backup payload (either real pg_dump or synthetic for test validation)
    if synthetic_payload is not None:
        raw_data = synthetic_payload
    else:
        raw_data = execute_pg_dump(
            host=host, port=port, user=user, database=database_name, password=password
        )

    unencrypted_checksum = calculate_sha256(raw_data)
    unencrypted_size = len(raw_data)

    # 2. Encrypt payload if key provided
    is_encrypted = False
    nonce_hex = None
    if encryption_key:
        final_payload, nonce = encrypt_payload(raw_data, encryption_key)
        is_encrypted = True
        nonce_hex = nonce.hex()
        file_ext = "dump.enc"
    else:
        final_payload = raw_data
        file_ext = "dump"

    final_checksum = calculate_sha256(final_payload)
    final_size = len(final_payload)

    # 3. Write archive file
    archive_filename = f"{backup_id}.{file_ext}"
    archive_path = output_dir / archive_filename
    archive_path.write_bytes(final_payload)

    # 4. Generate structured manifest
    manifest: dict[str, Any] = {
        "backup_id": backup_id,
        "archive_file": archive_filename,
        "database_name": database_name,
        "app_version": "2.0.0",
        "created_at": datetime.now(UTC).isoformat(),
        "unencrypted_size_bytes": unencrypted_size,
        "unencrypted_sha256": unencrypted_checksum,
        "archive_size_bytes": final_size,
        "archive_sha256": final_checksum,
        "encrypted": is_encrypted,
        "nonce_hex": nonce_hex,
        "status": "PENDING_VERIFICATION",
        "verified_at": None,
    }

    manifest_path = output_dir / f"{backup_id}.manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    logger.info(
        "Backup created successfully: id=%s, file=%s (%d bytes, sha256=%s, encrypted=%s)",
        backup_id,
        archive_filename,
        final_size,
        final_checksum[:12],
        is_encrypted,
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="VertexERP AI V2 Database Backup Utility")
    parser.add_argument(
        "--output-dir", default="backups", help="Directory to store backup artifacts"
    )
    parser.add_argument(
        "--database", default=os.getenv("DATABASE_NAME", "vertexerp_v2"), help="Database name"
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
    parser.add_argument("--encrypt", action="store_true", help="Enable AES-256-GCM encryption")
    parser.add_argument("--key", help="AES-256 Hex Key (32 bytes / 64 hex chars)")

    args = parser.parse_args()
    key_bytes = None
    if args.encrypt:
        if args.key:
            key_bytes = bytes.fromhex(args.key)
        else:
            key_bytes = generate_encryption_key()
            logger.info("Generated one-time AES-256 Key: %s", key_bytes.hex())

    out_path = Path(args.output_dir)
    password = os.getenv("DATABASE_PASSWORD")
    create_backup(
        output_dir=out_path,
        database_name=args.database,
        host=args.host,
        port=args.port,
        user=args.user,
        password=password,
        encryption_key=key_bytes,
    )


if __name__ == "__main__":
    main()
