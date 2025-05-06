"""
Supabase Document Loader for the Afeka ChatBot RAG system.
"""
import os
import logging
import json
from typing import List, Dict, Any, Optional, Iterator

import supabase
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

class SupabaseDocumentLoader:
    """
    Document loader for Supabase database.
    """
    
    def __init__(
        self,
        supabase_url: str,
        supabase_key: str,
        table_name: str = "documents",
        query_filter: Optional[Dict[str, Any]] = None,
        content_field: str = "content"
    ):
        """
        Initialize Supabase document loader.
        
        Args:
            supabase_url: Supabase URL. If None, tries to get from env var SUPABASE_URL.
            supabase_key: Supabase API key. If None, tries to get from env var SUPABASE_KEY.
            table_name: Name of the table in Supabase.
            query_filter: Optional filter for the query.
            content_field: The field containing the document content.
        """
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.table_name = table_name
        self.query_filter = query_filter or {}
        self.content_field = content_field
        self.client = None
        
        if not self.supabase_url:
            logger.warning("SUPABASE_URL not set - Supabase loader will not function")
        elif not self.supabase_key:
            logger.warning("SUPABASE_KEY not set - Supabase loader will not function")
        else:
            try:
                self.client = supabase.create_client(self.supabase_url, self.supabase_key)
                logger.info("Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing Supabase client: {e}")
                self.client = None
    
    def is_connected(self) -> bool:
        """
        Check if the Supabase client is initialized.
        
        Returns:
            True if connected, False otherwise.
        """
        if not self.client:
            return False
            
        try:
            # Try a simple query to check connection
            self.client.table(self.table_name).select("id").limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Error connecting to Supabase: {e}")
            return False
    
    def load(self) -> List[Document]:
        """
        Load documents from Supabase.
        
        Returns:
            List[Document]: The loaded documents.
        """
        if not self.client:
            logger.error("Supabase client not initialized")
            return []
            
        documents = []
        
        try:
            # Start with the base query
            query = self.client.table(self.table_name).select("*")
            
            # Add filters if provided
            if self.query_filter:
                for key, value in self.query_filter.items():
                    if isinstance(value, dict) and "operator" in value and "value" in value:
                        # Handle custom operators
                        op = value["operator"]
                        val = value["value"]
                        
                        if op == "eq":
                            query = query.eq(key, val)
                        elif op == "neq":
                            query = query.neq(key, val)
                        elif op == "gt":
                            query = query.gt(key, val)
                        elif op == "lt":
                            query = query.lt(key, val)
                        elif op == "gte":
                            query = query.gte(key, val)
                        elif op == "lte":
                            query = query.lte(key, val)
                        elif op == "like":
                            query = query.like(key, val)
                        elif op == "ilike":
                            query = query.ilike(key, val)
                        elif op == "is":
                            query = query.is_(key, val)
                        else:
                            logger.warning(f"Unsupported operator: {op}")
                    else:
                        # Simple equality filter
                        query = query.eq(key, value)
            
            # Execute the query
            response = query.execute()
            
            if not hasattr(response, 'data'):
                logger.warning("No data attribute in Supabase response")
                return []
                
            data = response.data
            logger.info(f"Retrieved {len(data)} records from Supabase")
            
            # Convert to Document objects
            for item in data:
                content = None
                
                # Try to get content directly from the content field
                if self.content_field in item and item[self.content_field]:
                    content = item[self.content_field]
                    logger.info(f"Got content directly from field '{self.content_field}'")
                
                # If no content found and URL exists, try to fetch content from URL
                if not content and "url" in item and item["url"]:
                    try:
                        import requests
                        url = item["url"]
                        logger.info(f"Attempting to fetch content from URL: {url}")
                        response = requests.get(url)
                        if response.status_code == 200:
                            content = response.text
                            logger.info(f"Successfully fetched content from URL: {url}")
                        else:
                            logger.warning(f"Failed to fetch content from URL: {url}, status: {response.status_code}")
                    except Exception as e:
                        logger.error(f"Error fetching content from URL: {str(e)}")
                
                # Skip if no content found
                if not content:
                    logger.warning(f"No content found for item: {item}")
                    continue
                    
                # Create metadata from all other fields
                metadata = {k: v for k, v in item.items() if k != self.content_field}
                
                documents.append(Document(page_content=content, metadata=metadata))
            
        except Exception as e:
            logger.error(f"Error loading documents from Supabase: {e}")
            
        return documents
    
    def load_and_split(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 128
    ) -> List[Document]:
        """
        Load documents from Supabase and split them into chunks.
        
        Args:
            chunk_size: The size of the chunks to split the documents into.
            chunk_overlap: The overlap between chunks.
            
        Returns:
            List[Document]: The loaded and split documents.
        """
        documents = self.load()
        
        if not documents:
            return []
            
        try:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
            split_docs = text_splitter.split_documents(documents)
            logger.info(f"Split {len(documents)} documents into {len(split_docs)} chunks")
            return split_docs
        except Exception as e:
            logger.error(f"Error splitting documents: {e}")
            return documents  # Return unsplit documents on error
            
    def count_documents(self) -> int:
        """
        Count the number of documents in the table.
        
        Returns:
            int: The number of documents.
        """
        if not self.client:
            logger.error("Supabase client not initialized")
            return 0
            
        try:
            # Start with the base query
            query = self.client.table(self.table_name).select("count", count="exact")
            
            # Add filters if provided
            if self.query_filter:
                for key, value in self.query_filter.items():
                    if isinstance(value, dict) and "operator" in value and "value" in value:
                        # Handle custom operators
                        op = value["operator"]
                        val = value["value"]
                        
                        if op == "eq":
                            query = query.eq(key, val)
                        elif op == "neq":
                            query = query.neq(key, val)
                        elif op == "gt":
                            query = query.gt(key, val)
                        elif op == "lt":
                            query = query.lt(key, val)
                        elif op == "gte":
                            query = query.gte(key, val)
                        elif op == "lte":
                            query = query.lte(key, val)
                        elif op == "like":
                            query = query.like(key, val)
                        elif op == "ilike":
                            query = query.ilike(key, val)
                        elif op == "is":
                            query = query.is_(key, val)
                        else:
                            logger.warning(f"Unsupported operator: {op}")
                    else:
                        # Simple equality filter
                        query = query.eq(key, value)
            
            # Execute the query
            response = query.execute()
            
            if not hasattr(response, 'count'):
                logger.warning("No count attribute in Supabase response")
                return 0
                
            return response.count
        except Exception as e:
            logger.error(f"Error counting documents in Supabase: {e}")
            return 0
    
    def get_document_by_id(self, document_id: str) -> Optional[Document]:
        """
        Get a document by ID from Supabase.
        
        Args:
            document_id: ID of the document to retrieve.
            
        Returns:
            Document object or None if not found.
        """
        if not self.client:
            logger.error("Supabase client not initialized")
            return None
            
        try:
            response = self.client.table(self.table_name).select("*").eq("id", document_id).execute()
            
            if not response.data or len(response.data) == 0:
                logger.warning(f"Document with ID {document_id} not found")
                return None
                
            doc_data = response.data[0]
            
            # Check if document has content
            content = doc_data.get(self.content_field)
            if not content:
                # Try to fetch content from URL if available (try both "file_url" and "url" fields)
                url = None
                if "file_url" in doc_data and doc_data["file_url"]:
                    url = doc_data["file_url"]
                elif "url" in doc_data and doc_data["url"]:
                    url = doc_data["url"]
                
                if url:
                    try:
                        import requests
                        logger.info(f"Attempting to fetch content from URL: {url}")
                        response = requests.get(url)
                        if response.status_code == 200:
                            content = response.text
                            logger.info(f"Successfully fetched content from URL: {url}")
                        else:
                            logger.warning(f"Could not fetch content from URL: {url}, status: {response.status_code}")
                    except Exception as e:
                        logger.error(f"Error fetching document content from URL: {e}")
            
            if not content:
                logger.warning(f"Document {document_id} has no content and no valid URL")
                return None
                
            # Create metadata dictionary from document data
            metadata = {k: v for k, v in doc_data.items() if k != self.content_field}
            
            # Create Document object
            doc = Document(
                page_content=content,
                metadata=metadata
            )
            
            return doc
            
        except Exception as e:
            logger.error(f"Error getting document from Supabase: {e}")
            return None 