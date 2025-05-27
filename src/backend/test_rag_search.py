#!/usr/bin/env python
"""
סקריפט לבדיקת חיפוש RAG עם הגדרות שונות
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
import dotenv
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the parent directory to the path
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

# Load environment variables
dotenv.load_dotenv(override=True)

# Import the document processor
try:
    from services.document_processor import DocumentProcessor
except ImportError:
    logger.error("Error importing DocumentProcessor. Make sure the module exists and is in the PYTHONPATH.")
    sys.exit(1)

async def test_search(query: str, threshold: float = 0.6):
    """בדיקת חיפוש סמנטי"""
    logger.info(f"Testing search with query: '{query}' and threshold: {threshold}")
    
    # Create document processor
    processor = DocumentProcessor()
    
    # Perform search with different thresholds
    results = await processor.search_documents(query, limit=10, threshold=threshold)
    
    # Print results
    print(f"Found {len(results)} results for query '{query}' with threshold {threshold}:")
    print(json.dumps(results, indent=2, ensure_ascii=False))
    
    return results

async def test_hybrid_search(query: str, threshold: float = 0.6):
    """בדיקת חיפוש היברידי"""
    logger.info(f"Testing hybrid search with query: '{query}' and threshold: {threshold}")
    
    # Create document processor
    processor = DocumentProcessor()
    
    # Perform hybrid search with different thresholds
    results = await processor.hybrid_search(query, limit=10, threshold=threshold)
    
    # Print results
    print(f"Found {len(results)} results for hybrid query '{query}' with threshold {threshold}:")
    print(json.dumps(results, indent=2, ensure_ascii=False))
    
    return results

async def main():
    """פונקציה ראשית"""
    
    # Define queries and thresholds to test
    queries = ["תקנון", "לימודים", "אפקה", "תקנון לימודים", "הנדסה"]
    thresholds = [0.7, 0.6, 0.5, 0.4]
    
    # Test each query with each threshold
    for query in queries:
        print(f"\n===== Testing query: '{query}' =====")
        
        # Try with different thresholds
        for threshold in thresholds:
            print(f"\n----- Semantic search with threshold {threshold} -----")
            await test_search(query, threshold)
            
            print(f"\n----- Hybrid search with threshold {threshold} -----")
            await test_hybrid_search(query, threshold)
    
if __name__ == "__main__":
    asyncio.run(main()) 