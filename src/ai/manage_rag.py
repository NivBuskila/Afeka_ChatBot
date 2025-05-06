#!/usr/bin/env python
"""
Command Line Interface for managing the RAG system.
"""
import os
import sys
import logging
import argparse
import json
from dotenv import load_dotenv
from core.rag import AfekaRAG

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def init_rag_system():
    """Initialize RAG system"""
    api_key = os.environ.get('GEMINI_API_KEY', '')
    vector_store_dir = os.environ.get('VECTOR_STORE_DIR', './data/vector_store')
    
    if not api_key:
        logger.error("GEMINI_API_KEY not found in environment variables")
        return None
    
    try:
        # Ensure vector store directory exists
        os.makedirs(vector_store_dir, exist_ok=True)
        
        rag = AfekaRAG(
            api_key=api_key,
            persist_directory=vector_store_dir,
            collection_name="afeka_docs"
        )
        
        return rag
    except Exception as e:
        logger.error(f"Error initializing RAG system: {str(e)}")
        return None

def add_document(args):
    """Add a document to the system"""
    rag = init_rag_system()
    if not rag:
        return 1
    
    try:
        # Parse metadata if provided
        metadata = {}
        if args.metadata:
            try:
                metadata = json.loads(args.metadata)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON metadata: {args.metadata}")
                return 1
        
        # Process based on source type
        if args.url:
            logger.info(f"Adding document from URL: {args.url}")
            success = rag.load_url(
                url=args.url,
                metadata=metadata,
                chunk_size=args.chunk_size,
                chunk_overlap=args.chunk_overlap
            )
        elif args.file:
            logger.info(f"Adding document from file: {args.file}")
            success = rag.load_document(
                file_path=args.file,
                metadata=metadata,
                chunk_size=args.chunk_size,
                chunk_overlap=args.chunk_overlap
            )
        elif args.directory:
            logger.info(f"Adding documents from directory: {args.directory}")
            success = rag.load_directory(
                directory_path=args.directory,
                glob_pattern=args.glob_pattern,
                metadata=metadata,
                chunk_size=args.chunk_size,
                chunk_overlap=args.chunk_overlap
            )
        else:
            logger.error("No source specified (--url, --file, or --directory)")
            return 1
        
        if success:
            logger.info("Document(s) added successfully")
            return 0
        else:
            logger.error("Failed to add document(s)")
            return 1
    except Exception as e:
        logger.error(f"Error adding document: {str(e)}")
        return 1

def test_query(args):
    """Test a query against the system"""
    rag = init_rag_system()
    if not rag:
        return 1
    
    try:
        logger.info(f"Testing query: {args.query}")
        
        answer = rag.answer_question(args.query)
        
        print("\n" + "="*80)
        print("Query: ", args.query)
        print("="*80)
        print("Answer:")
        print(answer)
        print("="*80 + "\n")
        
        return 0
    except Exception as e:
        logger.error(f"Error testing query: {str(e)}")
        return 1

def clear_documents(args):
    """Clear all documents from the system"""
    rag = init_rag_system()
    if not rag:
        return 1
    
    try:
        if not args.force:
            confirm = input("Are you sure you want to clear all documents? (y/N): ")
            if confirm.lower() != 'y':
                logger.info("Operation cancelled")
                return 0
        
        logger.info("Clearing all documents...")
        success = rag.clear_documents()
        
        if success:
            logger.info("Documents cleared successfully")
            return 0
        else:
            logger.error("Failed to clear documents")
            return 1
    except Exception as e:
        logger.error(f"Error clearing documents: {str(e)}")
        return 1

def info(args):
    """Show information about the RAG system"""
    rag = init_rag_system()
    if not rag:
        return 1
    
    try:
        vector_store = rag.get_vector_store()
        if not vector_store:
            logger.info("No documents loaded in the system")
            return 0
        
        # Try to get information about the vector store
        print("\n" + "="*80)
        print("RAG System Information")
        print("="*80)
        
        print(f"Persistence Directory: {rag.persist_directory}")
        print(f"Collection Name: {rag.collection_name}")
        
        # Try to get collection stats if available
        if hasattr(vector_store, '_collection'):
            try:
                collection_info = vector_store._collection.get()
                if hasattr(collection_info, 'count'):
                    print(f"Document Count: {collection_info.count}")
            except:
                pass
        
        print("="*80 + "\n")
        
        return 0
    except Exception as e:
        logger.error(f"Error getting system information: {str(e)}")
        return 1

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Manage RAG System")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Add document command
    add_parser = subparsers.add_parser("add", help="Add document to the system")
    source_group = add_parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--url", help="URL to load document from")
    source_group.add_argument("--file", help="File path to load document from")
    source_group.add_argument("--directory", help="Directory to load documents from")
    add_parser.add_argument("--glob-pattern", default="**/*.*", help="Glob pattern for directory loading")
    add_parser.add_argument("--metadata", help="JSON metadata to add to document")
    add_parser.add_argument("--chunk-size", type=int, default=1000, help="Size of document chunks")
    add_parser.add_argument("--chunk-overlap", type=int, default=200, help="Overlap between chunks")
    add_parser.set_defaults(func=add_document)
    
    # Test query command
    test_parser = subparsers.add_parser("test", help="Test a query against the system")
    test_parser.add_argument("query", help="Query to test")
    test_parser.set_defaults(func=test_query)
    
    # Clear documents command
    clear_parser = subparsers.add_parser("clear", help="Clear all documents from the system")
    clear_parser.add_argument("--force", action="store_true", help="Force clear without confirmation")
    clear_parser.set_defaults(func=clear_documents)
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Show information about the RAG system")
    info_parser.set_defaults(func=info)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    return args.func(args)

if __name__ == "__main__":
    sys.exit(main()) 