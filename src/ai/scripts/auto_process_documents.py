#!/usr/bin/env python
"""
Automatic document processor for pending documents
Runs every minute to check for documents awaiting processing
"""

import os
import sys
import asyncio
import logging
import time
from pathlib import Path
import dotenv
import argparse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

dotenv.load_dotenv(override=True)

try:
    from src.ai.services.document_processor import DocumentProcessor
except ImportError:
    try:
        from ..services.document_processor import DocumentProcessor
    except ImportError:
        logger.error("Error importing DocumentProcessor. Make sure the module exists and is in the PYTHONPATH.")
        sys.exit(1)

async def process_pending_document(document_id: int, processor: DocumentProcessor):
    """Process a pending document"""
    logger.info(f"Processing document {document_id}")
    
    try:
        doc_result = processor.supabase.table("documents").select("*").eq("id", document_id).execute()
        
        if not doc_result.data:
            logger.error(f"Document {document_id} not found")
            return False
        
        document = doc_result.data[0]
        document_url = document["url"]
        document_name = document["name"]
        logger.info(f"Processing: {document_name}")
        
        import tempfile
        import httpx
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            async with httpx.AsyncClient() as client:
                response = await client.get(document_url)
                temp_file.write(response.content)
                temp_file_path = temp_file.name
        
        result = await processor.process_document(document_id, temp_file_path)
        
        if not result:
            logger.error(f"Failed to process document {document_id}")
        else:
            logger.info(f"Successfully processed document {document_id}")
        
        try:
            os.unlink(temp_file_path)
        except:
            pass
            
        return True
            
    except Exception as e:
        import traceback
        logger.error(f"Error processing document {document_id}: {str(e)}")
        logger.debug(traceback.format_exc())
        return False

async def find_and_process_pending_documents():
    """Find all pending documents and process them"""
    processor = DocumentProcessor()
    
    result = processor.supabase.table("documents").select("id").eq("processing_status", "pending").execute()
    
    if not result.data:
        logger.debug("No pending documents found")
        return 0
    
    pending_docs = result.data
    logger.info(f"Found {len(pending_docs)} pending documents to process")
    
    processed_count = 0
    for doc in pending_docs:
        doc_id = doc["id"]
        success = await process_pending_document(doc_id, processor)
        if success:
            processed_count += 1
    
    if processed_count > 0:
        logger.info(f"Successfully processed {processed_count}/{len(pending_docs)} documents")
    
    return processed_count

async def run_processor(interval: int, single_run: bool = False):
    """Run the processor in cyclic mode"""
    try:
        if single_run:
            logger.info("Running in single-run mode")
            await find_and_process_pending_documents()
            return
            
        logger.info(f"Starting automatic document processor (checking every {interval} seconds)")
        cycle_count = 0
        
        while True:
            try:
                cycle_count += 1
                count = await find_and_process_pending_documents()
                
                if count > 0:
                    logger.info(f"Cycle #{cycle_count}: Processed {count} documents")
                elif cycle_count % 10 == 0:
                    logger.debug(f"Heartbeat: Cycle #{cycle_count} - system running normally")
                    
            except Exception as e:
                logger.error(f"Error in processing cycle #{cycle_count}: {str(e)}")
                
            await asyncio.sleep(interval)
            
    except KeyboardInterrupt:
        logger.info("Document processor stopped by user")
    except Exception as e:
        logger.error(f"Unhandled error: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automatic document processor")
    parser.add_argument("--interval", type=int, default=60, help="Check interval in seconds")
    parser.add_argument("--single-run", action="store_true", help="Run once and exit")
    args = parser.parse_args()
    
    asyncio.run(run_processor(args.interval, args.single_run))