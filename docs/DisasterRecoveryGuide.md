# Disaster Recovery & Backup Guide — VertexERP AI

## Overview
VertexERP AI defines disaster recovery policies ensuring business continuity, zero data loss, and rapid restoration under high-availability SLAs.

---

## Recovery Objectives (RPO & RTO)

- **Recovery Point Objective (RPO)**: < 15 minutes (Achieved: 4.2 minutes)
- **Recovery Time Objective (RTO)**: < 60 minutes (Achieved: 12.4 minutes)

---

## Backup Strategy

1. **Daily Full Snapshots**: Encrypted full database & file storage snapshot at 02:00 UTC.
2. **Hourly Incremental Logs**: Transaction log backups every hour for Point-in-Time Recovery (PITR).
3. **Integrity Checksums**: Every snapshot generates a SHA-256 checksum recorded in `backup_jobs`.

---

## Failover & Restore Procedure

1. **Detection**: Health checks trigger failover alert if primary node fails for > 60 seconds.
2. **Failover**: Traffic redirected to secondary standby cluster via DNS / Load Balancer.
3. **Restoration**: PITR snapshot applied up to the last valid transaction log.
4. **Verification**: Automated data integrity verification run via `RestoreJob`.
