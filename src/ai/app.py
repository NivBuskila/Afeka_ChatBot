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
from core.gemini_key_manager import safe_generate_content

# הוספת הנתיב לתיקיית backend כדי לאפשר גישה למודולים של RAG
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# טעינת משתני סביבה
dotenv.load_dotenv(override=True)

# ייבוא מודולי RAG - השבתה זמנית עד תיקון הבעיות
# הצ'אט יעבוד עם Gemini לבד ללא RAG
has_rag = False
enhanced_processor = None
get_supabase_client = None
doc_processor = None

logging.warning("RAG modules disabled - chat will use Gemini without document search")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Gemini API
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY not found in environment variables. Please set it in your .env file.")
    raise ValueError("GEMINI_API_KEY environment variable is required but not found")

# # שימוש ב-configure במקום ביצירת מופע Client
# genai.configure(api_key=GEMINI_API_KEY)
from core.gemini_key_manager import get_key_manager
# Initialize key manager
key_manager = get_key_manager()

# Create Flask app
app = Flask(__name__)
# הוספת תמיכה ב-CORS
CORS(app, resources={r"/*": {"origins": "*"}})

# Get environment settings
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
API_RATE_LIMIT = int(os.environ.get('API_RATE_LIMIT', '60'))  # Requests per minute per IP
MAX_MESSAGE_LENGTH = int(os.environ.get('MAX_MESSAGE_LENGTH', '2000'))  # Maximum length of input message

# Add security headers to all responses
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

