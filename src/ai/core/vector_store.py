"""
Vector Store module for the Afeka ChatBot RAG system.
"""
import os
import logging
from typing import List, Optional, Dict, Any
import chromadb
from langchain_chroma import Chroma
from langchain_core.vectorstores import VectorStore
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

logger = logging.getLogger(__name__)

def get_embeddings(api_key: Optional[str] = None) -> Embeddings:
    """
    Get embeddings model.
    
    Args:
        api_key: Optional Google API key.
        
    Returns:
        Embeddings object.
    """
    if not api_key:
        api_key = os.environ.get('GEMINI_API_KEY', '')
    
    if not api_key:
        logger.error("No API key provided for embeddings")
        raise ValueError("API key is required for embeddings")
    
    try:
        return GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key)
    except Exception as e:
        logger.error(f"Error creating embeddings: {str(e)}")
        raise

def create_vector_store(
    documents: List[Document],
    embeddings: Optional[Embeddings] = None,
    persist_directory: Optional[str] = None,
    collection_name: str = "afeka_docs"
) -> VectorStore:
    """
    Create a vector store from documents.
    
    Args:
        documents: List of Document objects to store.
        embeddings: Embeddings model. If not provided, it will be created.
        persist_directory: Directory to persist the vector store.
        collection_name: Name of the collection.
        
    Returns:
        VectorStore object.
    """
    if not documents:
        logger.warning("No documents to store in vector store")
        return None
    
    try:
        if not embeddings:
            embeddings = get_embeddings()
        
        if persist_directory:
            logger.info(f"Creating persistent vector store in {persist_directory}")
            os.makedirs(persist_directory, exist_ok=True)
            db = Chroma.from_documents(
                documents=documents,
                embedding=embeddings,
                persist_directory=persist_directory,
                collection_name=collection_name
            )
            db.persist()
        else:
            logger.info("Creating in-memory vector store")
            db = Chroma.from_documents(
                documents=documents,
                embedding=embeddings,
                collection_name=collection_name
            )
        
        logger.info(f"Successfully created vector store with {len(documents)} documents")
        return db
    except Exception as e:
        logger.error(f"Error creating vector store: {str(e)}")
        return None

def load_vector_store(
    persist_directory: str,
    embeddings: Optional[Embeddings] = None,
    collection_name: str = "afeka_docs"
) -> VectorStore:
    """
    Load a vector store from a directory.
    
    Args:
        persist_directory: Directory where the vector store is persisted.
        embeddings: Embeddings model. If not provided, it will be created.
        collection_name: Name of the collection.
        
    Returns:
        VectorStore object.
    """
    if not os.path.exists(persist_directory):
        logger.error(f"Persistence directory {persist_directory} does not exist")
        return None
    
    try:
        if not embeddings:
            embeddings = get_embeddings()
        
        db = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings,
            collection_name=collection_name
        )
        
        logger.info(f"Successfully loaded vector store from {persist_directory}")
        return db
    except Exception as e:
        logger.error(f"Error loading vector store: {str(e)}")
        return None

def add_documents_to_store(
    vector_store: VectorStore,
    documents: List[Document]
) -> bool:
    """
    Add documents to an existing vector store.
    
    Args:
        vector_store: VectorStore object to add documents to.
        documents: List of Document objects to add.
        
    Returns:
        Boolean indicating success or failure.
    """
    if not vector_store or not documents:
        logger.warning("Vector store or documents not provided")
        return False
    
    try:
        vector_store.add_documents(documents)
        logger.info(f"Successfully added {len(documents)} documents to vector store")
        
        if hasattr(vector_store, 'persist'):
            vector_store.persist()
            logger.info("Vector store persisted")
            
        return True
    except Exception as e:
        logger.error(f"Error adding documents to vector store: {str(e)}")
        return False

