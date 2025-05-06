"""
Document Manager module for the Afeka ChatBot RAG system.
"""
import os
import logging
import json
from typing import List, Dict, Any, Optional, Union, Tuple
import requests
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore
from langchain_core.embeddings import Embeddings

from .document_loader import (
    load_document, 
    load_from_url, 
    load_from_directory,
    load_from_database
)
from .document_splitter import split_documents
from .vector_store import (
    get_embeddings,
    create_vector_store,
    load_vector_store,
    add_documents_to_store
)

logger = logging.getLogger(__name__)

class DocumentManager:
    """Manager for document operations in the RAG system."""
    
    def __init__(
        self,
        persist_directory: Optional[str] = None,
        embeddings: Optional[Embeddings] = None,
        collection_name: str = "afeka_docs"
    ):
        """
        Initialize the DocumentManager.
        
        Args:
            persist_directory: Directory to persist the vector store.
            embeddings: Embeddings model to use.
            collection_name: Name of the collection in the vector store.
        """
        self.persist_directory = persist_directory
        self.embeddings = embeddings or get_embeddings()
        self.collection_name = collection_name
        self.vector_store = None
        
        # Try to load existing vector store
        if persist_directory and os.path.exists(persist_directory):
            try:
                self.vector_store = load_vector_store(
                    persist_directory=persist_directory,
                    embeddings=self.embeddings,
                    collection_name=collection_name
                )
                logger.info(f"Loaded existing vector store from {persist_directory}")
            except Exception as e:
                logger.error(f"Error loading vector store: {str(e)}")
                self.vector_store = None
    
    def add_document(
        self, 
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        extract_section_metadata: bool = False
    ) -> bool:
        """
        Process and add a document to the vector store.
        
        Args:
            file_path: Path to the document file.
            metadata: Additional metadata to add to the document.
            chunk_size: Size of chunks to split document into.
            chunk_overlap: Overlap between chunks.
            extract_section_metadata: Whether to extract section metadata from content.
            
        Returns:
            Boolean indicating success or failure.
        """
        try:
            # Load the document
            documents = load_document(file_path)
            if not documents:
                logger.error(f"Failed to load document from {file_path}")
                return False
            
            # Add optional metadata
            if metadata:
                for doc in documents:
                    doc.metadata.update(metadata)
            
            # Split the document
            split_docs = split_documents(
                documents,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                extract_section_metadata_flag=extract_section_metadata
            )
            
            # Create or update vector store
            if self.vector_store is None:
                logger.info("Creating new vector store for document")
                self.vector_store = create_vector_store(
                    documents=split_docs,
                    embeddings=self.embeddings,
                    persist_directory=self.persist_directory,
                    collection_name=self.collection_name
                )
                return self.vector_store is not None
            else:
                logger.info("Adding document to existing vector store")
                # Fix: Check if vector_store and split_docs are valid before adding
                if not self.vector_store or not split_docs:
                    logger.error("Vector store or documents invalid")
                    return False
                    
                return add_documents_to_store(self.vector_store, split_docs)
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {str(e)}")
            return False
    
    def add_url(
        self, 
        url: str,
        metadata: Optional[Dict[str, Any]] = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> bool:
        """
        Process and add a document from URL to the vector store.
        
        Args:
            url: URL of the document.
            metadata: Additional metadata to add to the document.
            chunk_size: Size of chunks to split document into.
            chunk_overlap: Overlap between chunks.
            
        Returns:
            Boolean indicating success or failure.
        """
        try:
            # Load the document from URL
            documents = load_from_url(url)
            if not documents:
                logger.error(f"Failed to load document from {url}")
                return False
            
            # Add optional metadata and URL source
            for doc in documents:
                doc.metadata["source"] = url
                if metadata:
                    doc.metadata.update(metadata)
            
            # Split the document
            split_docs = split_documents(
                documents,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
            
            # Create or update vector store
            if self.vector_store is None:
                logger.info("Creating new vector store for URL document")
                self.vector_store = create_vector_store(
                    documents=split_docs,
                    embeddings=self.embeddings,
                    persist_directory=self.persist_directory,
                    collection_name=self.collection_name
                )
                return self.vector_store is not None
            else:
                logger.info("Adding URL document to existing vector store")
                return add_documents_to_store(self.vector_store, split_docs)
        except Exception as e:
            logger.error(f"Error processing URL {url}: {str(e)}")
            return False
    
    def add_directory(
        self, 
        directory_path: str,
        glob_pattern: str = "**/*.*",
        metadata: Optional[Dict[str, Any]] = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> bool:
        """
        Process and add all documents from a directory to the vector store.
        
        Args:
            directory_path: Path to the directory containing documents.
            glob_pattern: Pattern to match files.
            metadata: Additional metadata to add to all documents.
            chunk_size: Size of chunks to split documents into.
            chunk_overlap: Overlap between chunks.
            
        Returns:
            Boolean indicating success or failure.
        """
        try:
            # Load documents from directory
            documents = load_from_directory(directory_path, glob_pattern)
            if not documents:
                logger.error(f"Failed to load documents from {directory_path}")
                return False
            
            # Add optional metadata
            if metadata:
                for doc in documents:
                    doc.metadata.update(metadata)
            
            # Split the documents
            split_docs = split_documents(
                documents,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
            
            # Create or update vector store
            if self.vector_store is None:
                logger.info("Creating new vector store for directory documents")
                self.vector_store = create_vector_store(
                    documents=split_docs,
                    embeddings=self.embeddings,
                    persist_directory=self.persist_directory,
                    collection_name=self.collection_name
                )
                return self.vector_store is not None
            else:
                logger.info("Adding directory documents to existing vector store")
                return add_documents_to_store(self.vector_store, split_docs)
        except Exception as e:
            logger.error(f"Error processing directory {directory_path}: {str(e)}")
            return False
    
    def add_from_database(
        self,
        supabase_url: str,
        supabase_key: str,
        table_name: str = "documents",
        query_filter: Optional[Dict[str, Any]] = None,
        content_field: str = "content",
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> bool:
        """
        Process and add documents from Supabase database to the vector store.
        
        Args:
            supabase_url: Supabase URL.
            supabase_key: Supabase API key.
            table_name: Name of the table containing documents.
            query_filter: Optional filter for database query.
            content_field: Name of the field containing document content.
            chunk_size: Size of chunks to split documents into.
            chunk_overlap: Overlap between chunks.
            
        Returns:
            Boolean indicating success or failure.
        """
        try:
            # Fetch documents from database using REST API
            headers = {
                "apikey": supabase_key,
                "Authorization": f"Bearer {supabase_key}",
                "Content-Type": "application/json"
            }
            
            endpoint = f"{supabase_url}/rest/v1/{table_name}"
            params = {"select": "*"}
            
            # Add filters if provided
            if query_filter:
                for key, value in query_filter.items():
                    params[key] = value
            
            response = requests.get(endpoint, headers=headers, params=params)
            response.raise_for_status()
            
            documents_data = response.json()
            logger.info(f"Retrieved {len(documents_data)} documents from database")
            
            # Convert to Document objects
            # Ensure content_field is used as the page_content
            for doc in documents_data:
                if content_field in doc:
                    doc["content"] = doc[content_field]
            
            documents = load_from_database(documents_data)
            
            if not documents:
                logger.error("Failed to create documents from database records")
                return False
            
            # Split the documents
            split_docs = split_documents(
                documents,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
            
            # Create or update vector store
            if self.vector_store is None:
                logger.info("Creating new vector store for database documents")
                self.vector_store = create_vector_store(
                    documents=split_docs,
                    embeddings=self.embeddings,
                    persist_directory=self.persist_directory,
                    collection_name=self.collection_name
                )
                return self.vector_store is not None
            else:
                logger.info("Adding database documents to existing vector store")
                return add_documents_to_store(self.vector_store, split_docs)
        except Exception as e:
            logger.error(f"Error processing documents from database: {str(e)}")
            return False
    
    def get_vector_store(self) -> Optional[VectorStore]:
        """
        Get the vector store.
        
        Returns:
            VectorStore object or None if not initialized.
        """
        return self.vector_store
    
    def clear_vector_store(self) -> bool:
        """
        Clear the vector store.
        
        Returns:
            Boolean indicating success or failure.
        """
        try:
            if self.vector_store:
                # Most vector stores have a delete or clear method
                if hasattr(self.vector_store, '_collection'):
                    self.vector_store._collection.delete(where={})
                elif hasattr(self.vector_store, 'delete_collection'):
                    self.vector_store.delete_collection()
                elif hasattr(self.vector_store, 'clear'):
                    self.vector_store.clear()
                
                # Re-initialize the vector store
                self.vector_store = None
                
                logger.info("Vector store cleared successfully")
                return True
            else:
                logger.warning("No vector store to clear")
                return False
        except Exception as e:
            logger.error(f"Error clearing vector store: {str(e)}")
            return False 