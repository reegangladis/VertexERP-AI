import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ml import MLModel, ModelVersion
from app.repositories.ml_repository import MLRepository
from app.schemas.ml import MLModelCreate, ModelVersionCreate, ModelVersionApprove


class ModelRegistryService:
    """Service handling Model Registry, Semantic Versioning, Model Metadata, and Approval Lifecycles."""

    def __init__(self, db: AsyncSession):
        self.repo = MLRepository(db)

    async def register_model(self, organization_id: uuid.UUID, data: MLModelCreate) -> MLModel:
        model = MLModel(
            organization_id=organization_id,
            model_code=data.model_code,
            name=data.name,
            description=data.description,
            model_type=data.model_type,
            ml_framework=data.ml_framework,
            business_domain=data.business_domain,
            target_column=data.target_column,
            feature_names=data.feature_names,
            status="ACTIVE",
            metadata_json=data.metadata_json or {},
        )
        return await self.repo.create_model(model)

    async def get_registered_models(self, organization_id: uuid.UUID) -> List[MLModel]:
        return await self.repo.get_models(organization_id)

    async def get_model_by_id(self, model_id: uuid.UUID) -> Optional[MLModel]:
        return await self.repo.get_model_by_id(model_id)

    async def create_model_version(self, model_id: uuid.UUID, data: ModelVersionCreate) -> ModelVersion:
        version = ModelVersion(
            model_id=model_id,
            version=data.version,
            status="CANDIDATE",
            hyperparameters=data.hyperparameters or {},
            metrics_json=data.metrics_json or {},
            artifact_path=data.artifact_path or f"s3://vertex-ml-registry/{model_id}/{data.version}/model.bin",
            approval_status="PENDING",
        )
        return await self.repo.create_model_version(version)

    async def approve_model_version(self, version_id: uuid.UUID, approve_data: ModelVersionApprove) -> Optional[ModelVersion]:
        """Approval Workflow Placeholder supporting production promotion."""
        return await self.repo.update_version_status(
            version_id=version_id,
            status="PRODUCTION",
            approval_status="APPROVED",
            approved_by=approve_data.approved_by,
        )

    async def promote_version_stage(self, version_id: uuid.UUID, target_stage: str) -> Optional[ModelVersion]:
        """Transitions version lifecycle stage (STAGING, PRODUCTION, ARCHIVED)."""
        return await self.repo.update_version_status(
            version_id=version_id,
            status=target_stage.upper(),
            approval_status="APPROVED",
        )
