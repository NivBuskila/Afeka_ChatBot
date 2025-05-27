#!/usr/bin/env python
"""
סקריפט לעיבוד אוטומטי של מסמכים במצב 'pending'
מריץ כל דקה בדיקה אם יש מסמכים שממתינים לעיבוד
"""

import os
import sys
import asyncio
import logging
import time
from pathlib import Path
import dotenv
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the parent directory to the path
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

# Load environment variables
dotenv.load_dotenv(override=True)

# Import required modules
try:
    from services.document_processor import DocumentProcessor
except ImportError:
    logger.error("Error importing DocumentProcessor. Make sure the module exists and is in the PYTHONPATH.")
    sys.exit(1)

async def process_pending_document(document_id: int, processor: DocumentProcessor):
    """עיבוד מסמך במצב pending"""
    logger.info(f"Processing document {document_id}")
    
    try:
        # Get document URL
        doc_result = processor.supabase.table("documents").select("*").eq("id", document_id).execute()
        
        if not doc_result.data:
            logger.error(f"Document {document_id} not found")
            return False
        
        document = doc_result.data[0]
        document_url = document["url"]
        document_name = document["name"]
        logger.info(f"Processing document {document_id}: {document_name}")
        logger.info(f"Document URL: {document_url}")
        
        # Create a temporary file with the document content
        import tempfile
        import httpx
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            # Download the file
            async with httpx.AsyncClient() as client:
                response = await client.get(document_url)
                temp_file.write(response.content)
                temp_file_path = temp_file.name
        
        # Process the document
        result = await processor.process_document(document_id, temp_file_path)
        
        # Log the result
        logger.info(f"Processing result: {result}")
        
        # Clean up
        try:
            os.unlink(temp_file_path)
        except:
            pass
            
        return True
            
    except Exception as e:
        import traceback
        logger.error(f"Error processing document: {str(e)}")
        logger.error(traceback.format_exc())
        return False

async def find_and_process_pending_documents():
    """מציאת כל המסמכים במצב pending ועיבוד שלהם"""
    processor = DocumentProcessor()
    
    # Find pending documents
    result = processor.supabase.table("documents").select("id").eq("processing_status", "pending").execute()
    
    if not result.data:
        logger.info("No pending documents found")
        return 0
    
    pending_docs = result.data
    logger.info(f"Found {len(pending_docs)} pending documents")
    
    # Process each document
    processed_count = 0
    for doc in pending_docs:
        doc_id = doc["id"]
        success = await process_pending_document(doc_id, processor)
        if success:
            processed_count += 1
    
    return processed_count

async def run_processor(interval: int, single_run: bool = False):
    """הפעלת המעבד באופן מחזורי"""
    try:
        if single_run:
            logger.info("Running in single-run mode")
            await find_and_process_pending_documents()
            return
            
        logger.info(f"Starting automatic document processor (interval: {interval} seconds)")
        
        while True:
            try:
                count = await find_and_process_pending_documents()
                if count > 0:
                    logger.info(f"Processed {count} documents")
            except Exception as e:
                logger.error(f"Error in processing cycle: {str(e)}")
                
            # Wait for next cycle
            logger.info(f"Waiting {interval} seconds until next check")
            await asyncio.sleep(interval)
            
    except KeyboardInterrupt:
        logger.info("Processor stopped by user")
    except Exception as e:
        logger.error(f"Unhandled error: {str(e)}")

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Automatic document processor")
    parser.add_argument("--interval", type=int, default=60, help="Check interval in seconds")
    parser.add_argument("--single-run", action="store_true", help="Run once and exit")
    args = parser.parse_args()
    
    # Run the processor
    asyncio.run(run_processor(args.interval, args.single_run)) 