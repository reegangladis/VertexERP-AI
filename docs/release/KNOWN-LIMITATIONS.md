# VertexERP AI V2 — Known Limitations & Operational Constraints

---

## 1. Known Architectural Invariants & Constraints

1. **PostgreSQL RLS Support**:
   - PostgreSQL 16+ is required for Row-Level Security (RLS) policies using `current_setting('app.current_tenant_id')`.
   - SQLite in-memory databases used for local unit tests emulate RLS via application-layer filtering; production and staging strictly require real PostgreSQL.

2. **Vector Dimension Alignment**:
   - The native pgvector embedding dimension is fixed to 1536 (OpenAI `text-embedding-3-small` / `text-embedding-ada-002` standard). Custom embedding models with different dimensions require a corresponding migration to alter `rag_document_chunks.embedding`.

3. **Rate Limiting Defaults**:
   - Default rate limits are configured for enterprise stability (500/min auth, 300/min AI, 1000/min general). High-throughput automated partner integrations must supply designated API keys configured in tenant integration profiles.

4. **Multi-Currency Transactions**:
   - System standardizes base currency conversions at the transaction level using `exchange_rate` snapshots. Real-time forex feed sync is scheduled daily via the background worker.
