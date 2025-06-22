from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List, Dict, Any, Optional
from ...services.api_key_services import ApiKeyService
from src.backend.core.dependencies import get_supabase_client
import logging
import json
import time

router = APIRouter(prefix="/api/keys", tags=["API Keys"])

logger = logging.getLogger(__name__)

# Global variable to store current key index from DatabaseKeyManager
_current_key_index_override = None

_cache = {
    "data": None,
    "timestamp": 0,
    "ttl": 30  # 🔧 הקטן מ-10 דקות ל-30 שניות כדי להראות נתונים בזמן אמת
}

def get_cached_result() -> Optional[Dict[str, Any]]:
    """Get cached result if still valid"""
    if _cache["data"] is None:
        return None
    
    age = time.time() - _cache["timestamp"]
    if age > _cache["ttl"]:
        _cache["data"] = None
        return None
    
    logger.info(f"[CACHE-HIT] Returning cached data (age: {age:.1f}s)")
    return _cache["data"]

def set_cached_result(data: Dict[str, Any]):
    """Cache the result"""
    _cache["data"] = data
    _cache["timestamp"] = time.time()
    logger.info("[CACHE-SET] Data cached for 30 seconds")

def invalidate_cache():
    """Invalidate the cache when new usage is recorded"""
    _cache["data"] = None
    _cache["timestamp"] = 0
    logger.info("[CACHE-INVALIDATE] Cache cleared due to new usage")

