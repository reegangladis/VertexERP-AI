"""Enterprise S3-compatible object storage adapter with tenant isolation."""

from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import UTC, datetime, timedelta
from io import BytesIO
from typing import Any

from minio import Minio

from app.core.config import settings

logger = logging.getLogger("vertexerp.storage")


class StorageClient:
    """S3/MinIO client with tenant-scoped object keys and real I/O."""

    def __init__(
        self,
        endpoint_url: str | None = None,
        bucket_name: str | None = None,
        access_key: str | None = None,
        secret_key: str | None = None,
        region_name: str = "us-east-1",
        secure: bool | None = None,
        public_endpoint_url: str | None = None,
    ) -> None:
        self.endpoint_url = endpoint_url or settings.STORAGE_ENDPOINT_URL
        self.public_endpoint_url = public_endpoint_url or settings.STORAGE_PUBLIC_ENDPOINT_URL
        self.bucket_name = bucket_name or settings.STORAGE_BUCKET_NAME
        self.access_key = access_key or settings.STORAGE_ACCESS_KEY
        self.secret_key = secret_key or settings.STORAGE_SECRET_KEY
        self.region_name = region_name
        self.secure = secure if secure is not None else self.endpoint_url.lower().startswith("https://")
        endpoint = self.endpoint_url.split("://", 1)[-1].rstrip("/")
        self._client = Minio(
            endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure,
            region=self.region_name,
        )

    @staticmethod
    def _build_tenant_key(tenant_id: uuid.UUID, entity_type: str, file_name: str) -> str:
        timestamp = datetime.now(UTC).strftime("%Y%m")
        clean_filename = file_name.replace("..", "").replace("\\", "/").lstrip("/")
        clean_filename = "/".join(
            part for part in clean_filename.split("/") if part not in ("", ".", "..")
        )
        if not clean_filename:
            raise ValueError("file_name must not be empty")
        return f"tenants/{tenant_id}/{entity_type}/{timestamp}/{clean_filename}"

    @staticmethod
    def _assert_tenant_key(tenant_id: uuid.UUID, object_key: str) -> None:
        expected_prefix = f"tenants/{tenant_id}/"
        if not object_key.startswith(expected_prefix):
            raise PermissionError(
                f"Access denied: object '{object_key}' does not belong to tenant {tenant_id}"
            )

    async def _ensure_bucket(self) -> None:
        exists = await asyncio.to_thread(self._client.bucket_exists, self.bucket_name)
        if not exists:
            await asyncio.to_thread(self._client.make_bucket, self.bucket_name)

    async def upload_file(
        self,
        tenant_id: uuid.UUID,
        entity_type: str,
        file_name: str,
        data: bytes,
        content_type: str = "application/octet-stream",
        metadata: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        object_key = self._build_tenant_key(tenant_id, entity_type, file_name)
        await self._ensure_bucket()
        meta = dict(metadata or {})
        meta.update(
            {
                "tenant_id": str(tenant_id),
                "uploaded_at": datetime.now(UTC).isoformat(),
                "file_size": str(len(data)),
            }
        )
        await asyncio.to_thread(
            self._client.put_object,
            self.bucket_name,
            object_key,
            BytesIO(data),
            length=len(data),
            content_type=content_type,
            metadata={"X-Amz-Meta-Tenant-Id": str(tenant_id)},
        )
        return {
            "bucket": self.bucket_name,
            "key": object_key,
            "size_bytes": len(data),
            "content_type": content_type,
            "metadata": meta,
            "url": self._public_url(object_key),
        }

    async def download_file(self, tenant_id: uuid.UUID, object_key: str) -> bytes:
        self._assert_tenant_key(tenant_id, object_key)
        response = await asyncio.to_thread(self._client.get_object, self.bucket_name, object_key)
        try:
            return await asyncio.to_thread(response.read)
        finally:
            response.close()
            response.release_conn()

    async def delete_file(self, tenant_id: uuid.UUID, object_key: str) -> bool:
        self._assert_tenant_key(tenant_id, object_key)
        await asyncio.to_thread(self._client.remove_object, self.bucket_name, object_key)
        return True

    def generate_presigned_url(
        self,
        tenant_id: uuid.UUID,
        object_key: str,
        expires_in_seconds: int = 3600,
    ) -> str:
        self._assert_tenant_key(tenant_id, object_key)
        if not 1 <= expires_in_seconds <= 7 * 24 * 3600:
            raise ValueError("expires_in_seconds must be between 1 second and 7 days")
        if self.public_endpoint_url.rstrip("/") != self.endpoint_url.rstrip("/"):
            raise ValueError(
                "STORAGE_ENDPOINT_URL must equal STORAGE_PUBLIC_ENDPOINT_URL for "
                "browser-accessible presigned URLs"
            )
        return str(
            self._client.presigned_get_object(
                self.bucket_name,
                object_key,
                expires=timedelta(seconds=expires_in_seconds),
            )
        )

    def _public_url(self, object_key: str) -> str:
        return f"{self.public_endpoint_url.rstrip('/')}/{self.bucket_name}/{object_key}"


storage_client = StorageClient()
