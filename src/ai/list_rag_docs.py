#!/usr/bin/env python
"""
Script to list all documents in the RAG system.
"""
import os
import logging
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def list_rag_documents():
    """
    List all documents in the RAG system.
    """
    try:
        from core.rag import AfekaRAG
        
        # Initialize RAG
        api_key = os.environ.get('GEMINI_API_KEY', '')
        vector_store_dir = os.environ.get('VECTOR_STORE_DIR', './data/vector_store')
        
        if not api_key:
            logger.error("GEMINI_API_KEY not found in environment variables")
            return False
        
        # Initialize RAG
        rag = AfekaRAG(
            api_key=api_key,
            persist_directory=vector_store_dir,
            collection_name="afeka_docs"
        )
        
        # Get all documents
        documents = rag.list_documents()
        
        # Print document information
        print("\n" + "=" * 80)
        print("RAG System Documents")
        print("=" * 80)
        
        if not documents:
            print("No documents found in the RAG system.")
            return True
        
        # Group documents by source
        docs_by_source = {}
        for doc in documents:
            source = doc.get('metadata', {}).get('source', 'Unknown')
            if source not in docs_by_source:
                docs_by_source[source] = []
            docs_by_source[source].append(doc)
        
        # Print document information by source
        for source, docs in docs_by_source.items():
            print(f"\nSource: {source}")
            print(f"Document Count: {len(docs)}")
            
            # Print example metadata
            if docs:
                print("Example Metadata:")
                metadata = docs[0].get('metadata', {})
                for key, value in metadata.items():
                    print(f"  - {key}: {value}")
            
            print("-" * 40)
        
        print(f"\nTotal Documents: {len(documents)}")
        print("=" * 80 + "\n")
        
        return True
        
    except Exception as e:
        logger.error(f"Error listing RAG documents: {e}")
        return False

def main():
    """Main entry point"""
    success = list_rag_documents()
    if not success:
        logger.error("Failed to list RAG documents")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 