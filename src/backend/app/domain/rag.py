# src/backend/app/domain/rag.py
"""RAG domain models for Phase 1 - Compatible with existing models"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum

from .base import BaseEntity


class ProcessingStatus(Enum):
    """Document processing status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing" 
    COMPLETED = "completed"
    FAILED = "failed"


class SearchType(Enum):
    """Search type enumeration"""
    SEMANTIC = "semantic"
    KEYWORD = "keyword"
    HYBRID = "hybrid"
    CONTEXTUAL = "contextual"


@dataclass
class Document(BaseEntity):
    """RAG Document domain entity (separate from existing Document model)"""
    title: str = ""
    content: str = ""
    file_path: Optional[str] = None
    processing_status: ProcessingStatus = ProcessingStatus.PENDING
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Initialize entity ID if not provided"""
        if not hasattr(self, 'id') or self.id is None:
            self.id = uuid4()
    
    def update_status(self, status: ProcessingStatus) -> None:
        """Update processing status and timestamp"""
        self.processing_status = status
        self.updated_at = datetime.utcnow()
    
    def is_completed(self) -> bool:
        """Check if document processing is completed"""
        return self.processing_status == ProcessingStatus.COMPLETED
    
    def is_failed(self) -> bool:
        """Check if document processing failed"""
        return self.processing_status == ProcessingStatus.FAILED
    
    def can_be_searched(self) -> bool:
        """Check if document can be used for search"""
        return self.processing_status == ProcessingStatus.COMPLETED


@dataclass
class DocumentChunk(BaseEntity):
    """Document chunk domain entity"""
    document_id: UUID = field(default_factory=uuid4)
    chunk_text: str = ""
    embedding: List[float] = field(default_factory=list)
    chunk_header: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    chunk_index: int = 0
    similarity_score: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Initialize entity ID if not provided"""
        if not hasattr(self, 'id') or self.id is None:
            self.id = uuid4()
    
    def has_embedding(self) -> bool:
        """Check if chunk has embedding vector"""
        return len(self.embedding) > 0
    
    def get_content_length(self) -> int:
        """Get length of chunk text"""
        return len(self.chunk_text)
    
    def get_display_content(self, max_length: int = 200) -> str:
        """Get truncated content for display"""
        if len(self.chunk_text) <= max_length:
            return self.chunk_text
        return self.chunk_text[:max_length] + "..."
    
    def set_similarity_score(self, score: float) -> None:
        """Set similarity score for search results"""
        self.similarity_score = max(0.0, min(1.0, score))  # Clamp between 0 and 1


@dataclass
class SearchResult:
    """Search result value object"""
    chunks: List[DocumentChunk] = field(default_factory=list)
    query: str = ""
    total_results: int = 0
    search_time_ms: int = 0
    similarity_threshold: float = 0.5
    search_type: SearchType = SearchType.SEMANTIC
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_top_chunks(self, count: int) -> List[DocumentChunk]:
        """Get top N chunks by similarity score"""
        sorted_chunks = sorted(
            self.chunks, 
            key=lambda c: c.similarity_score or 0.0, 
            reverse=True
        )
        return sorted_chunks[:count]
    
    def get_unique_documents(self) -> List[UUID]:
        """Get unique document IDs from search results"""
        return list(set(chunk.document_id for chunk in self.chunks))
    
    def has_results(self) -> bool:
        """Check if search returned any results"""
        return len(self.chunks) > 0
    
    def get_avg_similarity(self) -> float:
        """Get average similarity score"""
        if not self.chunks:
            return 0.0
        scores = [c.similarity_score for c in self.chunks if c.similarity_score is not None]
        return sum(scores) / len(scores) if scores else 0.0


@dataclass
class ProcessingResult:
    """Document processing result value object"""
    document_id: UUID = field(default_factory=uuid4)
    chunks_created: int = 0
    status: ProcessingStatus = ProcessingStatus.PENDING
    processing_time_ms: int = 0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_successful(self) -> bool:
        """Check if processing was successful"""
        return self.status == ProcessingStatus.COMPLETED
    
    def has_error(self) -> bool:
        """Check if processing resulted in error"""
        return self.status == ProcessingStatus.FAILED


@dataclass
class RAGResponse:
    """RAG (Retrieval-Augmented Generation) response value object"""
    answer: str = ""
    sources: List[Dict[str, Any]] = field(default_factory=list)
    query: str = ""
    context_used: int = 0
    search_time_ms: int = 0
    generation_time_ms: int = 0
    confidence_score: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_total_time_ms(self) -> int:
        """Get total processing time"""
        return self.search_time_ms + self.generation_time_ms
    
    def has_sources(self) -> bool:
        """Check if response has source documents"""
        return len(self.sources) > 0
    
    def get_source_count(self) -> int:
        """Get number of unique source documents"""
        return len(self.sources)


