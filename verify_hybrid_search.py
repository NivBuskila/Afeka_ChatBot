#!/usr/bin/env python
"""
This script verifies if the hybrid search functionality is properly set up
in the Supabase database by testing the hybrid_search_documents function.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
import dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
dotenv.load_dotenv(override=True)

# Set up path to import document_processor
project_root = Path(__file__).parent.resolve()
backend_dir = project_root / "src" / "backend"
sys.path.insert(0, str(backend_dir))

try:
    from services.document_processor import DocumentProcessor
except ImportError as e:
    logger.error(f"Error importing DocumentProcessor: {e}")
    logger.error("Make sure you're running this script from the project root directory.")
    sys.exit(1)

async def verify_hybrid_search():
    """Verify that the hybrid search function is working"""
    logger.info("Verifying hybrid search functionality...")
    
    # Initialize document processor
    doc_processor = DocumentProcessor()
    
    # Test queries with expected results
    test_queries = [
        "סטודנט",
        "זכויות סטודנט",
        "מהן אפשרויות הערעור על ציון?",
        "תנאי מעבר משנה לשנה"
    ]
    
    success = True
    
    # Test each query
    for query in test_queries:
        logger.info(f"Testing query: '{query}'")
        
        # Generate query embedding
        query_embedding = await doc_processor._generate_embedding(query, is_query=True)
        
        if not query_embedding:
            logger.error(f"Failed to generate embedding for query: '{query}'")
            success = False
            continue
        
        logger.info(f"Generated embedding for query. Testing hybrid search...")
        
        try:
            # Try semantic search first
            semantic_results = await doc_processor.search_documents(
                query=query, 
                limit=3, 
                threshold=0.5  # Lower threshold for testing
            )
            
            if semantic_results:
                logger.info(f"Semantic search found {len(semantic_results)} results for query: '{query}'")
                for i, result in enumerate(semantic_results[:2], 1):
                    similarity = result.get('similarity', 0)
                    snippet = result.get('chunk_text', '')[:100].replace('\n', ' ')
                    logger.info(f"  Result {i}: Similarity: {similarity:.4f}, Snippet: '{snippet}...'")
            else:
                logger.warning(f"Semantic search found no results for query: '{query}'")
            
            # Now try hybrid search
            hybrid_results = await doc_processor.hybrid_search(
                query=query, 
                limit=3, 
                threshold=0.5  # Lower threshold for testing
            )
            
            if hybrid_results:
                logger.info(f"Hybrid search found {len(hybrid_results)} results for query: '{query}'")
                # Print the raw results for debugging
                logger.info(f"Raw hybrid search results for '{query}': {hybrid_results}")
                for i, res in enumerate(hybrid_results):
                    # Correctly access the fields from SQL output
                    # SQL returns 'semantic_similarity' for the pure semantic score
                    # SQL returns 'similarity' for the final combined score
                    semantic_sim = res.get('semantic_similarity', 0) 
                    combined_sim = res.get('similarity', 0) # This is the actual combined score from SQL
                    keyword_sim = res.get('keyword_similarity', 0) # Also log this if available
                    snippet = res.get('chunk_text', '')[:100].replace('\n', ' ')
                    logger.info(f"  Result {i+1}: Semantic: {semantic_sim:.4f}, Keyword: {keyword_sim:.4f}, Combined: {combined_sim:.4f}, Snippet: '{snippet}...'")
            else:
                logger.warning(f"Hybrid search found no results for query: '{query}'")
                logger.warning("This could indicate the hybrid_search_documents function is not properly set up.")
                success = False
                
        except Exception as e:
            logger.error(f"Error testing hybrid search with query '{query}': {e}")
            success = False
    
    if success:
        logger.info("\n✅ Hybrid search functionality appears to be working correctly!")
        return True
    else:
        logger.error("\n❌ Hybrid search functionality is not working correctly!")
        logger.error("Please apply the SQL migration manually using the instructions in HYBRID_SEARCH_SETUP.md")
        return False

async def check_function_exists():
    """Check if the hybrid_search_documents function exists in the database"""
    logger.info("Checking if hybrid_search_documents function exists in the database...")
    
    doc_processor = DocumentProcessor()
    
    try:
        # Try to call the function with minimal parameters
        test_params = {
            "query_embedding": [0.0] * 768,
            "query_text": "test",
            "match_threshold": 0.5,
            "match_count": 1
        }
        
        response = doc_processor.supabase.rpc("hybrid_search_documents", test_params).execute()
        
        if hasattr(response, 'error') and response.error:
            if 'PGRST202' in str(response.error):
                logger.error("❌ The hybrid_search_documents function does not exist in the database.")
                return False
            else:
                logger.warning(f"Unexpected error calling hybrid_search_documents: {response.error}")
                logger.warning("The function might exist but has errors.")
                return False
        else:
            logger.info("✅ The hybrid_search_documents function exists in the database.")
            return True
            
    except Exception as e:
        logger.error(f"Error checking for hybrid_search_documents function: {e}")
        return False

async def main():
    """Main function"""
    logger.info("Starting hybrid search verification...")
    
    # First, check if the function exists
    function_exists = await check_function_exists()
    
    if function_exists:
        # If function exists, verify it works correctly
        await verify_hybrid_search()
    else:
        logger.error("The hybrid_search_documents function does not exist in the database.")
        logger.error("Please apply the SQL migration using the instructions in HYBRID_SEARCH_SETUP.md")
    
if __name__ == "__main__":
    asyncio.run(main()) 