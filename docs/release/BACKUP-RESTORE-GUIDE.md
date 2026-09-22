# VertexERP AI V2 — Backup & Disaster Recovery Guide

---

## 1. Backup Engine Overview
The VertexERP AI V2 Backup System provides:
- **AES-256-CBC Encryption**: Backups are encrypted at rest with high-entropy cryptographic keys.
- **HMAC-SHA256 Manifest Signing**: Tamper detection verifies signature before restore execution.
- **GFS Retention Policy**: Grandfather-Father-Son retention automatically prunes old snapshots.

---

## 2. Generating Automated Encrypted Backups

```bash
# Execute full database backup
python -c "
import asyncio
from app.core.backup import BackupService

async def run_backup():
    svc = BackupService()
    manifest = await svc.create_backup(backup_type='full', description='Automated nightly backup')
    print('Backup completed successfully. Manifest ID:', manifest.backup_id)

asyncio.run(run_backup())
"
```

---

## 3. Restoring from Encrypted Backup

```bash
# Execute restore with integrity verification
python -c "
import asyncio
from app.core.backup import BackupService

async def run_restore(backup_id: str):
    svc = BackupService()
    result = await svc.restore_backup(backup_id=backup_id)
    print('Restore verification result:', result)

asyncio.run(run_restore('<BACKUP_ID>'))
"
```

---

## 4. Disaster Recovery Targets
- **Recovery Point Objective (RPO)**: < 15 minutes (with automated WAL streaming)
- **Recovery Time Objective (RTO)**: < 60 minutes
- **Restore Verification**: Automated weekly drill in isolated environment
