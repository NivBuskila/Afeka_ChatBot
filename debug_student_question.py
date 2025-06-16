import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from ai.services.rag_service import get_rag_service

async def debug_student_question():
    rag = get_rag_service()
    query = 'מה זה סטודנט מן המניין?'
    
    print(f"Testing: {query}")
    print("="*60)
    
    # Get raw search results to see what we're working with
    search_results = await rag.hybrid_search(query)
    
    print(f"Found {len(search_results)} results")
    print("\nTop 10 results:")
    for i, result in enumerate(search_results[:10]):
        content = result.get('chunk_text', result.get('content', ''))
        doc_name = result.get('document_name', 'Unknown')
        similarity = result.get('similarity_score', result.get('similarity', 0))
        
        print(f"\n[{i+1}] Similarity: {similarity:.3f}")
        print(f"Document: {doc_name}")
        print(f"Content preview: {content[:150]}...")
        
        # Check if this chunk actually contains the definition
        if 'מן המניין' in content:
            print("✅ CONTAINS 'מן המניין' - This should be selected!")
    
    print("\n" + "="*60)
    print("Now testing chunk selection algorithm...")
    
    # Test our selection algorithm
    selected_chunk = rag._find_best_chunk_for_display(search_results, query)
    if selected_chunk:
        content = selected_chunk.get('chunk_text', selected_chunk.get('content', ''))
        doc_name = selected_chunk.get('document_name', 'Unknown')
        print(f"Selected: {doc_name}")
        print(f"Content: {content[:200]}...")
        
        if 'מן המניין' in content:
            print("✅ Correctly selected chunk with 'מן המניין'")
        else:
            print("❌ Selected chunk doesn't contain 'מן המניין'")

if __name__ == "__main__":
    asyncio.run(debug_student_question()) 