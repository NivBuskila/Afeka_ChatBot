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
import numpy as np # Added for cosine similarity
import mimetypes

# Configure logging more verbosely
# Set the root logger level to DEBUG and ensure the format is applied
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s',
                    force=True) # force=True ensures this config takes precedence

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

def cosine_similarity(vec1, vec2):
    """Computes the cosine similarity between two vectors."""
    if not isinstance(vec1, np.ndarray):
        vec1 = np.array(vec1)
    if not isinstance(vec2, np.ndarray):
        vec2 = np.array(vec2)
    
    if vec1.shape != vec2.shape:
        logger.error(f"Cannot compute cosine similarity for vectors of different shapes: {vec1.shape} vs {vec2.shape}")
        return 0.0
        
    dot_product = np.dot(vec1, vec2)
    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)
    
    if norm_vec1 == 0 or norm_vec2 == 0:
        logger.warning("Cannot compute cosine similarity if one or both vectors have zero norm.")
        return 0.0
        
    similarity = dot_product / (norm_vec1 * norm_vec2)
    return similarity

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

async def test_process_single_document(processor: DocumentProcessor, doc_id: int, file_path: str):
    logger.info(f"Starting test_process_single_document for doc_id: {doc_id}, Path: {file_path}")
    if not os.path.isabs(file_path):
        project_root = Path(__file__).parent.parent.parent
        absolute_file_path = project_root / file_path
        logger.info(f"Relative path provided. Constructed absolute path: {absolute_file_path}")
    else:
        absolute_file_path = Path(file_path)
        logger.info(f"Absolute path provided: {absolute_file_path}")

    if not absolute_file_path.exists():
        logger.error(f"File not found at absolute path: {absolute_file_path}. Skipping processing.")
        # Attempt to delete any existing document record to prevent orphaned entries if this ID was used before
        try:
            # delete_response = await processor.supabase.table("documents").delete().eq("id", doc_id).execute() # No await
            delete_response = processor.supabase.table("documents").delete().eq("id", doc_id).execute()
            if hasattr(delete_response, 'data') and delete_response.data:
                logger.info(f"Cleanup: Successfully deleted document record for ID {doc_id} as file was not found.")
            elif hasattr(delete_response, 'error') and delete_response.error:
                 logger.error(f"Cleanup: Error deleting document record for ID {doc_id} (file not found): {delete_response.error.message}")
        except Exception as e_del_cleanup:
            logger.error(f"Cleanup: Exception during document delete for ID {doc_id} (file not found): {e_del_cleanup}")
        return

    file_size = absolute_file_path.stat().st_size
    file_url = absolute_file_path.as_uri()
    file_type = mimetypes.guess_type(file_url)[0] or "application/octet-stream"

    logger.info(f"Ensuring document record exists for ID: {doc_id}, Name: {absolute_file_path.name}, Type: {file_type}, Size: {file_size}, URL: {file_url}")
    
    insert_doc_data = {
        "id": doc_id,
        "name": absolute_file_path.name,
        "type": file_type,
        "size": file_size,
        "url": file_url,
        "status": "pending",  # Initial status before processing
        "processing_status": "pending", 
        "category": "test_document", # Example category
        # Add other mandatory fields from your 'documents' table schema with default/appropriate values
        "embedding_model": "gemini-embedding-001" # Or your default
    }
    logger.debug(f"Attempting to insert/ensure document record: {insert_doc_data}")
    try:
        # Upsert to ensure the document record exists and is updated if necessary
        # response = await processor.supabase.table("documents").upsert(insert_doc_data).execute() # No await
        response = processor.supabase.table("documents").upsert(insert_doc_data).execute()
        if hasattr(response, 'data') and response.data:
            logger.info(f"Document record ensured/updated for ID: {doc_id}. Response: {response.data}")
        elif hasattr(response, 'error') and response.error:
            logger.error(f"Error ensuring/updating document record for ID {doc_id}: {response.error.message}. Details: {response.error.details}")
            # If we can't even create/update the parent document record, processing it will likely fail.
            # However, the original DocumentProcessor might try to fetch it.
            # For testing, let's log and proceed to see DocumentProcessor's behavior.
        else:
            logger.warning(f"No data or error from Supabase upsert for document ID {doc_id}. Status: {response.status_code if hasattr(response, 'status_code') else 'N/A'}")

    except Exception as e_doc_insert:
        logger.error(f"Exception during document record insertion/ensure for ID {doc_id}: {e_doc_insert}", exc_info=True)
        # Decide if to return or try processing anyway
        # For now, log and proceed to test DocumentProcessor resilience
    
    logger.info(f"Calling processor.process_document for doc_id: {doc_id}, Path: '{absolute_file_path}'")
    try:
        result = await processor.process_document(document_id=doc_id, file_path=str(absolute_file_path))
        logger.info(f"Processing result for doc_id {doc_id}: {result}")
    except Exception as e_process:
        logger.error(f"Exception calling process_document for doc_id {doc_id}: {e_process}", exc_info=True)

