# Build Verification Record

This package was rebuilt from the supplied VertexERP-AI-v2 source archive.

## Checks executed in the build environment

- Python AST/bytecode compilation: **PASS**
- Source-reference scan for the old reference project: **PASS**
- Docker Compose YAML parsing for development, staging and production: **PASS**
- Frontend TypeScript `tsc --noEmit`: **PASS**

## Changes applied

1. Reworked PostgreSQL RLS migration 0013 to inspect the actual database schema and only create tenant policies on tables that really contain `tenant_id`.
2. Added safe tenant bootstrap context for registration and authentication bootstrap flows.
3. Added native pgvector storage/backfill and HNSW indexing in migration 0014.
4. Changed RAG indexing to persist native vectors and PostgreSQL retrieval to use pgvector cosine distance.
5. Replaced simulated object storage operations with real S3-compatible MinIO operations.
6. Added explicit storage configuration.
7. Changed Redis Stream acknowledgements to happen after job execution and added stale pending-message reclamation.
8. Ensured scheduled jobs are enqueued by the worker scheduler.
9. Added database migration ordering to development Compose and added the development frontend service.
10. Fixed production MinIO network reachability.
11. Fixed release CI Dockerfile references.
12. Made production security CI fail on audit findings instead of swallowing them.
13. Made development authentication cookies work over localhost HTTP while retaining Secure cookies in staging/production.
14. Removed generated environments/caches from the distributable archive.

## Runtime verification boundary

A full Docker/PostgreSQL/Redis/MinIO runtime test could not be executed in the build sandbox because Docker is not available there. Frontend dependencies in the supplied archive were platform-specific Windows packages, so the production Vite bundle was not executed in Linux.

The project is therefore packaged as a **release candidate with verified source/build configuration**, not as a claim of an externally deployed production system.

Run `RUNBOOK.md` on Windows with Docker Desktop to execute the complete runtime verification.
