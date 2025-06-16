import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from ai.services.rag_service import get_rag_service

async def check_specific_chunks():
    rag = get_rag_service()
    
    chunk_ids = [27439, 27450, 27322, 27451, 27388, 27408]
    
    for chunk_id in chunk_ids:
        try:
            result = rag.supabase.table('document_chunks').select('id, chunk_text, documents(name)').eq('id', chunk_id).execute()
            
            if result.data:
                chunk = result.data[0]
                print(f"Chunk ID: {chunk_id}")
                print(f"Document: {chunk['documents']['name'] if chunk['documents'] else 'Unknown'}")
                # print(f"Chunk Number: {chunk['chunk_number']}")
                print("Full Content:")
                print(chunk['chunk_text'])
                print("="*80)
                print()
        except Exception as e:
            print(f"Error fetching chunk {chunk_id}: {e}")

if __name__ == "__main__":
    asyncio.run(check_specific_chunks()) 