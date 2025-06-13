import httpx
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone
import os

logger = logging.getLogger(__name__)

class DatabaseKeyManager:
    """מנגנון ניהול מפתחות מהדאטה בייס"""
    
    def __init__(self, backend_url: str = "http://localhost:8000", use_direct_supabase: bool = False):
        self.backend_url = backend_url
        self.api_keys = []
        self.current_key_index = 0
        self.last_refresh = None
        self.use_direct_supabase = use_direct_supabase
        
        # אם משתמשים בחיבור ישיר, אתחל Supabase
        if use_direct_supabase:
            self._init_supabase()
    
    def _init_supabase(self):
        """אתחול חיבור ישיר ל-Supabase"""
        try:
            from supabase import create_client
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")
            
            if supabase_url and supabase_key:
                self.supabase = create_client(supabase_url, supabase_key)
                logger.info(f"✅ Direct Supabase connection initialized with URL: {supabase_url}")
                logger.info(f"✅ Using key starting with: {supabase_key[:20]}...")
            else:
                logger.error("❌ Missing Supabase credentials for direct connection")
                logger.error(f"SUPABASE_URL: {'Found' if supabase_url else 'Missing'}")
                logger.error(f"SUPABASE_KEY: {'Found' if supabase_key else 'Missing'}")
                self.supabase = None
        except Exception as e:
            logger.error(f"❌ Failed to initialize direct Supabase connection: {e}")
            self.supabase = None
    
    async def refresh_keys(self):
        """רענון רשימת המפתחות מהדאטה בייס"""
        if self.use_direct_supabase and self.supabase:
            return await self._refresh_keys_direct()
        else:
            return await self._refresh_keys_http()
    
    async def _refresh_keys_direct(self):
        """טעינה ישירה מ-Supabase ללא HTTP"""
        try:
            logger.info("🔄 Loading keys directly from Supabase")
            
            if not self.supabase:
                logger.error("❌ Supabase client not initialized")
                return
                
            logger.info("📡 Executing query: SELECT * FROM api_keys WHERE is_active = true")
            response = self.supabase.table("api_keys").select("*").eq("is_active", True).execute()
            
            logger.info(f"📦 Supabase response received")
            logger.info(f"📦 Response data: {response.data}")
            logger.info(f"📦 Response count: {response.count if hasattr(response, 'count') else 'N/A'}")
            
            if response.data:
                self.api_keys = response.data
                self.last_refresh = datetime.now()
                logger.info(f"✅ Loaded {len(self.api_keys)} API keys directly from Supabase")
                
                # הדפס פרטי המפתחות (ללא החשיפת המפתח עצמו)
                for i, key in enumerate(self.api_keys):
                    logger.info(f"🔑 Key {i}: ID={key.get('id')}, Name={key.get('key_name')}, Active={key.get('is_active')}")
            else:
                logger.warning("⚠️  No active API keys found in database")
                self.api_keys = []
                
        except Exception as e:
            logger.error(f"❌ Error loading keys directly from Supabase: {e}")
            import traceback
            logger.error(f"🔍 Full traceback: {traceback.format_exc()}")
    
    async def _refresh_keys_http(self):
        """טעינה דרך HTTP API (הדרך המקורית)"""
        try:
            logger.info(f"🔄 Attempting to connect to backend at {self.backend_url}/api/keys/")
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(f"{self.backend_url}/api/keys/")
                
            logger.info(f"📡 Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"📦 Response data structure: {list(data.keys())}")
                
                if "keys" in data:
                    self.api_keys = data["keys"]
                    self.last_refresh = datetime.now()
                    logger.info(f"✅ Refreshed {len(self.api_keys)} API keys from database")
                else:
                    logger.error(f"❌ Missing 'keys' field in response: {data}")
            else:
                logger.error(f"❌ Failed to refresh keys: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"❌ Error refreshing keys: {e}")
            import traceback
            logger.error(f"🔍 Full traceback: {traceback.format_exc()}")
    
    async def get_available_key(self) -> Optional[Dict[str, Any]]:
        """קבלת מפתח זמין"""
        # רענן מפתחות אם עבר יותר מ-5 דקות
        if not self.last_refresh or datetime.now() - self.last_refresh > timedelta(minutes=5):
            await self.refresh_keys()
        
        if not self.api_keys:
            return None
            
        # מצא מפתח זמין
        for key in self.api_keys:
            if self._is_key_available(key):
                return key
        
        return None
    
    def _is_key_available(self, key: Dict[str, Any]) -> bool:
        """בדיקה אם מפתח זמין לשימוש"""
        usage = key.get("current_usage", {})
        
        # בדוק מגבלות יומיות
        if usage.get("daily_tokens", 0) >= key.get("daily_limit_tokens", 1000000):
            return False
        if usage.get("daily_requests", 0) >= key.get("daily_limit_requests", 1500):
            return False
            
        # בדוק מגבלות דקה
        if usage.get("minute_requests", 0) >= key.get("minute_limit_requests", 15):
            return False
            
        return True
    
    async def ensure_available_key(self) -> bool:
        """Compatibility method that wraps get_available_key for existing code"""
        key = await self.get_available_key()
        return key is not None
    
    def track_usage(self, tokens_used: int = 100):
        """Compatibility method for tracking usage - implements basic tracking"""
        logger.info(f"📊 [DatabaseKeyManager] Tracking usage: {tokens_used} tokens")
        # Note: This is a compatibility method. Real tracking is done via record_usage()
        # when the key_id is available. This method is mainly for backward compatibility
        # with existing code that expects synchronous tracking.
    
    async def record_usage(self, key_id: int, tokens_used: int, requests_count: int = 1):
        """רישום שימוש"""
        if self.use_direct_supabase and self.supabase:
            return await self._record_usage_direct(key_id, tokens_used, requests_count)
        else:
            return await self._record_usage_http(key_id, tokens_used, requests_count)
    
    async def _record_usage_direct(self, key_id: int, tokens_used: int, requests_count: int = 1):
        """רישום שימוש ישירות ב-Supabase"""
        try:
            from datetime import datetime, date
            # שימוש בזמן UTC כדי להתאים לדאטה בייס
            current_minute = datetime.now(timezone.utc).replace(second=0, microsecond=0)
            
            # בדוק אם יש כבר רשומה לדקה הזו
            existing = self.supabase.table("api_key_usage")\
                .select("id,tokens_used,requests_count")\
                .eq("api_key_id", key_id)\
                .eq("usage_minute", current_minute.isoformat())\
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
                
                logger.info(f"✅ Updated usage record {record_id}: key={key_id}, tokens={new_tokens}, requests={new_requests}")
            else:
                # יצור רשומה חדשה
                new_record = {
                    "api_key_id": key_id,
                    "usage_date": date.today().isoformat(),
                    "usage_minute": current_minute.isoformat(),
                    "tokens_used": tokens_used,
                    "requests_count": requests_count
                }
                
                result = self.supabase.table("api_key_usage").insert(new_record).execute()
                logger.info(f"✅ Created new usage record: key={key_id}, tokens={tokens_used}, requests={requests_count}")
                
        except Exception as e:
            logger.error(f"❌ Error recording usage directly: {e}")
            import traceback
            logger.error(f"🔍 Full traceback: {traceback.format_exc()}")
    
    async def _record_usage_http(self, key_id: int, tokens_used: int, requests_count: int = 1):
        """רישום שימוש דרך HTTP API (הדרך המקורית)"""
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{self.backend_url}/api/keys/{key_id}/usage",
                    params={"tokens_used": tokens_used, "requests_count": requests_count}
                )
            logger.info(f"✅ Recorded usage: key={key_id}, tokens={tokens_used}")
        except Exception as e:
            logger.error(f"❌ Error recording usage: {e}")

