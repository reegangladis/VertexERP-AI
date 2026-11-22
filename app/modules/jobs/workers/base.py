"""Abstract Base Worker for background task processors."""

import abc
import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.jobs.models.job import BackgroundJob

logger = logging.getLogger("vertexerp.jobs.worker")


class BaseWorker(abc.ABC):
    """Abstract Base Worker class for all dedicated domain workers."""

    job_type: str = "base"

    @abc.abstractmethod
    async def process(
        self,
        job: BackgroundJob,
        payload: dict[str, Any],
        session: AsyncSession,
    ) -> dict[str, Any]:
        """
        Execute worker domain logic.
        Returns result dictionary on success.
        Raises exception on failure (which triggers retry or DLQ).
        """
        raise NotImplementedError
