"""
Document Splitter module for the Afeka ChatBot RAG system.
"""
import logging
import re
from typing import List, Optional, Dict, Any
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    CharacterTextSplitter,
    MarkdownTextSplitter
)
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

def extract_section_metadata(text: str) -> Dict[str, Any]:
    """
    Extract section metadata from a text chunk.
    
    Args:
        text: Text content to analyze.
        
    Returns:
        Dictionary with extracted metadata.
    """
    metadata = {}
    
    # Extract section numbers (like 4.3, 5.1, etc.)
    section_pattern = re.compile(r'(?:^|\n)(?:#{1,6}\s+)?(?:סעיף\s+)?(\d+(?:\.\d+){0,2})\s+([^\n]+)', re.MULTILINE)
    match = section_pattern.search(text)
    
    if match:
        section_number = match.group(1)
        section_title = match.group(2).strip()
        level = len(section_number.split('.'))
        
        metadata["section_number"] = section_number
        metadata["section_title"] = section_title
        metadata["section_level"] = level
        
        # Add normalized section numbers for each level
        parts = section_number.split('.')
        if len(parts) >= 1:
            metadata["level_1"] = parts[0]
        if len(parts) >= 2:
            metadata["level_2"] = f"{parts[0]}.{parts[1]}"
        if len(parts) >= 3:
            metadata["level_3"] = f"{parts[0]}.{parts[1]}.{parts[2]}"
    
    return metadata

def split_documents(
    documents: List[Document], 
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    split_method: str = "recursive",
    document_type: Optional[str] = None,
    extract_section_metadata_flag: bool = False
) -> List[Document]:
    """
    Split documents into smaller chunks.
    
    Args:
        documents: List of Document objects to split.
        chunk_size: Maximum size of each chunk.
        chunk_overlap: Overlap between chunks.
        split_method: Method to use for splitting ("recursive", "character", "markdown").
        document_type: Document type to determine splitter if split_method is not specified.
        extract_section_metadata_flag: Whether to extract section metadata from content.
        
    Returns:
        List of Document objects after splitting.
    """
    if not documents:
        logger.warning("No documents to split")
        return []
    
    # For Hebrew text, use special separators that work well with RTL text
    hebrew_separators = ["\n\n", "\n", ".", "!", "?", ";", ":", " ", ""]
    
    # Check if documents contain Hebrew text
    contains_hebrew = False
    hebrew_pattern = re.compile(r'[\u0590-\u05FF\uFB1D-\uFB4F]')
    for doc in documents:
        if hebrew_pattern.search(doc.page_content):
            contains_hebrew = True
            break
    
    # Determine splitter to use
    if split_method == "recursive" or not split_method:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False,
            separators=hebrew_separators if contains_hebrew else None
        )
    elif split_method == "character":
        splitter = CharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separator="\n"
        )
    elif split_method == "markdown":
        splitter = MarkdownTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
    elif split_method == "html":
        # Fall back to RecursiveCharacterTextSplitter for HTML
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["</div>", "</p>", "</li>", "<br>", "\n", " ", ""]
        )
    else:
        logger.warning(f"Unknown split method: {split_method}, falling back to recursive")
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
    
    try:
        logger.info(f"Splitting {len(documents)} documents with {split_method} method")
        split_docs = splitter.split_documents(documents)
        logger.info(f"Successfully split into {len(split_docs)} chunks")
        
        # Add section numbering to metadata
        for i, doc in enumerate(split_docs):
            doc.metadata["chunk_id"] = i
            doc.metadata["total_chunks"] = len(split_docs)
            
            # Extract section metadata if requested
            if extract_section_metadata_flag:
                section_metadata = extract_section_metadata(doc.page_content)
                if section_metadata:
                    logger.info(f"Found section metadata in chunk {i}: {section_metadata}")
                    doc.metadata.update(section_metadata)
            
        return split_docs
    except Exception as e:
        logger.error(f"Error splitting documents: {str(e)}")
        return documents  # Return original documents on error

def split_by_category(documents: List[Document]) -> Dict[str, List[Document]]:
    """
    Organize documents by category from metadata.
    
    Args:
        documents: List of Document objects to organize.
        
    Returns:
        Dictionary mapping categories to lists of documents.
    """
    categories = {}
    
    for doc in documents:
        category = doc.metadata.get("category", "general")
        if category not in categories:
            categories[category] = []
        categories[category].append(doc)
    
    return categories

def split_by_doc_type(documents: List[Document]) -> Dict[str, List[Document]]:
    """
    Group documents by their type from metadata.
    
    Args:
        documents: List of Document objects to organize.
        
    Returns:
        Dictionary mapping document types to lists of documents.
    """
    doc_types = {}
    
    for doc in documents:
        doc_type = doc.metadata.get("doc_type", "unknown")
        if doc_type not in doc_types:
            doc_types[doc_type] = []
        doc_types[doc_type].append(doc)
    
    return doc_types 