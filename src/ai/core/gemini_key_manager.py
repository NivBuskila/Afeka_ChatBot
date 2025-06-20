"""Gemini API key management system"""

import os
import time
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import google.generativeai as genai
from .token_persistence import TokenUsagePersistence
import asyncio
from .database_key_manager import DatabaseKeyManager

logger = logging.getLogger(__name__)

class KeyUsage:
    def __init__(self):
        self.tokens_current_minute = 0
        self.tokens_today = 0
        self.requests_current_minute = 0
        self.requests_today = 0
        self.last_minute_reset = datetime.now()
        self.last_day_reset = datetime.now()
        self.blocked_until = None

class GeminiKeyManager:
    """Gemini API key management system"""
    
    def __init__(self):
        logger.info("Initializing Key Manager")
        
        self.database_manager = DatabaseKeyManager(use_direct_supabase=True)
        self.api_keys = []
        self.current_key_index = 0
        
        self._load_keys_with_fallback()
        
        self.usage = {}
        for key in self.api_keys:
            self.usage[key] = KeyUsage()
        
        self.persistence = TokenUsagePersistence()
        logger.info("Persistence initialized")
        
        logger.info("Loading existing usage data...")
        self._load_existing_usage()
        
        self._configure_current_key()
        
        self.limits = {
            'requests_per_minute': 15,
            'requests_per_day': 1500,
            'tokens_per_day': 1000000
        }
        
        logger.info(f"Initialized with {len(self.api_keys)} keys, current key: {self.current_key_index}")

    def _load_keys_with_fallback(self):
        """Load keys with fallback to .env"""
        try:
            logger.info("Attempting to load keys directly from Supabase...")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            future = asyncio.wait_for(self._load_keys_from_database(), timeout=5.0)
            loop.run_until_complete(future)
            
            if self.api_keys:
                print(f"Loaded {len(self.api_keys)} keys from database")
                return
            else:
                logger.warning("No keys found in database, falling back to .env")
                
        except (asyncio.TimeoutError, Exception) as e:
            logger.warning(f"Could not load from database: {e}")
            logger.info("Falling back to .env keys...")
        
        self._load_keys_from_env()

    def _load_keys_from_env(self):
        """Load keys from .env (fallback)"""
        env_keys = []
        
        main_key = os.getenv('GEMINI_API_KEY')
        if main_key:
            env_keys.append(main_key)
        
        for i in range(1, 8):
            key = os.getenv(f'GEMINI_API_KEY_{i}')
            if key and key not in env_keys:
                env_keys.append(key)
        
        self.api_keys = env_keys
        print(f"Loaded {len(self.api_keys)} keys from .env")

    async def _load_keys_from_database(self):
        """Load keys from database"""
        await self.database_manager.refresh_keys()
        self.api_keys = [key["api_key"] for key in self.database_manager.api_keys]
        print(f"Loaded {len(self.api_keys)} keys from database")

    async def get_next_available_key(self):
        """Get next available key"""
        available_key = await self.database_manager.get_available_key()
        if available_key:
            db_current_index = self.database_manager.current_key_index
            api_key_value = available_key["api_key"]
            
            self.current_key_index = db_current_index
            genai.configure(api_key=api_key_value)  # type: ignore
            
            logger.info(f"Using key index {self.current_key_index}: {available_key.get('key_name', 'Unknown')}")
            return api_key_value
        return None

    def _configure_current_key(self):
        """Configure current key in genai"""
        if self.api_keys:
            current_key = self.api_keys[self.current_key_index]
            genai.configure(api_key=current_key)  # type: ignore
            logger.debug(f"Configured key #{self.current_key_index}")

    def _reset_counters_if_needed(self, key: str):
        """Reset counters based on time"""
        now = datetime.now()
        usage = self.usage[key]
        
        if now - usage.last_minute_reset >= timedelta(minutes=1):
            usage.tokens_current_minute = 0
            usage.requests_current_minute = 0
            usage.last_minute_reset = now
        
        if now.date() > usage.last_day_reset.date():
            usage.tokens_today = 0
            usage.requests_today = 0
            usage.last_day_reset = now
            usage.blocked_until = None

    def _check_limits(self, key: str) -> bool:
        """Check if key is available within limits"""
        usage = self.usage[key]
        now = datetime.now()
        
        if usage.blocked_until and now < usage.blocked_until:
            return False
        
        safety_margin = 0.9
        
        if (usage.requests_today >= self.limits['requests_per_day'] * safety_margin or
            usage.requests_current_minute >= self.limits['requests_per_minute'] * safety_margin or
            usage.tokens_today >= self.limits['tokens_per_day'] * safety_margin):
            
            if usage.requests_current_minute >= self.limits['requests_per_minute'] * safety_margin:
                usage.blocked_until = now + timedelta(minutes=1)
                logger.warning(f"Key #{self.current_key_index} blocked for 1 minute - minute limit reached")
            else:
                usage.blocked_until = now + timedelta(minutes=5)
                logger.warning(f"Key #{self.current_key_index} blocked for 5 minutes - daily limits approached")
            return False
        
        return True

    def _find_available_key(self) -> Optional[int]:
        """Find available key"""
        for i, key in enumerate(self.api_keys):
            self._reset_counters_if_needed(key)
            if self._check_limits(key):
                return i
        return None

    def track_usage(self, tokens_used: int = 100):
        """Update usage after request"""
        logger.info(f"Tracking token usage: {tokens_used}")
        logger.info(f"Key index: {self.current_key_index}")
        
        current_key = self.api_keys[self.current_key_index]
        usage = self.usage[current_key]
        
        logger.info(f"Before update - Tokens today: {usage.tokens_today}, Requests today: {usage.requests_today}")
        
        usage.tokens_current_minute += tokens_used
        usage.tokens_today += tokens_used
        usage.requests_current_minute += 1
        usage.requests_today += 1
        
        logger.info(f"After update - Tokens today: {usage.tokens_today}, Requests today: {usage.requests_today}")
        
        try:
            logger.info("Saving to local persistence...")
            self.persistence.update_usage(
                key_index=self.current_key_index,
                tokens_used=tokens_used,
                requests_count=1
            )
            logger.info("Successfully saved to local persistence")
        except Exception as persistence_err:
            logger.error(f"Failed to save to local persistence: {persistence_err}")
        
        try:
            logger.info("Scheduling database save...")
            if self.database_manager.api_keys and len(self.database_manager.api_keys) > self.current_key_index:
                current_key_data = self.database_manager.api_keys[self.current_key_index]
                
                import threading
                
                def run_async_save():
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        loop.run_until_complete(
                            self.database_manager.record_usage(
                                current_key_data["id"], 
                                tokens_used, 
                                1
                            )
                        )
                        loop.close()
                        logger.info(f"Successfully saved to database for key ID {current_key_data['id']}")
                    except Exception as async_err:
                        logger.error(f"Background database save failed: {async_err}")
                
                threading.Thread(target=run_async_save, daemon=True).start()
                logger.info(f"Database save scheduled for key ID {current_key_data['id']}")
            else:
                logger.warning(f"No database key data available for index {self.current_key_index}")
        except Exception as db_err:
            logger.error(f"Failed to schedule database save: {db_err}")
        
        logger.info("Checking if key switch is needed after usage...")
        try:
            if not self._check_limits(current_key):
                logger.warning(f"Current key {self.current_key_index} reached limits, attempting switch...")
                available_index = self._find_available_key()
                if available_index is not None and available_index != self.current_key_index:
                    old_key = self.current_key_index
                    self.current_key_index = available_index
                    self._configure_current_key()
                    logger.warning(f"Switched from key {old_key} to key {self.current_key_index}")
                    
                    try:
                        self.persistence.log_key_switch(old_key, self.current_key_index)
                    except Exception as log_err:
                        logger.error(f"Failed to log key switch: {log_err}")
                else:
                    logger.error("No alternative key available!")
            else:
                logger.info(f"Current key {self.current_key_index} still within limits")
        except Exception as switch_err:
            logger.error(f"Error during key switch check: {switch_err}")

    def ensure_available_key(self) -> bool:
        """Ensure available key exists"""
        self._reset_counters_if_needed(self.api_keys[self.current_key_index])
        
        if self._check_limits(self.api_keys[self.current_key_index]):
            return True
        
        available_index = self._find_available_key()
        if available_index is not None:
            self.current_key_index = available_index
            self._configure_current_key()
            logger.info(f"Switched to key #{self.current_key_index}")
            return True
        
        logger.error("No available API keys!")
        return False

    def get_status(self) -> Dict[str, Any]:
        """Get system status"""
        available_keys = sum(1 for key in self.api_keys 
                           if self._check_limits(key))
        
        return {
            'current_key_index': self.current_key_index,
            'total_keys': len(self.api_keys),
            'available_keys': available_keys,
            'current_usage': {
                'tokens_today': self.usage[self.api_keys[self.current_key_index]].tokens_today,
                'tokens_current_minute': self.usage[self.api_keys[self.current_key_index]].tokens_current_minute,
                'requests_current_minute': self.usage[self.api_keys[self.current_key_index]].requests_current_minute,
                'requests_today': self.usage[self.api_keys[self.current_key_index]].requests_today
            }
        }

    def get_detailed_status(self) -> Dict[str, Any]:
        """Get detailed status with all key data"""
        logger.info("Getting detailed status")
        
        for i, key in enumerate(self.api_keys):
            self._reset_counters_if_needed(key)
        
        self._load_existing_usage()
        
        memory_status = self.get_status()
        logger.info(f"Memory status: {memory_status}")
        logger.info(f"Current key index from memory: {self.current_key_index}")
        
        all_keys_usage = self.persistence.get_all_keys_usage_today()
        daily_summary = self.persistence.get_daily_summary()
        
        keys_details = []
        for i in range(len(self.api_keys)):
            key_id = f"key_{i}"
            is_current = i == self.current_key_index
            
            persistent_data = all_keys_usage.get(key_id, {})
            tokens_today = persistent_data.get("tokens_used", 0)
            requests_today = persistent_data.get("requests_count", 0)
            
            minute_usage = self.persistence.get_current_minute_usage(i)
            tokens_minute = minute_usage["tokens"]
            requests_minute = minute_usage["requests"]
            
            is_blocked = self._is_key_blocked(i, tokens_today, requests_today, tokens_minute, requests_minute)
            
            if is_current:
                status = "current"
            elif is_blocked:
                status = "blocked"
            else:
                status = "available"
            
            logger.info(f"Key {i} ({key_id}): status={status}, today={tokens_today}t/{requests_today}r, minute={tokens_minute}t/{requests_minute}r")
            
            key_detail = {
                "id": i,
                "is_current": is_current,
                "status": status,
                "tokens_today": tokens_today,
                "requests_today": requests_today,
                "tokens_current_minute": tokens_minute,
                "requests_current_minute": requests_minute,
                "last_used": persistent_data.get("last_request"),
                "first_used_today": persistent_data.get("first_request"),
                "limits_info": {
                    "max_requests_per_minute": self.limits['requests_per_minute'],
                    "max_requests_per_day": self.limits['requests_per_day'],
                    "max_tokens_per_day": self.limits['tokens_per_day']
                }
            }
            
            keys_details.append(key_detail)
        
        available_count = sum(1 for detail in keys_details if detail['status'] == 'available')
        blocked_count = sum(1 for detail in keys_details if detail['status'] == 'blocked')
        
        result = {
            "total_keys": len(self.api_keys),
            "available_keys": available_count + 1,
            "blocked_keys": blocked_count,
            "current_key_index": self.current_key_index,
            "keys_status": keys_details,
            "daily_summary": daily_summary,
            "memory_status": memory_status,
            "last_updated": datetime.now().isoformat()
        }
        
        logger.info(f"Final result - Current key: {self.current_key_index}")
        logger.info(f"Available keys: {available_count + 1}, Blocked keys: {blocked_count}")
        
        return result

    def _is_key_blocked(self, key_index: int, tokens_today: int, requests_today: int, tokens_minute: int, requests_minute: int) -> bool:
        """Check if key is blocked based on existing data"""
        
        if requests_minute >= self.limits['requests_per_minute']:
            logger.info(f"Key {key_index} blocked: requests_minute {requests_minute} >= {self.limits['requests_per_minute']}")
            return True
        
        if requests_today >= self.limits['requests_per_day']:
            logger.info(f"Key {key_index} blocked: requests_today {requests_today} >= {self.limits['requests_per_day']}")
            return True
        
        if tokens_today >= self.limits['tokens_per_day']:
            logger.info(f"Key {key_index} blocked: tokens_today {tokens_today} >= {self.limits['tokens_per_day']}")
            return True
        
        logger.info(f"Key {key_index} available: within all limits")
        return False

    def _load_existing_usage(self):
        """Load existing data from file to memory"""
        logger.info("Loading existing usage data...")
        
        try:
            all_keys_usage = self.persistence.get_all_keys_usage_today()
            logger.info(f"Found usage data for {len(all_keys_usage)} keys")
            
            for i, key in enumerate(self.api_keys):
                key_id = f"key_{i}"
                if key_id in all_keys_usage:
                    persistent_data = all_keys_usage[key_id]
                    self.usage[key].tokens_today = persistent_data.get("tokens_used", 0)
                    self.usage[key].requests_today = persistent_data.get("requests_count", 0)
                    logger.info(f"Loaded key {i}: {self.usage[key].tokens_today} tokens, {self.usage[key].requests_today} requests")
                else:
                    logger.info(f"No existing data for key {i}")
                    
        except Exception as load_err:
            logger.error(f"Error loading existing usage: {load_err}")
    
    async def record_usage(self, tokens_used: int, requests_count: int = 1):
        """Record usage"""
        current_key_data = self.database_manager.api_keys[self.current_key_index]
        await self.database_manager.record_usage(
            current_key_data["id"], 
            tokens_used, 
            requests_count
        )