def search_vector_store(
    vector_store: VectorStore,
    query: str,
    k: int = 4,
    category: Optional[str] = None,
    doc_type: Optional[str] = None,
    section_number: Optional[str] = None
) -> List[Document]:
    """
    Search for documents in the vector store.
    
    Args:
        vector_store: VectorStore object to search in.
        query: Query string.
        k: Number of documents to return.
        category: Optional category filter.
        doc_type: Optional document type filter.
        section_number: Optional section number to search for.
        
    Returns:
        List of Document objects.
    """
    if not vector_store:
        logger.warning("Vector store not provided")
        return []
    
    try:
        logger.info(f"Searching vector store for query: '{query}'")
        
        # Preprocess Hebrew query to handle potential directionality issues
        clean_query = preprocess_hebrew_query(query)
        if clean_query != query:
            logger.info(f"Preprocessed query: '{clean_query}'")
            query = clean_query
            
        # Handle section numbers in query
        if section_number:
            enhanced_query = f"{query} סעיף {section_number}"
            logger.info(f"Enhanced query with section number: '{enhanced_query}'")
            query = enhanced_query
        
        # Build filter dictionary
        search_filter = {}
        if category:
            search_filter["category"] = category
        if doc_type:
            search_filter["doc_type"] = doc_type

        # Make sure we have valid embeddings for the Hebrew query
        if hasattr(vector_store, '_embedding'):
            try:
                # Try to get embeddings for the query to check for any issues
                logger.info("Testing embeddings for query")
                vector_store._embedding.embed_query(query)
                logger.info("Embeddings test successful")
            except Exception as embed_err:
                logger.warning(f"Embeddings issue with query: {embed_err}")
                # If there's an issue, continue anyway - the embedding function will handle it
        
        # Execute the search
        search_start_time = os.times()
        if search_filter:
            logger.info(f"Applying filter: {search_filter}")
            docs = vector_store.similarity_search(query, k=k, filter=search_filter)
        else:
            docs = vector_store.similarity_search(query, k=k)
        search_end_time = os.times()
        
        # Calculate search time
        search_time = (search_end_time.user - search_start_time.user) + (search_end_time.system - search_start_time.system)
        logger.info(f"Search completed in {search_time:.4f} seconds, found {len(docs)} matching documents")
        
        # Log some info about the retrieved documents
        if docs:
            logger.info("Retrieved document details:")
            for i, doc in enumerate(docs):
                source = doc.metadata.get("source", "unknown")
                score = doc.metadata.get("score", "N/A")
                logger.info(f"Result {i+1}: source={source}, score={score}, content_length={len(doc.page_content)}")
                
                # Check for encoding issues in content
                try:
                    doc.page_content.encode('utf-8')
                except UnicodeError:
                    logger.warning(f"Unicode issue detected in doc {i+1}, fixing encoding")
                    doc.page_content = doc.page_content.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
        
        return docs
    except Exception as e:
        logger.error(f"Error searching vector store: {str(e)}", exc_info=True)
        return []

def preprocess_hebrew_query(query: str) -> str:
    """
    Preprocess Hebrew query to handle directionality issues.
    
    Args:
        query: Original query string.
        
    Returns:
        Preprocessed query string.
    """
    # Fix common RTL/LTR issues with Hebrew text
    # Note: This is a basic implementation, might need adjustments for specific use cases
    
    # Check if query contains section references, extract and normalize them
    import re
    
    # Find section numbers in format X.Y.Z
    section_pattern = r'(\d+)\.(\d+)(?:\.(\d+))?'
    
    def normalize_section_ref(match):
        # Make sure section references are properly formatted
        if match.group(3):  # Has third level (X.Y.Z)
            return f"{match.group(1)}.{match.group(2)}.{match.group(3)}"
        else:  # Has two levels (X.Y)
            return f"{match.group(1)}.{match.group(2)}"
            
    # Replace section numbers with normalized form
    normalized_query = re.sub(section_pattern, normalize_section_ref, query)
    
    # Add common terms that might help in retrieval
    section_match = re.search(section_pattern, query)
    if section_match:
        section_num = section_match.group(0)
        # Add explicit section terms if not already in query
        terms_to_check = [f"סעיף {section_num}", f"פרק {section_num}"]
        for term in terms_to_check:
            if term not in normalized_query:
                normalized_query = f"{normalized_query} {term}"
    
    return normalized_query 