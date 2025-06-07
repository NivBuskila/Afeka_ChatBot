# src/backend/app/domain/base.py
"""Base domain models with support for both existing and new RAG models"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


# ===============================================
# EXISTING PYDANTIC-BASED MODELS (Your original)
# ===============================================

class DomainEntity(BaseModel):
    """Base domain entity with common fields"""
    
    class Config:
        # Allow ORM mode for easy conversion from database models
        from_attributes = True
        # Use enum values instead of names
        use_enum_values = True
        # Validate on assignment
        validate_assignment = True
        # Allow population by field name
        populate_by_name = True


class TimestampedEntity(DomainEntity):
    """Base entity with timestamp fields"""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


# ===============================================
# NEW DATACLASS-BASED MODELS (For RAG Phase 1)
# ===============================================

@dataclass
class BaseEntity:
    """Base class for new RAG domain entities using dataclasses"""
    id: UUID = field(default_factory=uuid4)
    
    def __eq__(self, other) -> bool:
        """Entities are equal if they have the same ID"""
        if not isinstance(other, BaseEntity):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash based on entity ID"""
        return hash(self.id)


class BaseValueObject(ABC):
    """Base class for value objects"""
    
    def __eq__(self, other) -> bool:
        """Value objects are equal if all their properties are equal"""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__
    
    def __hash__(self) -> int:
        """Hash based on all properties"""
        return hash(tuple(sorted(self.__dict__.items())))


@dataclass(frozen=True)
class FileMetadata(BaseValueObject):
    """Value object for file metadata"""
    filename: str
    file_size: int
    file_type: str
    content_type: Optional[str] = None
    encoding: Optional[str] = None
    checksum: Optional[str] = None
    upload_timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Validate file metadata"""
        if self.file_size < 0:
            raise ValueError("File size cannot be negative")
        if not self.filename or not self.filename.strip():
            raise ValueError("Filename cannot be empty")
        if not self.file_type:
            raise ValueError("File type is required")
    
    def get_extension(self) -> str:
        """Get file extension from filename"""
        return self.filename.split('.')[-1].lower() if '.' in self.filename else ''
    
    def is_supported_type(self, supported_types: list) -> bool:
        """Check if file type is supported"""
        extension = f".{self.get_extension()}"
        return extension in supported_types


@dataclass(frozen=True)
class EmbeddingVector(BaseValueObject):
    """Value object for embedding vectors"""
    values: list[float]
    model_name: str
    dimension: int
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Validate embedding vector"""
        if not self.values:
            raise ValueError("Embedding values cannot be empty")
        if len(self.values) != self.dimension:
            raise ValueError(f"Embedding dimension mismatch: expected {self.dimension}, got {len(self.values)}")
        if not all(isinstance(v, (int, float)) for v in self.values):
            raise ValueError("All embedding values must be numeric")
        if not self.model_name:
            raise ValueError("Model name is required")
    
    def to_list(self) -> list[float]:
        """Convert to list for database storage"""
        return list(self.values)


@dataclass(frozen=True)
class TextChunk(BaseValueObject):
    """Value object for text chunks"""
    text: str
    start_index: int
    end_index: int
    chunk_type: str = "content"
    metadata: dict = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate text chunk"""
        if not self.text.strip():
            raise ValueError("Chunk text cannot be empty")
        if self.start_index < 0:
            raise ValueError("Start index cannot be negative")
        if self.end_index <= self.start_index:
            raise ValueError("End index must be greater than start index")
    
    def get_length(self) -> int:
        """Get chunk text length"""
        return len(self.text)
    
    def get_word_count(self) -> int:
        """Get approximate word count"""
        return len(self.text.split())


# Domain Events
class DomainEvent(ABC):
    """Base class for domain events"""
    
    def __init__(self):
        self.occurred_at = datetime.utcnow()
        self.event_id = uuid4()
    
    @abstractmethod
    def get_event_type(self) -> str:
        """Get the event type identifier"""
        pass
    
    def to_dict(self) -> dict:
        """Convert event to dictionary"""
        return {
            "event_id": str(self.event_id),
            "event_type": self.get_event_type(),
            "occurred_at": self.occurred_at.isoformat(),
            **self._get_event_data()
        }
    
    @abstractmethod
    def _get_event_data(self) -> dict:
        """Get event-specific data"""
        pass


@dataclass
class DocumentProcessedEvent(DomainEvent):
    """Event raised when a document is successfully processed"""
    document_id: UUID
    chunks_created: int
    processing_time_ms: int
    
    def get_event_type(self) -> str:
        return "document_processed"
    
    def _get_event_data(self) -> dict:
        return {
            "document_id": str(self.document_id),
            "chunks_created": self.chunks_created,
            "processing_time_ms": self.processing_time_ms
        }


# ===============================================
# UTILITY FUNCTIONS
# ===============================================

def create_file_metadata_from_upload(
    filename: str, 
    content: bytes, 
    content_type: Optional[str] = None
) -> FileMetadata:
    """Create file metadata from uploaded file"""
    import hashlib
    
    file_type = filename.split('.')[-1].lower() if '.' in filename else 'unknown'
    
    metadata = FileMetadata(
        filename=filename,
        file_size=len(content),
        file_type=file_type,
        content_type=content_type,
        checksum=hashlib.sha256(content).hexdigest()
    )
    
    return metadata


def create_text_chunks_from_content(
    content: str, 
    chunk_size: int = 1000, 
    overlap: int = 100
) -> list[TextChunk]:
    """Create text chunks from content with overlap"""
    chunks = []
    start = 0
    chunk_index = 0
    
    while start < len(content):
        end = min(start + chunk_size, len(content))
        chunk_text = content[start:end]
        
        chunk = TextChunk(
            text=chunk_text,
            start_index=start,
            end_index=end,
            metadata={"chunk_index": chunk_index}
        )
        chunks.append(chunk)
        
        # Move start position with overlap
        start = max(start + chunk_size - overlap, start + 1)
        chunk_index += 1
        
        # Prevent infinite loop
        if start >= end:
            break
    
    return chunks