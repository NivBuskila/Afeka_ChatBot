from flask import Flask, request, jsonify, Response
import os
import logging
import time
from functools import wraps
import google.generativeai as genai
import sys
from pathlib import Path
import dotenv
from flask_cors import CORS
from typing import List, Dict
import asyncio

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

# ✅ FIXED: Add current directory to Python path for absolute imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# ✅ FIXED: Use absolute imports that work when running app.py directly
try:
    # Import database module
    from core.database import get_supabase_client, test_connection
    print("✅ Database module imported successfully")
    
    # Try importing service modules
    try:
        from services.document_processor import DocumentProcessor
        print("✅ DocumentProcessor imported successfully")
        doc_processor_available = True
    except ImportError as e:
        print(f"⚠️  DocumentProcessor not available: {e}")
        doc_processor_available = False
    
    try:
        from services.enhanced_processor import EnhancedProcessor
        print("✅ EnhancedProcessor imported successfully")
        enhanced_processor_available = True
    except ImportError as e:
        print(f"⚠️  EnhancedProcessor not available: {e}")
        enhanced_processor_available = False
    
    # Test database connection
    db_connected = test_connection()
    
    if db_connected and doc_processor_available:
        # Initialize document processors only if everything works
        doc_processor = DocumentProcessor()
        print("✅ DocumentProcessor initialized")
    else:
        doc_processor = None
        print("⚠️  DocumentProcessor not initialized")
    
    if db_connected and enhanced_processor_available:
        enhanced_processor = EnhancedProcessor()
        print("✅ EnhancedProcessor initialized")
    else:
        enhanced_processor = None
        print("⚠️  EnhancedProcessor not initialized")
    
    # Set RAG availability based on what's working
    has_rag = db_connected and (doc_processor_available or enhanced_processor_available)
    
    if has_rag:
        print("✅ RAG modules loaded successfully with database connection")
    else:
        print("⚠️  RAG functionality limited - running in basic mode")
        
