import json
import os
from datetime import datetime, date, timedelta, timezone
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class TokenUsagePersistence:
    """שמירה קבועה של נתוני שימוש בטוקנים"""
    
    def __init__(self, data_file: str = "token_usage_data.json"):
        self.data_file = data_file
        self.data = self._load_data()
    
    def _load_data(self) -> Dict[str, Any]:
        """טעינת נתונים מקובץ"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading token data: {e}")
        
        return {
            "keys_usage": {},
            "daily_totals": {},
            "last_updated": None
        }
    
    def _save_data(self):
        """שמירת נתונים לקובץ"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving token data: {e}")
    
    def update_usage(self, key_index: int, tokens_used: int, requests_count: int = 1):
        """עדכון שימוש עבור מפתח"""
        logger.info(f"💾 [PERSIST-DEBUG] ===== UPDATING PERSISTENT USAGE =====")
        logger.info(f"💾 [PERSIST-DEBUG] Key index: {key_index}")
        logger.info(f"💾 [PERSIST-DEBUG] Tokens used: {tokens_used}")
        logger.info(f"💾 [PERSIST-DEBUG] Requests count: {requests_count}")
        
        today = date.today().isoformat()
        # שימוש בזמן UTC כדי להתאים לדאטה בייס
        current_time_utc = datetime.now(timezone.utc)
        current_time = current_time_utc.isoformat()
        current_minute = current_time_utc.strftime("%Y-%m-%d %H:%M")  # דקה נוכחית ב-UTC
        
        logger.info(f"💾 [PERSIST-DEBUG] Date: {today}")
        logger.info(f"💾 [PERSIST-DEBUG] Time: {current_time}")
        logger.info(f"💾 [PERSIST-DEBUG] Current minute: {current_minute}")
        
        # יצירת entry עבור המפתח אם לא קיים
        key_id = f"key_{key_index}"
        if key_id not in self.data["keys_usage"]:
            logger.info(f"💾 [PERSIST-DEBUG] Creating new key entry: {key_id}")
            self.data["keys_usage"][key_id] = {}
        
        # יצירת entry עבור היום אם לא קיים
        if today not in self.data["keys_usage"][key_id]:
            logger.info(f"💾 [PERSIST-DEBUG] Creating new day entry for {key_id}: {today}")
            self.data["keys_usage"][key_id][today] = {
                "tokens_used": 0,
                "requests_count": 0,
                "first_request": current_time,
                "last_request": current_time,
                "current_minute_data": {}  # 🆕 נתונים של דקה נוכחית
            }
        
        day_data = self.data["keys_usage"][key_id][today]
        
        # לוג מצב לפני העדכון
        logger.info(f"💾 [PERSIST-DEBUG] Before update - {key_id} {today}:")
        logger.info(f"💾 [PERSIST-DEBUG] - Tokens: {day_data['tokens_used']}")
        logger.info(f"💾 [PERSIST-DEBUG] - Requests: {day_data['requests_count']}")
        
        # עדכון נתונים יומיים
        day_data["tokens_used"] += tokens_used
        day_data["requests_count"] += requests_count
        day_data["last_request"] = current_time
        
        # 🆕 עדכון נתונים של דקה נוכחית
        if "current_minute_data" not in day_data:
            day_data["current_minute_data"] = {}
        
        if current_minute not in day_data["current_minute_data"]:
            logger.info(f"💾 [PERSIST-DEBUG] Creating new minute entry: {current_minute}")
            day_data["current_minute_data"][current_minute] = {
                "tokens": 0,
                "requests": 0
            }
        
        # לוג מצב דקה נוכחית לפני העדכון
        minute_data = day_data["current_minute_data"][current_minute]
        logger.info(f"💾 [PERSIST-DEBUG] Before minute update - {current_minute}:")
        logger.info(f"💾 [PERSIST-DEBUG] - Minute tokens: {minute_data['tokens']}")
        logger.info(f"💾 [PERSIST-DEBUG] - Minute requests: {minute_data['requests']}")
        
        day_data["current_minute_data"][current_minute]["tokens"] += tokens_used
        day_data["current_minute_data"][current_minute]["requests"] += requests_count
        
        # לוג מצב דקה נוכחית אחרי העדכון
        logger.info(f"💾 [PERSIST-DEBUG] After minute update - {current_minute}:")
        logger.info(f"💾 [PERSIST-DEBUG] - Minute tokens: {minute_data['tokens']}")
        logger.info(f"💾 [PERSIST-DEBUG] - Minute requests: {minute_data['requests']}")
        
        # 🧹 נקה נתונים ישנים (שמור רק 5 דקות אחרונות)
        current_dt = datetime.now(timezone.utc)
        minutes_to_keep = []
        for i in range(5):
            minute_dt = current_dt - timedelta(minutes=i)
            minutes_to_keep.append(minute_dt.strftime("%Y-%m-%d %H:%M"))
        
        # ספור כמה דקות יש לפני הניקוי
        old_minutes_count = len(day_data["current_minute_data"])
        
        # מחק דקות ישנות
        day_data["current_minute_data"] = {
            minute: data for minute, data in day_data["current_minute_data"].items()
            if minute in minutes_to_keep
        }
        
        new_minutes_count = len(day_data["current_minute_data"])
        logger.info(f"💾 [PERSIST-DEBUG] Cleaned old minutes: {old_minutes_count} -> {new_minutes_count}")
        logger.info(f"💾 [PERSIST-DEBUG] Current minutes data: {list(day_data['current_minute_data'].keys())}")
        
        # לוג מצב אחרי העדכון
        logger.info(f"💾 [PERSIST-DEBUG] After update - {key_id} {today}:")
        logger.info(f"💾 [PERSIST-DEBUG] - Tokens: {day_data['tokens_used']}")
        logger.info(f"💾 [PERSIST-DEBUG] - Requests: {day_data['requests_count']}")
        
        # עדכון סיכום יומי
        if today not in self.data["daily_totals"]:
            logger.info(f"💾 [PERSIST-DEBUG] Creating new daily totals entry: {today}")
            self.data["daily_totals"][today] = {
                "total_tokens": 0,
                "total_requests": 0,
                "active_keys": []
            }
        
        self.data["daily_totals"][today]["total_tokens"] += tokens_used
        self.data["daily_totals"][today]["total_requests"] += requests_count
        
        # Add key only if not already in list
        if key_index not in self.data["daily_totals"][today]["active_keys"]:
            self.data["daily_totals"][today]["active_keys"].append(key_index)
        
        self.data["last_updated"] = current_time
        
        # שמירה
        logger.info(f"💾 [PERSIST-DEBUG] Saving data to file: {self.data_file}")
        try:
            self._save_data()
            logger.info(f"💾 [PERSIST-DEBUG] Successfully saved data to file")
        except Exception as save_err:
            logger.error(f"❌ [PERSIST-ERROR] Error saving data: {save_err}")
        
        logger.info(f"💾 [PERSIST-DEBUG] ===== PERSISTENT USAGE UPDATE COMPLETE =====")
    
    def get_current_minute_usage(self, key_index: int) -> Dict[str, int]:
        """קבלת שימוש של דקה נוכחית או האחרונה"""
        today = date.today().isoformat()
        current_minute = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
        key_id = f"key_{key_index}"
        
        logger.info(f"📊 [PERSIST-DEBUG] Getting current minute usage for {key_id}")
        logger.info(f"📊 [PERSIST-DEBUG] Current minute: {current_minute}")
        
        if (key_id in self.data["keys_usage"] and 
            today in self.data["keys_usage"][key_id] and
            "current_minute_data" in self.data["keys_usage"][key_id][today]):
            
            minute_data_dict = self.data["keys_usage"][key_id][today]["current_minute_data"]
            logger.info(f"📊 [PERSIST-DEBUG] Available minutes: {list(minute_data_dict.keys())}")
            
            # 🎯 תחילה נסה למצוא את הדקה הנוכחית
            if current_minute in minute_data_dict:
                minute_data = minute_data_dict[current_minute]
                result = {
                    "tokens": minute_data.get("tokens", 0),
                    "requests": minute_data.get("requests", 0)
                }
                logger.info(f"📊 [PERSIST-DEBUG] Found current minute data for {key_id}: {result}")
                return result
            
            # 🆕 אם לא נמצאה הדקה הנוכחית, קח את הדקה האחרונה
            if minute_data_dict:
                # מיין את הדקות ולקח את האחרונה
                sorted_minutes = sorted(minute_data_dict.keys(), reverse=True)
                latest_minute = sorted_minutes[0]
                
                # בדוק שהדקה האחרונה היא בטווח של 5 דקות אחרונות
                try:
                    latest_dt = datetime.strptime(latest_minute, "%Y-%m-%d %H:%M")
                    current_dt = datetime.now(timezone.utc)
                    time_diff = current_dt - latest_dt
                    
                    if time_diff.total_seconds() <= 300:  # 5 דקות
                        minute_data = minute_data_dict[latest_minute]
                        result = {
                            "tokens": minute_data.get("tokens", 0),
                            "requests": minute_data.get("requests", 0)
                        }
                        logger.info(f"📊 [PERSIST-DEBUG] Found latest minute data for {key_id} ({latest_minute}): {result}")
                        return result
                    else:
                        logger.info(f"📊 [PERSIST-DEBUG] Latest minute {latest_minute} is too old (>{time_diff.total_seconds()}s)")
                except Exception as time_err:
                    logger.error(f"❌ [PERSIST-DEBUG] Error parsing time: {time_err}")
        
        logger.info(f"📊 [PERSIST-DEBUG] No recent minute data found for {key_id}, returning zeros")
        return {"tokens": 0, "requests": 0}
    
    def get_key_usage_today(self, key_index: int) -> Dict[str, Any]:
        """קבלת שימוש של מפתח היום"""
        today = date.today().isoformat()
        key_id = f"key_{key_index}"
        
        if key_id in self.data["keys_usage"] and today in self.data["keys_usage"][key_id]:
            return self.data["keys_usage"][key_id][today]
        
        return {
            "tokens_used": 0,
            "requests_count": 0,
            "first_request": None,
            "last_request": None,
            "current_minute_data": {}
        }
    
    def get_all_keys_usage_today(self) -> Dict[str, Any]:
        """קבלת שימוש של כל המפתחות היום"""
        logger.info(f"📊 [PERSIST-DEBUG] ===== GET ALL KEYS USAGE TODAY =====")
        
        today = date.today().isoformat()
        logger.info(f"📊 [PERSIST-DEBUG] Today date: {today}")
        logger.info(f"📊 [PERSIST-DEBUG] Available keys in data: {list(self.data['keys_usage'].keys())}")
        
        result = {}
        
        for key_id, key_data in self.data["keys_usage"].items():
            logger.info(f"📊 [PERSIST-DEBUG] Processing key: {key_id}")
            logger.info(f"📊 [PERSIST-DEBUG] Key data dates: {list(key_data.keys())}")
            
            if today in key_data:
                result[key_id] = key_data[today]
                logger.info(f"📊 [PERSIST-DEBUG] Found today's data for {key_id}: tokens={key_data[today].get('tokens_used', 0)}, requests={key_data[today].get('requests_count', 0)}")
            else:
                result[key_id] = {
                    "tokens_used": 0,
                    "requests_count": 0,
                    "first_request": None,
                    "last_request": None,
                    "current_minute_data": {}
                }
                logger.info(f"📊 [PERSIST-DEBUG] No today's data for {key_id}, using defaults")
        
        logger.info(f"📊 [PERSIST-DEBUG] Final result keys: {list(result.keys())}")
        logger.info(f"📊 [PERSIST-DEBUG] ===== GET ALL KEYS USAGE TODAY COMPLETE =====")
        
        return result
    
    def get_daily_summary(self) -> Dict[str, Any]:
        """קבלת סיכום יומי"""
        today = date.today().isoformat()
        
        if today in self.data["daily_totals"]:
            return self.data["daily_totals"][today]
        
        return {
            "total_tokens": 0,
            "total_requests": 0,
            "active_keys": []
        } 