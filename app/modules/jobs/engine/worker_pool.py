"""Asynchronous Worker Pool for background job execution."""

import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.modules.jobs.engine.executor import JobExecutor
from app.modules.jobs.engine.job_queue import job_queue_manager

logger = logging.getLogger("vertexerp.jobs.pool")


class BackgroundWorkerPool:
    """Manages worker coroutine pool and job execution dispatching."""

    def __init__(self) -> None:
        self._running = False
        self._worker_tasks: list[asyncio.Task] = []
        self._concurrency = 4
        self._session_factory: async_sessionmaker[AsyncSession] | None = None
        self._active_workers_count = 0

    def configure(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        concurrency: int = 4,
    ) -> None:
        """Configure session factory and concurrency level."""
        self._session_factory = session_factory
        self._concurrency = concurrency

    async def start(self) -> None:
        """Start worker loop tasks in background."""
        if self._running:
            return
        self._running = True
        logger.info("Starting BackgroundWorkerPool with concurrency=%d", self._concurrency)

        for i in range(self._concurrency):
            worker_id = f"worker_proc_{i + 1}"
            task = asyncio.create_task(self._worker_loop(worker_id))
            self._worker_tasks.append(task)

    async def stop(self) -> None:
        """Stop worker tasks and gracefully drain."""
        if not self._running:
            return
        self._running = False
        logger.info("Stopping BackgroundWorkerPool...")

        for task in self._worker_tasks:
            task.cancel()

        await asyncio.gather(*self._worker_tasks, return_exceptions=True)
        self._worker_tasks.clear()
        logger.info("BackgroundWorkerPool stopped.")

    async def _worker_loop(self, worker_id: str) -> None:
        """Worker consumption loop."""
        logger.debug("Worker loop started for %s", worker_id)
        while self._running:
            try:
                job_id = await job_queue_manager.dequeue()
                if not job_id:
                    await asyncio.sleep(0.2)
                    continue

                if not self._session_factory:
                    logger.error("Session factory not configured in worker pool.")
                    await asyncio.sleep(1.0)
                    continue

                self._active_workers_count += 1
                try:
                    async with self._session_factory() as session:
                        async with session.begin():
                            await JobExecutor.execute_job(
                                session=session,
                                job_id=job_id,
                                worker_id=worker_id,
                            )
                    await job_queue_manager.ack(job_id)
                finally:
                    self._active_workers_count -= 1

            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error("Unexpected error in worker loop %s: %s", worker_id, exc)
                await asyncio.sleep(0.5)

    @property
    def is_running(self) -> bool:
        """Check if pool is running."""
        return self._running

    @property
    def active_workers(self) -> int:
        """Return currently busy workers count."""
        return self._active_workers_count


# Global worker pool singleton
worker_pool = BackgroundWorkerPool()
