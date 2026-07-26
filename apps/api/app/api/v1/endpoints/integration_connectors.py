import uuid
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.repositories.integration_repository import IntegrationRepository
from app.services.connector_framework import ConnectorFrameworkRegistry
from app.services.secret_manager import SecretManagerService
from app.models.integration import Connector, ConnectorConfig, ConnectorLog, IntegrationAudit
from app.schemas.integration import (
    ConnectorCreate,
    ConnectorUpdate,
    ConnectorOut,
    ConnectorConfigCreate,
    ConnectorConfigOut,
    ConnectorLogOut,
    ConnectorExecuteRequest,
    ConnectorExecuteResponse,
)

router = APIRouter()
secret_mgr = SecretManagerService()
connector_registry = ConnectorFrameworkRegistry()


@router.get("/connectors", response_model=List[ConnectorOut])
async def list_connectors(
    category: Optional[str] = Query(None),
    provider: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
):
    """List registered connectors in the marketplace/registry."""
    repo = IntegrationRepository(db)
    return await repo.list_connectors(category=category, provider=provider, status=status_filter)


@router.post("/connectors", response_model=ConnectorOut, status_code=status.HTTP_201_CREATED)
async def create_connector(
    payload: ConnectorCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register a new enterprise connector in the registry."""
    repo = IntegrationRepository(db)
    connector = Connector(
        organization_id=payload.organization_id,
        name=payload.name,
        slug=payload.slug,
        category=payload.category,
        version=payload.version,
        description=payload.description,
        provider=payload.provider,
        auth_type=payload.auth_type,
        status=payload.status,
        icon_url=payload.icon_url,
        schema_definition=payload.schema_definition,
        supported_actions=payload.supported_actions,
        is_custom=payload.is_custom,
    )
    return await repo.create_connector(connector)


@router.post("/configs", response_model=ConnectorConfigOut, status_code=status.HTTP_201_CREATED)
async def create_connector_config(
    payload: ConnectorConfigCreate,
    db: AsyncSession = Depends(get_db),
):
    """Configure tenant credentials and endpoint for a connector (encrypts secrets)."""
    repo = IntegrationRepository(db)
    encrypted_creds = secret_mgr.encrypt_credentials(payload.credentials)

    config = ConnectorConfig(
        connector_id=payload.connector_id,
        name=payload.name,
        encrypted_credentials=encrypted_creds,
        endpoint_url=payload.endpoint_url,
        environment=payload.environment,
        settings=payload.settings,
    )
    saved_config = await repo.create_connector_config(config)

    # Audit log
    await repo.log_audit(
        IntegrationAudit(
            action="connector_configured",
            resource_type="connector_config",
            resource_id=str(saved_config.id),
            performed_by="system_admin",
            details={"connector_id": str(payload.connector_id), "name": payload.name},
        )
    )
    return saved_config


@router.get("/configs", response_model=List[ConnectorConfigOut])
async def list_connector_configs(db: AsyncSession = Depends(get_db)):
    """List configured tenant connectors."""
    repo = IntegrationRepository(db)
    return await repo.list_connector_configs()


@router.post("/execute", response_model=ConnectorExecuteResponse)
async def execute_connector_action(
    payload: ConnectorExecuteRequest,
    db: AsyncSession = Depends(get_db),
):
    """Executes an action against a configured pluggable connector."""
    repo = IntegrationRepository(db)
    config = await repo.get_connector_config(payload.config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Connector configuration not found")

    connector_meta = await repo.get_connector_by_id(config.connector_id)
    provider_slug = connector_meta.provider if connector_meta else "sap"

    connector_instance = connector_registry.get_connector(provider_slug)
    if not connector_instance:
        # Fallback to SAP mock execution
        connector_instance = connector_registry.get_connector("sap")

    result = connector_instance.execute_action(payload.action, payload.payload)

    # Log invocation
    await repo.create_connector_log(
        ConnectorLog(
            connector_id=config.connector_id,
            action=payload.action,
            status=result.status,
            latency_ms=result.latency_ms,
            records_processed=result.records_affected,
            response_snippet=result.data,
        )
    )
    return result
