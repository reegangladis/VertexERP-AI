"""Tests validating PostgreSQL RLS tenant context isolation and SQLite test compatibility."""

import uuid
import pytest
from sqlalchemy import text
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.infrastructure.database.session import (
    set_superuser_context,
    set_tenant_context,
)
from app.modules.identity.schemas.auth import RegisterRequest
from app.modules.identity.services.auth_service import AuthService


import os

@pytest.fixture
async def pg_session_factory():
    """Provides a dedicated NullPool async engine for the test function's event loop."""
    port = os.getenv("TEST_DATABASE_PORT", os.getenv("DATABASE_PORT", "5432"))
    url = f"postgresql+asyncpg://{settings.DATABASE_USER}:{settings.DATABASE_PASSWORD}@{settings.DATABASE_HOST}:{port}/{settings.DATABASE_NAME}"
    engine = create_async_engine(url, poolclass=NullPool)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    try:
        async with factory() as session:
            await session.execute(text("SELECT 1"))
    except Exception as exc:
        await engine.dispose()
        pytest.skip(f"PostgreSQL test instance unavailable: {exc}")
    yield factory
    await engine.dispose()


@pytest.mark.asyncio
async def test_tenant_context_set_and_isolation_sqlite(db_session: AsyncSession):
    """Verifies that set_tenant_context and set_superuser_context safely no-op on SQLite."""
    test_tenant_id = uuid.uuid4()
    # Should not raise any syntax error on SQLite
    await set_tenant_context(db_session, test_tenant_id)
    await set_superuser_context(db_session, True)
    await set_superuser_context(db_session, False)


@pytest.mark.asyncio
async def test_tenant_context_postgres_transaction_local(pg_session_factory):
    """
    Directly exercises PostgreSQL transaction-local tenant context semantics:
    1. set_tenant_context establishes app.current_tenant_id in the active transaction using bound parameters.
    2. A new transaction starts with an empty/unbound tenant context (no leakage across connections/transactions).
    """
    tenant_id_1 = uuid.uuid4()
    tenant_id_2 = uuid.uuid4()

    # Transaction 1: Set tenant_id_1
    async with pg_session_factory() as session1:
        await set_tenant_context(session1, tenant_id_1)
        res = await session1.execute(text("SELECT current_setting('app.current_tenant_id', true)"))
        val = res.scalar()
        assert val == str(tenant_id_1)

    # Transaction 2: Fresh session should have empty setting (no cross-transaction leak)
    async with pg_session_factory() as session2:
        res = await session2.execute(text("SELECT current_setting('app.current_tenant_id', true)"))
        val = res.scalar()
        assert val == "" or val is None

        # Set tenant_id_2
        await set_tenant_context(session2, tenant_id_2)
        res2 = await session2.execute(text("SELECT current_setting('app.current_tenant_id', true)"))
        val2 = res2.scalar()
        assert val2 == str(tenant_id_2)


@pytest.mark.asyncio
async def test_superuser_context_postgres_transaction_local(pg_session_factory):
    """Verifies superuser flag can be toggled transaction-locally on PostgreSQL."""
    async with pg_session_factory() as session:
        await set_superuser_context(session, True)
        res = await session.execute(text("SELECT current_setting('app.is_superuser', true)"))
        assert res.scalar() == "true"

        await set_superuser_context(session, False)
        res2 = await session.execute(text("SELECT current_setting('app.is_superuser', true)"))
        assert res2.scalar() == "false"


@pytest.mark.asyncio
async def test_postgres_registration_flow(pg_session_factory):
    """
    Executes registration flow directly against PostgreSQL ensuring:
    1. Tenant, Organization, Admin User, Credentials, and System Roles are provisioned.
    2. Zero syntax error at or near parameter binding ($1).
    3. Tenant context is properly set for the new tenant within the transaction.
    """
    unique_suffix = uuid.uuid4().hex[:8]
    slug = f"test-corp-{unique_suffix}"
    email = f"admin-{unique_suffix}@testcorp.com"

    req = RegisterRequest(
        email=email,
        password="ValidStrongPassword123!",
        full_name="Integration Test User",
        tenant_name=f"Test Corp {unique_suffix}",
        tenant_slug=slug,
        organization_name=f"Test HQ {unique_suffix}",
        tax_identifier=f"TAX-{unique_suffix}",
    )

    async with pg_session_factory() as session:
        async with session.begin():
            auth_service = AuthService(session=session)
            user, tenant, org, tokens = await auth_service.register(req)

            assert tenant.id is not None
            assert org.id is not None
            assert user.id is not None
            assert tokens.access_token is not None
            assert tokens.refresh_token is not None
            assert "TenantAdmin" in tokens.roles

            # Verify tenant context in current transaction matches created tenant
            res = await session.execute(text("SELECT current_setting('app.current_tenant_id', true)"))
            assert res.scalar() == str(tenant.id)
