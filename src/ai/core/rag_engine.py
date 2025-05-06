"""
RAG Engine - Core module for the Afeka ChatBot RAG system.
"""
import os
import re
import logging
from typing import List, Dict, Any, Optional, Tuple, Union

from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from google.generativeai import configure as genai_configure
from google.generativeai.types import GenerationConfig
from langchain_google_genai import ChatGoogleGenerativeAI

from .supabase_loader import SupabaseDocumentLoader

logger = logging.getLogger(__name__)

class AfekaRAG:
    """
    Retrieval Augmented Generation system for the Afeka ChatBot.
    """
    
    DEFAULT_PERSISTENCE_DIR = "data/vector_store"
    DEFAULT_COLLECTION_NAME = "afeka_docs"
    DEFAULT_CHUNK_SIZE = 1000
    DEFAULT_CHUNK_OVERLAP = 200
    DEFAULT_SIMILARITY_TOP_K = 4
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        persistence_dir: Optional[str] = None,
        collection_name: Optional[str] = None,
        model_name: str = "gemini-pro",
        embedding_model_name: str = "models/embedding-001",
        similarity_top_k: int = DEFAULT_SIMILARITY_TOP_K
    ):
        """
        Initialize the RAG Engine.
        
        Args:
            api_key: Google API key for Gemini.
            persistence_dir: Directory for persisting vector store.
            collection_name: Name for the Chroma collection.
            model_name: Name of the Gemini model to use.
            embedding_model_name: Name of the embedding model to use.
            similarity_top_k: Number of similar documents to retrieve.
        """
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        self.persistence_dir = persistence_dir or os.environ.get("VECTOR_STORE_DIR", self.DEFAULT_PERSISTENCE_DIR)
        self.collection_name = collection_name or self.DEFAULT_COLLECTION_NAME
        self.model_name = model_name
        self.embedding_model_name = embedding_model_name
        self.similarity_top_k = similarity_top_k
        
        # Create directories if they don't exist
        os.makedirs(self.persistence_dir, exist_ok=True)
        
        self.embeddings = None
        self.vector_store = None
        self.llm = None
        self.supabase_loader = None
        
        # Initialize
        if not self.api_key:
            logger.error("GOOGLE_API_KEY not set - RAG system will not function correctly")
        else:
            self._initialize_components()
    
    def _initialize_components(self):
        """Initialize embeddings, vector store and LLM."""
        try:
            # Configure Google Gemini API
            genai_configure(api_key=self.api_key)
            
            # Initialize embeddings
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model=self.embedding_model_name,
                google_api_key=self.api_key,
            )
            
            # Initialize vector store
            self._load_vector_store()
            
            # Initialize LLM
            generation_config = GenerationConfig(
                temperature=0.2,
                top_p=0.95,
                top_k=40,
                max_output_tokens=2048,
            )
            
            self.llm = ChatGoogleGenerativeAI(
                model=self.model_name,
                google_api_key=self.api_key,
                generation_config=generation_config,
                convert_system_message_to_human=True
            )
            
            # Initialize Supabase document loader
            self.supabase_loader = SupabaseDocumentLoader()
            
            logger.info("AfekaRAG components initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing RAG components: {e}")
    
    def _load_vector_store(self):
        """Load or create vector store."""
        try:
            self.vector_store = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.persistence_dir
            )
            logger.info(f"Vector store loaded successfully with {self.vector_store._collection.count()} documents")
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
    
    def add_documents(self, documents: List[Document], chunk_size: int = DEFAULT_CHUNK_SIZE, 
                     chunk_overlap: int = DEFAULT_CHUNK_OVERLAP) -> bool:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of Document objects to add.
            chunk_size: Size of chunks for splitting documents.
            chunk_overlap: Overlap between chunks.
            
        Returns:
            Boolean indicating success.
        """
        if not documents:
            logger.warning("No documents provided to add")
            return False
        
        if not self.vector_store or not self.embeddings:
            logger.error("Vector store or embeddings not initialized")
            return False
        
        try:
            # Split documents into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
            chunks = text_splitter.split_documents(documents)
            
            if not chunks:
                logger.warning("No chunks generated from documents")
                return False
            
            # Add chunks to vector store
            self.vector_store.add_documents(chunks)
            self.vector_store.persist()
            
            logger.info(f"Added {len(chunks)} chunks from {len(documents)} documents to vector store")
            return True
            
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            return False
    
    def load_from_supabase(self, limit: int = 100) -> bool:
        """
        Load documents directly from Supabase.
        
        Args:
            limit: Maximum number of documents to load.
            
        Returns:
            Boolean indicating success.
        """
        if not self.supabase_loader:
            logger.error("Supabase loader not initialized")
            return False
            
        try:
            # Get documents from Supabase
            documents = self.supabase_loader.get_documents(limit=limit)
            
            if not documents:
                logger.warning("No documents retrieved from Supabase")
                return False
                
            # Add documents to vector store
            result = self.add_documents(documents)
            
            return result
            
        except Exception as e:
            logger.error(f"Error loading documents from Supabase: {e}")
            return False
    
    def clear_vector_store(self) -> bool:
        """
        Clear all documents from the vector store.
        
        Returns:
            Boolean indicating success.
        """
        if not self.vector_store:
            logger.error("Vector store not initialized")
            return False
        
        try:
            self.vector_store.delete_collection()
            self._load_vector_store()  # Recreate an empty collection
            logger.info("Vector store cleared successfully")
            return True
        except Exception as e:
            logger.error(f"Error clearing vector store: {e}")
            return False
    
    def get_documents_count(self) -> int:
        """
        Get the number of documents in the vector store.
        
        Returns:
            Integer count of documents.
        """
        if not self.vector_store:
            logger.error("Vector store not initialized")
            return 0
        
        try:
            return self.vector_store._collection.count()
        except Exception as e:
            logger.error(f"Error getting document count: {e}")
            return 0
    
    def get_vector_store_info(self) -> Dict[str, Any]:
        """
        Get information about the vector store.
        
        Returns:
            Dictionary with vector store info.
        """
        info = {
            "persistence_dir": self.persistence_dir,
            "collection_name": self.collection_name,
            "document_count": self.get_documents_count(),
            "is_initialized": self.vector_store is not None and self.embeddings is not None,
            "supabase_connected": self.supabase_loader.is_connected() if self.supabase_loader else False
        }
        return info
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        Query the RAG system with a question.
        
        Args:
            question: The question to answer.
            
        Returns:
            Dictionary with answer and source documents.
        """
        if not self.vector_store or not self.llm:
            logger.error("Vector store or LLM not initialized")
            return {
                "answer": "מערכת ה-RAG לא מאותחלת כראוי. אנא בדוק את מפתח ה-API ושהמסמכים נטענו בהצלחה.",
                "sources": [],
                "error": "System not initialized"
            }
        
        try:
            # Retrieve relevant documents
            retrieved_docs = self.vector_store.similarity_search(question, k=self.similarity_top_k)
            
            if not retrieved_docs:
                return {
                    "answer": "לא נמצאו מסמכים רלוונטיים לשאלה שלך. אנא נסח את השאלה אחרת או בקש מידע בנושא אחר.",
                    "sources": [],
                    "error": "No relevant documents found"
                }
            
            # Prepare source documents info
            sources = []
            for doc in retrieved_docs:
                source_info = {
                    "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                    "metadata": doc.metadata
                }
                sources.append(source_info)
            
            # Prepare context for the LLM
            context = "\n\n".join([doc.page_content for doc in retrieved_docs])
            
            # Construct the prompt
            prompt = f"""
            אתה עוזר לסטודנטים במכללת אפקה להנדסה. השב על השאלה בהתבסס על המידע הבא בלבד.
            אם המידע לא מכיל תשובה ברורה, ציין זאת ואל תמציא מידע.
            השתמש בשפה עברית בתשובתך.
            
            מידע:
            {context}
            
            שאלה: {question}
            
            תשובה:
            """
            
            # Get answer from LLM
            response = self.llm.invoke(prompt)
            answer = response.content
            
            return {
                "answer": answer,
                "sources": sources,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Error querying RAG system: {e}")
            return {
                "answer": "חלה שגיאה בעיבוד השאלה שלך. אנא נסה שוב מאוחר יותר.",
                "sources": [],
                "error": str(e)
            } 