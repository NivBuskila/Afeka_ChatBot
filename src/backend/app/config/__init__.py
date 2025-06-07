# src/backend/app/config/__init__.py
"""Configuration module exports"""

# Import main settings
try:
    from .settings import Settings, settings
    _HAS_SETTINGS = True
except ImportError:
    _HAS_SETTINGS = False

# Import RAG settings if available
try:
    from .rag_settings import RAGSettings, create_rag_settings, rag_settings
    _HAS_RAG_SETTINGS = True
except ImportError:
    _HAS_RAG_SETTINGS = False

# Build exports
__all__ = []

if _HAS_SETTINGS:
    __all__.extend(["Settings", "settings"])

if _HAS_RAG_SETTINGS:
    __all__.extend(["RAGSettings", "create_rag_settings", "rag_settings"])