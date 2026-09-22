"""Durable Distributed Redis Streams & Priority Queue Manager with In-Memory Fallback."""

import asyncio
import heapq
import logging
import uuid
from datetime import UTC, datetime

from redis.asyncio import Redis

from app.infrastructure.redis.client import get_redis_client
from app.modules.jobs.models.job import JobPriority

logger = logging.getLogger("vertexerp.jobs.queue")

STREAM_PREFIX = "vertexerp:jobs:stream"
DELAYED_ZSET = "vertexerp:jobs:delayed"
CONSUMER_GROUP = "vertexerp_workers"


class JobQueueManager:
    """
    Durable distributed queue engine leveraging Redis Streams and consumer groups.
    Includes in-memory fallback for offline/isolated execution environments.
    """

    def __init__(self) -> None:
        self._consumer_name = f"worker_{uuid.uuid4().hex[:8]}"
        self._group_initialized = False
        self._pending_messages: dict[uuid.UUID, tuple[str, str]] = {}

        # In-memory fallback structures
        self._local_queues: dict[int, asyncio.Queue] = {
            JobPriority.CRITICAL.value: asyncio.Queue(),
            JobPriority.HIGH.value: asyncio.Queue(),
            JobPriority.NORMAL.value: asyncio.Queue(),
        }
        self._delayed_heap: list[tuple[float, int, str]] = []
        self._lock = asyncio.Lock()

    async def _get_redis(self) -> Redis | None:
        """Safely retrieves connected Redis client or None."""
        try:
            client = await get_redis_client()
            if client:
                await client.ping()
                return client
        except Exception:
            pass
        return None

    async def _ensure_consumer_groups(self, redis: Redis) -> None:
        """Ensures Redis Stream consumer groups exist for all priority levels."""
        if self._group_initialized:
            return
        for prio_name in ("critical", "high", "normal"):
            stream_key = f"{STREAM_PREFIX}:{prio_name}"
            try:
                await redis.xgroup_create(stream_key, CONSUMER_GROUP, id="0", mkstream=True)
            except Exception as exc:
                if "BUSYGROUP" not in str(exc):
                    logger.debug("Consumer group creation note: %s", exc)
        self._group_initialized = True

    def _prio_to_stream(self, priority: int) -> str:
        if priority >= JobPriority.CRITICAL.value:
            return f"{STREAM_PREFIX}:critical"
        elif priority == JobPriority.HIGH.value:
            return f"{STREAM_PREFIX}:high"
        return f"{STREAM_PREFIX}:normal"

    async def enqueue(
        self,
        job_id: uuid.UUID,
        priority: int = JobPriority.NORMAL.value,
        scheduled_at: datetime | None = None,
    ) -> None:
        """Enqueue a job either into durable Redis Streams or the in-memory fallback."""
        priority_clamped = max(0, min(2, priority))
        now = datetime.now(UTC)
        redis = await self._get_redis()

        if redis:
            try:
                if scheduled_at and scheduled_at > now:
                    # Enqueue into Redis Delayed Sorted Set
                    score = scheduled_at.timestamp()
                    val = f"{priority_clamped}:{str(job_id)}"
                    await redis.zadd(DELAYED_ZSET, {val: score})
                    logger.debug(
                        "Job %s scheduled in Redis delayed zset at %s",
                        job_id,
                        scheduled_at.isoformat(),
                    )
                else:
                    # Enqueue directly into priority Redis Stream
                    stream_key = self._prio_to_stream(priority_clamped)
                    await redis.xadd(
                        stream_key,
                        {"job_id": str(job_id), "priority": str(priority_clamped)},
                    )
                    logger.debug("Job %s enqueued to Redis stream %s", job_id, stream_key)
                return
            except Exception as e:
                logger.warning("Redis stream enqueue failed, using local queue: %s", e)

        # In-memory fallback
        async with self._lock:
            if scheduled_at and scheduled_at > now:
                timestamp = scheduled_at.timestamp()
                heapq.heappush(self._delayed_heap, (timestamp, -priority_clamped, str(job_id)))
            else:
                await self._local_queues[priority_clamped].put(job_id)

    async def dequeue(self) -> uuid.UUID | None:
        """
        Retrieve highest priority job available across Redis Streams or local queues.
        Migrates matured delayed jobs and checks CRITICAL -> HIGH -> NORMAL.
        """
        redis = await self._get_redis()
        now_ts = datetime.now(UTC).timestamp()

        if redis:
            try:
                await self._ensure_consumer_groups(redis)

                # 1. Migrate matured delayed jobs from Redis Sorted Set to Streams
                matured = await redis.zrangebyscore(DELAYED_ZSET, "-inf", now_ts, start=0, num=20)
                if matured:
                    for item in matured:
                        if await redis.zrem(DELAYED_ZSET, item):
                            parts = item.split(":", 1)
                            if len(parts) == 2:
                                prio_int = int(parts[0])
                                j_id = parts[1]
                                await redis.xadd(
                                    self._prio_to_stream(prio_int),
                                    {"job_id": j_id, "priority": str(prio_int)},
                                )

                # 2. Reclaim stale pending messages from crashed workers.
                for prio_name in ("critical", "high", "normal"):
                    stream_key = f"{STREAM_PREFIX}:{prio_name}"
                    try:
                        reclaimed = await redis.xautoclaim(
                            stream_key,
                            CONSUMER_GROUP,
                            self._consumer_name,
                            min_idle_time=30_000,
                            start_id="0-0",
                            count=10,
                        )
                        messages = reclaimed[1] if reclaimed else []
                        for msg_id, fields in messages:
                            job_id_str = fields.get("job_id")
                            if job_id_str:
                                job_uuid = uuid.UUID(job_id_str)
                                self._pending_messages[job_uuid] = (stream_key, msg_id)
                                return job_uuid
                    except Exception as exc:
                        logger.debug("Pending job reclaim failed for %s: %s", stream_key, exc)

                # 3. Dequeue from Streams in priority order
                for prio_name in ("critical", "high", "normal"):
                    stream_key = f"{STREAM_PREFIX}:{prio_name}"
                    res = await redis.xreadgroup(
                        groupname=CONSUMER_GROUP,
                        consumername=self._consumer_name,
                        streams={stream_key: ">"},
                        count=1,
                        block=10,
                    )
                    if res:
                        for _s_name, messages in res:
                            for msg_id, fields in messages:
                                job_id_str = fields.get("job_id")
                                if job_id_str:
                                    job_uuid = uuid.UUID(job_id_str)
                                    # Acknowledge only after JobExecutor has
                                    # durably completed the job. Keeping the
                                    # message pending allows crash recovery.
                                    self._pending_messages[job_uuid] = (stream_key, msg_id)
                                    return job_uuid
            except Exception as e:
                logger.debug("Redis dequeue error, checking local queue: %s", e)

        # In-memory fallback
        async with self._lock:
            while self._delayed_heap and self._delayed_heap[0][0] <= now_ts:
                _, neg_prio, job_id_str = heapq.heappop(self._delayed_heap)
                prio = -neg_prio
                job_uuid = uuid.UUID(job_id_str)
                await self._local_queues[prio].put(job_uuid)

            for prio in (
                JobPriority.CRITICAL.value,
                JobPriority.HIGH.value,
                JobPriority.NORMAL.value,
            ):
                q = self._local_queues[prio]
                if not q.empty():
                    return await q.get()

            return None

    async def ack(self, job_id: uuid.UUID) -> None:
        """Acknowledge a successfully processed Redis Stream message."""
        pending = self._pending_messages.pop(job_id, None)
        if not pending:
            return
        stream_key, msg_id = pending
        redis = await self._get_redis()
        if redis:
            await redis.xack(stream_key, CONSUMER_GROUP, msg_id)

    async def get_queue_depths(self) -> dict[str, int]:
        """Get current queue depths across streams and delayed backlog."""
        redis = await self._get_redis()
        if redis:
            try:
                c_len = await redis.xlen(f"{STREAM_PREFIX}:critical")
                h_len = await redis.xlen(f"{STREAM_PREFIX}:high")
                n_len = await redis.xlen(f"{STREAM_PREFIX}:normal")
                d_len = await redis.zcard(DELAYED_ZSET)
                return {
                    "critical": c_len,
                    "high": h_len,
                    "normal": n_len,
                    "delayed": d_len,
                    "total_queued": c_len + h_len + n_len + d_len,
                }
            except Exception:
                pass

        async with self._lock:
            return {
                "critical": self._local_queues[JobPriority.CRITICAL.value].qsize(),
                "high": self._local_queues[JobPriority.HIGH.value].qsize(),
                "normal": self._local_queues[JobPriority.NORMAL.value].qsize(),
                "delayed": len(self._delayed_heap),
                "total_queued": (
                    self._local_queues[JobPriority.CRITICAL.value].qsize()
                    + self._local_queues[JobPriority.HIGH.value].qsize()
                    + self._local_queues[JobPriority.NORMAL.value].qsize()
                    + len(self._delayed_heap)
                ),
            }

    async def clear(self) -> None:
        """Clear all queues for testing and resets."""
        redis = await self._get_redis()
        if redis:
            try:
                for p in ("critical", "high", "normal"):
                    await redis.delete(f"{STREAM_PREFIX}:{p}")
                await redis.delete(DELAYED_ZSET)
            except Exception:
                pass

        async with self._lock:
            for q in self._local_queues.values():
                while not q.empty():
                    try:
                        q.get_nowait()
                    except asyncio.QueueEmpty:
                        break
            self._delayed_heap.clear()


# Global queue manager instance
job_queue_manager = JobQueueManager()
