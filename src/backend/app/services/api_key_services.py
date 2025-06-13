from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta, timezone
import logging
from supabase import Client
import httpx
import os
from functools import lru_cache

logger = logging.getLogger(__name__)

class ApiKeyService:
    def __init__(self, supabase: Client):
        self.supabase = supabase
        self._usage_cache = {}
        self._cache_timeout = timedelta(minutes=1)
    
    async def get_all_keys(self) -> List[Dict[str, Any]]:
        """קבלת כל המפתחות הפעילים"""
        try:
            response = self.supabase.table("api_keys").select("*").eq("is_active", True).execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching API keys: {e}")
            return []
    
    async def get_current_active_key_index(self) -> int:
        """קבלת אינדקס המפתח הפעיל הנוכחי מה-AI service"""
        try:
            ai_service_url = os.environ.get("AI_SERVICE_URL", "http://localhost:5000")
            
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{ai_service_url}/status")
                if response.status_code == 200:
                    data = response.json()
                    current_index = data.get("key_management", {}).get("current_key_index", 0)
                    logger.info(f"🔍 Got current key index from AI service: {current_index}")
                    return current_index
                else:
                    logger.warning(f"AI service status check failed: {response.status_code}")
                    return 0
        except Exception as e:
            logger.warning(f"Could not get current key from AI service: {e}")
            return 0  # fallback לפערך ראשון
    
    async def get_key_current_usage(self, key_id: int) -> Dict[str, int]:
        """קבלת שימוש נוכחי של מפתח עם cache"""
        today = date.today().isoformat()
        # שימוש בזמן UTC כדי להתאים לדאטה בייס
        current_minute_utc = datetime.now(timezone.utc).replace(second=0, microsecond=0)
        
        try:
            # 🚀 FIXED: Separate queries but optimized logic
            # Daily usage
            daily_response = self.supabase.table("api_key_usage")\
                .select("tokens_used,requests_count")\
                .eq("api_key_id", key_id)\
                .eq("usage_date", today)\
                .execute()
            
            daily_tokens = sum([row["tokens_used"] for row in daily_response.data])
            daily_requests = sum([row["requests_count"] for row in daily_response.data])
            
            # Current minute usage
            minute_response = self.supabase.table("api_key_usage")\
                .select("tokens_used,requests_count")\
                .eq("api_key_id", key_id)\
                .eq("usage_minute", current_minute_utc.isoformat())\
                .execute()
            
            minute_tokens = sum([row["tokens_used"] for row in minute_response.data])
            minute_requests = sum([row["requests_count"] for row in minute_response.data])
            
            logger.info(f"🔍 [FIXED-USAGE] Key {key_id}: Daily={daily_tokens}t/{daily_requests}r, Minute={minute_tokens}t/{minute_requests}r")
            
            usage_data = {
                "daily_tokens": daily_tokens,
                "daily_requests": daily_requests,
                "minute_tokens": minute_tokens,
                "minute_requests": minute_requests
            }
            
            return usage_data
            
        except Exception as e:
            logger.error(f"Error fetching usage for key {key_id}: {e}")
            return {"daily_tokens": 0, "daily_requests": 0, "minute_tokens": 0, "minute_requests": 0}
    
    async def record_usage(self, key_id: int, tokens_used: int, requests_count: int = 1):
        """רישום שימוש"""
        try:
            current_minute_utc = datetime.now(timezone.utc).replace(second=0, microsecond=0)
            
            # בדוק אם יש כבר רשומה לדקה הזו (UTC)
            existing = self.supabase.table("api_key_usage")\
                .select("id,tokens_used,requests_count")\
                .eq("api_key_id", key_id)\
                .eq("usage_minute", current_minute_utc.isoformat())\
                .execute()
            
            if existing.data:
                # עדכן רשומה קיימת
                record_id = existing.data[0]["id"]
                new_tokens = existing.data[0]["tokens_used"] + tokens_used
                new_requests = existing.data[0]["requests_count"] + requests_count
                
                self.supabase.table("api_key_usage")\
                    .update({"tokens_used": new_tokens, "requests_count": new_requests})\
                    .eq("id", record_id)\
                    .execute()
            else:
                # יצור רשומה חדשה
                self.supabase.table("api_key_usage").insert({
                    "api_key_id": key_id,
                    "usage_date": date.today().isoformat(),
                    "usage_minute": current_minute_utc.isoformat(),
                    "tokens_used": tokens_used,
                    "requests_count": requests_count
                }).execute()
                
            logger.info(f"✅ Recorded usage for key {key_id}: {tokens_used} tokens, {requests_count} requests")
            
        except Exception as e:
            logger.error(f"❌ Error recording usage for key {key_id}: {e}")

