import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.ai.services.rag_service import RAGService

async def debug_rag_response():
    print("🔍 Debugging RAG response structure...")
    
    # Test with optimized_testing profile
    rag_service = RAGService(config_profile="optimized_testing")
    
    query = "מה זה סטודנט מן המניין?"
    
    print(f"📝 Query: {query}")
    print(f"📊 Similarity threshold: {rag_service.search_config.SIMILARITY_THRESHOLD}")
    
    try:
        result = await rag_service.generate_answer(query)
        print(f"\n🔍 RAG Response Structure:")
        print(f"   Keys: {list(result.keys())}")
        
        # Check specific fields
        sources = result.get("sources", [])
        chunks_selected = result.get("chunks_selected", [])
        
        print(f"\n📊 Field Analysis:")
        print(f"   sources: {len(sources)} items")
        print(f"   chunks_selected: {len(chunks_selected)} items")
        
        # Debug sources content
        if sources:
            print(f"\n🔍 Sources Content:")
            print(f"   Type of sources: {type(sources)}")
            print(f"   Type of first source: {type(sources[0])}")
            print(f"   First 3 sources: {sources[:3]}")
        
        # Debug chunks content
        if chunks_selected:
            print(f"\n🔍 Chunks Content:")
            print(f"   Type of chunks_selected: {type(chunks_selected)}")
            print(f"   Type of first chunk: {type(chunks_selected[0])}")
            print(f"   First chunk keys: {list(chunks_selected[0].keys())}")
        
        # Test the chat service logic
        has_sources = result.get("sources") and len(result["sources"]) > 0
        has_chunks = result.get("chunks_selected") and len(result["chunks_selected"]) > 0
        
        print(f"\n🧪 Chat Service Logic Test:")
        print(f"   has_sources: {has_sources}")
        print(f"   has_chunks: {has_chunks}")
        print(f"   would_use_rag: {has_sources or has_chunks}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_rag_response()) 