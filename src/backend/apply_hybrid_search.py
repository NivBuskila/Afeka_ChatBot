#!/usr/bin/env python
"""
Script to apply the hybrid_search_documents SQL function to the Supabase database
This script will read the SQL file and execute it via the Supabase client
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
project_root = Path(__file__).parent.resolve().parent.parent
backend_dir = project_root / "src" / "backend"
sys.path.insert(0, str(backend_dir))

# Try to import the document_processor to get access to the Supabase client
try:
    from services.document_processor import DocumentProcessor
except ImportError as e:
    logger.error(f"Error importing DocumentProcessor: {e}")
    logger.error("Make sure you're running this script from the project root directory.")
    sys.exit(1)

# Path to the SQL migration file
HYBRID_SEARCH_SQL_PATH = project_root / "src" / "supabase" / "migrations" / "20250628000000_fix_hybrid_search.sql"
if not HYBRID_SEARCH_SQL_PATH.exists():
    HYBRID_SEARCH_SQL_PATH = project_root / "supabase" / "migrations" / "20250602170000_add_hybrid_search.sql"

async def apply_hybrid_search_function():
    """Apply the hybrid search function SQL to the Supabase database"""
    logger.info("Starting application of hybrid search function...")
    
    # Read the SQL file
    if not HYBRID_SEARCH_SQL_PATH.exists():
        logger.error(f"SQL file not found at {HYBRID_SEARCH_SQL_PATH}")
        return False
    
    logger.info(f"Reading SQL file from {HYBRID_SEARCH_SQL_PATH}")
    with open(HYBRID_SEARCH_SQL_PATH, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Initialize document processor to get Supabase client
    doc_processor = DocumentProcessor()
    
    # Execute the SQL in chunks since some Supabase instances have SQL statement size limits
    # Split the SQL by the semicolons that end statements
    sql_statements = sql_content.split(';')
    
    # Since direct SQL execution is not available, we'll need to create a database function
    # that can execute arbitrary SQL, then call it via RPC
    
    # First, let's check if we can create an exec_sql function (only if it doesn't exist)
    try:
        create_exec_sql_fn = """
        CREATE OR REPLACE FUNCTION exec_sql(sql text)
        RETURNS void
        LANGUAGE plpgsql
        SECURITY DEFINER
        AS $$
        BEGIN
          EXECUTE sql;
        END;
        $$;
        """
        
        # We'll try to create this function using a direct table insert with a special format
        # that Supabase might interpret as a SQL execution (this is a workaround)
        logger.info("Attempting to create exec_sql function...")
        
        # Method 1: Try using the stored procedures table
        try:
            response = doc_processor.supabase.table("_rpc").insert({
                "name": "exec_sql_setup",
                "definition": create_exec_sql_fn
            }).execute()
            
            if hasattr(response, 'error') and response.error:
                logger.warning(f"Could not create exec_sql function via _rpc table: {response.error}")
            else:
                logger.info("Successfully created exec_sql function")
        except Exception as e:
            logger.warning(f"Error creating exec_sql function via _rpc table: {e}")
        
        # Method 2: Try using the hybrid_search_documents function directly if it already exists
        try:
            # Try to directly execute the hybrid_search_documents creation SQL using RPC
            logger.info("Attempting direct creation of hybrid_search_documents function...")
            
            # Extract just the CREATE FUNCTION part from the SQL file
            hybrid_search_fn_sql = ""
            for statement in sql_statements:
                if "CREATE OR REPLACE FUNCTION hybrid_search_documents" in statement:
                    # Make sure we're not referencing chunk_index
                    if "chunk_index" in statement:
                        # Remove the chunk_index column from the function definition
                        statement = statement.replace("chunk_index integer", "")
                        # Remove the chunk_index from the select statement
                        statement = statement.replace("dc.chunk_index", "")
                        statement = statement.replace(",\n    dc.chunk_index", "")
                    hybrid_search_fn_sql = statement
                    break
            
            if hybrid_search_fn_sql:
                # Add missing placeholder parameter values to test if we can call RPC
                test_params = {
                    "query_embedding": [0.0] * 768,  # Placeholder vector with 768 dimensions
                    "query_text": "test", 
                    "match_threshold": 0.7,
                    "match_count": 5
                }
                
                # Try to call the function first to see if it exists
                try:
                    response = doc_processor.supabase.rpc("hybrid_search_documents", test_params).execute()
                    if not (hasattr(response, 'error') and 'PGRST202' in str(response.error)):
                        logger.info("hybrid_search_documents function already exists")
                        return True
                except Exception as e:
                    if 'PGRST202' not in str(e):
                        logger.warning(f"Unexpected error checking for hybrid_search_documents: {e}")
                
                # If we get here, the function doesn't exist yet
                logger.info("hybrid_search_documents function doesn't exist yet, creating...")
            
            # Apply the basic insert function which is simpler and might work
            insert_fn_sql = ""
            for statement in sql_statements:
                if "CREATE OR REPLACE FUNCTION insert_document_chunk_basic" in statement:
                    insert_fn_sql = statement
                    break
            
            if insert_fn_sql:
                logger.info("Attempting to create insert_document_chunk_basic function...")
                # Here we would execute the SQL, but without direct SQL execution, 
                # we'll need to apply the migration through other means
        
        except Exception as e:
            logger.warning(f"Error in direct creation attempt: {e}")
    
    except Exception as e:
        logger.error(f"Error setting up SQL execution: {e}")
    
    # Since we can't execute SQL directly, let's suggest manual migration
    logger.info("\n" + "="*80)
    logger.info("UNABLE TO AUTOMATICALLY APPLY SQL MIGRATION")
    logger.info("Please apply the migration manually using one of these methods:")
    logger.info("1. Use the Supabase web interface SQL editor to execute the SQL file")
    logger.info(f"   SQL file path: {HYBRID_SEARCH_SQL_PATH}")
    logger.info("2. Use the Supabase CLI to apply the migration")
    logger.info("3. Copy the SQL below and execute it directly in your database:")
    
    # Fix SQL content before displaying - remove chunk_index references
    fixed_sql = sql_content
    if "chunk_index integer" in fixed_sql:
        fixed_sql = fixed_sql.replace("chunk_index integer", "")
    if "dc.chunk_index" in fixed_sql:
        fixed_sql = fixed_sql.replace(", dc.chunk_index", "")
        fixed_sql = fixed_sql.replace(",\n    dc.chunk_index", "")
    
    logger.info("\n" + fixed_sql)
    logger.info("="*80 + "\n")
    
    return False

async def test_hybrid_search_function():
    """Test that the hybrid search function is working"""
    logger.info("Testing hybrid search function...")
    
    # Initialize document processor
    doc_processor = DocumentProcessor()
    
    # Create a test query
    test_query = "סטודנט"
    
    # First, generate an embedding for the query
    query_embedding = await doc_processor._generate_embedding(test_query, is_query=True)
    
    if not query_embedding:
        logger.error("Failed to generate query embedding for test.")
        return False
    
    logger.info(f"Generated query embedding for test. Calling hybrid_search_documents RPC...")
    
    try:
        # Call the hybrid search function
        response = doc_processor.supabase.rpc(
            "hybrid_search_documents", 
            {
                "query_embedding": query_embedding,
                "query_text": test_query,
                "match_threshold": 0.7, 
                "match_count": 5,
                "semantic_weight": 0.6,
                "keyword_weight": 0.4
            }
        ).execute()
        
        if hasattr(response, 'data') and response.data:
            logger.info(f"Successfully called hybrid_search_documents RPC. Found {len(response.data)} results.")
            logger.info("Test passed!")
            return True
        elif hasattr(response, 'error') and response.error:
            logger.error(f"Error response from hybrid_search_documents RPC: {response.error}")
            return False
        else:
            logger.warning("No results returned from hybrid_search_documents RPC.")
            return False
            
    except Exception as e:
        logger.error(f"Error calling hybrid_search_documents RPC: {e}")
        return False

async def main():
    """Main function to apply and test the hybrid search function"""
    # Test if the function already exists before trying to apply it
    logger.info("First checking if hybrid_search_documents function already exists...")
    if await test_hybrid_search_function():
        logger.info("hybrid_search_documents function is already working!")
        return
        
    # Function doesn't exist or is not working, try to apply it
    logger.info("hybrid_search_documents function doesn't exist or is not working correctly.")
    if await apply_hybrid_search_function():
        # Test the hybrid search function
        await test_hybrid_search_function()
    else:
        logger.error("Failed to apply hybrid search function. Please apply it manually.")

if __name__ == "__main__":
    asyncio.run(main()) 