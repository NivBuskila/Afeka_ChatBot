"""מנגנון ניהול מפתחות גמיני - פתרון מינימלי"""

import os
import time
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import google.generativeai as genai
from .token_persistence import TokenUsagePersistence

logger = logging.getLogger(__name__)

class KeyUsage:
    def __init__(self):
        self.tokens_current_minute = 0
        self.tokens_today = 0
        self.requests_current_minute = 0
        self.requests_today = 0  # הוספת מעקב בקשות יומי
        self.last_minute_reset = datetime.now()
        self.last_day_reset = datetime.now()
        self.blocked_until = None

class GeminiKeyManager:
    """מנגנון פשוט לניהול מפתחות גמיני"""
    
    def __init__(self):
        logger.info("🔧 [KEY-MANAGER] ===== INITIALIZING KEY MANAGER =====")
        self.api_keys = self._load_keys()
        logger.info(f"🔧 [KEY-MANAGER] Loaded {len(self.api_keys)} API keys")
        
        # Initialize usage tracking for each key
        self.usage = {}
        for key in self.api_keys:
            self.usage[key] = KeyUsage()
        
        # Initialize persistence
        self.persistence = TokenUsagePersistence()
        logger.info("🔧 [KEY-MANAGER] Persistence initialized")
        
        # Load existing data from persistence
        logger.info("🔧 [KEY-MANAGER] Loading existing usage data...")
        self._load_existing_usage()
        
        self.current_key_index = 0
        self._configure_current_key()
        
        # Rate limiting configuration
        self.limits = {
            'requests_per_minute': 15,
            'requests_per_day': 1500,
            'tokens_per_day': 1000000
        }
        
        logger.info(f"🔧 [KEY-MANAGER] Initialized with {len(self.api_keys)} keys, current key: {self.current_key_index}")
        logger.info("🔧 [KEY-MANAGER] ===== KEY MANAGER INITIALIZATION COMPLETE =====")

    def _load_keys(self) -> List[str]:
        """טעינת מפתחות מסביבה"""
        keys = []
        
        # מפתח יחיד (תאימות אחורה)
        single_key = os.getenv('GEMINI_API_KEY')
        if single_key:
            keys.append(single_key)
        
        # מפתחות מרובים
        for i in range(1, 8):  # תמיכה ב-7 מפתחות
            key = os.getenv(f'GEMINI_API_KEY_{i}')
            if key:
                keys.append(key)
        
        return list(set(keys))  # הסרת כפילויות

    def _configure_current_key(self):
        """הגדרת המפתח הנוכחי ב-genai"""
        if self.api_keys:
            current_key = self.api_keys[self.current_key_index]
            genai.configure(api_key=current_key)
            logger.debug(f"Configured key #{self.current_key_index}")

    def _reset_counters_if_needed(self, key: str):
        """איפוס מונים לפי זמן"""
        now = datetime.now()
        usage = self.usage[key]
        
        # איפוס דקה
        if now - usage.last_minute_reset >= timedelta(minutes=1):
            usage.tokens_current_minute = 0
            usage.requests_current_minute = 0
            usage.last_minute_reset = now
        
        # איפוס יום
        if now.date() > usage.last_day_reset.date():
            usage.tokens_today = 0
            usage.requests_today = 0  # איפוס בקשות יומי
            usage.last_day_reset = now
            usage.blocked_until = None

    def _check_limits(self, key: str) -> bool:
        """בדיקה האם המפתח זמין"""
        usage = self.usage[key]
        now = datetime.now()
        
        # בדיקת חסימה
        if usage.blocked_until and now < usage.blocked_until:
            return False
        
        # בדיקת גבולות עם מרווח ביטחון
        safety_margin = 0.9
        
        if (usage.requests_today >= self.limits['requests_per_day'] * safety_margin or  # שונה מ-tokens_current_minute
            usage.requests_current_minute >= self.limits['requests_per_minute'] * safety_margin or
            usage.tokens_today >= self.limits['tokens_per_day'] * safety_margin):
            
            usage.blocked_until = now + timedelta(days=1)
            logger.warning(f"Key #{self.current_key_index} blocked - limits reached")
            return False
        
        return True

    def _find_available_key(self) -> Optional[int]:
        """מציאת מפתח זמין"""
        for i, key in enumerate(self.api_keys):
            self._reset_counters_if_needed(key)
            if self._check_limits(key):
                return i
        return None

    def track_usage(self, tokens_used: int = 100):
        """עדכון שימוש לאחר בקשה"""
        # 🔍 DEBUG: לוגים מפורטים
        logger.info(f"🔢 [TOKEN-TRACK] ===== TRACKING TOKEN USAGE =====")
        logger.info(f"🔢 [TOKEN-TRACK] Key index: {self.current_key_index}")
        logger.info(f"🔢 [TOKEN-TRACK] Tokens to add: {tokens_used}")
        
        current_key = self.api_keys[self.current_key_index]
        usage = self.usage[current_key]
        
        # לוג מצב לפני העדכון
        logger.info(f"🔢 [TOKEN-TRACK] Before update:")
        logger.info(f"🔢 [TOKEN-TRACK] - Tokens today: {usage.tokens_today}")
        logger.info(f"🔢 [TOKEN-TRACK] - Tokens current minute: {usage.tokens_current_minute}")
        logger.info(f"🔢 [TOKEN-TRACK] - Requests today: {usage.requests_today}")
        logger.info(f"🔢 [TOKEN-TRACK] - Requests current minute: {usage.requests_current_minute}")
        
        usage.tokens_current_minute += tokens_used
        usage.tokens_today += tokens_used
        usage.requests_current_minute += 1
        usage.requests_today += 1
        
        # לוג מצב אחרי העדכון
        logger.info(f"🔢 [TOKEN-TRACK] After update:")
        logger.info(f"🔢 [TOKEN-TRACK] - Tokens today: {usage.tokens_today}")
        logger.info(f"🔢 [TOKEN-TRACK] - Tokens current minute: {usage.tokens_current_minute}")
        logger.info(f"🔢 [TOKEN-TRACK] - Requests today: {usage.requests_today}")
        logger.info(f"🔢 [TOKEN-TRACK] - Requests current minute: {usage.requests_current_minute}")
        
        # 🆕 שמירה קבועה
        try:
            logger.info(f"🔢 [TOKEN-TRACK] Saving to persistence...")
            self.persistence.update_usage(
                key_index=self.current_key_index,
                tokens_used=tokens_used,
                requests_count=1
            )
            logger.info(f"🔢 [TOKEN-TRACK] Successfully saved to persistence")
        except Exception as persistence_err:
            logger.error(f"❌ [TOKEN-ERROR] Failed to save to persistence: {persistence_err}")
        
        # 🆕 בדיקה האם צריך לעבור למפתח אחר אחרי השימוש
        logger.info(f"🔍 [TOKEN-TRACK] Checking if key switch is needed after usage...")
        try:
            if not self._check_limits(current_key):
                logger.warning(f"🔄 [TOKEN-TRACK] Current key {self.current_key_index} reached limits, attempting switch...")
                available_index = self._find_available_key()
                if available_index is not None and available_index != self.current_key_index:
                    old_key = self.current_key_index
                    self.current_key_index = available_index
                    self._configure_current_key()
                    logger.warning(f"🔄 [TOKEN-TRACK] Switched from key {old_key} to key {self.current_key_index}")
                    
                    # 🆕 תיעוד החלפה
                    try:
                        self.persistence.log_key_switch(old_key, self.current_key_index)
                    except Exception as log_err:
                        logger.error(f"❌ [TOKEN-TRACK] Failed to log key switch: {log_err}")
                else:
                    logger.error(f"❌ [TOKEN-TRACK] No alternative key available!")
            else:
                logger.info(f"✅ [TOKEN-TRACK] Current key {self.current_key_index} still within limits")
        except Exception as switch_err:
            logger.error(f"❌ [TOKEN-TRACK] Error during key switch check: {switch_err}")
        
        logger.info(f"🔢 [TOKEN-TRACK] ===== TOKEN TRACKING COMPLETE =====")

    def ensure_available_key(self) -> bool:
        """וידוא שיש מפתח זמין"""
        self._reset_counters_if_needed(self.api_keys[self.current_key_index])
        
        if self._check_limits(self.api_keys[self.current_key_index]):
            return True
        
        # חיפוש מפתח חלופי
        available_index = self._find_available_key()
        if available_index is not None:
            self.current_key_index = available_index
            self._configure_current_key()
            logger.info(f"Switched to key #{self.current_key_index}")
            return True
        
        logger.error("No available API keys!")
        return False

    def get_status(self) -> Dict[str, Any]:
        """מצב המערכת"""
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
                'requests_today': self.usage[self.api_keys[self.current_key_index]].requests_today  # הוספת בקשות יומי
            }
        }

    def get_detailed_status(self) -> Dict[str, Any]:
        """מצב מפורט עם נתונים מכל המפתחות"""
        logger.info(f"📊 [KEY-MANAGER-DEBUG] ===== GET DETAILED STATUS =====")
        
        # 🔧 עדכון מיידי של המונים לפני החזרת הסטטוס
        for i, key in enumerate(self.api_keys):
            self._reset_counters_if_needed(key)
        
        # טען נתונים עדכניים מהקובץ לזיכרון
        self._load_existing_usage()
        
        # נתונים מהזיכרון (current)
        memory_status = self.get_status()
        logger.info(f"📊 [KEY-MANAGER-DEBUG] Memory status: {memory_status}")
        logger.info(f"📊 [KEY-MANAGER-DEBUG] Current key index from memory: {self.current_key_index}")
        
        # נתונים קבועים מהקובץ
        all_keys_usage = self.persistence.get_all_keys_usage_today()
        daily_summary = self.persistence.get_daily_summary()
        
        # שילוב הנתונים
        keys_details = []
        for i in range(len(self.api_keys)):
            key_id = f"key_{i}"
            is_current = i == self.current_key_index  # 🎯 זה הקריטריון העיקרי
            
            # נתונים יומיים מהקובץ
            persistent_data = all_keys_usage.get(key_id, {})
            tokens_today = persistent_data.get("tokens_used", 0)
            requests_today = persistent_data.get("requests_count", 0)
            
            # נתונים של דקה נוכחית מהקובץ
            minute_usage = self.persistence.get_current_minute_usage(i)
            tokens_minute = minute_usage["tokens"]
            requests_minute = minute_usage["requests"]
            
            # 🎯 חישוב סטטוס מדויק על בסיס הלימיטים האמיתיים
            is_blocked = self._is_key_blocked(i, tokens_today, requests_today, tokens_minute, requests_minute)
            
            if is_current:
                status = "current"
            elif is_blocked:
                status = "blocked"
            else:
                status = "available"
            
            logger.info(f"📊 [KEY-MANAGER-DEBUG] Key {i} ({key_id}):")
            logger.info(f"📊 [KEY-MANAGER-DEBUG] - Today: tokens={tokens_today}, requests={requests_today}")
            logger.info(f"📊 [KEY-MANAGER-DEBUG] - Current minute: tokens={tokens_minute}, requests={requests_minute}")
            logger.info(f"📊 [KEY-MANAGER-DEBUG] - Is current: {is_current}")
            logger.info(f"📊 [KEY-MANAGER-DEBUG] - Is blocked: {is_blocked}")
            logger.info(f"📊 [KEY-MANAGER-DEBUG] - Final status: {status}")
            
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
                # 🆕 הוספת מידע על הגבלות
                "limits_info": {
                    "max_requests_per_minute": self.limits['requests_per_minute'],
                    "max_requests_per_day": self.limits['requests_per_day'],
                    "max_tokens_per_day": self.limits['tokens_per_day']
                }
            }
            
            keys_details.append(key_detail)
        
        # 🔧 חישוב מחדש של מפתחות זמינים ומחוסמים
        available_count = sum(1 for detail in keys_details if detail['status'] == 'available')
        blocked_count = sum(1 for detail in keys_details if detail['status'] == 'blocked')
        
        result = {
            "total_keys": len(self.api_keys),
            "available_keys": available_count + 1,  # +1 for current key
            "blocked_keys": blocked_count,
            "current_key_index": self.current_key_index,
            "keys_status": keys_details,
            "daily_summary": daily_summary,
            "memory_status": memory_status,
            "last_updated": datetime.now().isoformat()
        }
        
        logger.info(f"📊 [KEY-MANAGER-DEBUG] Final result - Current key: {self.current_key_index}")
        logger.info(f"📊 [KEY-MANAGER-DEBUG] Available keys: {available_count + 1}, Blocked keys: {blocked_count}")
        logger.info(f"📊 [KEY-MANAGER-DEBUG] ===== GET DETAILED STATUS COMPLETE =====")
        
        return result

    def _is_key_blocked(self, key_index: int, tokens_today: int, requests_today: int, tokens_minute: int, requests_minute: int) -> bool:
        """בדיקה האם מפתח חסום על בסיס הנתונים הקיימים"""
        # 🎯 בדיקת לימיטים מדויקת - אם הגיע לליטמיט בדיוק, זה blocked
        
        # לימיט בקשות בדקה (15)
        if requests_minute >= self.limits['requests_per_minute']:
            logger.info(f"🚫 [LIMIT-CHECK] Key {key_index} blocked: requests_minute {requests_minute} >= {self.limits['requests_per_minute']}")
            return True
        
        # לימיט בקשות ביום (1500)
        if requests_today >= self.limits['requests_per_day']:
            logger.info(f"🚫 [LIMIT-CHECK] Key {key_index} blocked: requests_today {requests_today} >= {self.limits['requests_per_day']}")
            return True
        
        # לימיט טוקנים ביום (1,000,000)
        if tokens_today >= self.limits['tokens_per_day']:
            logger.info(f"🚫 [LIMIT-CHECK] Key {key_index} blocked: tokens_today {tokens_today} >= {self.limits['tokens_per_day']}")
            return True
        
        logger.info(f"✅ [LIMIT-CHECK] Key {key_index} available: within all limits")
        return False


    def _load_existing_usage(self):
        """טעינת נתונים קיימים מהקובץ לזיכרון"""
        logger.info("🔧 [KEY-MANAGER] Loading existing usage data...")
        
        try:
            all_keys_usage = self.persistence.get_all_keys_usage_today()
            logger.info(f"🔧 [KEY-MANAGER] Found usage data for {len(all_keys_usage)} keys")
            
            for i, key in enumerate(self.api_keys):
                key_id = f"key_{i}"
                if key_id in all_keys_usage:
                    persistent_data = all_keys_usage[key_id]
                    self.usage[key].tokens_today = persistent_data.get("tokens_used", 0)
                    self.usage[key].requests_today = persistent_data.get("requests_count", 0)
                    logger.info(f"🔧 [KEY-MANAGER] Loaded key {i}: {self.usage[key].tokens_today} tokens, {self.usage[key].requests_today} requests")
                else:
                    logger.info(f"🔧 [KEY-MANAGER] No existing data for key {i}")
                    
        except Exception as load_err:
            logger.error(f"❌ [KEY-MANAGER] Error loading existing usage: {load_err}")
    
    def safe_generate_content(*args, **kwargs) -> Any:
        """Wrapper בטוח לgenerative content"""
        manager = get_key_manager()
        
        # 🎯 וידוא שיש מפתח זמין ועדכון current_key_index אם צריך
        if not manager.ensure_available_key():
            raise Exception("No available Gemini API keys")
        
        # 🆕 לוג המפתח שבשימוש לפני הבקשה
        logger.info(f"🔥 [API-CALL] Using key #{manager.current_key_index} for content generation")
        
        try:
            # ביצוע הבקשה
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            response = model.generate_content(*args, **kwargs)
            
            # עדכון שימוש (הערכה)
            estimated_tokens = len(str(args)) // 4 if args else 100
            
            # 🆕 לוג השימוש
            logger.info(f"🔥 [API-CALL] Generated content with key #{manager.current_key_index}, tracking {estimated_tokens} tokens")
            
            manager.track_usage(estimated_tokens)
            
            return response
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise

