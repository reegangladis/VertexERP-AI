"""Worker registry mapping job types to dedicated worker instances."""

import logging

from app.modules.jobs.workers.base import BaseWorker
from app.modules.jobs.workers.document_ingestion_worker import DocumentIngestionWorker
from app.modules.jobs.workers.email_worker import EmailWorker
from app.modules.jobs.workers.embeddings_worker import EmbeddingsWorker
from app.modules.jobs.workers.integrations_worker import IntegrationsWorker
from app.modules.jobs.workers.notifications_worker import NotificationsWorker
from app.modules.jobs.workers.reports_worker import ReportsWorker
from app.modules.jobs.workers.scheduled_jobs_worker import ScheduledJobsWorker

logger = logging.getLogger("vertexerp.jobs.registry")


class WorkerRegistry:
    """Registry maintaining active workers for each domain job type."""

    def __init__(self) -> None:
        self._workers: dict[str, BaseWorker] = {}
        self._register_default_workers()

    def _register_default_workers(self) -> None:
        """Register default enterprise workers."""
        self.register(EmailWorker())
        self.register(DocumentIngestionWorker())
        self.register(EmbeddingsWorker())
        self.register(ReportsWorker())
        self.register(NotificationsWorker())
        self.register(ScheduledJobsWorker())
        self.register(IntegrationsWorker())

    def register(self, worker: BaseWorker) -> None:
        """Register a worker instance for its declared job_type."""
        self._workers[worker.job_type] = worker
        logger.debug("Registered worker for job_type: %s", worker.job_type)

    def get_worker(self, job_type: str) -> BaseWorker:
        """Retrieve registered worker for given job_type."""
        worker = self._workers.get(job_type)
        if not worker:
            raise ValueError(
                f"No worker registered for job_type='{job_type}'. "
                f"Available types: {list(self._workers.keys())}"
            )
        return worker

    def list_job_types(self) -> list[str]:
        """List all supported job types."""
        return list(self._workers.keys())


# Singleton registry instance
worker_registry = WorkerRegistry()
