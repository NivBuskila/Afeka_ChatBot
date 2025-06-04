from app.exceptions.base import BusinessLogicError

class ChatSessionNotFoundError(BusinessLogicError):
    """Raised when chat session is not found"""
    pass

class TooManySessionsError(BusinessLogicError):
    """Raised when user has too many active sessions"""
    pass

class InvalidMessageError(BusinessLogicError):
    """Raised when message validation fails"""
    pass