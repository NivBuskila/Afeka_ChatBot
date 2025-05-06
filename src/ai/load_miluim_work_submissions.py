#!/usr/bin/env python
"""
Script to load the additional military service work submissions information
into the RAG system.
"""
import os
import logging
import sys
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_text_to_rag(text_file_path: str, metadata: Optional[dict] = None) -> bool:
    """
    Load a text file into the RAG system.
    
    Args:
        text_file_path: Path to the text file
        metadata: Optional metadata for the document
        
    Returns:
        bool: Success status
    """
    try:
        from core.rag import AfekaRAG
        
        # Initialize RAG
        api_key = os.environ.get('GEMINI_API_KEY', '')
        vector_store_dir = os.environ.get('VECTOR_STORE_DIR', './data/vector_store')
        
        if not api_key:
            logger.error("GEMINI_API_KEY not found in environment variables")
            return False
        
        # Ensure vector store directory exists
        os.makedirs(vector_store_dir, exist_ok=True)
        
        # Initialize RAG
        rag = AfekaRAG(
            api_key=api_key,
            persist_directory=vector_store_dir,
            collection_name="afeka_docs"
        )
        
        # Default metadata if not provided
        if metadata is None:
            metadata = {
                "source": "נוהל זכויות סטודנטים המשרתים במילואים - הנחיות הגשת עבודות",
                "title": "הנחיות להגשת עבודות לסטודנטים במילואים",
                "type": "regulation",
                "category": "military_service",
                "language": "hebrew",
                "doc_type": "נוהל", 
                "audience": "סטודנטים",
                "keywords": "מילואים, זכויות סטודנטים, הגשת עבודות, דחיית מועדים, הקלות"
            }
        
        # Load document
        success = rag.load_document(
            file_path=text_file_path,
            metadata=metadata,
            chunk_size=1000,
            chunk_overlap=200
        )
        
        if success:
            logger.info(f"Successfully loaded document {text_file_path} into RAG")
            return True
        else:
            logger.error(f"Failed to load document {text_file_path} into RAG")
            return False
            
    except Exception as e:
        logger.error(f"Error loading document into RAG: {e}")
        return False

def main():
    """Main entry point"""
    file_path = "data/docs/miluim_work_submissions.txt"
    
    # Check if file exists
    if not os.path.isfile(file_path):
        logger.error(f"Text file not found: {file_path}")
        return 1
    
    # Load text file into RAG
    success = load_text_to_rag(file_path)
    if not success:
        logger.error("Failed to load text file into RAG")
        return 1
    
    logger.info("Military service work submissions document loaded into RAG successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 