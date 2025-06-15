"""
Test Utilities and Helper Functions
Common utilities and helper functions for testing
"""
import json
import time
import uuid
import random
import string
from typing import Dict, Any, List
from faker import Faker

fake = Faker()


class TestDataGenerator:
    """Generate test data for various scenarios"""
    
    @staticmethod
    def generate_user_data() -> Dict[str, Any]:
        """Generate realistic user data"""
        return {
            "id": str(uuid.uuid4()),
            "email": fake.email(),
            "name": fake.name(),
            "created_at": fake.iso8601(),
            "role": random.choice(["user", "admin", "student"])
        }
    
    @staticmethod
    def generate_chat_session_data(user_id: str = None) -> Dict[str, Any]:
        """Generate chat session data"""
        return {
            "id": str(uuid.uuid4()),
            "user_id": user_id or str(uuid.uuid4()),
            "title": fake.sentence(nb_words=4),
            "created_at": fake.iso8601(),
            "updated_at": fake.iso8601()
        }
    
    @staticmethod
    def generate_message_data(session_id: str = None, user_id: str = None) -> Dict[str, Any]:
        """Generate message data"""
        return {
            "id": str(uuid.uuid4()),
            "session_id": session_id or str(uuid.uuid4()),
            "user_id": user_id or str(uuid.uuid4()),
            "content": fake.text(max_nb_chars=200),
            "role": random.choice(["user", "assistant"]),
            "created_at": fake.iso8601()
        }
    
    @staticmethod
    def generate_document_data() -> Dict[str, Any]:
        """Generate document data"""
        return {
            "id": str(uuid.uuid4()),
            "title": fake.sentence(nb_words=6),
            "content": fake.text(max_nb_chars=1000),
            "category": random.choice(["regulations", "policies", "procedures", "guidelines"]),
            "tags": [fake.word() for _ in range(random.randint(1, 5))],
            "uploaded_at": fake.iso8601(),
            "processed": random.choice([True, False])
        }
    
    @staticmethod
    def generate_hebrew_text(length: int = 100) -> str:
        """Generate Hebrew text for testing"""
        hebrew_words = [
            "שלום", "בוקר", "טוב", "איך", "שלומך", "תודה", "רבה", "מה", "נשמע", "כיף",
            "ללמוד", "באפקה", "קולג'", "סטודנט", "לימודים", "מבחן", "תואר", "קורס",
            "הרצאה", "מטלה", "פרויקט", "מחקר", "ביבליוגרפיה", "מדריך", "עזרה"
        ]
        
        selected_words = random.choices(hebrew_words, k=length // 10)
        return " ".join(selected_words)
    
    @staticmethod
    def generate_malicious_inputs() -> List[str]:
        """Generate malicious input strings for security testing"""
        return [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "<?php echo 'php injection'; ?>",
            "../../../etc/passwd",
            "javascript:alert('xss')",
            "onload=alert('xss')",
            "${7*7}",
            "{{7*7}}",
            "%3Cscript%3Ealert('xss')%3C/script%3E"
        ]


class TestAssertions:
    """Custom assertions for testing"""
    
    @staticmethod
    def assert_valid_uuid(value: str) -> bool:
        """Assert that a string is a valid UUID"""
        try:
            uuid.UUID(value)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def assert_valid_timestamp(value: str) -> bool:
        """Assert that a string is a valid ISO timestamp"""
        try:
            import datetime
            datetime.datetime.fromisoformat(value.replace('Z', '+00:00'))
            return True
        except ValueError:
            return False
    
    @staticmethod
    def assert_response_time(response_time_ms: float, max_time_ms: float = 1000) -> bool:
        """Assert that response time is within acceptable limits"""
        return response_time_ms <= max_time_ms
    
    @staticmethod
    def assert_no_sensitive_data(text: str, sensitive_terms: List[str] = None) -> bool:
        """Assert that text doesn't contain sensitive information"""
        if sensitive_terms is None:
            sensitive_terms = ["password", "secret", "key", "token", "auth"]
        
        text_lower = text.lower()
        return not any(term in text_lower for term in sensitive_terms)
    
    @staticmethod
    def assert_hebrew_support(text: str) -> bool:
        """Assert that text contains Hebrew characters"""
        hebrew_range = range(0x0590, 0x05FF)
        return any(ord(char) in hebrew_range for char in text)


class PerformanceTracker:
    """Track performance metrics during testing"""
    
    def __init__(self):
        self.metrics = []
    
    def start_timer(self, operation_name: str) -> str:
        """Start timing an operation"""
        timer_id = str(uuid.uuid4())
        start_time = time.time()
        
        self.metrics.append({
            "id": timer_id,
            "operation": operation_name,
            "start_time": start_time,
            "end_time": None,
            "duration": None
        })
        
        return timer_id
    
    def end_timer(self, timer_id: str) -> float:
        """End timing an operation and return duration"""
        end_time = time.time()
        
        for metric in self.metrics:
            if metric["id"] == timer_id:
                metric["end_time"] = end_time
                metric["duration"] = end_time - metric["start_time"]
                return metric["duration"]
        
        return 0.0
    
    def get_metrics(self) -> List[Dict[str, Any]]:
        """Get all collected metrics"""
        return self.metrics
    
    def get_average_duration(self, operation_name: str) -> float:
        """Get average duration for a specific operation"""
        durations = [
            metric["duration"] for metric in self.metrics
            if metric["operation"] == operation_name and metric["duration"] is not None
        ]
        
        return sum(durations) / len(durations) if durations else 0.0


class MockDataStore:
    """Mock data store for testing"""
    
    def __init__(self):
        self.users = {}
        self.sessions = {}
        self.messages = {}
        self.documents = {}
    
    def add_user(self, user_data: Dict[str, Any]) -> str:
        """Add a user to the mock store"""
        user_id = user_data.get("id", str(uuid.uuid4()))
        self.users[user_id] = user_data
        return user_id
    
    def add_session(self, session_data: Dict[str, Any]) -> str:
        """Add a session to the mock store"""
        session_id = session_data.get("id", str(uuid.uuid4()))
        self.sessions[session_id] = session_data
        return session_id
    
    def add_message(self, message_data: Dict[str, Any]) -> str:
        """Add a message to the mock store"""
        message_id = message_data.get("id", str(uuid.uuid4()))
        self.messages[message_id] = message_data
        return message_id
    
    def add_document(self, document_data: Dict[str, Any]) -> str:
        """Add a document to the mock store"""
        document_id = document_data.get("id", str(uuid.uuid4()))
        self.documents[document_id] = document_data
        return document_id
    
    def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all sessions for a user"""
        return [
            session for session in self.sessions.values()
            if session.get("user_id") == user_id
        ]
    
    def get_session_messages(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all messages for a session"""
        return [
            message for message in self.messages.values()
            if message.get("session_id") == session_id
        ]
    
    def clear_all(self):
        """Clear all mock data"""
        self.users.clear()
        self.sessions.clear()
        self.messages.clear()
        self.documents.clear()


# Global instances for easy access
test_data_generator = TestDataGenerator()
test_assertions = TestAssertions()
performance_tracker = PerformanceTracker()
mock_data_store = MockDataStore()