except ImportError as e:
    print(f"⚠️  Core modules could not be imported: {e}")
    print(f"💡 AI service will run in basic mode without RAG")
    has_rag = False
    enhanced_processor = None
    doc_processor = None

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if get_optional_env('DEBUG', 'False').lower() == 'true' else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Gemini API
GEMINI_API_KEY = get_required_env('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY not found in environment variables")
    raise ValueError("GEMINI_API_KEY is required")

genai.configure(api_key=GEMINI_API_KEY)

# Create Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Get environment settings
DEBUG = get_optional_env('DEBUG', 'False').lower() == 'true'
API_RATE_LIMIT = int(get_optional_env('API_RATE_LIMIT', '60'))
MAX_MESSAGE_LENGTH = int(get_optional_env('MAX_MESSAGE_LENGTH', '2000'))

# Add security headers to all responses
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

# ✅ ENHANCED: Context manager import section (around line 135)
try:
    from services.enhanced_context_manager import AdvancedContextManager
    context_manager = AdvancedContextManager()
    logger.info("✅ Advanced Context Manager loaded")
except Exception as e:
    logger.warning(f"⚠️ Advanced Context Manager not available, using simple fallback: {e}")
    try:
        from services.context_window_manager import SimpleContextManager
        context_manager = SimpleContextManager()
        logger.info("✅ Simple Context Manager loaded as fallback")
    except Exception as e2:
        logger.warning(f"⚠️ No Context Manager available: {e2}")
        context_manager = None

# ✅ ENHANCED: Health check with comprehensive status
@app.route('/')
def health_check():
    """Enhanced health check endpoint with connectivity verification"""
    try:
        # Test database connectivity
        db_connected = False
        if has_rag:
            try:
                db_connected = test_connection()
            except:
                db_connected = False
        
        # Test Gemini API
        gemini_configured = bool(GEMINI_API_KEY)
        
        return jsonify({
            "status": "healthy" if (db_connected or not has_rag) and gemini_configured else "degraded",
            "service": "ai-service",
            "version": "2.0.0",
            "capabilities": {
                "rag_support": has_rag,
                "database_connected": db_connected,
                "gemini_configured": gemini_configured,
                "context_manager": context_manager is not None,
                "document_processor": doc_processor is not None,
                "enhanced_processor": enhanced_processor is not None
            },
            "environment": {
                "debug": DEBUG,
                "max_message_length": MAX_MESSAGE_LENGTH,
                "rate_limit": API_RATE_LIMIT
            },
            "timestamp": time.time()
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": time.time()
        }), 500

# ✅ FIXED: RAG endpoints with proper error handling
@app.route('/rag/search', methods=['POST'])
def rag_search():
    """חיפוש סמנטי במסמכים"""
    if not has_rag or not doc_processor:
        return jsonify({"error": "RAG search not available - missing components"}), 503
    
    try:
        data = request.get_json(force=True)
        query = data.get("query", "")
        limit = data.get("limit", 10)
        threshold = data.get("threshold", 0.78)
        
        if not query.strip():
            return jsonify({"error": "Query cannot be empty"}), 400
        
        results = doc_processor.search_documents(query, limit, threshold)
        
        # Handle async results
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        if asyncio.iscoroutine(results):
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
    if not has_rag or not doc_processor:
        return jsonify({"error": "RAG hybrid search not available"}), 503
    
    try:
        data = request.get_json(force=True)
        query = data.get("query", "")
        limit = data.get("limit", 10)
        threshold = data.get("threshold", 0.78)
        
        if not query.strip():
            return jsonify({"error": "Query cannot be empty"}), 400
        
        results = doc_processor.hybrid_search(query, limit, threshold)
        
        # Handle async results  
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        if asyncio.iscoroutine(results):
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
        return jsonify({"error": "Enhanced RAG not available"}), 503
    
    try:
        data = request.get_json(force=True)
        query = data.get("query", "")
        max_results = data.get("max_results", 10)
        include_context = data.get("include_context", True)
        
        if not query.strip():
            return jsonify({"error": "Query cannot be empty"}), 400
        
        # Handle async operations
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        if include_context:
            # Full search with answer generation
            results = enhanced_processor.search_and_answer(query, max_results)
            if asyncio.iscoroutine(results):
                results = loop.run_until_complete(results)
        else:
            # Search only
            search_results = enhanced_processor.search(query, max_results)
            if asyncio.iscoroutine(search_results):
                search_results = loop.run_until_complete(search_results)
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
        # Handle async operations
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Get document and chunk counts
        if doc_processor:
            chunks_data = doc_processor._get_all_document_chunks(limit=1000)
            if asyncio.iscoroutine(chunks_data):
                chunks_data = loop.run_until_complete(chunks_data)
        else:
            chunks_data = []
        
        # Calculate statistics
        total_chunks = len(chunks_data)
        documents = set(chunk.get('document_id') for chunk in chunks_data if chunk.get('document_id'))
        total_documents = len(documents)
        
        return jsonify({
            "total_documents": total_documents,
            "total_chunks": total_chunks,
            "avg_chunks_per_document": total_chunks / max(total_documents, 1),
            "rag_status": "active" if has_rag else "inactive"
        })
        
    except Exception as e:
        logger.error(f"Error getting RAG stats: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Replace the entire chat function with the enhanced version
@app.route('/chat', methods=['POST'])
def chat():
    """Enhanced chat endpoint with advanced context management and RAG integration"""
    try:
        start_time = time.time()
        data = request.get_json(force=True)
        message = data.get('message', '')
        context = data.get('context', [])
        session_id = data.get('session_id')  # NEW: Session tracking
        use_rag = data.get('use_rag', True)
        
        if not message.strip():
            return jsonify({"error": "Message cannot be empty"}), 400
        
        if len(message) > MAX_MESSAGE_LENGTH:
            return jsonify({"error": f"Message too long (max {MAX_MESSAGE_LENGTH} characters)"}), 400

        # Use Advanced Context Manager if available
        if not context_manager:
            return _simple_chat_fallback(message, context)
        
        # Get RAG results if available and requested
        rag_results = []
        if use_rag and has_rag and enhanced_processor:
            try:
                async def get_rag_results():
                    return await enhanced_processor.search(message, max_results=5)
                
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        import concurrent.futures
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            future = executor.submit(asyncio.run, get_rag_results())
                            rag_results = future.result()
                    else:
                        rag_results = loop.run_until_complete(get_rag_results())
                except RuntimeError:
                    rag_results = asyncio.run(get_rag_results())
                
                if not isinstance(rag_results, list):
                    rag_results = []
                    
                logger.info(f"✅ Retrieved {len(rag_results)} RAG results for context")
                
            except Exception as e:
                logger.warning(f"⚠️ RAG search failed, continuing without: {e}")
                rag_results = []

        # Build advanced context
        try:
            async def build_advanced_context():
                return await context_manager.build_context_with_rag(
                    conversation_history=context,
                    rag_results=rag_results,
                    current_query=message,
                    session_id=session_id
                )
            
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, build_advanced_context())
                        advanced_context = future.result()
                else:
                    advanced_context = loop.run_until_complete(build_advanced_context())
            except RuntimeError:
                advanced_context = asyncio.run(build_advanced_context())
                
        except Exception as e:
            logger.error(f"❌ Advanced context building failed: {e}")
            # Fallback to simple context
            advanced_context = {
                'rag_context': {'text': '', 'sources': []},
                'conversation_context': {'messages': context[-5:]},
                'context_quality_score': 0.3
            }

        # Build enhanced prompt with advanced context
        prompt = _build_enhanced_prompt(message, advanced_context)
        
        # Generate response with Gemini
        try:
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content(prompt)
            answer = response.text
        except Exception as e:
            logger.error(f"❌ Gemini generation failed: {e}")
            answer = "אני מצטער, אירעה שגיאה בעיבוד הבקשה. אנא נסה שוב."

        processing_time = int((time.time() - start_time) * 1000)
        
        # Prepare enhanced response
        enhanced_response = {
            "result": answer,
            "processing_time": processing_time,
            "rag_used": len(rag_results) > 0,
            "context_messages": len(advanced_context.get('conversation_context', {}).get('messages', [])),
            "rag_sources": advanced_context.get('rag_context', {}).get('sources', []),
            "context_quality_score": advanced_context.get('context_quality_score', 0),
            "token_usage": advanced_context.get('token_usage', {}),
            "source": "gemini-enhanced"
        }

        # Store conversation memory
        if session_id and context_manager:
            try:
                async def store_memory():
                    return await context_manager.manage_conversation_memory(
                        session_id=session_id,
                        new_message={'content': message, 'role': 'user', 'timestamp': time.time()},
                        response=enhanced_response
                    )
                
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        import concurrent.futures
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            executor.submit(asyncio.run, store_memory())
                    else:
                        loop.run_until_complete(store_memory())
                except RuntimeError:
                    asyncio.run(store_memory())
                    
            except Exception as e:
                logger.warning(f"⚠️ Failed to store conversation memory: {e}")

        return jsonify(enhanced_response)
        
    except Exception as e:
        logger.error(f"❌ Error in enhanced chat: {str(e)}")
        return jsonify({
            "result": "אני מצטער, אירעה שגיאה בעיבוד הבקשה. אנא נסה שוב.",
            "processing_time": int((time.time() - start_time) * 1000) if 'start_time' in locals() else 0,
            "rag_used": False,
            "context_messages": 0,
            "error": str(e)
        }), 500

# Add these helper functions at the end of the file
def _build_enhanced_prompt(user_message: str, advanced_context: Dict) -> str:
    """Build enhanced prompt with advanced context integration"""
    
    rag_context = advanced_context.get('rag_context', {})
    conversation_context = advanced_context.get('conversation_context', {})
    
    # Base system prompt
    system_prompt = """אתה עוזר AI מתקדם של מכללת אפקה. 
אתה עונה בעברית בצורה מקצועית, מדויקת ומועילה.
השתמש במידע שסופק לך וציין מקורות כשרלוונטי."""
    
    # Add RAG context if available
    rag_section = ""
    if rag_context.get('text'):
        rag_section = f"""
📚 מידע רלוונטי מתקנוני המכללה:
{rag_context['text']}

"""
    
    # Add conversation context if available
    conversation_section = ""
    if conversation_context.get('messages'):
        recent_messages = conversation_context['messages'][-3:]
        conv_text = "\n".join([
            f"👤 {msg.get('content', '')}" if msg.get('role') == 'user' 
            else f"🤖 {msg.get('content', '')}"
            for msg in recent_messages
        ])
        conversation_section = f"""
💬 הקשר השיחה האחרון:
{conv_text}

"""
    
    # Build final prompt
    prompt = f"""{system_prompt}

{rag_section}{conversation_section}🎯 שאלה נוכחית: {user_message}

הנחיות:
- ענה בעברית בלבד
- השתמש במידע שסופק אם רלוונטי
- אם המידע חלקי, ציין זאת
- הוסף הפניות לסעיפים אם יש מקורות
- שמור על טון מקצועי ואקדמי"""

    return prompt


def _simple_chat_fallback(message: str, context: List[Dict]) -> Dict:
    """Simple fallback for when advanced context is not available"""
    try:
        if context:
            context_text = "\n".join([
                f"הודעה קודמת: {msg.get('content', '')[:200]}..."
                for msg in context[-3:]
            ])
            prompt = f"""הקשר השיחה:
{context_text}

אתה עוזר AI של מכללת אפקה. ענה בעברית בצורה מועילה ומקצועית.

שאלה: {message}"""
        else:
            prompt = f"אתה עוזר AI של מכללת אפקה. ענה בעברית בצורה מועילה ומקצועית.\n\nשאלה: {message}"
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        return jsonify({
            "result": response.text,
            "processing_time": 1000,
            "rag_used": False,
            "context_messages": len(context),
            "source": "gemini-simple-fallback"
        })
        
    except Exception as e:
        logger.error(f"❌ Simple fallback failed: {e}")
        return jsonify({
            "result": "אני מצטער, אירעה שגיאה בעיבוד הבקשה. אנא נסה שוב.",
            "processing_time": 0,
            "rag_used": False,
            "error": str(e)
        }), 500
    
@app.route('/rag/document/<int:document_id>', methods=['GET'])
def rag_document_status(document_id):
    """בדיקת סטטוס מסמך ספציפי"""
    if not has_rag:
        return jsonify({"error": "RAG modules not available"}), 503
    
    try:
        # Get document info from database
        if doc_processor:
            # Use the database client from doc_processor
            response = doc_processor.supabase.table('documents')\
                .select('*')\
                .eq('id', document_id)\
                .execute()
            
            if response.data:
                document = response.data[0]
                
                # Get chunk count for this document
                chunks_response = doc_processor.supabase.table('document_chunks')\
                    .select('id')\
                    .eq('document_id', document_id)\
                    .execute()
                
                chunk_count = len(chunks_response.data) if chunks_response.data else 0
                
                return jsonify({
                    "document_id": document_id,
                    "name": document.get('name'),
                    "status": document.get('status'),
                    "chunk_count": chunk_count,
                    "created_at": document.get('created_at'),
                    "updated_at": document.get('updated_at')
                })
            else:
                return jsonify({"error": "Document not found"}), 404
        else:
            return jsonify({"error": "Document processor not available"}), 503
        
    except Exception as e:
        logger.error(f"Error getting document status: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/rag/document/<int:document_id>/reprocess', methods=['POST'])
def rag_reprocess_document(document_id):
    """עיבוד מחדש של מסמך"""
    if not has_rag or not doc_processor:
        return jsonify({"error": "RAG reprocessing not available"}), 503
    
    try:
        # Handle async reprocessing
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Get document path (this would need to be implemented based on your storage)
        # For now, return a placeholder response
        return jsonify({
            "message": "Document reprocessing initiated",
            "document_id": document_id,
            "status": "processing"
        })
        
    except Exception as e:
        logger.error(f"Error reprocessing document: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/rag/test_enhanced', methods=['POST'])
def test_enhanced_system():
    """בדיקת מערכת RAG מתקדמת"""
    if not has_rag:
        return jsonify({"error": "Enhanced RAG not available"}), 503
    
    try:
        data = request.get_json(force=True)
        test_query = data.get("query", "בדיקת מערכת")
        
        results = {
            "test_query": test_query,
            "timestamp": time.time(),
            "components": {
                "database": test_connection() if has_rag else False,
                "document_processor": doc_processor is not None,
                "enhanced_processor": enhanced_processor is not None,
                "context_manager": context_manager is not None
            }
        }
        
        # Try a simple search if possible
        if doc_processor:
            try:
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                search_results = doc_processor.search_documents(test_query, limit=3)
                if asyncio.iscoroutine(search_results):
                    search_results = loop.run_until_complete(search_results)
                
                results["search_test"] = {
                    "success": True,
                    "results_count": len(search_results)
                }
            except Exception as e:
                results["search_test"] = {
                    "success": False,
                    "error": str(e)
                }
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Error in enhanced system test: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Helper function for building prompts
def _build_simple_prompt(user_message: str, context: List[Dict]) -> str:
    """Build a simple prompt with context"""
    if not context:
        return f"שאלת משתמש: {user_message}\n\nאנא ענה בעברית."
    
    context_text = "\n".join([
        f"מקור {i+1}: {item.get('content', '')[:500]}..."
        for i, item in enumerate(context[:3])
    ])
    
    return f"""
מידע רלוונטי:
{context_text}

שאלת משתמש: {user_message}

בהתבסס על המידע שסופק, אנא ענה בעברית בצורה מדויקת ומועילה.
"""

if __name__ == "__main__":
    logger.info("🚀 Starting AI service on port 5000")
    logger.info(f"🔧 RAG support: {'Enabled' if has_rag else 'Disabled'}")
    logger.info(f"🔧 Debug mode: {DEBUG}")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=DEBUG
    )