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

# הוספת הנתיב לתיקיית backend כדי לאפשר גישה למודולים של RAG
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# טעינת משתני סביבה
dotenv.load_dotenv(override=True)

# ייבוא מודולי RAG
try:
    from services.document_processor import DocumentProcessor
    from app.core.database import get_supabase_client
    has_rag = True
    # Initialize document processor once
    doc_processor = DocumentProcessor()
except ImportError as e:
    logging.warning(f"RAG modules could not be imported: {e}")
    has_rag = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Gemini API
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
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
            "status_counts": status_counts
        })
        
    except Exception as e:
        logger.error(f"Error getting RAG stats: {str(e)}")
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
        conversation_history = data.get('conversation_history', [])
        session_id = data.get('session_id', None)
        
        logger.info(f"User message type: {type(user_message)}")
        logger.info(f"Conversation history length: {len(conversation_history)}")
        logger.info(f"Session ID: {session_id}")
        
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
        
        # קבלת תוצאות מהמסמכים אם RAG זמין
        rag_results = []
        if has_rag and 'use_rag' in data and data['use_rag']:
            try:
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                rag_results = loop.run_until_complete(doc_processor.search_documents(user_message, limit=3, threshold=0.75))
                logger.info(f"Found {len(rag_results)} relevant documents with RAG")
            except Exception as rag_err:
                logger.error(f"Error using RAG: {str(rag_err)}")
        
        # Use Gemini API to generate a response
        try:
            # שימוש ישיר במודל Gemini לפי הגרסה החדשה
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            # בניית prompt עם היסטוריית השיחה
            prompt_parts = []
            
            # אם יש תוצאות מ-RAG, נוסיף אותן להקשר
            if rag_results:
                context_parts = ["הנה מידע שעשוי להיות רלוונטי לשאלתך:"]
                for i, result in enumerate(rag_results[:3]):
                    context_parts.append(f"מסמך {i+1}: {result.get('content', '')[:300]}...")
                context_parts.append("\nעכשיו לשיחה:")
                prompt_parts.append("\n\n".join(context_parts))
            
            # הוספת היסטוריית השיחה
            if conversation_history and len(conversation_history) > 1:
                prompt_parts.append("היסטוריית השיחה:")
                for msg in conversation_history[:-1]:  # כל ההודעות חוץ מהאחרונה
                    role_name = "משתמש" if msg['role'] == 'user' else "עוזר"
                    prompt_parts.append(f"{role_name}: {msg['content']}")
                prompt_parts.append("\nההודעה הנוכחית:")
            
            # הוספת ההודעה הנוכחית
            prompt_parts.append(user_message)
            
            # יצירת prompt מלא
            full_prompt = "\n\n".join(prompt_parts)
            
            logger.info(f"Full prompt length: {len(full_prompt)}")
            
            gemini_response = model.generate_content(full_prompt)
            ai_response = gemini_response.text
            logger.info(f"Gemini API response received: {ai_response[:30]}...")
        except Exception as gemini_error:
            logger.error(f"Gemini API error: {str(gemini_error)}")
            ai_response = "מצטער, אירעה שגיאה בעת עיבוד הבקשה שלך. אנא נסה שוב מאוחר יותר."
        
        # Prepare the response
        result = {
            "result": ai_response,
            "processing_time": round(time.time() - request_start_time, 3),
            "rag_used": len(rag_results) > 0,
            "rag_count": len(rag_results)
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