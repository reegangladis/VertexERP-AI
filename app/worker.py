"""Standalone Background Worker Process with Graceful Signal Handling and Task Draining."""

import asyncio
import contextlib
import json
import os
from pathlib import Path
import signal
import sys
import tempfile
import time
from typing import Any


def get_heartbeat_path() -> Path:
    """Returns the path to the worker heartbeat file."""
    tmp_dir = Path("/tmp")
    if tmp_dir.exists() and tmp_dir.is_dir():
        return tmp_dir / "worker_heartbeat.json"
    return Path(tempfile.gettempdir()) / "worker_heartbeat.json"


def write_heartbeat_atomic(heartbeat_file: Path, payload: str) -> None:
    """Atomically writes payload to heartbeat_file using a temporary file and atomic replace."""
    tmp_file = heartbeat_file.with_suffix(".tmp")
    tmp_file.write_text(payload, encoding="utf-8")
    os.replace(tmp_file, heartbeat_file)


def check_health(max_age_seconds: float = 30.0) -> bool:
    """Verifies that the worker heartbeat exists, reports healthy, and is actively refreshed."""
    try:
        heartbeat_file = get_heartbeat_path()
        if not heartbeat_file.exists():
            return False
        data = json.loads(heartbeat_file.read_text(encoding="utf-8"))
        if data.get("status") != "healthy":
            return False
        last_beat = float(data.get("timestamp", 0))
        if (time.time() - last_beat) > max_age_seconds:
            return False
        return True
    except Exception:
        return False


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] in ("--healthcheck", "--health-check", "healthcheck"):
    sys.exit(0 if check_health() else 1)


# Application imports (loaded when running the daemon process or importing worker components)
from app.core.config import settings
from app.core.logging import logger, setup_logging
from app.infrastructure.database.session import (
    async_session_factory,
    close_db_engine,
    init_db_engine,
)
from app.infrastructure.redis.client import close_redis_client, init_redis_client
from app.modules.jobs.engine.worker_pool import worker_pool


