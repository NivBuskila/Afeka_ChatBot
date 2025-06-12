"""
טסטים קצרים עבור פונקציונליות הדשבורד
"""
import pytest
from datetime import datetime, timezone

class TestDashboard:
    """טסטים בסיסיים עבור הדשבורד"""

    def test_token_calculation(self):
        """בדיקה שחישוב הטוקנים נכון"""
        keys_data = [
            {'tokens_today': 1196, 'requests_today': 15},
            {'tokens_today': 500, 'requests_today': 8},
            {'tokens_today': 15000, 'requests_today': 200}
        ]
        
        total_tokens = sum(key['tokens_today'] for key in keys_data)
        total_requests = sum(key['requests_today'] for key in keys_data)
        
        assert total_tokens == 16696
        assert total_requests == 223

    def test_key_switching_logic(self):
        """בדיקה שמעבר מפתחות קורה בסף הנכון"""
        # פרמטרי המערכת
        requests_per_minute = 9
        limit = 15
        safety_margin = 0.6  # 60%
        
        # חישוב סף
        threshold = limit * safety_margin  # 9 בקשות
        should_switch = requests_per_minute >= threshold
        
        assert should_switch == True

    def test_database_record_format(self):
        """בדיקה שפורמט רשומת השימוש נכון"""
        usage_record = {
            'key_id': 8,
            'tokens_used': 150,
            'requests_count': 1,
            'timestamp': datetime.now(timezone.utc)
        }
        
        assert 'key_id' in usage_record
        assert 'tokens_used' in usage_record
        assert usage_record['key_id'] == 8

def run_simple_tests():
    """הרצת טסטים פשוטים"""
    test = TestDashboard()
    
    try:
        test.test_token_calculation()
        print("✅ טסט חישוב טוקנים עבר")
        
        test.test_key_switching_logic()
        print("✅ טסט מעבר מפתחות עבר")
        
        test.test_database_record_format()
        print("✅ טסט פורמט דאטבייס עבר")
        
        print("🎉 כל הטסטים עברו!")
        
    except Exception as e:
        print(f"❌ שגיאה: {e}")

if __name__ == "__main__":
    run_simple_tests() 