from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models.ml_studio import (
    DatasetRegistry,
    DatasetVersionModel,
    EvaluationReport,
    ExplainabilityReport,
    Notebook,
    RegisteredModel,
)


class MLStudioDatasetRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(
        self, organization_id: UUID, domain: str | None = None
    ) -> list[DatasetRegistry]:
        stmt = (
            select(DatasetRegistry)
            .options(selectinload(DatasetRegistry.versions))
            .where(DatasetRegistry.organization_id == organization_id)
        )
        if domain:
            stmt = stmt.where(DatasetRegistry.domain == domain)
        stmt = stmt.order_by(DatasetRegistry.created_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, dataset_id: UUID) -> DatasetRegistry | None:
        stmt = (
            select(DatasetRegistry)
            .options(selectinload(DatasetRegistry.versions))
            .where(DatasetRegistry.id == dataset_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, dataset: DatasetRegistry) -> DatasetRegistry:
        self.db.add(dataset)
        await self.db.commit()
        await self.db.refresh(dataset)
        return dataset

    async def add_version(
        self, version_model: DatasetVersionModel
    ) -> DatasetVersionModel:
        self.db.add(version_model)
        await self.db.commit()
        await self.db.refresh(version_model)
        return version_model


class MLStudioNotebookRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, organization_id: UUID) -> list[Notebook]:
        stmt = (
            select(Notebook)
            .where(Notebook.organization_id == organization_id)
            .order_by(Notebook.updated_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, notebook_id: UUID) -> Notebook | None:
        stmt = select(Notebook).where(Notebook.id == notebook_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, notebook: Notebook) -> Notebook:
        self.db.add(notebook)
        await self.db.commit()
        await self.db.refresh(notebook)
        return notebook

    async def update_status(
        self, notebook_id: UUID, status: str, logs: list[dict[str, Any]]
    ) -> Notebook | None:
        notebook = await self.get_by_id(notebook_id)
        if notebook:
            notebook.status = status
            notebook.execution_logs = logs
            await self.db.commit()
            await self.db.refresh(notebook)
        return notebook


class MLStudioModelRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(
        self, organization_id: UUID, stage: str | None = None
    ) -> list[RegisteredModel]:
        stmt = (
            select(RegisteredModel)
            .options(selectinload(RegisteredModel.artifacts))
            .where(RegisteredModel.organization_id == organization_id)
        )
        if stage:
            stmt = stmt.where(RegisteredModel.stage == stage)
        stmt = stmt.order_by(RegisteredModel.updated_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, model_id: UUID) -> RegisteredModel | None:
        stmt = (
            select(RegisteredModel)
            .options(selectinload(RegisteredModel.artifacts))
            .where(RegisteredModel.id == model_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, model: RegisteredModel) -> RegisteredModel:
        self.db.add(model)
        await self.db.commit()
        await self.db.refresh(model)
        return model

    async def update_approval(
        self,
        model_id: UUID,
        approval_status: str,
        approved_by: str,
        approval_notes: str,
    ) -> RegisteredModel | None:
        model = await self.get_by_id(model_id)
        if model:
            model.approval_status = approval_status
            model.approved_by = approved_by
            model.approval_notes = approval_notes
            if approval_status == "APPROVED":
                model.stage = "APPROVED"
            await self.db.commit()
            await self.db.refresh(model)
        return model

    async def update_stage(self, model_id: UUID, stage: str) -> RegisteredModel | None:
        model = await self.get_by_id(model_id)
        if model:
            model.stage = stage
            await self.db.commit()
            await self.db.refresh(model)
        return model


class MLStudioEvaluationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_model(self, model_id: UUID) -> list[EvaluationReport]:
        stmt = (
            select(EvaluationReport)
            .where(EvaluationReport.model_id == model_id)
            .order_by(EvaluationReport.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, report: EvaluationReport) -> EvaluationReport:
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        return report


class MLStudioExplainabilityRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_model(self, model_id: UUID) -> list[ExplainabilityReport]:
        stmt = (
            select(ExplainabilityReport)
            .where(ExplainabilityReport.model_id == model_id)
            .order_by(ExplainabilityReport.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, report: ExplainabilityReport) -> ExplainabilityReport:
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        return report
