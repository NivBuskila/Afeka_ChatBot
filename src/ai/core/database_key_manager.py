import asyncio
import logging
import os
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from supabase import create_client, Client

logger = logging.getLogger(__name__)

class DatabaseKeyManager:
    """Database API key management system"""
    
    def __init__(self, use_direct_supabase: bool = False):
        self.api_keys: List[Dict[str, Any]] = []
        self.current_key_index = 0
        self.use_direct_supabase = use_direct_supabase
        self.last_refresh = None
        self.refresh_interval = 1800  # 30 minutes
        
        self.key_usage_stats = {}
        self.rotation_threshold = 3
        self.rate_limit_cooldown = 30
        
        if self.use_direct_supabase:
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")
            
            if not supabase_url or not supabase_key:
                raise ValueError("Missing Supabase configuration for direct connection")
            
            self.supabase = create_client(supabase_url, supabase_key)
            logger.info("DatabaseKeyManager initialized with direct Supabase connection")
        else:
            import httpx
            self.client = httpx.AsyncClient(timeout=30.0)
            self.base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
            logger.info("DatabaseKeyManager initialized with HTTP client")
            
        self._auto_refresh_task = None
        self._start_auto_refresh()
        self._initial_load_done = False

    def _start_auto_refresh(self):
        """Start background task for automatic key refresh"""
        async def auto_refresh_loop():
            while True:
                try:
                    await asyncio.sleep(self.refresh_interval)
                    await self.refresh_keys()
                    logger.info("Keys auto-refreshed successfully")
                except Exception as e:
                    logger.error(f"Auto-refresh failed: {e}")
                    await asyncio.sleep(300)  # 5 minutes instead of 1 minute
        
        try:
            loop = asyncio.get_running_loop()
            self._auto_refresh_task = loop.create_task(auto_refresh_loop())
        except RuntimeError:
            logger.info("Auto-refresh will start when event loop is available")

    async def _should_rotate_key(self, key_data: Dict[str, Any]) -> bool:
        """Check if current key should be rotated based on usage patterns"""
        key_id = key_data.get('id')
        
        usage_count = self.key_usage_stats.get(key_id, {}).get('count', 0)
        if usage_count >= self.rotation_threshold:
            logger.info(f"Key {key_data.get('key_name')} reached session rotation threshold ({usage_count} requests)")
            return True
        
        # Only check database usage occasionally (every 10th request per key)
        try:
            if not self.use_direct_supabase and usage_count % 10 == 0:
                logger.debug(f"Performing periodic database usage check for key {key_id} (usage: {usage_count})")
                response = await self.client.get(f"{self.base_url}/api/keys/")
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == 'ok':
                        keys_status = data.get('key_management', {}).get('keys_status', [])
                        for key_status in keys_status:
                            if key_status.get('id') == key_id:
                                current_minute_requests = key_status.get('requests_current_minute', 0)
                                if current_minute_requests >= 12:
                                    logger.info(f"Key {key_data.get('key_name')} high current minute usage ({current_minute_requests} requests)")
                                    return True
                                break
        except Exception as e:
            logger.debug(f"Could not check database usage for rotation: {e}")
        
        last_rate_limit = self.key_usage_stats.get(key_id, {}).get('last_rate_limit')
        if last_rate_limit:
            time_since_limit = time.time() - last_rate_limit
            if time_since_limit < self.rate_limit_cooldown:
                logger.info(f"Key {key_data.get('key_name')} still in cooldown ({int(self.rate_limit_cooldown - time_since_limit)}s remaining)")
                return True
        
        return False

    async def _notify_backend_key_change(self, old_index: int, new_index: int):
        """Notify backend about key rotation for dashboard sync"""
        try:
            if not self.use_direct_supabase:
                # Update backend about the new key
                await self.client.post(f"{self.base_url}/api/keys/set-current", json={
                    'current_key_index': new_index,
                    'old_key_index': old_index
                })
                logger.info(f"Notified backend: key rotation {old_index} → {new_index}")
        except Exception as e:
            logger.warning(f"Failed to notify backend about key change: {e}")

    async def _restore_last_active_key(self):
        """Restore the last active key from backend to avoid always starting from key 0"""
        try:
            if not self.use_direct_supabase:
                # Ask backend which key was active recently
                response = await self.client.get(f"{self.base_url}/api/keys/")
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == 'ok' and 'key_management' in data:
                        backend_current_index = data['key_management'].get('current_key_index', 0)
                        # Verify that the index is valid
                        if 0 <= backend_current_index < len(self.api_keys):
                            self.current_key_index = backend_current_index
                            logger.info(f"🔄 [KEY-RESTORE] Restored key index from backend: {self.current_key_index}")
                        else:
                            logger.warning(f"Invalid backend key index {backend_current_index}, using 0")
                            self.current_key_index = 0
                    else:
                        logger.info("No backend key management data, starting from key 0")
        except Exception as e:
            logger.warning(f"Could not restore last active key: {e}, starting from key 0")

    async def refresh_keys(self):
        """Refresh API keys from database"""
        try:
            if self.use_direct_supabase:
                response = self.supabase.table('api_keys').select('*').eq('is_active', True).execute()
                self.api_keys = response.data or []
            else:
                try:
                    # Try fast endpoint first
                    ai_response = await self.client.get(f"{self.base_url}/api/keys/for-ai-service")
                    if ai_response.status_code == 200:
                        ai_keys_data = ai_response.json()
                        self.api_keys = ai_keys_data.get('keys', [])
                        logger.info(f"Got {len(self.api_keys)} keys from fast endpoint")
                    else:
                        raise Exception("Fast endpoint failed")
                except Exception as fast_error:
                    logger.warning(f"Fast endpoint failed, using heavy endpoint: {fast_error}")
                    # Fallback to heavy endpoint only if fast one fails
                    response = await self.client.get(f"{self.base_url}/api/keys/")
                    response.raise_for_status()
                    keys_data = response.json()
                    
                    if keys_data.get('status') == 'ok' and 'key_management' in keys_data:
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
                        self.api_keys = keys_data.get('keys', [])
            
            self.last_refresh = datetime.now()
            logger.info(f"Refreshed {len(self.api_keys)} API keys from database")
            
            # After refreshing keys, try to restore the last active key
            if not self._initial_load_done:
                await self._restore_last_active_key()
            
            # Verify that the index is valid
            if self.current_key_index >= len(self.api_keys):
                self.current_key_index = 0
                logger.warning(f"Key index out of range, reset to 0")
                
        except Exception as e:
            logger.error(f"Failed to refresh API keys: {e}")
            if not self.api_keys:
                raise Exception("No API keys available and refresh failed")

    async def get_available_key(self) -> Optional[Dict[str, Any]]:
        """Get next available API key with smart rotation"""
        try:
            if not self._initial_load_done:
                await self.refresh_keys()
                self._initial_load_done = True
            
            if (not self.last_refresh or 
                (datetime.now() - self.last_refresh).seconds > self.refresh_interval):
                await self.refresh_keys()
            
            key_data = await self._get_next_available_key()
            if not key_data:
                raise Exception("No available API keys found")
            
            key_id = key_data.get('id')
            if key_id not in self.key_usage_stats:
                self.key_usage_stats[key_id] = {'count': 0, 'last_used': time.time()}
            
            self.key_usage_stats[key_id]['count'] += 1
            self.key_usage_stats[key_id]['last_used'] = time.time()
            
            logger.info(f"Using key: {key_data.get('key_name')} (usage: {self.key_usage_stats[key_id]['count']})")
            return key_data
            
        except Exception as e:
            logger.error(f"Error getting available key: {e}")
            return None

    async def record_usage(self, key_id: int, tokens_used: int, requests_count: int = 1):
        """Record API key usage for analytics and rotation decisions"""
        try:
            if self.use_direct_supabase:
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
                await self.client.post(f"{self.base_url}/api/keys/{key_id}/usage", json={
                    'tokens_used': tokens_used,
                    'requests_count': requests_count
                })
                
            logger.info(f"Recorded {tokens_used} tokens usage for key {key_id}")
        except Exception as e:
            logger.error(f"Failed to record usage: {e}")

    async def mark_rate_limited(self, key_id: int):
        """Mark a key as rate-limited for temporary avoidance"""
        if key_id in self.key_usage_stats:
            self.key_usage_stats[key_id]['last_rate_limit'] = time.time()
            logger.warning(f"Key {key_id} marked as rate-limited")

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
        logger.info("Getting detailed status...")
        
        if not self._initial_load_done:
            await self.refresh_keys()
            self._initial_load_done = True
        
        try:
            from datetime import date, timezone, datetime
            today = date.today().isoformat()
            current_minute_utc = datetime.now(timezone.utc).replace(second=0, microsecond=0)
            
            key_ids = [key_data.get('id') for key_data in self.api_keys]
            
            daily_response = self.supabase.table("api_key_usage")\
                .select("api_key_id,tokens_used,requests_count")\
                .in_("api_key_id", key_ids)\
                .eq("usage_date", today)\
                .execute()
            
            minute_response = self.supabase.table("api_key_usage")\
                .select("api_key_id,tokens_used,requests_count")\
                .in_("api_key_id", key_ids)\
                .eq("usage_minute", current_minute_utc.isoformat())\
                .execute()
            
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
            
            logger.info(f"Batch query complete: {len(daily_response.data)} daily records, {len(minute_response.data)} minute records")
            
        except Exception as e:
            logger.error(f"Error in batch queries: {e}")
            daily_usage = {}
            minute_usage = {}
        
        keys_status = []
        total_tokens_today = 0
        total_requests_today = 0
        
        for i, key_data in enumerate(self.api_keys):
            key_id = key_data.get('id')
            is_current = i == self.current_key_index
            
            daily_data = daily_usage.get(key_id, {"tokens": 0, "requests": 0})
            minute_data = minute_usage.get(key_id, {"tokens": 0, "requests": 0})
            
            tokens_today = daily_data["tokens"]
            requests_today = daily_data["requests"]
            tokens_current_minute = minute_data["tokens"]
            requests_current_minute = minute_data["requests"]
            
            status = "current" if is_current else "available"
            
            if tokens_today > 800000 or requests_today > 1400:
                status = "blocked"
            
            keys_status.append({
                "id": i,
                "is_current": is_current,
                "status": status,
                "tokens_today": tokens_today,
                "requests_today": requests_today,
                "tokens_current_minute": tokens_current_minute,
                "requests_current_minute": requests_current_minute,
                "last_used": None,
                "first_used_today": None
            })
            
            total_tokens_today += tokens_today
            total_requests_today += requests_today
        
        available_count = sum(1 for k in keys_status if k["status"] == "available")
        blocked_count = sum(1 for k in keys_status if k["status"] == "blocked")
        
        result = {
            "total_keys": len(self.api_keys),
            "available_keys": available_count + 1,
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
        
        logger.info(f"Returning optimized status with {len(keys_status)} keys, current: {self.current_key_index}")
        return result

    def __del__(self):
        """Clean up background tasks"""
        if self._auto_refresh_task and not self._auto_refresh_task.done():
            self._auto_refresh_task.cancel()

    async def _get_next_available_key(self) -> Optional[Dict[str, Any]]:
        """Find next available key with intelligent rotation"""
        if not self.api_keys:
            await self.refresh_keys()
        
        if not self.api_keys:
            return None
        
        # Smarter selection of the next key
        old_index = self.current_key_index
        
        # Instead of always moving to the next key, first check if current key is still available
        # Only rotate if there's a reason (e.g. usage threshold)
        should_rotate = False
        
        if self.api_keys and old_index < len(self.api_keys):
            current_key = self.api_keys[old_index]
            key_id = current_key.get('id')
            
            # Check if rotation is needed based on usage
            usage_count = self.key_usage_stats.get(key_id, {}).get('count', 0)
            if usage_count >= self.rotation_threshold:
                should_rotate = True
                logger.info(f"Key {current_key.get('key_name')} reached rotation threshold ({usage_count})")
        else:
            should_rotate = True  # No valid current key
        
        if should_rotate:
            # Smart rotation - looking for key with low usage
            best_key_index = (old_index + 1) % len(self.api_keys)
            min_usage = float('inf')
            
            for i in range(len(self.api_keys)):
                check_index = (old_index + 1 + i) % len(self.api_keys)
                key_data = self.api_keys[check_index]
                key_id = key_data.get('id')
                usage_count = self.key_usage_stats.get(key_id, {}).get('count', 0)
                
                # Prefer key with lower usage
                if usage_count < min_usage:
                    min_usage = usage_count
                    best_key_index = check_index
                
                # If found a key without usage, use it immediately
                if usage_count == 0:
                    break
            
            self.current_key_index = best_key_index
            logger.info(f"🔄 [KEY-ROTATION] Intelligent rotation: {old_index} → {self.current_key_index} (usage: {min_usage})")
        else:
            logger.info(f"♻️ [KEY-REUSE] Continuing with current key {self.current_key_index}")
        
        # Update backend about the new key (even if not changed)
        await self._notify_backend_key_change(old_index, self.current_key_index)
        
        current_key = self.api_keys[self.current_key_index]
        logger.info(f"Selected key: {current_key.get('key_name', f'Key {self.current_key_index}')} (index: {self.current_key_index})")
        return current_key