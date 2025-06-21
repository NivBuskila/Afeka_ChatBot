from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List, Dict, Any, Optional
from ...services.api_key_services import ApiKeyService
from src.backend.core.dependencies import get_supabase_client
import logging
import json
import time

router = APIRouter(prefix="/api/keys", tags=["API Keys"])

logger = logging.getLogger(__name__)

# Simple in-memory cache with longer TTL for better performance
_cache = {
    "data": None,
    "timestamp": 0,
    "ttl": 120  # 2 minutes cache - longer for better performance
}

def get_cached_result() -> Optional[Dict[str, Any]]:
    """Get cached result if still valid"""
    if _cache["data"] is None:
        return None
    
    age = time.time() - _cache["timestamp"]
    if age > _cache["ttl"]:
        _cache["data"] = None
        return None
    
    logger.info(f"🚀 [CACHE-HIT] Returning cached data (age: {age:.1f}s)")
    return _cache["data"]

def set_cached_result(data: Dict[str, Any]):
    """Cache the result"""
    _cache["data"] = data
    _cache["timestamp"] = time.time()
    logger.info("💾 [CACHE-SET] Data cached for 2 minutes")

@router.get("/")
async def get_api_keys(
    supabase_client = Depends(get_supabase_client)
) -> Dict[str, Any]:
    """קבלת מצב כל המפתחות ושימוש"""
    try:
        # Check cache first
        cached_result = get_cached_result()
        if cached_result:
            return cached_result
        
        logger.info("🔑 [API-KEYS] Cache miss - fetching fresh data")
        
        service = ApiKeyService(supabase_client)
        
        # קבל כל המפתחות
        keys = await service.get_all_keys()
        if not keys:
            return {"status": "error", "message": "No API keys found"}
        
        logger.info(f"🔑 [API-KEYS] Found {len(keys)} keys")
        
        # קבל אינדקס המפתח הנוכחי מה-AI service
        current_key_index = await service.get_current_active_key_index()
        logger.info(f"🔑 [API-KEYS] Current key index: {current_key_index}")
        
        # 🚀 OPTIMIZED: Batch query for all keys usage
        from datetime import date, timezone, datetime
        today = date.today().isoformat()
        current_minute_utc = datetime.now(timezone.utc).replace(second=0, microsecond=0)
        
        # Get all key IDs
        key_ids = [key["id"] for key in keys]
        
        # Single query for all daily usage
        daily_response = supabase_client.table("api_key_usage")\
            .select("api_key_id,tokens_used,requests_count")\
            .in_("api_key_id", key_ids)\
            .eq("usage_date", today)\
            .execute()
        
        # Single query for all current minute usage
        minute_response = supabase_client.table("api_key_usage")\
            .select("api_key_id,tokens_used,requests_count")\
            .in_("api_key_id", key_ids)\
            .eq("usage_minute", current_minute_utc.isoformat())\
            .execute()
        
        # Process batch results
        daily_usage = {}
        for row in daily_response.data:
            key_id = row["api_key_id"]
            if key_id not in daily_usage:
                daily_usage[key_id] = {"tokens": 0, "requests": 0}
            daily_usage[key_id]["tokens"] += row["tokens_used"]
            daily_usage[key_id]["requests"] += row["requests_count"]
        
        minute_usage = {}
        for row in minute_response.data:
            key_id = row["api_key_id"]
            if key_id not in minute_usage:
                minute_usage[key_id] = {"tokens": 0, "requests": 0}
            minute_usage[key_id]["tokens"] += row["tokens_used"]
            minute_usage[key_id]["requests"] += row["requests_count"]
        
        logger.info(f"🚀 [API-KEYS] Batch queries complete: {len(daily_response.data)} daily, {len(minute_response.data)} minute records")
        
        # בניית נתונים
        keys_status = []
        total_tokens_today = 0
        total_requests_today = 0
        
        for i, key in enumerate(keys):
            key_id = key["id"]
            
            # Get usage from batch results
            daily_data = daily_usage.get(key_id, {"tokens": 0, "requests": 0})
            minute_data = minute_usage.get(key_id, {"tokens": 0, "requests": 0})
            
            # חשב סטטוס המפתח
            is_current = i == current_key_index
            status = "current" if is_current else "available"
            
            # בדוק אם המפתח חסום (למשל עבר מגבלות)
            if daily_data["requests"] >= 900:  # 60% ממגבלת 1500
                status = "blocked"
            elif minute_data["requests"] >= 9:  # 60% ממגבלת 15
                status = "rate_limited"
            
            key_status = {
                "id": i,
                "is_current": is_current,
                "status": status,
                "tokens_today": daily_data["tokens"],
                "requests_today": daily_data["requests"], 
                "tokens_current_minute": minute_data["tokens"],
                "requests_current_minute": minute_data["requests"],
                "created_at": key.get("created_at"),
                "last_used": None  # ניתן להוסיף בעתיד
            }
            
            keys_status.append(key_status)
            total_tokens_today += daily_data["tokens"]
            total_requests_today += daily_data["requests"]
        
        # חשב סטטיסטיקות כלליות
        available_count = sum(1 for k in keys_status if k["status"] in ["available", "current"])
        blocked_count = sum(1 for k in keys_status if k["status"] in ["blocked", "rate_limited"])
        
        response = {
            "status": "ok",
            "key_management": {
                "total_keys": len(keys),
                "available_keys": available_count,
                "blocked_keys": blocked_count,
                "current_key_index": current_key_index,
                "keys_status": keys_status,
                "daily_summary": {
                    "total_tokens": total_tokens_today,
                    "total_requests": total_requests_today,
                    "active_keys": len([k for k in keys_status if k["tokens_today"] > 0])
                }
            }
        }
        
        set_cached_result(response)
        return response
        
    except Exception as e:
        logger.error(f"Error getting API keys status: {e}")
        return {
            "status": "error", 
            "message": str(e),
            "key_management": {
                "total_keys": 0,
                "available_keys": 0, 
                "blocked_keys": 0,
                "current_key_index": 0,
                "keys_status": []
            }
        }

