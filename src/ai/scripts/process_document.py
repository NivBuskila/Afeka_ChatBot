#!/usr/bin/env python
"""
Manual document processing script
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
import dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

dotenv.load_dotenv(override=True)

try:
    from ..services.document_processor import DocumentProcessor
except ImportError:
    logger.error("Error importing DocumentProcessor. Make sure the module exists and is in the PYTHONPATH.")
    sys.exit(1)

async def process_document(document_id: int):
    """Process document by ID"""
    logger.info(f"Starting manual processing of document {document_id}")
    
    processor = DocumentProcessor()
    
    try:
        doc_result = processor.supabase.table("documents").select("*").eq("id", document_id).execute()
        
        if not doc_result.data:
            logger.error(f"Document {document_id} not found")
            return
        
        document = doc_result.data[0]
        document_url = document["url"]
        document_name = document["name"]
        logger.info(f"Processing document {document_id}: {document_name}")
        logger.info(f"Document URL: {document_url}")
        
        import tempfile
        import httpx
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            async with httpx.AsyncClient() as client:
                response = await client.get(document_url)
                temp_file.write(response.content)
                temp_file_path = temp_file.name
        
        result = await processor.process_document(document_id, temp_file_path)
        
        logger.info(f"Processing result: {result}")
        
        try:
            os.unlink(temp_file_path)
        except:
            pass
            
    except Exception as e:
        import traceback
        logger.error(f"Error processing document: {str(e)}")
        logger.error(traceback.format_exc())
        
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python process_document.py <document_id>")
        sys.exit(1)
        
    try:
        document_id = int(sys.argv[1])
    except ValueError:
        print("Error: document_id must be an integer")
        sys.exit(1)
    
    asyncio.run(process_document(document_id))