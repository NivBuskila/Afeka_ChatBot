import asyncio
import logging
import os
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from supabase import create_client, Client

logger = logging.getLogger(__name__)

class DatabaseKeyManager:
    """מנגנון ניהול מפתחות מהדאטה בייס"""
    
    def __init__(self, use_direct_supabase: bool = False):
        self.api_keys: List[Dict[str, Any]] = []
        self.current_key_index = 0
        self.use_direct_supabase = use_direct_supabase
        self.last_refresh = None
        self.refresh_interval = 300  # 5 minutes
        
        # ⚡ Performance: Track key usage for smart rotation
        self.key_usage_stats = {}
        self.rotation_threshold = 5  # 🔥 REDUCED: Rotate after 5 requests for testing
        self.rate_limit_cooldown = 60  # 1 minute cooldown for rate-limited keys
        
        # Initialize supabase client based on configuration
        if self.use_direct_supabase:
            # Direct connection to Supabase (best for server-side services)
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")
            
            if not supabase_url or not supabase_key:
                raise ValueError("Missing Supabase configuration for direct connection")
            
            self.supabase = create_client(supabase_url, supabase_key)
            logger.info("🔑 DatabaseKeyManager initialized with direct Supabase connection")
        else:
            # HTTP-based connection (for external API calls)
            import httpx
            self.client = httpx.AsyncClient(timeout=30.0)
            self.base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
            logger.info("🔑 DatabaseKeyManager initialized with HTTP client")
            
        # Auto-refresh keys periodically 
        self._auto_refresh_task = None
        self._start_auto_refresh()
        
        # 🔥 FIX: Load keys immediately on initialization
        self._initial_load_done = False

    def _start_auto_refresh(self):
        """Start background task for automatic key refresh"""
        async def auto_refresh_loop():
            while True:
                try:
                    await asyncio.sleep(self.refresh_interval)
                    await self.refresh_keys()
                    logger.info("🔄 Keys auto-refreshed successfully")
                except Exception as e:
                    logger.error(f"❌ Auto-refresh failed: {e}")
                    await asyncio.sleep(60)  # Retry in 1 minute on failure
        
        # Start background task if event loop is running
        try:
            loop = asyncio.get_running_loop()
            self._auto_refresh_task = loop.create_task(auto_refresh_loop())
        except RuntimeError:
            # No event loop running, will be started when needed
            logger.info("🔄 Auto-refresh will start when event loop is available")

    async def _should_rotate_key(self, key_data: Dict[str, Any]) -> bool:
        """Check if current key should be rotated based on usage patterns"""
        key_id = key_data.get('id')
        
        # Check in-memory usage count (for session-based rotation)
        usage_count = self.key_usage_stats.get(key_id, {}).get('count', 0)
        if usage_count >= self.rotation_threshold:
            logger.info(f"🔄 Key {key_data.get('key_name')} reached session rotation threshold ({usage_count} requests)")
            return True
        
        # 🔥 NEW: Check database usage for current minute (for real-time rotation)
        try:
            if not self.use_direct_supabase:
                # Get current minute usage from API
                current_time = datetime.now().replace(second=0, microsecond=0)
                minute_str = current_time.strftime('%Y-%m-%dT%H:%M:00+00:00')
                
                # Make a quick check to the API for current usage
                response = await self.client.get(f"{self.base_url}/api/keys/")
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == 'ok':
                        keys_status = data.get('key_management', {}).get('keys_status', [])
                        for key_status in keys_status:
                            if key_status.get('id') == key_id:
                                current_minute_requests = key_status.get('requests_current_minute', 0)
                                # Rotate if current minute has high usage (15+ requests per minute = aggressive usage)
                                if current_minute_requests >= 15:
                                    logger.info(f"🔄 Key {key_data.get('key_name')} high current minute usage ({current_minute_requests} requests)")
                                    return True
                                break
        except Exception as e:
            logger.debug(f"Could not check database usage for rotation: {e}")
        
        # Check for rate limiting
        last_rate_limit = self.key_usage_stats.get(key_id, {}).get('last_rate_limit')
        if last_rate_limit:
            time_since_limit = time.time() - last_rate_limit
            if time_since_limit < self.rate_limit_cooldown:
                logger.info(f"🚫 Key {key_data.get('key_name')} still in cooldown ({int(self.rate_limit_cooldown - time_since_limit)}s remaining)")
                return True
        
        return False

    async def _get_next_available_key(self) -> Optional[Dict[str, Any]]:
        """Find next available key that's not rate-limited"""
        if not self.api_keys:
            await self.refresh_keys()
        
        if not self.api_keys:
            return None
        
        # 🔥 IMPROVED: Simple rotation logic - rotate on every request
        # This ensures all keys get used and no single key gets overloaded
        logger.info(f"🔄 Rotating from key index {self.current_key_index} to {(self.current_key_index + 1) % len(self.api_keys)}")
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        
        # Return the current key
        current_key = self.api_keys[self.current_key_index]
        logger.info(f"🔑 Selected key: {current_key.get('key_name', f'Key {self.current_key_index}')} (index: {self.current_key_index})")
        return current_key

    async def refresh_keys(self):
        """Refresh API keys from database"""
        try:
            if self.use_direct_supabase:
                # Direct Supabase query
                response = self.supabase.table('api_keys').select('*').eq('is_active', True).execute()
                self.api_keys = response.data or []
            else:
                # HTTP request to our API
                response = await self.client.get(f"{self.base_url}/api/keys/")
                response.raise_for_status()
                keys_data = response.json()
                
                # 🔥 FIX: Handle correct response format
                if keys_data.get('status') == 'ok' and 'key_management' in keys_data:
                    # Get the raw API key data from database for token usage
                    # The keys_status array doesn't have the actual API keys, just usage stats
                    # We need to fetch the actual keys from Supabase
                    if hasattr(self, 'supabase') and self.supabase:
                        db_response = self.supabase.table('api_keys').select('*').eq('is_active', True).execute()
                        self.api_keys = db_response.data or []
                    else:
                        # Since we don't have direct Supabase access, we need to get the keys via another endpoint
                        # Create a new endpoint that returns actual key data for the AI service
                        try:
                            # Try to get keys from a dedicated AI service endpoint
                            ai_response = await self.client.get(f"{self.base_url}/api/keys/for-ai-service")
                            if ai_response.status_code == 200:
                                ai_keys_data = ai_response.json()
                                self.api_keys = ai_keys_data.get('keys', [])
                            else:
                                # Fallback: create dummy key entries based on keys_status
                                keys_status = keys_data['key_management'].get('keys_status', [])
                                self.api_keys = []
                                for i, key_stat in enumerate(keys_status):
                                    self.api_keys.append({
                                        'id': key_stat.get('id', i + 8),  # Use actual ID if available
                                        'key_name': f'Key {i}',
                                        'is_active': True,
                                        'index': i
                                    })
                        except Exception as endpoint_error:
                            logger.warning(f"Failed to get keys from AI endpoint: {endpoint_error}")
                            # Final fallback: create dummy key entries
                            keys_status = keys_data['key_management'].get('keys_status', [])
                            self.api_keys = []
                            for i, key_stat in enumerate(keys_status):
                                self.api_keys.append({
                                    'id': key_stat.get('id', i + 8),
                                    'key_name': f'Key {i}',
                                    'is_active': True,
                                    'index': i
                                })
                else:
                    # Fallback to old format
                    self.api_keys = keys_data.get('keys', [])
            
            self.last_refresh = datetime.now()
            logger.info(f"✅ Refreshed {len(self.api_keys)} API keys from database")
            
            # Reset current index if it's out of bounds
            if self.current_key_index >= len(self.api_keys):
                self.current_key_index = 0
                
        except Exception as e:
            logger.error(f"❌ Failed to refresh API keys: {e}")
            if not self.api_keys:
                raise Exception("No API keys available and refresh failed")

    async def get_available_key(self) -> Optional[Dict[str, Any]]:
        """Get next available API key with smart rotation"""
        try:
            # 🔥 FIX: Ensure initial load is done
            if not self._initial_load_done:
                await self.refresh_keys()
                self._initial_load_done = True
            
            # Refresh keys if needed
            if (not self.last_refresh or 
                (datetime.now() - self.last_refresh).seconds > self.refresh_interval):
                await self.refresh_keys()
            
            # Get next available key
            key_data = await self._get_next_available_key()
            if not key_data:
                raise Exception("No available API keys found")
            
            # Track usage
            key_id = key_data.get('id')
            if key_id not in self.key_usage_stats:
                self.key_usage_stats[key_id] = {'count': 0, 'last_used': time.time()}
            
            self.key_usage_stats[key_id]['count'] += 1
            self.key_usage_stats[key_id]['last_used'] = time.time()
            
            logger.info(f"🔑 Using key: {key_data.get('key_name')} (usage: {self.key_usage_stats[key_id]['count']})")
            return key_data
            
        except Exception as e:
            logger.error(f"❌ Error getting available key: {e}")
            return None

    async def record_usage(self, key_id: int, tokens_used: int, requests_count: int = 1):
        """Record API key usage for analytics and rotation decisions"""
        try:
            if self.use_direct_supabase:
                # Direct database insert - 🔥 FIX: Use correct schema
                from datetime import date, timezone
                current_time_utc = datetime.now(timezone.utc).replace(second=0, microsecond=0)
                
                self.supabase.table('api_key_usage').insert({
                    'api_key_id': key_id,
                    'usage_date': date.today().isoformat(),
                    'usage_minute': current_time_utc.isoformat(),
                    'tokens_used': tokens_used,
                    'requests_count': requests_count
                }).execute()
            else:
                # HTTP request to our API
                await self.client.post(f"{self.base_url}/api/keys/{key_id}/usage", json={
                    'tokens_used': tokens_used,
                    'requests_count': requests_count
                })
                
            logger.info(f"📊 Recorded {tokens_used} tokens usage for key {key_id}")
        except Exception as e:
            logger.error(f"❌ Failed to record usage: {e}")

    async def mark_rate_limited(self, key_id: int):
        """Mark a key as rate-limited for temporary avoidance"""
        if key_id in self.key_usage_stats:
            self.key_usage_stats[key_id]['last_rate_limit'] = time.time()
            logger.warning(f"🚫 Key {key_id} marked as rate-limited")

    # Backward compatibility methods
    async def ensure_available_key(self) -> Optional[Dict[str, Any]]:
        """Backward compatibility - same as get_available_key"""
        return await self.get_available_key()

    async def track_usage(self, key_id: int, tokens_used: int, requests_count: int = 1):
        """Backward compatibility - same as record_usage"""
        return await self.record_usage(key_id, tokens_used, requests_count)

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics for monitoring"""
        return {
            'total_keys': len(self.api_keys),
            'current_key_index': self.current_key_index,
            'last_refresh': self.last_refresh.isoformat() if self.last_refresh else None,
            'key_usage_stats': self.key_usage_stats,
            'rotation_threshold': self.rotation_threshold
        }

    async def get_detailed_status(self) -> Dict[str, Any]:
        """Get detailed status with all keys information for frontend display"""
        logger.info("📊 [DATABASE-KEY-MANAGER] Getting detailed status...")
        
        # Ensure we have fresh data
        if not self._initial_load_done:
            await self.refresh_keys()
            self._initial_load_done = True
        
        # 🚀 OPTIMIZED: Single batch query for all keys usage
        try:
            from datetime import date, timezone, datetime
            today = date.today().isoformat()
            current_minute_utc = datetime.now(timezone.utc).replace(second=0, microsecond=0)
            
            # Get all active key IDs
            key_ids = [key_data.get('id') for key_data in self.api_keys]
            
            # 🚀 SINGLE QUERY for all daily usage
            daily_response = self.supabase.table("api_key_usage")\
                .select("api_key_id,tokens_used,requests_count")\
                .in_("api_key_id", key_ids)\
                .eq("usage_date", today)\
                .execute()
            
            # 🚀 SINGLE QUERY for all current minute usage
            minute_response = self.supabase.table("api_key_usage")\
                .select("api_key_id,tokens_used,requests_count")\
                .in_("api_key_id", key_ids)\
                .eq("usage_minute", current_minute_utc.isoformat())\
                .execute()
            
            # Process results into dictionaries for fast lookup
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
            
            logger.info(f"📊 [DATABASE-KEY-MANAGER] Batch query complete: {len(daily_response.data)} daily records, {len(minute_response.data)} minute records")
            
        except Exception as e:
            logger.error(f"❌ [DATABASE-KEY-MANAGER] Error in batch queries: {e}")
            daily_usage = {}
            minute_usage = {}
        
        # Build keys status using the batch query results
        keys_status = []
        total_tokens_today = 0
        total_requests_today = 0
        
        for i, key_data in enumerate(self.api_keys):
            key_id = key_data.get('id')
            is_current = i == self.current_key_index
            
            # Get usage from batch results
            daily_data = daily_usage.get(key_id, {"tokens": 0, "requests": 0})
            minute_data = minute_usage.get(key_id, {"tokens": 0, "requests": 0})
            
            tokens_today = daily_data["tokens"]
            requests_today = daily_data["requests"]
            tokens_current_minute = minute_data["tokens"]
            requests_current_minute = minute_data["requests"]
            
            # Determine status based on rate limits
            status = "current" if is_current else "available"
            
            # Simple rate limit check (can be enhanced)
            if tokens_today > 800000 or requests_today > 1400:  # Near daily limits
                status = "blocked"
            
            keys_status.append({
                "id": i,
                "is_current": is_current,
                "status": status,
                "tokens_today": tokens_today,
                "requests_today": requests_today,
                "tokens_current_minute": tokens_current_minute,
                "requests_current_minute": requests_current_minute,
                "last_used": None,  # Could be enhanced with last_used tracking
                "first_used_today": None  # Could be enhanced
            })
            
            total_tokens_today += tokens_today
            total_requests_today += requests_today
        
        available_count = sum(1 for k in keys_status if k["status"] == "available")
        blocked_count = sum(1 for k in keys_status if k["status"] == "blocked")
        
        result = {
            "total_keys": len(self.api_keys),
            "available_keys": available_count + 1,  # +1 for current key
            "blocked_keys": blocked_count,
            "current_key_index": self.current_key_index,
            "keys_status": keys_status,
            "daily_summary": {
                "total_tokens": total_tokens_today,
                "total_requests": total_requests_today,
                "active_keys": len([k for k in keys_status if k["tokens_today"] > 0])
            },
            "last_updated": datetime.now().isoformat()
        }
        
        logger.info(f"📊 [DATABASE-KEY-MANAGER] Returning optimized status with {len(keys_status)} keys, current: {self.current_key_index}")
        return result

    def __del__(self):
        """Clean up background tasks"""
        if self._auto_refresh_task and not self._auto_refresh_task.done():
            self._auto_refresh_task.cancel()

