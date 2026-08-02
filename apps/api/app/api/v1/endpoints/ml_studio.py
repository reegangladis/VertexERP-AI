from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.schemas.ml_studio import (
    ApprovalRequest,
    DatasetCreate,
    DatasetPreviewResponse,
    DatasetResponse,
    DatasetValidationResponse,
    EvaluationReportResponse,
    ExplainabilityReportResponse,
    LocalExplainRequest,
    ModelComparisonResponse,
    NotebookCreate,
    NotebookExecutionResponse,
    NotebookResponse,
    PackagingPreparationResponse,
    PromotionRequest,
    RegisteredModelCreate,
    RegisteredModelResponse,
)
from app.services.ml_studio_service import MLStudioService

router = APIRouter()

# Default hardcoded org id for tenant API testing
DEFAULT_ORG_ID = UUID("00000000-0000-0000-0000-000000000001")


# ==========================================
# DATASET REGISTRY ENDPOINTS
# ==========================================


@router.get(
    "/datasets",
    response_model=list[DatasetResponse],
    summary="List registered datasets in ML Studio",
)
async def list_datasets(
    domain: str | None = Query(None, description="Filter by domain"),
    db: AsyncSession = Depends(get_db),
):
    service = MLStudioService(db)
    return await service.list_datasets(DEFAULT_ORG_ID, domain)


@router.post(
    "/datasets",
    response_model=DatasetResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new dataset with versioning and stats",
)
async def create_dataset(payload: DatasetCreate, db: AsyncSession = Depends(get_db)):
    service = MLStudioService(db)
    return await service.create_dataset(DEFAULT_ORG_ID, payload)


@router.get(
    "/datasets/{dataset_id}/preview",
    response_model=DatasetPreviewResponse,
    summary="Preview dataset head rows and types",
)
async def get_dataset_preview(dataset_id: UUID, db: AsyncSession = Depends(get_db)):
    service = MLStudioService(db)
    try:
        return await service.get_dataset_preview(dataset_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get(
    "/datasets/{dataset_id}/statistics",
    summary="Get dataset column statistics and missing ratios",
)
async def get_dataset_statistics(dataset_id: UUID, db: AsyncSession = Depends(get_db)):
    service = MLStudioService(db)
    dataset = await service.dataset_repo.get_by_id(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return service.calculate_dataset_statistics(dataset)


@router.post(
    "/datasets/{dataset_id}/validate",
    response_model=DatasetValidationResponse,
    summary="Validate dataset quality and integrity rules",
)
async def validate_dataset(dataset_id: UUID, db: AsyncSession = Depends(get_db)):
    service = MLStudioService(db)
    try:
        return await service.validate_dataset(dataset_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


# ==========================================
# NOTEBOOK REGISTRY ENDPOINTS
# ==========================================


@router.get(
    "/notebooks",
    response_model=list[NotebookResponse],
    summary="List science & exploratory notebooks",
)
async def list_notebooks(db: AsyncSession = Depends(get_db)):
    service = MLStudioService(db)
    return await service.list_notebooks(DEFAULT_ORG_ID)


@router.post(
    "/notebooks",
    response_model=NotebookResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new interactive notebook",
)
async def create_notebook(payload: NotebookCreate, db: AsyncSession = Depends(get_db)):
    service = MLStudioService(db)
    return await service.create_notebook(DEFAULT_ORG_ID, payload)


@router.post(
    "/notebooks/{notebook_id}/execute",
    response_model=NotebookExecutionResponse,
    summary="Execute notebook cells (simulation)",
)
async def execute_notebook(notebook_id: UUID, db: AsyncSession = Depends(get_db)):
    service = MLStudioService(db)
    try:
        return await service.execute_notebook(notebook_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get(
    "/notebooks/templates", summary="Get pre-built data science notebook templates"
)
async def get_notebook_templates(db: AsyncSession = Depends(get_db)):
    service = MLStudioService(db)
    return service.get_notebook_templates()


# ==========================================
# MODEL REGISTRY & APPROVAL WORKFLOW
# ==========================================


@router.get(
    "/models",
    response_model=list[RegisteredModelResponse],
    summary="List registered models in Model Registry",
)
async def list_models(
    stage: str | None = Query(
        None, description="Filter by stage: CANDIDATE, APPROVED, PRODUCTION"
    ),
    db: AsyncSession = Depends(get_db),
):
    service = MLStudioService(db)
    return await service.list_models(DEFAULT_ORG_ID, stage)


@router.post(
    "/models",
    response_model=RegisteredModelResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a model in Model Registry",
)
async def register_model(
    payload: RegisteredModelCreate, db: AsyncSession = Depends(get_db)
):
    service = MLStudioService(db)
    return await service.register_model(DEFAULT_ORG_ID, payload)


@router.post(
    "/models/{model_id}/approve",
    response_model=RegisteredModelResponse,
    summary="Approve model version",
)
async def approve_model(
    model_id: UUID, payload: ApprovalRequest, db: AsyncSession = Depends(get_db)
):
    service = MLStudioService(db)
    try:
        return await service.approve_model_version(model_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post(
    "/models/{model_id}/promote",
    response_model=RegisteredModelResponse,
    summary="Promote model lifecycle stage",
)
async def promote_model(
    model_id: UUID, payload: PromotionRequest, db: AsyncSession = Depends(get_db)
):
    service = MLStudioService(db)
    try:
        return await service.promote_model_stage(model_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


# ==========================================
# EVALUATION & EXPLAINABILITY ENDPOINTS
# ==========================================


@router.get(
    "/evaluations/{model_id}",
    response_model=list[EvaluationReportResponse],
    summary="Get evaluation report (ROC, PR curves, Confusion Matrix, Residuals)",
)
async def get_evaluation_report(model_id: UUID, db: AsyncSession = Depends(get_db)):
    service = MLStudioService(db)
    reports = await service.get_evaluation_reports(model_id)
    if not reports:
        # Auto-generate baseline evaluation report if first request
        new_report = await service.generate_evaluation_report(
            model_id, "v1.0.0", "Automated Evaluation"
        )
        return [new_report]
    return reports


@router.get(
    "/explainability/{model_id}",
    response_model=list[ExplainabilityReportResponse],
    summary="Get explainability report (SHAP, LIME, Permutation Importance)",
)
async def get_explainability_report(model_id: UUID, db: AsyncSession = Depends(get_db)):
    service = MLStudioService(db)
    reports = await service.explain_repo.get_by_model(model_id)
    if not reports:
        new_report = await service.generate_explainability_report(model_id, "v1.0.0")
        return [new_report]
    return reports


@router.post(
    "/explainability/local-explain",
    summary="Generate instance-level local waterfall prediction explanation",
)
async def explain_local_prediction(
    payload: LocalExplainRequest, db: AsyncSession = Depends(get_db)
):
    service = MLStudioService(db)
    return await service.explain_local_prediction(payload)


# ==========================================
# MODEL COMPARISON & PACKAGING
# ==========================================


@router.get(
    "/models/compare",
    response_model=ModelComparisonResponse,
    summary="Compare registered models side-by-side on metrics & speed",
)
async def compare_models(db: AsyncSession = Depends(get_db)):
    service = MLStudioService(db)
    return await service.compare_models(DEFAULT_ORG_ID)


@router.post(
    "/packaging/{model_id}/prepare",
    response_model=PackagingPreparationResponse,
    summary="Prepare model packaging bundle & Dockerfile template",
)
async def prepare_packaging(model_id: UUID, db: AsyncSession = Depends(get_db)):
    service = MLStudioService(db)
    return await service.prepare_packaging(model_id)
