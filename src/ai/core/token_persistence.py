import json
import os
from datetime import datetime, date, timedelta, timezone
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class TokenUsagePersistence:
    """Persistent storage for token usage data"""
    
    def __init__(self, data_file: str = "token_usage_data.json"):
        self.data_file = data_file
        self.data = self._load_data()
    
    def _load_data(self) -> Dict[str, Any]:
        """Load data from file"""
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
        """Save data to file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving token data: {e}")
    
    def update_usage(self, key_index: int, tokens_used: int, requests_count: int = 1):
        """Update usage for a key"""
        logger.info(f"Updating persistent usage - Key: {key_index}, Tokens: {tokens_used}, Requests: {requests_count}")
        
        today = date.today().isoformat()
        current_time_utc = datetime.now(timezone.utc)
        current_time = current_time_utc.isoformat()
        current_minute = current_time_utc.strftime("%Y-%m-%d %H:%M")
        
        logger.info(f"Date: {today}, Current minute: {current_minute}")
        
        key_id = f"key_{key_index}"
        if key_id not in self.data["keys_usage"]:
            logger.info(f"Creating new key entry: {key_id}")
            self.data["keys_usage"][key_id] = {}
        
        if today not in self.data["keys_usage"][key_id]:
            logger.info(f"Creating new day entry for {key_id}: {today}")
            self.data["keys_usage"][key_id][today] = {
                "tokens_used": 0,
                "requests_count": 0,
                "first_request": current_time,
                "last_request": current_time,
                "current_minute_data": {}
            }
        
        day_data = self.data["keys_usage"][key_id][today]
        
        logger.info(f"Before update - {key_id} {today}: Tokens={day_data['tokens_used']}, Requests={day_data['requests_count']}")
        
        day_data["tokens_used"] += tokens_used
        day_data["requests_count"] += requests_count
        day_data["last_request"] = current_time
        
        if "current_minute_data" not in day_data:
            day_data["current_minute_data"] = {}
        
        if current_minute not in day_data["current_minute_data"]:
            logger.info(f"Creating new minute entry: {current_minute}")
            day_data["current_minute_data"][current_minute] = {
                "tokens": 0,
                "requests": 0
            }
        
        minute_data = day_data["current_minute_data"][current_minute]
        logger.info(f"Before minute update - {current_minute}: Tokens={minute_data['tokens']}, Requests={minute_data['requests']}")
        
        day_data["current_minute_data"][current_minute]["tokens"] += tokens_used
        day_data["current_minute_data"][current_minute]["requests"] += requests_count
        
        logger.info(f"After minute update - {current_minute}: Tokens={minute_data['tokens']}, Requests={minute_data['requests']}")
        
        current_dt = datetime.now(timezone.utc)
        minutes_to_keep = []
        for i in range(5):
            minute_dt = current_dt - timedelta(minutes=i)
            minutes_to_keep.append(minute_dt.strftime("%Y-%m-%d %H:%M"))
        
        old_minutes_count = len(day_data["current_minute_data"])
        
        day_data["current_minute_data"] = {
            minute: data for minute, data in day_data["current_minute_data"].items()
            if minute in minutes_to_keep
        }
        
        new_minutes_count = len(day_data["current_minute_data"])
        logger.info(f"Cleaned old minutes: {old_minutes_count} -> {new_minutes_count}")
        
        logger.info(f"After update - {key_id} {today}: Tokens={day_data['tokens_used']}, Requests={day_data['requests_count']}")
        
        if today not in self.data["daily_totals"]:
            logger.info(f"Creating new daily totals entry: {today}")
            self.data["daily_totals"][today] = {
                "total_tokens": 0,
                "total_requests": 0,
                "active_keys": []
            }
        
        self.data["daily_totals"][today]["total_tokens"] += tokens_used
        self.data["daily_totals"][today]["total_requests"] += requests_count
        
        if key_index not in self.data["daily_totals"][today]["active_keys"]:
            self.data["daily_totals"][today]["active_keys"].append(key_index)
        
        self.data["last_updated"] = current_time
        
        logger.info(f"Saving data to file: {self.data_file}")
        try:
            self._save_data()
            logger.info("Successfully saved data to file")
        except Exception as save_err:
            logger.error(f"Error saving data: {save_err}")
    
    def get_current_minute_usage(self, key_index: int) -> Dict[str, int]:
        """Get current or most recent minute usage"""
        today = date.today().isoformat()
        current_minute = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
        key_id = f"key_{key_index}"
        
        logger.info(f"Getting current minute usage for {key_id}, minute: {current_minute}")
        
        if (key_id in self.data["keys_usage"] and 
            today in self.data["keys_usage"][key_id] and
            "current_minute_data" in self.data["keys_usage"][key_id][today]):
            
            minute_data_dict = self.data["keys_usage"][key_id][today]["current_minute_data"]
            logger.info(f"Available minutes: {list(minute_data_dict.keys())}")
            
            if current_minute in minute_data_dict:
                minute_data = minute_data_dict[current_minute]
                result = {
                    "tokens": minute_data.get("tokens", 0),
                    "requests": minute_data.get("requests", 0)
                }
                logger.info(f"Found current minute data for {key_id}: {result}")
                return result
            
            if minute_data_dict:
                sorted_minutes = sorted(minute_data_dict.keys(), reverse=True)
                latest_minute = sorted_minutes[0]
                
                try:
                    latest_dt = datetime.strptime(latest_minute, "%Y-%m-%d %H:%M")
                    current_dt = datetime.now(timezone.utc)
                    time_diff = current_dt - latest_dt
                    
                    if time_diff.total_seconds() <= 300:
                        minute_data = minute_data_dict[latest_minute]
                        result = {
                            "tokens": minute_data.get("tokens", 0),
                            "requests": minute_data.get("requests", 0)
                        }
                        logger.info(f"Found latest minute data for {key_id} ({latest_minute}): {result}")
                        return result
                    else:
                        logger.info(f"Latest minute {latest_minute} is too old ({time_diff.total_seconds()}s)")
                except Exception as time_err:
                    logger.error(f"Error parsing time: {time_err}")
        
        logger.info(f"No recent minute data found for {key_id}, returning zeros")
        return {"tokens": 0, "requests": 0}
    
    def get_key_usage_today(self, key_index: int) -> Dict[str, Any]:
        """Get today's usage for a key"""
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
        """Get today's usage for all keys"""
        logger.info("Getting all keys usage for today")
        
        today = date.today().isoformat()
        logger.info(f"Today date: {today}")
        logger.info(f"Available keys in data: {list(self.data['keys_usage'].keys())}")
        
        result = {}
        
        for key_id, key_data in self.data["keys_usage"].items():
            logger.info(f"Processing key: {key_id}")
            logger.info(f"Key data dates: {list(key_data.keys())}")
            
            if today in key_data:
                result[key_id] = key_data[today]
                logger.info(f"Found today's data for {key_id}: tokens={key_data[today].get('tokens_used', 0)}, requests={key_data[today].get('requests_count', 0)}")
            else:
                result[key_id] = {
                    "tokens_used": 0,
                    "requests_count": 0,
                    "first_request": None,
                    "last_request": None,
                    "current_minute_data": {}
                }
                logger.info(f"No today's data for {key_id}, using defaults")
        
        logger.info(f"Final result keys: {list(result.keys())}")
        
        return result
    
    def get_daily_summary(self) -> Dict[str, Any]:
        """Get daily summary"""
        today = date.today().isoformat()
        
        if today in self.data["daily_totals"]:
            return self.data["daily_totals"][today]
        
        return {
            "total_tokens": 0,
            "total_requests": 0,
            "active_keys": []
        }
    
    def log_key_switch(self, old_key: int, new_key: int):
        """Log key switch event"""
        logger.info(f"Key switch logged: {old_key} -> {new_key}")
        
        if "key_switches" not in self.data:
            self.data["key_switches"] = []
        
        switch_event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "old_key": old_key,
            "new_key": new_key
        }
        
        self.data["key_switches"].append(switch_event)
        
        # Keep only last 100 switch events
        self.data["key_switches"] = self.data["key_switches"][-100:]
        
        try:
            self._save_data()
        except Exception as e:
            logger.error(f"Error saving key switch data: {e}")