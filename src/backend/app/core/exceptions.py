from typing import Optional

class RepositoryError(Exception):
    """Base exception for repository-related errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code or 500
        super().__init__(self.message)