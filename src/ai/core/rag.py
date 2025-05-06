"""
Main RAG module for the Afeka ChatBot system.
"""
import os
import logging
from typing import List, Dict, Any, Optional, Union, Tuple
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore

from .document_manager import DocumentManager
from .retriever import get_answer, get_llm, analyze_query
from .supabase_loader import SupabaseDocumentLoader

logger = logging.getLogger(__name__)

class AfekaRAG:
    """
    Main RAG class for the Afeka ChatBot system.
    Combines document management and retrieval functionality.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        persist_directory: str = "vector_store",
        collection_name: str = "afeka_docs",
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None
    ):
        """
        Initialize the RAG system.
        
        Args:
            api_key: The Google API key. If None, will try to get from environment.
            persist_directory: Directory to persist vector store.
            collection_name: Name of the collection in the vector store.
            supabase_url: The Supabase URL. If None, will try to get from environment.
            supabase_key: The Supabase API key. If None, will try to get from environment.
        """
        self.api_key = api_key
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.initialized = False
        self.document_manager = None
        
        # Supabase configuration
        self.supabase_url = supabase_url or os.environ.get("SUPABASE_URL")
        self.supabase_key = supabase_key or os.environ.get("SUPABASE_KEY")
        self.supabase_connected = False
        
        # Initialize language model and document manager
        try:
            # Try to get LLM
            try:
                self.llm = get_llm(api_key)
            except Exception as e:
                logger.error(f"Failed to initialize LLM: {e}")
                self.llm = None
            
            # Try to initialize document manager
            try:
                self.document_manager = DocumentManager(
                    persist_directory=persist_directory,
                    embeddings=None,  # Will use default embeddings
                    collection_name=collection_name
                )
                self.initialized = True
                logger.info(f"RAG system initialized with vector store at {persist_directory}")
            except Exception as e:
                logger.error(f"Failed to initialize document manager: {e}")
                self.document_manager = None
                
            # Test Supabase connection if credentials are provided
            if self.supabase_url and self.supabase_key:
                try:
                    # Create a test loader to validate connection
                    test_loader = SupabaseDocumentLoader(
                        supabase_url=self.supabase_url,
                        supabase_key=self.supabase_key,
                        table_name="documents",  # Default table name
                        query_filter={},         # No filter
                        content_field="content"  # Default content field
                    )
                    self.supabase_connected = True
                    logger.info("Supabase connection successful")
                except Exception as e:
                    logger.error(f"Supabase connection error: {e}")
                    self.supabase_connected = False
            
        except Exception as e:
            logger.error(f"Error initializing RAG system: {e}")
            self.initialized = False
            
    def load_document(
        self,
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> bool:
        """
        Load a document into the RAG system.
        
        Args:
            file_path: Path to the document.
            metadata: Optional metadata for the document.
            chunk_size: Size of text chunks.
            chunk_overlap: Overlap between chunks.
            
        Returns:
            Success status.
        """
        if not self.initialized or not self.document_manager:
            logger.error("RAG system not initialized")
            return False
            
        try:
            # Handle document loading
            logger.info(f"Loading document: {file_path}")
            
            # Set default metadata if not provided
            if metadata is None:
                metadata = {
                    "source": os.path.basename(file_path),
                    "type": "unknown",
                    "language": "hebrew" if file_path.endswith('.txt') else "unknown"
                }
            
            # Load document
            loader = DocumentLoader(file_path)
            documents = loader.load()
            
            # Split document into chunks
            document_splitter = DocumentSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
            document_chunks = document_splitter.split_documents(documents)
            
            # Add metadata to each chunk
            for chunk in document_chunks:
                chunk.metadata.update(metadata)
            
            # Add documents to vector store
            self.document_manager.add_documents(document_chunks)
            
            logger.info(f"Document loaded from {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading document: {e}")
            return False
            
    def load_url(
        self,
        url: str,
        metadata: Optional[Dict[str, Any]] = None,
        chunk_size: int = 512,
        chunk_overlap: int = 128
    ) -> bool:
        """
        Load a document from a URL into the RAG system.
        
        Args:
            url: URL to load the document from.
            metadata: Optional metadata for the document.
            chunk_size: Size of text chunks.
            chunk_overlap: Overlap between chunks.
            
        Returns:
            Success status.
        """
        if not self.initialized or not self.document_manager:
            logger.error("RAG system not initialized")
            return False
            
        try:
            self.document_manager.add_url(
                url=url,
                metadata=metadata or {},
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
            logger.info(f"Document loaded from {url}")
            return True
        except Exception as e:
            logger.error(f"Error loading URL: {e}")
            return False
            
    def load_directory(
        self,
        directory_path: str,
        glob_pattern: str = "**/*.*",
        metadata: Optional[Dict[str, Any]] = None,
        chunk_size: int = 512,
        chunk_overlap: int = 128
    ) -> bool:
        """
        Load documents from a directory into the RAG system.
        
        Args:
            directory_path: Path to the directory.
            glob_pattern: Pattern to match files.
            metadata: Optional metadata for the documents.
            chunk_size: Size of text chunks.
            chunk_overlap: Overlap between chunks.
            
        Returns:
            Success status.
        """
        if not self.initialized or not self.document_manager:
            logger.error("RAG system not initialized")
            return False
            
        try:
            self.document_manager.add_directory(
                directory_path=directory_path,
                glob_pattern=glob_pattern,
                metadata=metadata or {},
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
            logger.info(f"Documents loaded from {directory_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading directory: {e}")
            return False
            
    def load_from_supabase(
        self,
        table_name: str = "documents",
        query_filter: Optional[Dict[str, Any]] = None,
        content_field: str = "content",
        chunk_size: int = 512,
        chunk_overlap: int = 128
    ) -> Tuple[bool, int]:
        """
        Load documents from a Supabase table.
        
        Args:
            table_name: Name of the table in Supabase.
            query_filter: Optional filter for the query.
            content_field: Field containing the document content.
            chunk_size: Size of text chunks.
            chunk_overlap: Overlap between chunks.
            
        Returns:
            Tuple of (success, document count).
        """
        if not self.initialized or not self.document_manager:
            logger.error("RAG system not initialized")
            return False, 0
            
        if not self.supabase_url or not self.supabase_key:
            logger.error("Supabase credentials not set")
            return False, 0
            
        try:
            # Create loader
            loader = SupabaseDocumentLoader(
                supabase_url=self.supabase_url,
                supabase_key=self.supabase_key,
                table_name=table_name,
                query_filter=query_filter or {},
                content_field=content_field
            )
            
            # Load documents
            docs = loader.load()
            
            if not docs:
                logger.warning("No documents found in Supabase using content field")
                
                # Try to directly query Supabase for document URLs
                if loader.is_connected():
                    logger.info("Attempting to directly load documents from URLs in Supabase")
                    try:
                        response = loader.client.table(table_name).select("*").execute()
                        data = response.data if hasattr(response, 'data') else []
                        
                        logger.info(f"Found {len(data)} documents in Supabase table")
                        
                        doc_count = 0
                        for item in data:
                            if "url" in item and item["url"]:
                                url = item["url"]
                                logger.info(f"Loading document from URL: {url}")
                                
                                # Create metadata from item data
                                metadata = {
                                    "source": url,
                                    "title": item.get("name", ""),
                                    "id": item.get("id", ""),
                                    "supabase_doc_id": item.get("id", "")
                                }
                                
                                # Load the document from URL
                                success = self.load_url(
                                    url=url,
                                    metadata=metadata,
                                    chunk_size=chunk_size,
                                    chunk_overlap=chunk_overlap
                                )
                                
                                if success:
                                    doc_count += 1
                                    logger.info(f"Successfully loaded document from URL: {url}")
                                else:
                                    logger.warning(f"Failed to load document from URL: {url}")
                        
                        if doc_count > 0:
                            logger.info(f"Loaded {doc_count} documents from URLs in Supabase")
                            return True, doc_count
                    except Exception as e:
                        logger.error(f"Error trying to load documents from URLs: {e}")
                
                return True, 0
                
            # Process and add documents to vector store
            vector_store = self.document_manager.get_vector_store()
            if not vector_store:
                logger.error("Vector store not initialized")
                return False, 0
                
            # Process chunks
            from langchain_text_splitters import RecursiveCharacterTextSplitter
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size, 
                chunk_overlap=chunk_overlap
            )
            
            split_docs = text_splitter.split_documents(docs)
            
            # Add to vector store
            self.document_manager.add_documents_to_store(split_docs)
            
            logger.info(f"Loaded {len(docs)} documents from Supabase table {table_name}")
            return True, len(docs)
        except Exception as e:
            logger.error(f"Error loading from Supabase: {e}")
            return False, 0
     
    def answer_question(
        self,
        question: str,
        model_name: str = "gemini-1.5-flash"
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Answer a question using the RAG system.
        
        Args:
            question: The question to answer.
            model_name: Name of the model to use.
            
        Returns:
            Tuple of (answer text, list of relevant documents as dictionaries)
        """
        if not self.initialized or not self.document_manager:
            error_msg = "מערכת ה-RAG לא אותחלה כראוי. אנא פנה למנהל המערכת."
            return error_msg, []
            
        vector_store = self.document_manager.get_vector_store()
        if not vector_store:
            error_msg = "מאגר המסמכים אינו זמין כרגע. אנא פנה למנהל המערכת."
            return error_msg, []
            
        try:
            # Log the question that was received for debugging purposes
            logger.info(f"Received question: {repr(question)}")
            logger.info(f"Using model: {model_name}")
            
            # Get LLM with specified model
            llm = get_llm(self.api_key, model_name=model_name)
            
            # Get answer and relevant documents
            logger.info("Starting RAG retrieval and generation")
            answer, docs = get_answer(question, vector_store, llm)
            
            # Log the retrieved documents for debugging
            logger.info(f"Retrieved {len(docs)} documents")
            for i, doc in enumerate(docs):
                source = doc.metadata.get("source", "unknown")
                logger.info(f"Document {i+1}: Source={source}, Content preview: {doc.page_content[:100]}...")
            
            # Log the generated answer
            logger.info(f"Generated answer (preview): {answer[:200]}...")
            
            # Convert documents to dictionary representation for API response
            doc_dicts = []
            for doc in docs:
                doc_dict = {
                    "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                    "metadata": doc.metadata
                }
                doc_dicts.append(doc_dict)
                
            return answer, doc_dicts
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            error_msg = f"אירעה שגיאה בעת עיבוד השאלה שלך: {str(e)}"
            return error_msg, []
            
    def clear_documents(self) -> bool:
        """
        Clear all documents from the RAG system.
        
        Returns:
            Success status.
        """
        if not self.initialized or not self.document_manager:
            logger.error("RAG system not initialized")
            return False
            
        try:
            success = self.document_manager.clear_vector_store()
            if success:
                logger.info("Documents cleared from vector store")
            return success
        except Exception as e:
            logger.error(f"Error clearing documents: {e}")
            return False
            
    def get_vector_store(self) -> Optional[VectorStore]:
        """
        Get the vector store.
        
        Returns:
            Vector store or None if not initialized.
        """
        if not self.initialized or not self.document_manager:
            return None
            
        return self.document_manager.get_vector_store()
        
    def get_status(self) -> Dict[str, Any]:
        """
        Get the status of the RAG system.
        
        Returns:
            Dictionary with status information.
        """
        status = {
            "initialized": self.initialized,
            "vector_store_path": self.persist_directory,
            "collection_name": self.collection_name,
            "supabase_connected": self.supabase_connected,
            "document_count": 0
        }
        
        if self.initialized and self.document_manager:
            vector_store = self.document_manager.get_vector_store()
            if vector_store:
                try:
                    # Try to get document count if possible
                    # Access the ChromaDB client directly for accurate count
                    if hasattr(vector_store, "_collection") and hasattr(vector_store._collection, "count"):
                        status["document_count"] = vector_store._collection.count()
                    elif hasattr(vector_store, "_client") and hasattr(vector_store, "_collection_name"):
                        # Alternative way to get count
                        try:
                            collection = vector_store._client.get_collection(vector_store._collection_name)
                            if collection:
                                status["document_count"] = collection.count()
                            # If that fails, try to estimate count from get()
                            else:
                                try:
                                    items = vector_store.get()
                                    if items and hasattr(items, "__len__"):
                                        status["document_count"] = len(items)
                                    elif isinstance(items, dict) and "ids" in items:
                                        status["document_count"] = len(items["ids"])
                                except Exception as inner_e:
                                    logger.warning(f"Could not estimate document count via get(): {inner_e}")
                        except Exception as e:
                            logger.warning(f"Could not get document count via client: {e}")
                except Exception as e:
                    logger.warning(f"Could not get document count: {e}")
                    
        return status 

    def list_documents(self):
        """
        List all documents in the RAG system.
        
        Returns:
            list: List of documents with their metadata
        """
        try:
            # Get the ChromaDB client from the vector store
            chroma_client = self.document_manager.vector_store._client
            collection = chroma_client.get_collection(self.collection_name)
            
            # Get all documents
            all_docs = collection.get()
            
            # Format the results
            documents = []
            for i, doc_id in enumerate(all_docs['ids']):
                metadata = all_docs['metadatas'][i] if 'metadatas' in all_docs else {}
                content = all_docs['documents'][i] if 'documents' in all_docs else ""
                
                documents.append({
                    'id': doc_id,
                    'metadata': metadata,
                    'content_preview': content[:100] + '...' if len(content) > 100 else content
                })
                
            return documents
            
        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            return [] 