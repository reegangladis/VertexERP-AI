from typing import Any

from fastapi import APIRouter, Query

from app.schemas.integration import (
    APIKeyVerifyRequest,
    APIKeyVerifyResponse,
)
from app.services.api_gateway import ApiGatewayService

router = APIRouter()
gateway_service = ApiGatewayService()


@router.post("/route")
async def route_api_request(
    path: str = Query(..., description="URI route path e.g. /v1/erp/sync"),
    method: str = Query("GET"),
):
    """API Gateway dynamic route resolution and versioning policy check."""
    return gateway_service.route_request(path=path, method=method)


@router.post("/verify-key", response_model=APIKeyVerifyResponse)
async def verify_gateway_api_key(payload: APIKeyVerifyRequest):
    """Validates API Key signature and permissions."""
    return gateway_service.verify_api_key(payload.api_key)


@router.get("/rate-limit-check")
async def check_rate_limit(
    client_id: str = Query("default_client"),
    limit_rps: int = Query(50),
):
    """Executes token bucket rate limit evaluation."""
    allowed, remaining = gateway_service.check_rate_limit(client_id, limit_rps)
    return {
        "client_id": client_id,
        "allowed": allowed,
        "remaining_tokens": remaining,
        "limit_rps": limit_rps,
    }


@router.get("/cache")
async def get_cached_item(cache_key: str = Query(...)):
    """Retrieves cached response payload if unexpired."""
    val = gateway_service.get_cached_response(cache_key)
    if val is None:
        return {"cache_hit": False, "data": None}
    return {"cache_hit": True, "data": val}


@router.post("/cache")
async def set_cached_item(
    cache_key: str, payload: dict[str, Any], ttl_seconds: int = 60
):
    """Sets cached response payload with TTL."""
    gateway_service.set_cached_response(cache_key, payload, ttl_seconds)
    return {"status": "cached", "key": cache_key, "ttl_seconds": ttl_seconds}