@dataclass
class EmbeddingResult:
    """Embedding generation result value object"""
    text: str = ""
    embedding: List[float] = field(default_factory=list)
    model_name: str = "default"
    generation_time_ms: int = 0
    success: bool = True
    error_message: Optional[str] = None
    
    def is_valid(self) -> bool:
        """Check if embedding is valid"""
        return self.success and len(self.embedding) > 0
    
    def get_dimension(self) -> int:
        """Get embedding dimension"""
        return len(self.embedding)


@dataclass
class ContextWindow:
    """Context window value object for LLM interactions"""
    content: str = ""
    token_count: int = 0
    chunk_count: int = 0
    max_tokens: int = 4000
    sources: List[str] = field(default_factory=list)
    
    def is_within_limit(self) -> bool:
        """Check if context is within token limit"""
        return self.token_count <= self.max_tokens
    
    def get_utilization_ratio(self) -> float:
        """Get context window utilization ratio"""
        return self.token_count / self.max_tokens if self.max_tokens > 0 else 0.0
    
    def has_content(self) -> bool:
        """Check if context has any content"""
        return len(self.content.strip()) > 0


# Domain Services (Business Logic)
class DocumentDomainService:
    """Domain service for document-related business logic"""
    
    @staticmethod
    def can_process_file_type(filename: str) -> bool:
        """Check if file type is supported for processing"""
        supported_extensions = {'.pdf', '.docx', '.txt', '.md'}
        return any(filename.lower().endswith(ext) for ext in supported_extensions)
    
    @staticmethod
    def validate_document_for_processing(document: Document) -> List[str]:
        """Validate document for processing and return list of errors"""
        errors = []
        
        if not document.title or not document.title.strip():
            errors.append("Document title cannot be empty")
        
        if not document.content or not document.content.strip():
            errors.append("Document content cannot be empty")
        
        if len(document.content) < 50:
            errors.append("Document content too short (minimum 50 characters)")
        
        if len(document.content) > 10_000_000:  # 10MB text limit
            errors.append("Document content too large (maximum 10MB)")
        
        return errors
    
    @staticmethod
    def should_reprocess_document(document: Document) -> bool:
        """Determine if document should be reprocessed"""
        return (
            document.processing_status == ProcessingStatus.FAILED or
            (document.processing_status == ProcessingStatus.PENDING and 
             (datetime.utcnow() - document.updated_at).total_seconds() > 3600)  # 1 hour timeout
        )


class ChunkDomainService:
    """Domain service for chunk-related business logic"""
    
    @staticmethod
    def validate_chunk_for_embedding(chunk: DocumentChunk) -> List[str]:
        """Validate chunk for embedding generation"""
        errors = []
        
        if not chunk.chunk_text or not chunk.chunk_text.strip():
            errors.append("Chunk text cannot be empty")
        
        if len(chunk.chunk_text) < 10:
            errors.append("Chunk text too short (minimum 10 characters)")
        
        if len(chunk.chunk_text) > 8192:  # Gemini embedding limit
            errors.append("Chunk text too long for embedding (maximum 8192 characters)")
        
        return errors
    
    @staticmethod
    def calculate_chunk_quality_score(chunk: DocumentChunk) -> float:
        """Calculate quality score for chunk (0.0 - 1.0)"""
        score = 1.0
        
        # Penalize very short chunks
        if len(chunk.chunk_text) < 100:
            score *= 0.5
        
        # Penalize chunks without headers
        if not chunk.chunk_header:
            score *= 0.9
        
        # Reward chunks with metadata
        if chunk.metadata:
            score *= 1.1
        
        # Ensure score is within bounds
        return max(0.0, min(1.0, score))


class SearchDomainService:
    """Domain service for search-related business logic"""
    
    @staticmethod
    def validate_search_query(query: str) -> List[str]:
        """Validate search query and return list of errors"""
        errors = []
        
        if not query or not query.strip():
            errors.append("Search query cannot be empty")
        
        if len(query.strip()) < 3:
            errors.append("Search query too short (minimum 3 characters)")
        
        if len(query) > 1000:
            errors.append("Search query too long (maximum 1000 characters)")
        
        return errors
    
    @staticmethod
    def filter_results_by_quality(
        results: List[DocumentChunk], 
        min_similarity: float = 0.5
    ) -> List[DocumentChunk]:
        """Filter search results by quality thresholds"""
        return [
            chunk for chunk in results 
            if chunk.similarity_score and chunk.similarity_score >= min_similarity
        ]
    
    @staticmethod
    def rank_results_by_relevance(results: List[DocumentChunk]) -> List[DocumentChunk]:
        """Rank results by multiple relevance factors"""
        def relevance_score(chunk: DocumentChunk) -> float:
            score = chunk.similarity_score or 0.0
            
            # Boost chunks with headers
            if chunk.chunk_header:
                score += 0.05
            
            # Boost chunks with rich metadata
            if len(chunk.metadata) > 2:
                score += 0.03
            
            # Consider chunk quality
            quality_score = ChunkDomainService.calculate_chunk_quality_score(chunk)
            score *= quality_score
            
            return score
        
        return sorted(results, key=relevance_score, reverse=True)