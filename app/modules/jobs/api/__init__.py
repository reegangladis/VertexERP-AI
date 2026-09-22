"""Jobs API package re-exports."""

from app.modules.jobs.api.job_endpoints import router as jobs_router

__all__ = ["jobs_router"]
