#!/usr/bin/env python
"""
Script to load the PDF file of military service (miluim) rights
into the RAG system.
"""
import os
import logging
import argparse
import sys
from pathlib import Path
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

def convert_pdf_to_text(pdf_path: str, output_text_path: Optional[str] = None) -> Optional[str]:
    """
    Convert a PDF file to text.
    
    Args:
        pdf_path: Path to the PDF file
        output_text_path: Optional path to save the text file
        
    Returns:
        str: Path to the saved text file, or None if failed
    """
    try:
        from PyPDF2 import PdfReader
        
        # Check if file exists
        if not os.path.isfile(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            return None
        
        # Create PDF reader
        reader = PdfReader(pdf_path)
        
        # Extract text from all pages
        text_content = ""
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                text_content += f"--- עמוד {page_num + 1} ---\n{text}\n\n"
        
        # If output path provided, save to file
        if output_text_path:
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(output_text_path)), exist_ok=True)
            
            with open(output_text_path, 'w', encoding='utf-8') as f:
                f.write(text_content)
            
            logger.info(f"PDF converted and saved to {output_text_path}")
            return output_text_path
        
        return text_content
    
    except ImportError:
        logger.error("PyPDF2 library not installed. Install with 'pip install PyPDF2'")
        return None
    except Exception as e:
        logger.error(f"Error converting PDF to text: {e}")
        return None

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
                "source": "נוהל זכויות סטודנטים המשרתים במילואים",
                "type": "regulation",
                "category": "military_service",
                "language": "hebrew"
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
    parser = argparse.ArgumentParser(description="Load military service rights PDF into RAG")
    parser.add_argument("--pdf", default="data/docs/נוהל-זכויות-סטודנטים-המשרתים-בשירות-מילואיםcleaned.pdf", 
                        help="Path to the PDF file")
    parser.add_argument("--output", default="data/docs/miluim_rights.txt", 
                        help="Path to save the text file")
    parser.add_argument("--load-only", action="store_true", 
                        help="Load the existing text file without converting PDF")
    
    args = parser.parse_args()
    
    # If load-only is specified, skip PDF conversion
    if args.load_only:
        if not os.path.isfile(args.output):
            logger.error(f"Text file not found: {args.output}")
            return 1
        
        success = load_text_to_rag(args.output)
        if not success:
            logger.error("Failed to load text file into RAG")
            return 1
        
        logger.info("Text file loaded into RAG successfully")
        return 0
    
    # Convert PDF to text
    text_file_path = convert_pdf_to_text(args.pdf, args.output)
    if not text_file_path:
        logger.error("Failed to convert PDF to text")
        return 1
    
    # Load text file into RAG
    success = load_text_to_rag(text_file_path)
    if not success:
        logger.error("Failed to load text file into RAG")
        return 1
    
    logger.info("Military service rights document processed and loaded into RAG successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 