# Basic route for health checks
@app.route('/')
def health_check():
    """Basic health check endpoint"""
    return jsonify({
        "status": "ok", 
        "service": "ai-service",
        "rag_support": has_rag
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

# Main chat endpoint
@app.route('/chat', methods=['POST'])
def chat():
    """
    Process user message with Gemini API
    """
    request_start_time = time.time()
    
    try:
        # Log raw request for debugging
        logger.info(f"Request content type: {request.content_type}")
        
        # Get raw data and decode manually if needed
        try:
            # Try parsing as JSON first
            data = request.get_json(force=True, silent=True)
            if not data and request.data:
                # If JSON parsing failed, try manual decoding
                raw_data = request.data.decode('utf-8', errors='replace')
                logger.info(f"Raw data (length {len(raw_data)}): {raw_data[:100]}...")
                import json
                data = json.loads(raw_data)
        except Exception as json_err:
            logger.error(f"JSON parsing error: {str(json_err)}")
            # If JSON parsing failed completely, check raw data
            data = {}
            if request.data:
                logger.info(f"Raw request data (bytes): {request.data[:100]}")
        
        if not data or 'message' not in data:
            logger.warning("Invalid request: missing message field")
            response = jsonify({
                "error": "Message field is required"
            })
            response.headers['Content-Type'] = 'application/json; charset=utf-8'
            return response, 400
            
        user_message = data['message']
        logger.info(f"User message type: {type(user_message)}")
        
        # Ensure message is properly decoded if it's bytes
        if isinstance(user_message, bytes):
            user_message = user_message.decode('utf-8', errors='replace')
        
        # Validate message length
        if not user_message or len(user_message) > MAX_MESSAGE_LENGTH:
            logger.warning(f"Message too long: {len(user_message)} chars (max: {MAX_MESSAGE_LENGTH})")
            response = jsonify({
                "error": f"Message too long (max {MAX_MESSAGE_LENGTH} characters)"
            })
            response.headers['Content-Type'] = 'application/json; charset=utf-8'
            return response, 400
                
        logger.info(f"Received message (length {len(user_message)}): {user_message[:30]}...")
        
        # Use enhanced RAG if available
        ai_response = "מצטער, אירעה שגיאה בעת עיבוד הבקשה שלך. אנא נסה שוב מאוחר יותר."
        rag_used = False
        rag_count = 0
        
        if has_rag and enhanced_processor and ('use_rag' not in data or data.get('use_rag', True)):
            try:
                logger.info("Using enhanced RAG system for response generation")
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Use the enhanced search and answer function
                enhanced_result = loop.run_until_complete(
                    enhanced_processor.search_and_answer(user_message, max_results=3)
                )
                
                ai_response = enhanced_result.get('answer', ai_response)
                rag_used = True
                rag_count = len(enhanced_result.get('sources', []))
                logger.info(f"Enhanced RAG generated response with {rag_count} sources")
                
            except Exception as rag_err:
                logger.error(f"Error using enhanced RAG: {str(rag_err)}")
                # Fallback to regular Gemini without RAG
                try:
                    gemini_response = safe_generate_content(user_message)
                    ai_response = gemini_response.text
                    logger.info("Fallback to basic Gemini response")
                except Exception as gemini_error:
                    logger.error(f"Gemini fallback also failed: {str(gemini_error)}")
        else:
            # Use basic Gemini without RAG
            try:
                gemini_response = safe_generate_content(user_message)
                ai_response = gemini_response.text
                logger.info("Using basic Gemini response (no RAG)")
            except Exception as gemini_error:
                logger.error(f"Gemini API error: {str(gemini_error)}")
        
        # Prepare the response
        result = {
            "result": ai_response,
            "processing_time": round(time.time() - request_start_time, 3),
            "rag_used": rag_used,
            "rag_count": rag_count
        }
        
        logger.info(f"Message processed successfully in {result['processing_time']}s")
        response = jsonify(result)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response
        
    except Exception as e:
        import traceback
        logger.error(f"Unexpected error in chat endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        response = jsonify({
            "error": "Internal server error",
            "message": str(e)
        })
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response, 500

@app.route('/api/key-status')
def key_status():
    """מצב מנגנון המפתחות"""
    print("🚨🚨🚨 KEY-STATUS CALLED! 🚨🚨🚨")
    
    try:
        from core.gemini_key_manager import get_key_manager
        from core.token_persistence import TokenUsagePersistence
        manager = get_key_manager()
        
        print("🔍 Getting manager status...")
        
        # 🆕 תמיד טען נתונים עדכניים מהקובץ
        import os
        import shutil
        
        current_dir = os.getcwd()
        ai_file = os.path.join(current_dir, "token_usage_data.json")
        backend_file = os.path.join(current_dir, "..", "backend", "token_usage_data.json")
        backend_file = os.path.abspath(backend_file)
        
        print(f"📁 AI file exists: {os.path.exists(ai_file)}")
        print(f"📁 Backend file exists: {os.path.exists(backend_file)}")
        
        # 🔄 תמיד העתק את הקובץ העדכני מהבקאנד
        if os.path.exists(backend_file):
            try:
                shutil.copy2(backend_file, ai_file)
                print(f"✅ Updated file from backend")
            except Exception as copy_err:
                print(f"❌ Error copying file: {copy_err}")
        
        # 🔄 צור persistence חדש וטען נתונים מחדש
        print("🔄 Creating fresh persistence and reloading data...")
        try:
            # צור persistence חדש
            manager.persistence = TokenUsagePersistence()
            print("✅ Created new persistence instance")
            
        except Exception as reload_err:
            print(f"❌ Error creating persistence: {reload_err}")
        
        # 🎯 השתמש בפונקציה החדשה get_detailed_status
        print("🔍 Getting detailed status with current minute data...")
        detailed_status = manager.get_detailed_status()
        
        print(f"🎯 Detailed status result:")
        print(f"🎯 - Total keys: {detailed_status.get('total_keys', 'N/A')}")
        print(f"🎯 - Current key index: {detailed_status.get('current_key_index', 'N/A')}")
        print(f"🎯 - Keys status count: {len(detailed_status.get('keys_status', []))}")
        
        # הדפס נתונים של המפתח הנוכחי
        keys_status = detailed_status.get('keys_status', [])
        current_key_index = detailed_status.get('current_key_index', 0)
        
        if current_key_index < len(keys_status):
            current_key = keys_status[current_key_index]
            print(f"🎯 Current key data:")
            print(f"🎯 - Tokens today: {current_key.get('tokens_today', 'N/A')}")
            print(f"🎯 - Requests today: {current_key.get('requests_today', 'N/A')}")
            print(f"🎯 - Tokens current minute: {current_key.get('tokens_current_minute', 'N/A')}")
            print(f"🎯 - Requests current minute: {current_key.get('requests_current_minute', 'N/A')}")
        else:
            print(f"❌ Current key index {current_key_index} is out of range for {len(keys_status)} keys")
        
        response_data = {
            "status": "ok",
            "key_management": detailed_status
        }
        
        print(f"🎯 Sending response with {len(keys_status)} keys")
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            "status": "error", 
            "error": str(e)
        }), 500

if __name__ == '__main__':
    # Set up server start time for uptime tracking
    app.start_time = time.time()
    
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 5000))
    
    # Run the Flask app
    logger.info(f"Starting AI service on port {port}")
    logger.info(f"RAG support: {'Enabled' if has_rag else 'Disabled'}")
    app.run(
        host='0.0.0.0', 
        port=port, 
        debug=DEBUG,
        threaded=True
    ) 