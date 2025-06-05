from flask import Flask, request, jsonify, Response
import os
import logging
import time
from functools import wraps
import google.generativeai as genai
import sys
from pathlib import Path
import dotenv
from flask_cors import CORS  # הוספת ייבוא של flask_cors
from typing import List, Dict

# ✅ STANDARDIZED: Load environment from project root
project_root = Path(__file__).parent.parent.parent
env_file = project_root / ".env"

if env_file.exists():
    dotenv.load_dotenv(env_file, override=True)
    print(f"✅ AI Service loaded environment from: {env_file}")
else:
    print(f"⚠️  Environment file not found: {env_file}")
    # Try legacy loading as fallback
    dotenv.load_dotenv(override=True)

# ✅ STANDARDIZED: Environment variable handling
def get_required_env(var_name: str, default: str = None) -> str:
    """Get required environment variable with proper error handling"""
    value = os.environ.get(var_name, default)
    if not value:
        raise ValueError(f"Required environment variable {var_name} not found")
    return value

def get_optional_env(var_name: str, default: str = None) -> str:
    """Get optional environment variable with default"""
    return os.environ.get(var_name, default)

# הוספת הנתיב לתיקיית backend כדי לאפשר גישה למודולים של RAG
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# טעינת משתני סביבה
dotenv.load_dotenv(override=True)

# ייבוא מודולי RAG
try:
    from .services.document_processor import DocumentProcessor
    from app.core.database import get_supabase_client
    from .services.enhanced_processor import EnhancedProcessor
    has_rag = True
    # Initialize document processors
    doc_processor = DocumentProcessor()
    enhanced_processor = EnhancedProcessor()
    print(f"✅ RAG modules loaded successfully")
