from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from ...services.api_key_services import ApiKeyService
from src.backend.core.dependencies import get_supabase_client
import logging

router = APIRouter(prefix="/api/keys", tags=["API Keys"])

logger = logging.getLogger(__name__)

@router.get("/")
async def get_api_keys(
    supabase_client = Depends(get_supabase_client)
) -> Dict[str, Any]:
    """קבלת כל המפתחות מהדאטה בייס בפורמט נכון"""
    service = ApiKeyService(supabase_client)
    
    try:
        keys = await service.get_all_keys()
        
        if not keys:
            # אם אין מפתחות בדאטה בייס, החזר fallback response
            return {
                "status": "error", 
                "message": "No API keys found in database. Please run migration.",
                "keys": [],
                "key_management": {
                    "current_key_index": 0,
                    "total_keys": 0,
                    "available_keys": 0,
                    "keys_status": []
                }
            }
        
        # יצירת keys_status מהדאטה בייס
        keys_status = []
        
        # 🆕 קבלת המפתח הפעיל האמיתי מה-AI service
        current_key_index = await service.get_current_active_key_index()
        
        for i, key in enumerate(keys):
            usage = await service.get_key_current_usage(key["id"])
            
            # קביעת סטטוס מפתח בהתאם לשימוש עם safety margin של 60%
            status = "available"
            is_current = (i == current_key_index)
            
            # חישוב מגבלות עם safety margin (60% כמו ב-AI service)
            safety_margin = 0.6
            daily_request_limit = key.get("daily_limit_requests", 1500) * safety_margin
            daily_token_limit = key.get("daily_limit_tokens", 1000000) * safety_margin
            minute_request_limit = key.get("minute_limit_requests", 15) * safety_margin
            
            # בדיקת מגבלות עם המרווח ביטחון
            if usage.get("daily_requests", 0) >= daily_request_limit:
                status = "blocked"
            elif usage.get("daily_tokens", 0) >= daily_token_limit:
                status = "blocked"  
            elif usage.get("minute_requests", 0) >= minute_request_limit:
                status = "rate_limited"
            
            # אם זה המפתח הנוכחי, תן לו סטטוס "current" (גם אם rate_limited)
            if is_current:
                if status == "blocked":
                    status = "blocked"  # חסום נשאר חסום
                else:
                    status = "current"  # זמין או rate_limited הופך ל-current
            
            keys_status.append({
                "id": i,
                "key_id": key["id"],
                "key_name": key["key_name"],
                "status": status,
                "is_current": is_current,
                "tokens_today": usage.get("daily_tokens", 0),
                "tokens_limit": key.get("daily_limit_tokens", 1000000),
                "requests_today": usage.get("daily_requests", 0),
                "requests_limit": key.get("daily_limit_requests", 1500),
                "tokens_current_minute": usage.get("minute_tokens", 0),
                "requests_current_minute": usage.get("minute_requests", 0),
                "minute_limit": key.get("minute_limit_requests", 15),
                "usage_percentage": round((usage.get("daily_tokens", 0) / key.get("daily_limit_tokens", 1000000)) * 100, 1),
                "last_used": None,
                "first_used_today": None
            })
        
        # 🆕 הוספת נתוני המפתח הנוכחי למענה 
        current_key_usage = {}
        if 0 <= current_key_index < len(keys_status):
            current_key_data = keys_status[current_key_index]
            current_key_usage = {
                "current_key_index": current_key_index,
                "key_name": current_key_data["key_name"],
                "tokens_today": current_key_data["tokens_today"],
                "tokens_current_minute": current_key_data["tokens_current_minute"],
                "requests_today": current_key_data["requests_today"],
                "requests_current_minute": current_key_data["requests_current_minute"],
                "status": current_key_data["status"]
            }

        return {
            "status": "ok",
            "keys": keys,  # For DatabaseKeyManager
            "key_management": {
                "current_key_index": current_key_index,
                "total_keys": len(keys),
                "available_keys": len([k for k in keys_status if k["status"] not in ["blocked"]]),
                "keys_status": keys_status,
                "current_key_usage": current_key_usage  # 🆕 נתוני המפתח הנוכחי
            }
        }

    except Exception as e:
        logger.error(f"Error in get_api_keys: {e}")
        return {
            "status": "error",
            "message": f"Database error: {str(e)}",
            "keys": [],
            "key_management": {
                "current_key_index": 0,
                "total_keys": 0,
                "available_keys": 0,
                "keys_status": []
            }
        }

@router.post("/{key_id}/usage")
async def record_usage(
    key_id: int,
    tokens_used: int,
    requests_count: int = 1,
    supabase_client = Depends(get_supabase_client)
):
    """רישום שימוש במפתח"""
    service = ApiKeyService(supabase_client)
    await service.record_usage(key_id, tokens_used, requests_count)
    return {"status": "recorded"}
