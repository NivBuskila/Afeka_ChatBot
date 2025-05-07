from flask import Flask, request, jsonify, Response
import os
import logging
import time
import json
from functools import wraps
import google.generativeai as genai
from werkzeug.utils import secure_filename
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime
from typing import Dict, List, Any, Optional

# Import RAG system
from core.rag import AfekaRAG

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log")
    ]
)
logger = logging.getLogger(__name__)

# Initialize Gemini API
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyBBw-VlqWekqnd_vPXCS7LSuKfrkbOro7s')

# For testing purposes, use a fixed API key if the environment variable is not set
if not GEMINI_API_KEY or GEMINI_API_KEY == "AIzaSyBBw-VlqWekqnd_vPXCS7LSuKfrkbOro7s":
    logger.warning("Using dummy API key. Please set a valid GEMINI_API_KEY environment variable for production.")
    logger.warning("The chatbot will not work properly without a valid API key.")

# Configure Gemini API
try:
    genai.configure(api_key=GEMINI_API_KEY)
    logger.info("Gemini API configured successfully")
except Exception as e:
    logger.error(f"Error configuring Gemini API: {e}")
    logger.warning("Application will run but AI features may not work properly")

# Create Flask app
app = Flask(__name__)
CORS(app)

# Get environment settings
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
API_RATE_LIMIT = int(os.environ.get('API_RATE_LIMIT', '60'))  # Requests per minute per IP
MAX_MESSAGE_LENGTH = int(os.environ.get('MAX_MESSAGE_LENGTH', '1000'))  # Maximum length of input message
UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "uploads")
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'txt', 'md', 'csv', 'json', 'html'}
DEFAULT_MODEL = os.environ.get('DEFAULT_MODEL', 'gemini-1.5-flash')  # Default model name

# Vector store persistence directory
VECTOR_STORE_DIR = os.environ.get('VECTOR_STORE_DIR', './data/vector_store')
COLLECTION_NAME = os.environ.get("COLLECTION_NAME", "afeka_docs")

# Initialize RAG system
rag_system = AfekaRAG(
    api_key=GEMINI_API_KEY,
    persist_directory=VECTOR_STORE_DIR,
    collection_name=COLLECTION_NAME,
    supabase_url=os.environ.get("SUPABASE_URL"),
    supabase_key=os.environ.get("SUPABASE_KEY")
)

# Add security headers to all responses
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

# Health check endpoint
@app.route('/')
def health_check():
    """Health check endpoint."""
    status = {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "rag_status": rag_system.get_status()
    }
    return jsonify(status)

# API health check
@app.route('/api/health')
def api_health():
    """API health check endpoint"""
    return jsonify({
        "status": "ok", 
        "service": "ai-service",
        "rag_status": "active" if rag_system and rag_system.get_vector_store() else "inactive"
    })

# Main chat endpoint
@app.route('/chat', methods=['POST'])
@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Process user message with RAG system
    """
    request_start_time = time.time()
    
    try:
        # Set response encoding to ensure Hebrew is handled correctly
        response_encoding = 'utf-8'
        
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
        
        # Get the model name from request or use default
        model_name = data.get('model', DEFAULT_MODEL)
        
        # Check if sources should be included in response
        include_sources = data.get('include_sources', False)
        
        # Ensure message is properly decoded if it's bytes
        if isinstance(user_message, bytes):
            user_message = user_message.decode('utf-8', errors='replace')
        
        # Log the message content to help diagnose Hebrew encoding issues
        logger.info(f"Message content (first 100 chars): {repr(user_message[:100])}")
        
        # Validate message length
        if not user_message or len(user_message) > MAX_MESSAGE_LENGTH:
            logger.warning(f"Message too long: {len(user_message)} chars (max: {MAX_MESSAGE_LENGTH})")
            response = jsonify({
                "error": f"Message too long (max {MAX_MESSAGE_LENGTH} characters)"
            })
            response.headers['Content-Type'] = 'application/json; charset=utf-8'
            return response, 400
                
        logger.info(f"Received message (length {len(user_message)}): {user_message[:30]}...")
        
        # Use RAG system to generate a response
        try:
            # Check if RAG system is ready
            if rag_system and rag_system.get_vector_store():
                # Process with RAG
                logger.info("Processing with RAG system")
                answer, sources = rag_system.answer_question(user_message, model_name=model_name)
                
                # Log for debugging
                logger.info(f"RAG response received, length: {len(answer) if answer else 0}")
                logger.info(f"Response preview: {answer[:100] if answer else 'None'}")
                logger.info(f"Number of sources: {len(sources) if sources else 0}")
            else:
                # Fallback to direct Gemini API
                logger.info("Using direct Gemini API (no RAG)")
                try:
                    # Create model with safe settings for multilingual content
                    model = genai.GenerativeModel(
                        model_name,
                        safety_settings=[
                            {
                                "category": "HARM_CATEGORY_HARASSMENT",
                                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                            },
                            {
                                "category": "HARM_CATEGORY_HATE_SPEECH",
                                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                            },
                            {
                                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                            },
                            {
                                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                            }
                        ],
                        generation_config={
                            "temperature": 0.2,
                            "top_p": 0.95,
                            "top_k": 64,
                            "max_output_tokens": 2048,
                        }
                    )
                    
                    # Add a clear system prompt for Hebrew content
                    system_prompt = "אתה עוזר חכם של מכללת אפקה להנדסה. ענה על השאלה בעברית."
                    response = model.generate_content([system_prompt, user_message])
                    answer = response.text
                    sources = []
                    
                    # Log for debugging
                    logger.info(f"Direct API response received, length: {len(answer) if answer else 0}")
                    logger.info(f"Response preview: {answer[:100] if answer else 'None'}")
                except Exception as e:
                    logger.error(f"Error with Gemini API: {e}")
                    return jsonify({"error": "Failed to generate response"}), 500

            # Format response based on whether sources are requested
            if include_sources:
                api_response = {
                    "message": answer,
                    "sources": sources,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                api_response = {
                    "message": answer,
                    "timestamp": datetime.now().isoformat()
                }
            
            response = jsonify(api_response)
            response.headers['Content-Type'] = f'application/json; charset={response_encoding}'
            return response
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            error_details = str(e) if DEBUG else "An internal error occurred"
            return jsonify({"error": error_details}), 500
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500

# Document management endpoints
@app.route('/api/documents/status', methods=['GET'])
def list_documents():
    """Return the status of documents in the system."""
    status = rag_system.get_status()
    return jsonify(status)

@app.route('/api/documents/load', methods=['POST'])
def load_document():
    """Load a document from a file or URL."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400
            
        # Extract parameters
        url = data.get('url')
        file_path = data.get('file_path')
        metadata = data.get('metadata', {})
        chunk_size = data.get('chunk_size', 512)
        chunk_overlap = data.get('chunk_overlap', 128)
        extract_section_metadata = data.get('extract_section_metadata', False)
        
        if not url and not file_path:
            return jsonify({"error": "Either url or file_path must be provided"}), 400
            
        # Load from URL or file
        if url:
            success = rag_system.load_url(
                url=url,
                metadata=metadata,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
            source = url
        else:
            success = rag_system.load_document(
                file_path=file_path,
                metadata=metadata,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                extract_section_metadata=extract_section_metadata
            )
            source = file_path
            
        if success:
            return jsonify({
                "status": "success",
                "message": f"Document loaded successfully from {source}"
            })
        else:
            return jsonify({
                "status": "error",
                "message": f"Failed to load document from {source}"
            }), 500
    except Exception as e:
        logger.error(f"Error loading document: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e) if DEBUG else "Internal server error"
        }), 500