@router.get("/")
async def get_api_keys(
    supabase_client = Depends(get_supabase_client)
) -> Dict[str, Any]:
    """Get status of all keys and usage"""
    try:
        cached_result = get_cached_result()
        if cached_result:
            return cached_result
        
        logger.info("[API-KEYS] Cache miss - fetching fresh data")
        
        service = ApiKeyService(supabase_client)
        
        keys = await service.get_all_keys()
        if not keys:
            return {"status": "error", "message": "No API keys found"}
        
        logger.info(f"[API-KEYS] Found {len(keys)} keys")
        
        # 🔧 השתמש בoverride אם קיים, אחרת נסה לקבל מAI service
        if _current_key_index_override is not None:
            current_key_index = _current_key_index_override
            logger.info(f"[API-KEYS] Using override current key index: {current_key_index}")
        else:
            current_key_index = await service.get_current_active_key_index()
            logger.info(f"[API-KEYS] Current key index from AI service: {current_key_index}")
        
        from datetime import date, timezone, datetime
        today = date.today().isoformat()
        current_minute_utc = datetime.now(timezone.utc).replace(second=0, microsecond=0)
        
        key_ids = [key["id"] for key in keys]
        
        # 🔧 שיפור: קריאה אחת עם aggregation במקום שתיים נפרדות
        logger.info("[API-KEYS] Starting aggregated usage queries...")
        start_time = time.time()
        
        # קריאה יחידה עם סינון מתקדם לשני סוגי הנתונים
        try:
            # 🚀 נסה להשתמש בfunction החדש שמחזיר הכל בקריאה אחת
            all_stats_response = supabase_client.rpc("get_all_keys_usage_stats", {
                "target_date": today,
                "target_minute": current_minute_utc.isoformat()
            }).execute()
            
            logger.info(f"[API-KEYS] Single comprehensive query took {time.time() - start_time:.2f}s")
            
            # המרה לפורמט הישן של המערכת
            daily_usage = {}
            minute_usage = {}
            
            if all_stats_response.data:
                for row in all_stats_response.data:
                    key_id = row["api_key_id"]
                    daily_usage[key_id] = {
                        "tokens": row["daily_tokens"],
                        "requests": row["daily_requests"]
                    }
                    minute_usage[key_id] = {
                        "tokens": row["minute_tokens"],
                        "requests": row["minute_requests"]
                    }
            
            logger.info(f"[API-KEYS] ✅ Used optimized RPC - processed {len(daily_usage)} keys in {time.time() - start_time:.2f}s")
            
        except Exception as e:
            logger.warning(f"[API-KEYS] 🔄 Optimized RPC not available, using fallback aggregation: {e}")
            
            # Fallback לRPC functions נפרדים
            try:
                # Daily aggregation בקריאה אחת
                daily_response = supabase_client.rpc("aggregate_daily_usage", {
                    "target_date": today,
                    "key_ids": key_ids
                }).execute()
                
                minute_response = supabase_client.rpc("aggregate_minute_usage", {
                    "target_minute": current_minute_utc.isoformat(),
                    "key_ids": key_ids
                }).execute()
                
                # המרה לפורמט רצוי
                daily_usage = {}
                minute_usage = {}
                
                if daily_response.data:
                    for row in daily_response.data:
                        daily_usage[row["api_key_id"]] = {
                            "tokens": row["total_tokens"],
                            "requests": row["total_requests"]
                        }
                
                if minute_response.data:
                    for row in minute_response.data:
                        minute_usage[row["api_key_id"]] = {
                            "tokens": row["total_tokens"],
                            "requests": row["total_requests"]
                        }
                
                logger.info(f"[API-KEYS] ✅ Used separate RPC functions in {time.time() - start_time:.2f}s")
                
            except Exception as e2:
                logger.warning(f"[API-KEYS] 🔄 RPC functions not available, using manual queries: {e2}")
                
                # Fallback לקריאות מקוריות
                daily_response = supabase_client.table("api_key_usage")\
                    .select("api_key_id,tokens_used,requests_count")\
                    .in_("api_key_id", key_ids)\
                    .eq("usage_date", today)\
                    .limit(10000)\
                    .execute()  # 🔧 הגבלת תוצאות

                minute_response = supabase_client.table("api_key_usage")\
                    .select("api_key_id,tokens_used,requests_count")\
                    .in_("api_key_id", key_ids)\
                    .eq("usage_minute", current_minute_utc.isoformat())\
                    .limit(1000)\
                    .execute()  # 🔧 הגבלת תוצאות למניעת עומס
                
                # חזרה לעיבוד הישן
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
                
                logger.info(f"[API-KEYS] ⚠️ Used legacy manual queries in {time.time() - start_time:.2f}s")
        
        query_time = time.time() - start_time
        logger.info(f"[API-KEYS] Total query time: {query_time:.2f}s")
        
        # אם הקריאות לוקחות יותר מ-5 שניות, החזר קאש ישן אם קיים
        if query_time > 5.0 and _cache["data"] is not None:
            logger.warning(f"[API-KEYS] Queries too slow ({query_time:.1f}s), returning stale cache")
            stale_response = _cache["data"].copy()
            stale_response["cache_warning"] = f"Data may be up to {time.time() - _cache['timestamp']:.0f}s old due to slow queries"
            return stale_response
        
        keys_status = []
        total_tokens_today = 0
        total_requests_today = 0
        
        for i, key in enumerate(keys):
            key_id = key["id"]
            
            daily_data = daily_usage.get(key_id, {"tokens": 0, "requests": 0})
            minute_data = minute_usage.get(key_id, {"tokens": 0, "requests": 0})
            
            is_current = i == current_key_index
            status = "current" if is_current else "available"
            
            if daily_data["requests"] >= 900:
                status = "blocked"
            elif minute_data["requests"] >= 9:
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
                "last_used": None
            }
            
            keys_status.append(key_status)
            total_tokens_today += daily_data["tokens"]
            total_requests_today += daily_data["requests"]
        
        available_count = sum(1 for k in keys_status if k["status"] in ["available", "current"])
        blocked_count = sum(1 for k in keys_status if k["status"] in ["blocked", "rate_limited"])
        
        # 🆕 הוסף current_key_usage למידע
        current_key_data = None
        if 0 <= current_key_index < len(keys):
            current_db_key = keys[current_key_index]
            current_daily_data = daily_usage.get(current_db_key["id"], {"tokens": 0, "requests": 0})
            current_minute_data = minute_usage.get(current_db_key["id"], {"tokens": 0, "requests": 0})
            
            current_key_data = {
                "current_key_index": current_key_index,
                "tokens_today": current_daily_data["tokens"],
                "tokens_current_minute": current_minute_data["tokens"],
                "requests_today": current_daily_data["requests"],
                "requests_current_minute": current_minute_data["requests"],
                "status": "current",
                "key_name": current_db_key.get("key_name", f"Key #{current_key_index + 1}")
            }
        
        response = {
            "status": "ok",
            "key_management": {
                "total_keys": len(keys),
                "available_keys": available_count,
                "blocked_keys": blocked_count,
                "current_key_index": current_key_index,
                "keys_status": keys_status,
                "current_key_usage": current_key_data,  # 🆕 הוסף את החלק החסר
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
                "keys_status": [],
                "current_key_usage": None
            }
        }