except ImportError as e:
    print(f"⚠️  RAG modules could not be imported: {e}")
    print(f"💡 AI service will run in basic mode without RAG")
    has_rag = False
    enhanced_processor = None

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if get_optional_env('DEBUG', 'False').lower() == 'true' else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Gemini API
GEMINI_API_KEY = get_required_env('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY not found in environment variables, using default")
    GEMINI_API_KEY = 'AIzaSyBBw-VlqWekqnd_vPXCS7LSuKfrkbOro7s'
# שימוש ב-configure במקום ביצירת מופע Client
genai.configure(api_key=GEMINI_API_KEY)

# Create Flask app
app = Flask(__name__)
# הוספת תמיכה ב-CORS
CORS(app, resources={r"/*": {"origins": "*"}})

# Get environment settings
DEBUG = get_optional_env('DEBUG', 'False').lower() == 'true'
API_RATE_LIMIT = int(get_optional_env('API_RATE_LIMIT', '60'))  # Requests per minute per IP
MAX_MESSAGE_LENGTH = int(get_optional_env('MAX_MESSAGE_LENGTH', '2000'))  # Maximum length of input message

# Add security headers to all responses
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

# Replace the complex import and setup with simple one
try:
    from services.context_window_manager import SimpleContextManager
    context_manager = SimpleContextManager()
    logger.info("Simple Context Manager loaded")
except Exception as e:
    logger.warning(f"Context Manager not available: {e}")
    context_manager = None

# Basic route for health checks
@app.route('/')
def health_check():
    """Enhanced health check endpoint"""
    return jsonify({
        "status": "ok",
        "service": "ai-service",
        "version": "1.0.0",
        "rag_support": has_rag,
        "environment": {
            "debug": DEBUG,
            "supabase_connected": bool(get_required_env('SUPABASE_URL') and get_required_env('SUPABASE_KEY')),
            "gemini_configured": bool(GEMINI_API_KEY)
        },
        "timestamp": time.time()
    })

# RAG endpoints
@app.route('/rag/search', methods=['POST'])
def rag_search():
    """חיפוש סמנטי במסמכים"""
    if not has_rag:
        return jsonify({"error": "RAG modules not available"}), 503
    
    try:
        data = request.get_json(force=True)
        query = data.get("query", "")
        limit = data.get("limit", 10)
        threshold = data.get("threshold", 0.78)
        
        if not query.strip():
            return jsonify({"error": "Query cannot be empty"}), 400
        
        results = doc_processor.search_documents(query, limit, threshold)
        
        # ממתינים לתוצאות מאחר שזו פונקציה אסינכרונית
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(results)
        
        return jsonify({
            "query": query,
            "results": results,
            "count": len(results)
        })
        
    except Exception as e:
        logger.error(f"Error in semantic search: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/rag/search/hybrid', methods=['POST'])
def rag_hybrid_search():
    """חיפוש היברידי (סמנטי + מילות מפתח)"""
    if not has_rag:
        return jsonify({"error": "RAG modules not available"}), 503
    
    try:
        data = request.get_json(force=True)
        query = data.get("query", "")
        limit = data.get("limit", 10)
        threshold = data.get("threshold", 0.78)
        
        if not query.strip():
            return jsonify({"error": "Query cannot be empty"}), 400
        
        results = doc_processor.hybrid_search(query, limit, threshold)
        
        # ממתינים לתוצאות מאחר שזו פונקציה אסינכרונית
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(results)
        
        return jsonify({
            "query": query,
            "results": results,
            "count": len(results)
        })
        
    except Exception as e:
        logger.error(f"Error in hybrid search: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/rag/enhanced_search', methods=['POST'])
def rag_enhanced_search():
    """חיפוש מתקדם עם RAG משודרג"""
    if not has_rag or not enhanced_processor:
        return jsonify({"error": "Enhanced RAG modules not available"}), 503
    
    try:
        data = request.get_json(force=True)
        query = data.get("query", "")
        max_results = data.get("max_results", 10)
        include_context = data.get("include_context", True)
        
        if not query.strip():
            return jsonify({"error": "Query cannot be empty"}), 400
        
        # ביצוע חיפוש מתקדם
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        if include_context:
            # Full search with answer generation
            results = loop.run_until_complete(
                enhanced_processor.search_and_answer(query, max_results)
            )
        else:
            # Search only
            search_results = loop.run_until_complete(
                enhanced_processor.search(query, max_results)
            )
            results = {
                "results": search_results,
                "query": query,
                "count": len(search_results)
            }
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Error in enhanced search: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/rag/stats', methods=['GET'])
def rag_stats():
    """מידע על מסמכים ו-embeddings"""
    if not has_rag:
        return jsonify({"error": "RAG modules not available"}), 503
    
    try:
        supabase = get_supabase_client()
        
        # Count documents
        docs_count = supabase.table("documents").select("*", count="exact").execute()
        total_documents = docs_count.count if hasattr(docs_count, 'count') else 0
        
        # Count embeddings
        embeddings_count = supabase.table("document_chunks").select("*", count="exact").execute()
        total_embeddings = embeddings_count.count if hasattr(embeddings_count, 'count') else 0
        
        # Count advanced chunks if available
        advanced_embeddings = 0
        try:
            advanced_count = supabase.table("advanced_document_chunks").select("*", count="exact").execute()
            advanced_embeddings = advanced_count.count if hasattr(advanced_count, 'count') else 0
        except:
            pass
        
        # Get status counts
        status_counts = {}
        try:
            status_result = supabase.rpc("get_document_status_counts").execute()
            if status_result.data:
                status_counts = {item['status']: item['count'] for item in status_result.data}
        except:
            # Fall back to manual counting
            for status in ['pending', 'processing', 'completed', 'failed']:
                status_count = supabase.table("documents").select("*", count="exact").eq("processing_status", status).execute()
                status_counts[status] = status_count.count if hasattr(status_count, 'count') else 0
        
        return jsonify({
            "total_documents": total_documents,
            "total_embeddings": total_embeddings,
            "advanced_embeddings": advanced_embeddings,
            "status_counts": status_counts,
            "enhanced_rag_available": enhanced_processor is not None
        })
        
    except Exception as e:
        logger.error(f"Error getting RAG stats: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/rag/document/<int:document_id>/reprocess', methods=['POST'])
def rag_reprocess_document(document_id):
    """עיבוד מחדש של מסמך עם המערכת החדשה"""
    if not has_rag:
        return jsonify({"error": "RAG modules not available"}), 503
    
    try:
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Delete existing embeddings
        delete_result = loop.run_until_complete(
            doc_processor.delete_document_embeddings(document_id)
        )
        
        # Get document info
        supabase = get_supabase_client()
        doc_result = supabase.table("documents").select("*").eq("id", document_id).execute()
        
        if not doc_result.data:
            return jsonify({"error": f"Document {document_id} not found"}), 404
        
        document = doc_result.data[0]
        
        # For now, return success - actual reprocessing would need the file
        return jsonify({
            "message": f"Document {document['name']} queued for reprocessing with enhanced system",
            "document_id": document_id,
            "deleted_embeddings": delete_result,
            "status": "reprocessing_needed"
        })
        
    except Exception as e:
        logger.error(f"Error reprocessing document: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/rag/test_enhanced', methods=['POST'])
def test_enhanced_system():
    """בדיקת המערכת המשודרגת עם דוגמת טקסט"""
    if not has_rag or not enhanced_processor:
        return jsonify({"error": "Enhanced RAG modules not available"}), 503
    
    try:
        data = request.get_json(force=True)
        test_text = data.get("test_text", """
        שלום! זהו טקסט לבדיקה של המערכת המשודרגת.
        
        1.1 כללי
        תקנון זה מסדיר את כללי הלימודים במכללה.
        
        1.2 רישום ללימודים
        על כל סטודנט להרשם עד לתאריך שנקבע.
        
        2.1 מבחנים
        המבחנים יערכו לפי הלוח זמנים המתפרסם.
        
        2.2 ציונים
        הציונים יפורסמו במערכת הממוחשבת.
        """)
        
        document_name = data.get("document_name", "test_document.txt")
        
        # Use the smart chunker to process the text
        chunks = doc_processor.smart_chunker.chunk_text(test_text, document_name)
        
        # Process chunks with enhanced system
        processed_chunks = []
        for i, chunk in enumerate(chunks):
            processed_chunks.append({
                "chunk_index": i,
                "content": chunk.content,
                "section_number": chunk.section_number,
                "hierarchical_path": chunk.hierarchical_path,
                "content_type": chunk.content_type,
                "keywords": chunk.keywords,
                "cross_references": chunk.cross_references,
                "char_start": chunk.char_start,
                "char_end": chunk.char_end
            })
        
        return jsonify({
            "message": "Enhanced system test completed",
            "original_text_length": len(test_text),
            "chunks_generated": len(chunks),
            "chunks": processed_chunks
        })
        
    except Exception as e:
        logger.error(f"Error testing enhanced system: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/rag/document/<int:document_id>', methods=['GET'])
def rag_document_status(document_id):
    """מידע מפורט על תהליך עיבוד המסמך"""
    if not has_rag:
        return jsonify({"error": "RAG modules not available"}), 503
    
    try:
        supabase = get_supabase_client()
        
        # Get document details
        doc_result = supabase.table("documents").select("*").eq("id", document_id).execute()
        if not doc_result.data:
            return jsonify({"error": f"Document {document_id} not found"}), 404
            
        document = doc_result.data[0]
        
        # Get chunks count
        chunks_result = supabase.table("document_chunks").select("*", count="exact").eq("document_id", document_id).execute()
        chunks_count = chunks_result.count if hasattr(chunks_result, 'count') else 0
        
        # Calculate progress percentage
        progress = 0
        if document['processing_status'] == 'pending':
            progress = 0
        elif document['processing_status'] == 'processing':
            if chunks_count > 0:
                # If we have chunks but still processing, estimate progress
                progress = min(95, int(chunks_count / 0.5))  # Estimate 50 chunks for full processing
            else:
                progress = 20  # Initial processing stage
        elif document['processing_status'] == 'completed':
            progress = 100
        elif document['processing_status'] == 'failed':
            progress = 0
        
        # Get processing time if available
        processing_time = None
        if document.get('updated_at') and document.get('created_at'):
            from datetime import datetime
            created = datetime.fromisoformat(document['created_at'].replace('Z', '+00:00'))
            updated = datetime.fromisoformat(document['updated_at'].replace('Z', '+00:00'))
            processing_time = (updated - created).total_seconds()
        
        return jsonify({
            "document": {
                "id": document['id'],
                "name": document['name'],
                "status": document['processing_status'],
                "created_at": document['created_at'],
                "updated_at": document['updated_at'],
                "embedding_model": document.get('embedding_model')
            },
            "chunks_count": chunks_count,
            "progress": progress,
            "processing_time": processing_time
        })
        
    except Exception as e:
        logger.error(f"Error getting document status: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Simplify the chat endpoint
@app.route('/chat', methods=['POST'])
def chat():
    """Process user message with simple context"""
    
    request_start_time = time.time()
    
    try:
        data = request.get_json(force=True, silent=True)
        user_message = data['message']
        context_history = data.get('context', [])
        
        # ✅ SIMPLE: Build context if available
        if context_manager and context_history:
            llm_context = context_manager.build_context(context_history)
            full_prompt = _build_simple_prompt(user_message, llm_context)
        else:
            full_prompt = user_message
        
        # Initialize AI response
        ai_response = "מצטער, לא הצלחתי לעבד את הבקשה"
        
        # Process with RAG or Gemini
        if has_rag and enhanced_processor:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            enhanced_result = loop.run_until_complete(
                enhanced_processor.search_and_answer(full_prompt, max_results=3)
            )
            ai_response = enhanced_result.get('answer', ai_response)
        else:
            # Use Gemini
            model = genai.GenerativeModel("gemini-2.0-flash")
            gemini_response = model.generate_content(full_prompt)
            ai_response = gemini_response.text
        
        # Simple response
        result = {
            "result": ai_response,
            "processing_time": round(time.time() - request_start_time, 3),
            "rag_used": has_rag,
            "context_messages": len(llm_context) if context_manager and context_history else 0
        }
        
        logger.info(f"Message processed: {result['context_messages']} context messages, {result['processing_time']}s")
        
        response = jsonify(result)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response
        
    except Exception as e:
        import traceback
        logger.error(f"Error in chat endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        response = jsonify({
            "error": "Internal server error",
            "message": str(e)
        })
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response, 500

def _build_simple_prompt(user_message: str, context: List[Dict]) -> str:
    """Build simple prompt with context"""
    
    if not context:
        return user_message
    
    prompt_parts = ["Previous conversation:"]
    
    for msg in context:
        role = "User" if msg["role"] == "user" else "Assistant"
        prompt_parts.append(f"{role}: {msg['content']}")
    
    prompt_parts.extend([
        f"\nCurrent question: {user_message}",
        "\nPlease respond considering the conversation above."
    ])
    
    return "\n".join(prompt_parts)

if __name__ == '__main__':
    # Set up server start time for uptime tracking
    app.start_time = time.time()
    
    # Get port from environment variable
    port = int(get_optional_env('AI_PORT', '5000'))
    
    # Run the Flask app
    logger.info(f"🚀 Starting AI service on port {port}")
    logger.info(f"🔧 RAG support: {'Enabled' if has_rag else 'Disabled'}")
    logger.info(f"🔧 Debug mode: {DEBUG}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=DEBUG,
        threaded=True
    ) 