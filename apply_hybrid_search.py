#!/usr/bin/env python
"""
Script to apply the hybrid_search_documents SQL function to the Supabase database
"""

import os
import sys
import logging
import asyncio
from pathlib import Path
import dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
dotenv.load_dotenv(override=True)

# Check if we're in the project root
project_root = Path(__file__).parent.resolve()
backend_dir = project_root / "src" / "backend"
sys.path.insert(0, str(backend_dir))

# Try to import the document_processor
try:
    from services.document_processor import DocumentProcessor
except ImportError:
    logger.error("Error importing DocumentProcessor. Make sure you're running this from the project root.")
    sys.exit(1)

async def apply_hybrid_search_function():
    """
    Apply the hybrid_search_documents SQL function to the Supabase database
    """
    # Create an instance of DocumentProcessor to use its Supabase client
    doc_processor = DocumentProcessor()
    
    # Check if the function already exists
    try:
        check_sql = "SELECT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'hybrid_search_documents')"
        check_result = doc_processor.supabase.table("document_chunks").execute(check_sql)
        logger.info(f"Function check result: {check_result}")
        
        # Read the SQL file
        migration_path = project_root / "supabase" / "migrations" / "20250602170000_add_hybrid_search.sql"
        if not migration_path.exists():
            logger.error(f"Migration file not found at: {migration_path}")
            return False
        
        with open(migration_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Execute the SQL
        logger.info("Applying hybrid_search_documents function to database...")
        result = doc_processor.supabase.rpc("exec_sql", {"sql": sql_content}).execute()
        
        # Verify the function was created
        check_result = doc_processor.supabase.rpc("check_hybrid_search_exists").execute()
        if hasattr(check_result, 'data') and check_result.data:
            logger.info("Successfully applied hybrid_search_documents function!")
            return True
        else:
            logger.error("Failed to verify the hybrid_search_documents function was created.")
            return False
            
    except Exception as e:
        logger.error(f"Error applying hybrid_search_documents function: {e}", exc_info=True)
        return False

# Alternative method: use direct SQL through the SQL API
async def apply_hybrid_search_direct():
    """Apply hybrid search function directly through SQL"""
    try:
        doc_processor = DocumentProcessor()
        
        # First check if the function exists
        logger.info("Checking if hybrid_search_documents function already exists...")
        try:
            check_result = doc_processor.supabase.rpc("hybrid_search_documents", {
                "query_embedding": [0] * 768,
                "query_text": "test",
                "match_threshold": 0.7,
                "match_count": 1
            }).execute()
            logger.info("hybrid_search_documents function already exists!")
            return True
        except Exception as e:
            logger.info(f"hybrid_search_documents function doesn't exist yet or error: {e}")
        
        # Read the SQL file
        migration_path = project_root / "supabase" / "migrations" / "20250602170000_add_hybrid_search.sql"
        if not migration_path.exists():
            logger.error(f"Migration file not found at: {migration_path}")
            return False
        
        with open(migration_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Split the SQL into individual statements
        statements = sql_content.split(';')
        
        # Execute each statement separately
        for i, stmt in enumerate(statements):
            if stmt.strip():
                try:
                    logger.info(f"Executing SQL statement {i+1}...")
                    # Use execute_sql RPC function if available
                    result = doc_processor.supabase.rpc("execute_sql", {"query": stmt}).execute()
                    logger.info(f"Result: {result}")
                except Exception as e:
                    logger.error(f"Error executing statement {i+1}: {e}")
        
        # Test if the function was created
        try:
            logger.info("Testing if hybrid_search_documents function was created...")
            test_result = doc_processor.supabase.rpc("hybrid_search_documents", {
                "query_embedding": [0] * 768,
                "query_text": "test",
                "match_threshold": 0.7,
                "match_count": 1
            }).execute()
            logger.info("hybrid_search_documents function successfully created!")
            return True
        except Exception as e:
            logger.error(f"Failed to verify hybrid_search_documents function: {e}")
            return False
            
    except Exception as e:
        logger.error(f"Error in apply_hybrid_search_direct: {e}", exc_info=True)
        return False

async def main():
    """Main entry point"""
    logger.info("Starting hybrid search function application...")
    
    # Try both methods
    success = await apply_hybrid_search_function()
    if not success:
        logger.info("Trying alternative direct SQL method...")
        success = await apply_hybrid_search_direct()
    
    if success:
        logger.info("Successfully applied hybrid_search_documents function!")
        # Run test to confirm
        test_cmd = sys.executable + " " + str(backend_dir / "test_rag_search.py")
        logger.info(f"Running test: {test_cmd}")
        os.system(test_cmd)
    else:
        logger.error("Failed to apply hybrid_search_documents function.")

if __name__ == "__main__":
    asyncio.run(main()) 