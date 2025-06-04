# app/api/v1/health.py
"""Health check endpoints"""

from fastapi import APIRouter, Depends
from typing import Dict, Any
from app.schemas.common import SuccessResponse

router = APIRouter(
    prefix="/health",
    tags=["health"],
    responses={
        200: {"description": "Success"},
        503: {"description": "Service Unavailable"}
    }
)

@router.get("", response_model=Dict[str, str])
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint for monitoring
    
    Returns basic service status
    """
    # TODO: Add actual health checks (database, external services, etc.)
    return {
        "status": "healthy",
        "service": "Afeka ChatBot API"
    }

@router.get("/ready", response_model=Dict[str, Any])
async def readiness_check() -> Dict[str, Any]:
    """
    Readiness check endpoint
    
    Returns detailed service readiness status
    """
    from app.dependencies import get_repository_factory
    
    ready = True
    checks = {
        "database": False,
        "ai_service": False,
        "storage": False
    }
    
    try:
        # Check database connection
        factory = get_repository_factory()
        if factory.supabase_client:
            checks["database"] = True
    except:
        ready = False
    
    return {
        "ready": ready,
        "checks": checks
    }

@router.get("/live", response_model=Dict[str, str])
async def liveness_check() -> Dict[str, str]:
    """
    Liveness check endpoint
    
    Simple endpoint to verify service is running
    """
    return {"status": "alive"}