async def safe_generate_content(*args, **kwargs) -> Any:
    """Safe wrapper for generative content"""
    manager = get_key_manager()
    
    key = await manager.get_available_key()
    if not key:
        raise Exception("No available Gemini API keys")
    
    logger.info(f"Using key #{manager.current_key_index} for content generation")
    
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-exp')  # type: ignore
        response = model.generate_content(*args, **kwargs)
        
        estimated_tokens = len(str(args)) // 4 if args else 100
        
        logger.info(f"Generated content with key #{manager.current_key_index}, tracking {estimated_tokens} tokens")
        
        # Use track_usage for DatabaseKeyManager
        manager.track_usage(tokens_used=estimated_tokens)  # type: ignore
        
        return response
            
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        raise

async def safe_embed_content(*args, **kwargs) -> Any:
    """Safe wrapper for embedding content"""
    manager = get_key_manager()
    
    key = await manager.get_available_key()
    if not key:
        raise Exception("No available Gemini API keys")
    
    logger.info(f"Using key #{manager.current_key_index} for embedding")
    
    try:
        response = genai.embed_content(*args, **kwargs)  # type: ignore
        
        estimated_tokens = len(str(args)) // 4 if args else 50
        
        logger.info(f"Generated embedding with key #{manager.current_key_index}, tracking {estimated_tokens} tokens")
        
        # Use track_usage for DatabaseKeyManager
        manager.track_usage(tokens_used=estimated_tokens)  # type: ignore
        
        return response
        
    except Exception as e:
        logger.error(f"Gemini Embedding API error: {e}")
        raise

_key_manager = None

def get_key_manager():
    """Get global key manager instance - now uses DatabaseKeyManager"""
    from .database_key_manager import DatabaseKeyManager
    import threading
    global _key_manager
    
    thread_id = threading.current_thread().ident
    process_id = os.getpid()
    
    logger.info(f"get_key_manager called - Thread ID: {thread_id}, Process ID: {process_id}")
    logger.info(f"Current instance: {id(_key_manager) if _key_manager else 'None'}")
    
    if _key_manager is None:
        logger.info("Creating NEW Database Key Manager instance")
        _key_manager = DatabaseKeyManager()
        logger.info(f"Created instance with ID: {id(_key_manager)}")
    else:
        logger.info(f"Using EXISTING Database Key Manager instance ID: {id(_key_manager)}")
        
    return _key_manager