"""0014_pgvector_hnsw_indexes

Revision ID: 0014_pgvector_hnsw_indexes
Revises: 0013_enforce_postgresql_rls
Create Date: 2026-09-13 12:15:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0014_pgvector_hnsw_indexes"
down_revision: str | None = "0013_enforce_postgresql_rls"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    # 1. Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # 2. Add native vector column to rag_document_chunks
    op.execute("ALTER TABLE rag_document_chunks ADD COLUMN IF NOT EXISTS embedding vector(1536);")

    # 3. Backfill native vectors from legacy JSONB embeddings.
    op.execute("""
        UPDATE rag_document_chunks
        SET embedding = embedding_json::text::vector
        WHERE embedding IS NULL
          AND embedding_json IS NOT NULL;
    """)

    # 4. Create high-performance HNSW index for cosine similarity search.
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_rag_chunks_vector_hnsw
        ON rag_document_chunks
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64);
    """)


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    op.execute("DROP INDEX IF EXISTS idx_rag_chunks_vector_hnsw;")
    op.execute("ALTER TABLE rag_document_chunks DROP COLUMN IF EXISTS embedding;")