async def main():
    """פונקציה ראשית"""
    
    logger.debug("Initializing DocumentProcessor in main...")
    doc_processor_instance = DocumentProcessor()
    logger.debug("DocumentProcessor initialized.")

    # >>> Direct Insert/Select Test <<<
    logger.info("Performing direct insert/select test on 'document_chunks'...")
    test_chunk_data = {
        "document_id": 9999, # Use a distinct, temporary document_id
        "chunk_text": "Direct insert test chunk text from script.",
        "embedding": [0.1] * 768, # Dummy embedding of correct dimension
        "content_token_count": 10,
        "chunk_header": "Direct Insert Test Header",
        "page_number": 1,
        "section": "Direct Insert Test Section"
    }
    try:
        logger.debug(f"Attempting direct insert of test chunk: {test_chunk_data}")
        direct_insert_response = doc_processor_instance.supabase.table("document_chunks").insert(test_chunk_data).execute()
        
        if hasattr(direct_insert_response, 'data') and direct_insert_response.data:
            logger.info(f"Direct insert test: Successfully received data from insert: {direct_insert_response.data}")
            inserted_chunk_id = direct_insert_response.data[0].get('id')
            if inserted_chunk_id:
                logger.info(f"Direct insert test: Attempting to select back inserted chunk with id: {inserted_chunk_id}")
                select_response = doc_processor_instance.supabase.table("document_chunks").select("*").eq("id", inserted_chunk_id).execute()
                if select_response.data:
                    logger.info(f"Direct insert test: SUCCESSFULLY selected back the test chunk: {select_response.data}")
                else:
                    logger.error(f"Direct insert test: FAILED to select back the test chunk with id: {inserted_chunk_id}. Select response: {select_response}")
            else:
                logger.error("Direct insert test: Insert response data did not contain an 'id' for the new chunk.")
        elif hasattr(direct_insert_response, 'error') and direct_insert_response.error:
            logger.error(f"Direct insert test: Supabase error during insert: {direct_insert_response.error.message} (Code: {direct_insert_response.error.code})")
        else:
            logger.error(f"Direct insert test: Unknown response from Supabase during insert: {direct_insert_response}")
        
        # Attempt to clean up the test chunk if it was inserted by document_id
        logger.debug("Direct insert test: Attempting to delete test chunk by document_id 9999")
        cleanup_response = doc_processor_instance.supabase.table("document_chunks").delete().eq("document_id", 9999).execute()
        if hasattr(cleanup_response, 'error') and cleanup_response.error:
            logger.warning(f"Direct insert test: Could not clean up test chunk (doc_id 9999). Error: {cleanup_response.error.message}")
        else:
            logger.info(f"Direct insert test: Cleaned up test chunk (doc_id 9999). Deleted count (from response data): {len(cleanup_response.data) if hasattr(cleanup_response, 'data') else 'N/A'}")
            
    except Exception as e_direct_test:
        logger.error(f"Direct insert test: Exception occurred: {e_direct_test}", exc_info=True)
    logger.info("Direct insert/select test finished.")
    # >>> End Direct Insert/Select Test <<<

    # Define the document to process
    document_to_process_id = 1 # Example document ID
    # Corrected relative path from the root of the Afeka_ChatBot workspace
    document_file_path = "תקנון לימודים תואר ראשון.pdf" 
    logger.info(f"Document to process: ID={document_to_process_id}, Relative Path='{document_file_path}'")

    # >>> Delete the document and its chunks before processing to ensure a clean state <<<
    logger.info(f"Attempting to delete existing document and chunks for ID: {document_to_process_id} before processing...")
    try:
        # delete_result = await doc_processor_instance.delete_document_and_all_chunks(document_to_process_id) # delete_document_and_all_chunks is async
        # The delete_document_and_all_chunks was removed earlier. Let's do direct deletes for testing.
        
        # Delete from 'document_chunks' first due to foreign key
        logger.debug(f"Deleting from 'document_chunks' for document_id: {document_to_process_id}")
        # delete_chunks_response = await doc_processor_instance.supabase.table("document_chunks").delete().eq("document_id", document_to_process_id).execute() # No await
        delete_chunks_response = doc_processor_instance.supabase.table("document_chunks").delete().eq("document_id", document_to_process_id).execute()
        chunks_deleted_count = len(delete_chunks_response.data) if hasattr(delete_chunks_response, 'data') and delete_chunks_response.data else 0
        if hasattr(delete_chunks_response, 'error') and delete_chunks_response.error:
            logger.error(f"Error deleting from 'document_chunks' for doc_id {document_to_process_id}: {delete_chunks_response.error.message}")

        logger.debug(f"Deleting from 'documents' for id: {document_to_process_id}")
        # delete_doc_response = await doc_processor_instance.supabase.table("documents").delete().eq("id", document_to_process_id).execute() # No await
        delete_doc_response = doc_processor_instance.supabase.table("documents").delete().eq("id", document_to_process_id).execute()
        doc_deleted = True if hasattr(delete_doc_response, 'data') and delete_doc_response.data else False
        if hasattr(delete_doc_response, 'error') and delete_doc_response.error:
            logger.error(f"Error deleting from 'documents' for id {document_to_process_id}: {delete_doc_response.error.message}")
            doc_deleted = False
            
        logger.info(f"Cleanup: Chunks deleted: {chunks_deleted_count}. Document record deleted: {doc_deleted} for ID: {document_to_process_id}.")

    except Exception as e_del:
        logger.error(f"Exception during pre-processing deletion for ID {document_to_process_id}: {e_del}", exc_info=True)

    await test_process_single_document(doc_processor_instance, document_to_process_id, document_file_path)

    logger.info(f"Fetching some chunks for document ID {document_to_process_id} for inspection (after processing)...")
    try:
        # Remove 'chunk_index' from select as it does not exist. Order by 'id' instead if sequential view is needed.
        chunks_response = doc_processor_instance.supabase.table("document_chunks") \
            .select("id, chunk_header, chunk_text, page_number, embedding") \
            .eq("document_id", document_to_process_id) \
            .order("id", desc=False) \
            .limit(3) \
            .execute() # This is synchronous

        if hasattr(chunks_response, 'error') and chunks_response.error:
            logger.error(f"Error fetching chunks for inspection: {chunks_response.error.message} (Code: {chunks_response.error.code})")
        elif hasattr(chunks_response, 'data') and chunks_response.data:
            logger.info(f"Found {len(chunks_response.data)} chunks in 'document_chunks' for doc ID {document_to_process_id}:")
            for i, chunk_item in enumerate(chunks_response.data):
                embedding_present = chunk_item.get('embedding') is not None
                log_message = (
                    f"  Chunk {i+1}/{len(chunks_response.data)} (DB ID: {chunk_item.get('id')}):\n"
                    f"    Header: {chunk_item.get('chunk_header')}\n"
                    f"    Page: {chunk_item.get('page_number')}\n"
                    f"    Text: {chunk_item.get('chunk_text', '')[:150]}...\n"
                    f"    Embedding type: {type(chunk_item.get('embedding')) if embedding_present else 'N/A'}\n"
                    f"    Embedding length: {len(chunk_item['embedding']) if embedding_present and isinstance(chunk_item['embedding'], list) else 'N/A'}\n"
                    f"    Embedding first 5: {str(chunk_item['embedding'][:5]) if embedding_present and isinstance(chunk_item['embedding'], list) and len(chunk_item['embedding']) >=5 else 'N/A'}"
                )
                logger.info(log_message)
        else:
            logger.info(f"No chunks found in 'document_chunks' for doc ID {document_to_process_id} after processing, or unexpected response.")
            
    except Exception as e_fetch_chunks:
        logger.error(f"Exception fetching chunks for inspection: {e_fetch_chunks}", exc_info=True)

    queries_to_test = [
        ("מהן אפשרויות הערעור על ציון?", 0.5), # Lowered from 0.78
        ("תנאי מעבר משנה לשנה", 0.5),      # Lowered from 0.75
        ("נהלי בחינות", 0.45),            # Lowered from 0.7
        ("זכויות הסטודנט", 0.4),         # Lowered from 0.7
        ("איך מקבלים פטור מקורס?", 0.5),   # Lowered
        ("פסילת קורס עקב נוכחות", 0.5),   # Lowered
        ("הליך רישום לקורסים", 0.45),     # Lowered
        ("סטודנט", 0.3)                  # Very broad, low threshold
    ]

    for query, threshold in queries_to_test:
        print(f"\n===== Testing query: '{query}' =====") # Using print for clearer section breaks in terminal
        
        query_embedding_vector = None
        try:
            logger.info(f"Generating embedding for query: '{query}'")
            # _generate_embedding is async
            query_embedding_vector = await doc_processor_instance._generate_embedding(query) 
            if not query_embedding_vector:
                logger.error(f"Failed to generate embedding for query: '{query}'. Skipping search tests for this query.")
                continue
            logger.info(f"Query embedding generated successfully for: '{query}'. Length: {len(query_embedding_vector)}")
        except Exception as e_query_emb:
            logger.error(f"Exception generating embedding for query '{query}': {e_query_emb}", exc_info=True)
            continue # Skip to next query

        # Test semantic search with a specific query and threshold
        logger.info(f"----- Testing Semantic Search with Threshold: {threshold} -----")
        semantic_results = await doc_processor_instance.search_documents(query, limit=5, threshold=threshold)
        if semantic_results:
            logger.info(f"Found {len(semantic_results)} results for semantic query '{query}' with threshold {threshold}:")
            for i, res in enumerate(semantic_results):
                similarity = res.get('similarity')
                similarity_str = f"{similarity:.4f}" if isinstance(similarity, float) else str(similarity)
                logger.info(f"  {i+1}. ID: {res.get('id')}, DocID: {res.get('document_id')}, Similarity: {similarity_str}, Content: '{res.get('chunk_text', '')[:100]}...'")
        else:
            logger.info(f"No results found for semantic query '{query}' with threshold {threshold}")

        # Test hybrid search with the same query and threshold
        logger.info(f"----- Testing Hybrid Search with Threshold: {threshold} -----")
        hybrid_results = await doc_processor_instance.hybrid_search(query, limit=5, threshold=threshold)
        if hybrid_results:
            logger.info(f"Found {len(hybrid_results)} results for hybrid query '{query}' with threshold {threshold}:")
            for i, res in enumerate(hybrid_results):
                similarity = res.get('similarity')
                similarity_str = f"{similarity:.4f}" if isinstance(similarity, float) else str(similarity)
                combined_score = res.get('combined_score')
                combined_score_str = f"{combined_score:.4f}" if isinstance(combined_score, float) else str(combined_score)
                logger.info(f"  {i+1}. ID: {res.get('id')}, DocID: {res.get('document_id')}, Similarity: {similarity_str}, Combined: {combined_score_str}, Content: '{res.get('chunk_text', '')[:100]}...'")
        else:
            logger.info(f"No results found for hybrid query '{query}' with threshold {threshold}")
    
if __name__ == "__main__":
    asyncio.run(main()) 