def safe_embed_content(*args, **kwargs) -> Any:
    """Wrapper בטוח לembedding content"""
    manager = get_key_manager()
    
    # 🎯 וידוא שיש מפתח זמין
    if not manager.ensure_available_key():
        raise Exception("No available Gemini API keys")
    
    # 🆕 לוג המפתח שבשימוש לפני הבקשה
    logger.info(f"🔥 [API-CALL] Using key #{manager.current_key_index} for embedding")
    
    try:
        response = genai.embed_content(*args, **kwargs)
        
        # עדכון שימוש
        estimated_tokens = len(str(args)) // 4 if args else 50
        
        # 🆕 לוג השימוש
        logger.info(f"🔥 [API-CALL] Generated embedding with key #{manager.current_key_index}, tracking {estimated_tokens} tokens")
        
        manager.track_usage(estimated_tokens)
        
        return response
        
    except Exception as e:
        logger.error(f"Gemini Embedding API error: {e}")
        raise

# Instance יחיד גלובלי
_key_manager = None

def get_key_manager() -> GeminiKeyManager:
    """קבלת מנגנון הניהול הגלובלי"""
    import threading
    global _key_manager
    
    # 🔍 DEBUG: מידע מפורט על ה-instance
    thread_id = threading.current_thread().ident
    process_id = os.getpid()
    
    logger.info(f"🔧 [KEY-MANAGER] get_key_manager called")
    logger.info(f"🔧 [KEY-MANAGER] Thread ID: {thread_id}")
    logger.info(f"🔧 [KEY-MANAGER] Process ID: {process_id}")
    logger.info(f"🔧 [KEY-MANAGER] Current instance: {id(_key_manager) if _key_manager else 'None'}")
    
    if _key_manager is None:
        logger.info("🔧 [KEY-MANAGER] Creating NEW Key Manager instance")
        _key_manager = GeminiKeyManager()
        logger.info(f"🔧 [KEY-MANAGER] Created instance with ID: {id(_key_manager)}")
    else:
        logger.info(f"🔧 [KEY-MANAGER] Using EXISTING Key Manager instance ID: {id(_key_manager)}")
        
    return _key_manager

def safe_generate_content(*args, **kwargs) -> Any:
    """Wrapper בטוח לgenerative content"""
    manager = get_key_manager()
    
    if not manager.ensure_available_key():
        raise Exception("No available Gemini API keys")
    
    try:
        # ביצוע הבקשה
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content(*args, **kwargs)
        
        # עדכון שימוש (הערכה)
        estimated_tokens = len(str(args)) // 4 if args else 100
        manager.track_usage(estimated_tokens)
        
        return response
        
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        raise

def safe_embed_content(*args, **kwargs) -> Any:
    """Wrapper בטוח לembedding content"""
    manager = get_key_manager()
    
    if not manager.ensure_available_key():
        raise Exception("No available Gemini API keys")
    
    try:
        response = genai.embed_content(*args, **kwargs)
        
        # עדכון שימוש
        estimated_tokens = len(str(args)) // 4 if args else 50
        manager.track_usage(estimated_tokens)
        
        return response
        
    except Exception as e:
        logger.error(f"Gemini Embedding API error: {e}")
        raise