class WorkerDaemon:
    """Manages the lifecycle, signal handling, and execution of background worker tasks."""

    def __init__(self, concurrency: int = 4) -> None:
        self.concurrency = concurrency
        self._stop_event = asyncio.Event()

    async def run(self) -> None:
        """Starts worker pool and awaits termination signals."""
        setup_logging()
        logger.info(
            "Starting VertexERP Background Worker Daemon",
            version=settings.APP_VERSION,
            environment=settings.APP_ENV.value,
            concurrency=self.concurrency,
        )

        # Ensure any stale heartbeat file from a previous crashed run is cleaned up on start
        heartbeat_file = get_heartbeat_path()
        with contextlib.suppress(Exception):
            if heartbeat_file.exists():
                heartbeat_file.unlink()

        # 1. Initialize persistent storage connections
        await init_db_engine()
        await init_redis_client()

        # 2. Configure and start worker pool
        worker_pool.configure(
            session_factory=async_session_factory,
            concurrency=self.concurrency,
        )
        await worker_pool.start()
        logger.info("Background Worker Pool is operational and consuming jobs.")

        # 3. Start recurring scheduler loop task
        scheduler_task = asyncio.create_task(self._run_scheduler_loop())

        # 4. Start heartbeat loop task for health checking
        heartbeat_task = asyncio.create_task(self._run_heartbeat_loop(scheduler_task))

        # 5. Register signal handlers
        self._register_signals()

        # 6. Wait until stop signal received
        await self._stop_event.wait()

        # 7. Graceful shutdown sequence
        heartbeat_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await heartbeat_task

        scheduler_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await scheduler_task
        await self._shutdown()

    async def _run_heartbeat_loop(self, scheduler_task: asyncio.Task) -> None:
        """Periodically writes health check heartbeat file to signal operational liveness."""
        heartbeat_file = get_heartbeat_path()
        try:
            while not self._stop_event.is_set():
                try:
                    is_healthy = worker_pool.is_running and not scheduler_task.done()
                    if is_healthy:
                        payload = json.dumps(
                            {
                                "status": "healthy",
                                "timestamp": time.time(),
                                "pid": os.getpid(),
                                "concurrency": self.concurrency,
                                "active_workers": worker_pool.active_workers,
                            }
                        )
                    else:
                        payload = json.dumps(
                            {
                                "status": "unhealthy",
                                "timestamp": time.time(),
                                "error": "worker pool or scheduler loop stopped",
                            }
                        )
                    write_heartbeat_atomic(heartbeat_file, payload)
                except Exception as exc:
                    logger.warning("Failed writing worker heartbeat: %s", exc)

                with contextlib.suppress(TimeoutError):
                    await asyncio.wait_for(self._stop_event.wait(), timeout=5.0)
        finally:
            with contextlib.suppress(Exception):
                if heartbeat_file.exists():
                    heartbeat_file.unlink()

    async def _run_scheduler_loop(self) -> None:
        """Continuously evaluates recurring job schedules every 60 seconds with distributed lock."""
        from app.infrastructure.redis.client import get_redis_client
        from app.modules.jobs.engine.scheduler import CronScheduler

        logger.info("Recurring Cron Scheduler background loop active.")
        while not self._stop_event.is_set():
            try:
                redis = None
                with contextlib.suppress(Exception):
                    redis = await get_redis_client()

                # Distributed lock to prevent duplicate execution across multiple worker replicas
                acquired = True
                if redis:
                    try:
                        acquired = bool(
                            await redis.set("vertexerp:scheduler:lock", "active", nx=True, ex=50)
                        )
                    except Exception:
                        acquired = True

                if acquired:
                    async with async_session_factory() as session:
                        async with session.begin():
                            triggered = await CronScheduler.evaluate_schedules(session)

                        if triggered:
                            from app.modules.jobs.engine.job_queue import job_queue_manager

                            for job in triggered:
                                await job_queue_manager.enqueue(
                                    job.id,
                                    priority=job.priority,
                                    scheduled_at=job.scheduled_at,
                                )
                            logger.info(
                                "CronScheduler triggered and queued %d recurring jobs",
                                len(triggered),
                            )
            except Exception as exc:
                logger.warning("Error in CronScheduler loop: %s", exc)

            with contextlib.suppress(TimeoutError):
                await asyncio.wait_for(self._stop_event.wait(), timeout=60.0)

    def _register_signals(self) -> None:
        """Registers SIGTERM and SIGINT listeners across POSIX and Windows."""
        loop = asyncio.get_running_loop()

        def _handle_signal(sig_name: str) -> None:
            logger.info(
                "Received termination signal (%s). Initiating graceful worker drain...", sig_name
            )
            self._stop_event.set()

        if sys.platform != "win32":
            for sig in (signal.SIGTERM, signal.SIGINT):
                loop.add_signal_handler(sig, lambda s=sig: _handle_signal(s.name))
        else:
            # Windows fallback
            for sig in (signal.SIGTERM, signal.SIGINT):

                def _win_handler(signum: int, frame: Any, name: str = sig.name) -> None:
                    _handle_signal(name)

                signal.signal(sig, _win_handler)

    async def _shutdown(self) -> None:
        """Drains in-flight worker tasks and cleans up infrastructure connections."""
        logger.info("Initiating worker graceful shutdown sequence...")
        try:
            # Drain workers with timeout
            await asyncio.wait_for(worker_pool.stop(), timeout=30.0)
        except TimeoutError:
            logger.warning("Worker drain timed out after 30s. Forcing connection termination.")
        except Exception as exc:
            logger.error("Error occurred while stopping worker pool: %s", exc)

        await close_redis_client()
        await close_db_engine()
        logger.info("VertexERP Background Worker Daemon stopped cleanly.")


async def main() -> None:
    daemon = WorkerDaemon(concurrency=4)
    await daemon.run()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("--healthcheck", "--health-check", "healthcheck"):
        is_healthy = check_health()
        sys.exit(0 if is_healthy else 1)

    with contextlib.suppress(KeyboardInterrupt, SystemExit):
        asyncio.run(main())
