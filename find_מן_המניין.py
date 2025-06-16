import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from ai.services.rag_service import get_rag_service

async def find_student_definition():
    rag = get_rag_service()
    
    # Search in database for chunks containing "מן המניין"
    query = """
    SELECT dc.id, dc.chunk_text, d.name as document_name, dc.chunk_number
    FROM document_chunks dc
    JOIN documents d ON dc.document_id = d.id
    WHERE dc.chunk_text ILIKE '%מן המניין%'
    ORDER BY dc.id;
    """
    
    try:
        result = rag.supabase.rpc('execute_sql', {'sql': query}).execute()
        chunks = result.data
        
        print(f"Found {len(chunks)} chunks containing 'מן המניין':")
        print("="*60)
        
        for chunk in chunks:
            print(f"\nChunk ID: {chunk['id']}")
            print(f"Document: {chunk['document_name']}")
            print(f"Chunk Number: {chunk['chunk_number']}")
            print(f"Content: {chunk['chunk_text'][:300]}...")
            print("-" * 60)
            
    except Exception as e:
        print(f"Error: {e}")
        
    # Also try direct text search
    print("\nTrying direct text search...")
    try:
        result = rag.supabase.table('document_chunks').select('id, chunk_text, documents(name)').ilike('chunk_text', '%מן המניין%').execute()
        chunks = result.data
        
        print(f"Direct search found {len(chunks)} chunks:")
        for chunk in chunks:
            print(f"Chunk ID: {chunk['id']}")
            print(f"Content preview: {chunk['chunk_text'][:200]}...")
            print()
            
    except Exception as e:
        print(f"Direct search error: {e}")

if __name__ == "__main__":
    asyncio.run(find_student_definition()) 