@app.route('/api/documents/load-from-url', methods=['POST'])
def load_from_url():
    """Load a document from a URL."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400
            
        # Extract parameters
        url = data.get('url')
        metadata = data.get('metadata', {})
        chunk_size = data.get('chunk_size', 512)
        chunk_overlap = data.get('chunk_overlap', 128)
        
        if not url:
            return jsonify({"error": "URL must be provided"}), 400

        # Add a short delay to prevent race conditions
        time.sleep(1)
            
        # Load from URL
        success = rag_system.load_url(
            url=url,
            metadata=metadata,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
            
        if success:
            return jsonify({
                "status": "success",
                "message": f"Document loaded successfully from URL: {url}"
            })
        else:
            return jsonify({
                "status": "error",
                "message": f"Failed to load document from URL: {url}"
            }), 500
    except Exception as e:
        logger.error(f"Error loading document from URL: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error: {str(e)}"
        }), 500

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/documents/upload', methods=['POST'])
def upload_document():
    """Upload a document file."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if file and allowed_file(file.filename):
        # Get metadata from form data
        metadata = {}
        try:
            metadata_str = request.form.get('metadata', '{}')
            metadata = json.loads(metadata_str)
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid metadata JSON"}), 400
            
        # Save file
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # Extract chunk parameters
        try:
            chunk_size = int(request.form.get('chunk_size', '512'))
            chunk_overlap = int(request.form.get('chunk_overlap', '128'))
        except ValueError:
            return jsonify({"error": "Invalid chunk parameters"}), 400
        
        # Add file to RAG system
        success = rag_system.load_document(
            file_path=file_path,
            metadata=metadata,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        if success:
            return jsonify({
                "status": "success",
                "message": f"Document {filename} uploaded and processed successfully",
                "file_path": file_path
            })
        else:
            # Remove file if processing failed
            try:
                os.remove(file_path)
            except:
                pass
                
            return jsonify({
                "status": "error",
                "message": "Failed to process document"
            }), 500
    else:
        return jsonify({
            "error": f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        }), 400

@app.route('/api/documents/load-from-supabase', methods=['POST'])
def load_from_supabase():
    """Load documents from Supabase."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400
            
        # Extract parameters
        table_name = data.get('table_name', 'documents')
        query_filter = data.get('query_filter', {})
        content_field = data.get('content_field', 'content')
        chunk_size = data.get('chunk_size', 512)
        chunk_overlap = data.get('chunk_overlap', 128)
        
        # Load from Supabase
        success, count = rag_system.load_from_supabase(
            table_name=table_name,
            query_filter=query_filter,
            content_field=content_field,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
            
        if success:
            return jsonify({
                "status": "success",
                "message": f"Loaded {count} documents from Supabase table {table_name}",
                "count": count
            })
        else:
            return jsonify({
                "status": "error",
                "message": f"Failed to load documents from Supabase table {table_name}"
            }), 500
    except Exception as e:
        logger.error(f"Error loading from Supabase: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e) if DEBUG else "Internal server error"
        }), 500

@app.route('/api/documents/clear', methods=['POST'])
def clear_documents():
    """Clear all documents from the system."""
    success = rag_system.clear_documents()
    
    if success:
        return jsonify({
            "status": "success",
            "message": "All documents cleared successfully"
        })
    else:
        return jsonify({
            "status": "error",
            "message": "Failed to clear documents"
        }), 500

if __name__ == '__main__':
    # Set up server start time for uptime tracking
    app.start_time = time.time()
    
    # Create directories if they don't exist
    os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
    
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 5000))
    
    # Run the Flask app
    logger.info(f"Starting AI service on port {port}")
    app.run(
        host='0.0.0.0', 
        port=port, 
        debug=DEBUG,
        threaded=True
    ) 