@router.post("/{key_id}/usage")
async def record_usage(
    key_id: int,
    request: Request,
    supabase_client = Depends(get_supabase_client)
):
    """Record key usage - accepts JSON body with tokens_used and requests_count"""
    try:
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
        
        # 🔧 בטל קאש כדי שהדשבורד יעדכן מיד
        invalidate_cache()
        
        logger.info(f"[USAGE-API] Recorded {tokens_used} tokens, {requests_count} requests for key {key_id}")
        return {"status": "recorded", "tokens_used": tokens_used, "requests_count": requests_count}
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in request body")
    except Exception as e:
        logger.error(f"Error recording usage for key {key_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to record usage: {str(e)}")

@router.post("/test/simulate-usage/{key_id}")
async def simulate_heavy_usage(
    key_id: int,
    requests_to_add: int = 10,
    supabase_client = Depends(get_supabase_client)
):
    """Simulate heavy usage for rotation testing"""
    try:
        service = ApiKeyService(supabase_client)
        
        logger.info(f"[TEST] Simulating {requests_to_add} requests for key {key_id}")
        
        for i in range(requests_to_add):
            await service.record_usage(key_id, 100, 1)
        
        # 🔧 בטל קאש אחרי סימולציה
        invalidate_cache()
        
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
    """Check key limits status"""
    try:
        service = ApiKeyService(supabase_client)
        usage = await service.get_key_current_usage(key_id)
        
        max_requests_per_minute = 15
        max_requests_per_day = 1500
        max_tokens_per_day = 1000000
        
        minute_percentage = (usage["minute_requests"] / max_requests_per_minute) * 100
        daily_requests_percentage = (usage["daily_requests"] / max_requests_per_day) * 100
        daily_tokens_percentage = (usage["daily_tokens"] / max_tokens_per_day) * 100
        
        is_minute_limited = usage["minute_requests"] >= (max_requests_per_minute * 0.6)
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

_fast_cache = {
    "keys": None,
    "timestamp": 0,
    "ttl": 1800
}

def get_fast_cached_keys() -> Optional[List[Dict[str, Any]]]:
    """Get cached keys if still valid"""
    if _fast_cache["keys"] is None:
        return None
    
    age = time.time() - _fast_cache["timestamp"]
    if age > _fast_cache["ttl"]:
        _fast_cache["keys"] = None
        return None
    
    return _fast_cache["keys"]

def set_fast_cached_keys(keys: List[Dict[str, Any]]):
    """Cache the keys for fast access"""
    _fast_cache["keys"] = keys
    _fast_cache["timestamp"] = time.time()

@router.get("/for-ai-service")
async def get_keys_for_ai_service(
    supabase_client = Depends(get_supabase_client)
) -> Dict[str, Any]:
    """Fast: Get API keys for AI service with minimal overhead"""
    try:
        cached_keys = get_fast_cached_keys()
        if cached_keys:
            logger.info(f"[FAST-CACHE] Returning {len(cached_keys)} cached keys")
            return {
                "status": "ok",
                "keys": cached_keys,
                "total_keys": len(cached_keys)
            }
        
        logger.info("[AI-SERVICE] Cache miss - fetching fresh data")
        
        response = supabase_client.table("api_keys")\
            .select("id, key_name, api_key, is_active, created_at")\
            .eq("is_active", True)\
            .execute()
        
        keys = response.data or []
        logger.info(f"[AI-SERVICE] Found {len(keys)} active API keys")
        
        set_fast_cached_keys(keys)
        
        return {
            "status": "ok",
            "keys": keys,
            "total_keys": len(keys)
        }
        
    except Exception as e:
        logger.error(f"[AI-SERVICE] Error getting API keys: {e}")
        return {
            "status": "error", 
            "message": str(e),
            "keys": []
        }

@router.post("/set-current")
async def set_current_key_index(request: Request):
    """Set current key index from DatabaseKeyManager"""
    global _current_key_index_override
    try:
        body = await request.json()
        new_index = body.get('current_key_index')
        old_index = body.get('old_key_index')
        
        if new_index is None:
            raise HTTPException(status_code=400, detail="current_key_index is required")
        
        _current_key_index_override = new_index
        logger.info(f"[KEY-ROTATION] Updated current key index: {old_index} → {new_index}")
        
        # ביטול קאש כדי שהנתונים החדשים יוצגו מיד
        invalidate_cache()
        
        return {
            "status": "ok",
            "old_index": old_index,
            "new_index": new_index,
            "message": f"Current key index updated to {new_index}"
        }
        
    except Exception as e:
        logger.error(f"Error setting current key index: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to set current key index: {str(e)}")