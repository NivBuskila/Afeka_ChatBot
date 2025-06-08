import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.ai.services.rag_service import RAGService

async def debug_hybrid_params():
    print("🔍 Debugging hybrid search parameters...")
    
    # Test with direct RAG service
    rag_service = RAGService(config_profile="maximum_accuracy")
    
    query = "מה זה סטודנט מן המניין?"
    
    print(f"📝 Query: {query}")
    print(f"🎯 Profile: {getattr(rag_service, 'config_profile', 'Not set')}")
    print(f"📊 Similarity threshold: {rag_service.search_config.SIMILARITY_THRESHOLD}")
    print(f"📈 Max chunks: {rag_service.search_config.MAX_CHUNKS_RETRIEVED}")
    print(f"🔍 Hybrid search function: {rag_service.db_config.HYBRID_SEARCH_FUNCTION}")
    
    # Let's patch the search method to see what parameters are actually sent
    original_search = rag_service.supabase.rpc
    
    def debug_rpc(function_name, params=None, **kwargs):
        if function_name == "hybrid_search_documents":
            print(f"\n🔧 RPC Call Parameters:")
            print(f"   Function: {function_name}")
            if params:
                for key, value in params.items():
                    if key == 'query_embedding':
                        print(f"   {key}: [embedding vector of length {len(value)}]")
                    else:
                        print(f"   {key}: {value} (type: {type(value).__name__})")
            print()
        return original_search(function_name, params, **kwargs)
    
    rag_service.supabase.rpc = debug_rpc
    
    try:
        result = await rag_service.generate_answer(query)
        print(f"✅ RAG Result: {result['answer'][:100] if result.get('answer') else 'No answer'}...")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_hybrid_params()) 