@router.post("/{key_id}/usage")
async def record_usage(
    key_id: int,
    request: Request,
    supabase_client = Depends(get_supabase_client)
):
    """רישום שימוש במפתח - accepts JSON body with tokens_used and requests_count"""
    try:
        # Parse JSON body
        body_bytes = await request.body()
        body_str = body_bytes.decode('utf-8')
        body = json.loads(body_str)
        
        tokens_used = body.get('tokens_used')
        requests_count = body.get('requests_count', 1)
        
        if tokens_used is None:
            raise HTTPException(status_code=400, detail="tokens_used is required")
        
        if not isinstance(tokens_used, int) or tokens_used < 0:
            raise HTTPException(status_code=400, detail="tokens_used must be a non-negative integer")
            
        if not isinstance(requests_count, int) or requests_count < 0:
            raise HTTPException(status_code=400, detail="requests_count must be a non-negative integer")
        
        service = ApiKeyService(supabase_client)
        await service.record_usage(key_id, tokens_used, requests_count)
        
        logger.info(f"📊 [USAGE-API] Recorded {tokens_used} tokens, {requests_count} requests for key {key_id}")
        return {"status": "recorded", "tokens_used": tokens_used, "requests_count": requests_count}
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in request body")
    except Exception as e:
        logger.error(f"Error recording usage for key {key_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to record usage: {str(e)}")

# 🆕 Test endpoints for rotation testing
@router.post("/test/simulate-usage/{key_id}")
async def simulate_heavy_usage(
    key_id: int,
    requests_to_add: int = 10,
    supabase_client = Depends(get_supabase_client)
):
    """סימולציה של שימוש כבד לבדיקת רוטציה"""
    try:
        service = ApiKeyService(supabase_client)
        
        logger.info(f"🧪 [TEST] Simulating {requests_to_add} requests for key {key_id}")
        
        # רשום כמה בקשות ברצף
        for i in range(requests_to_add):
            await service.record_usage(key_id, 100, 1)  # 100 tokens per request
            
        # קבל את המצב אחרי הסימולציה
        usage = await service.get_key_current_usage(key_id)
        
        return {
            "status": "simulated",
            "key_id": key_id,
            "requests_added": requests_to_add,
            "current_usage": usage,
            "note": "This was a simulation. Check if rotation triggered."
        }
        
    except Exception as e:
        logger.error(f"Error simulating usage for key {key_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to simulate usage: {str(e)}")

@router.get("/test/check-limits/{key_id}")
async def check_key_limits(
    key_id: int,
    supabase_client = Depends(get_supabase_client)
):
    """בדיקת מצב מגבלות של מפתח"""
    try:
        service = ApiKeyService(supabase_client)
        usage = await service.get_key_current_usage(key_id)
        
        # מגבלות Google Free Tier
        max_requests_per_minute = 15
        max_requests_per_day = 1500
        max_tokens_per_day = 1000000
        
        # חישוב אחוזים
        minute_percentage = (usage["minute_requests"] / max_requests_per_minute) * 100
        daily_requests_percentage = (usage["daily_requests"] / max_requests_per_day) * 100
        daily_tokens_percentage = (usage["daily_tokens"] / max_tokens_per_day) * 100
        
        # בדיקת סטטוס
        is_minute_limited = usage["minute_requests"] >= (max_requests_per_minute * 0.6)  # 60% threshold
        is_daily_limited = usage["daily_requests"] >= (max_requests_per_day * 0.6)
        
        status = "available"
        if is_minute_limited:
            status = "rate_limited"
        elif is_daily_limited:
            status = "blocked"
            
        return {
            "key_id": key_id,
            "status": status,
            "usage": usage,
            "limits": {
                "requests_per_minute": max_requests_per_minute,
                "requests_per_day": max_requests_per_day,
                "tokens_per_day": max_tokens_per_day
            },
            "percentages": {
                "minute_requests": round(minute_percentage, 1),
                "daily_requests": round(daily_requests_percentage, 1),
                "daily_tokens": round(daily_tokens_percentage, 1)
            },
            "warnings": {
                "minute_limited": is_minute_limited,
                "daily_limited": is_daily_limited,
                "should_rotate": is_minute_limited or is_daily_limited
            }
        }
        
    except Exception as e:
        logger.error(f"Error checking limits for key {key_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to check limits: {str(e)}")

@router.get("/for-ai-service")
async def get_keys_for_ai_service(
    supabase_client = Depends(get_supabase_client)
) -> Dict[str, Any]:
    """Get API keys for AI service with actual key values"""
    try:
        # This endpoint is specifically for the AI service to get actual API key values
        # It should only be accessible internally (add authentication if needed)
        
        logger.info("🔑 [AI-SERVICE] Fetching API keys for AI service")
        
        # Get active API keys with actual key values
        response = supabase_client.table("api_keys")\
            .select("id, key_name, api_key, is_active, created_at")\
            .eq("is_active", True)\
            .execute()
        
        keys = response.data or []
        logger.info(f"🔑 [AI-SERVICE] Found {len(keys)} active API keys")
        
        return {
            "status": "ok",
            "keys": keys,
            "total_keys": len(keys)
        }
        
    except Exception as e:
        logger.error(f"❌ [AI-SERVICE] Error getting API keys: {e}")
        return {
            "status": "error", 
            "message": str(e),
            "keys": []
        }
