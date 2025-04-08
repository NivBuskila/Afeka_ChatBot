import logging
import time
import json
import traceback

from flask import Blueprint, request, jsonify, Response

# Use absolute imports instead of relative
from ai.core import config
# Import the service layer
from ai.services.rag_service import get_rag_service, RAGService
from ai.services.gemini_service import get_gemini_service, GeminiService

logger = logging.getLogger(__name__)
api_bp = Blueprint('api', __name__)

# Basic route for health checks
@api_bp.route('/')
def health_check():
    """Basic health check endpoint"""
    return jsonify({"status": "ok", "service": "ai-service"})

# Main chat endpoint - uses RAG service which now uses Gemini
@api_bp.route('/chat', methods=['POST'])
def chat():
    """
    Processes user queries.
    Handles request validation and calls the RAG service.
    """
    # request_start_time = time.time() # Service calculates processing time now
    
    try:
        # Validate content type or attempt flexible parsing
        content_type = request.content_type
        logger.info(f"Request content type: {content_type}")

        # Get raw data and decode, then parse JSON
        try:
            raw_data = request.data
            if not raw_data:
                 raise ValueError("Request body is empty")
            body_str = raw_data.decode('utf-8', errors='replace')
            data = json.loads(body_str)
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to decode or parse request body: {e}")
            return jsonify({"error": "Invalid request body. Expecting valid JSON."}), 400
        
        # Validate required fields and message length
        user_message = data.get('message')
        if not user_message:
            logger.warning("Invalid request: missing 'message' field")
            return jsonify({"error": "'message' field is required"}), 400
            
        if not isinstance(user_message, str):
             logger.warning("Invalid request: 'message' field must be a string")
             return jsonify({"error": "'message' field must be a string"}), 400

        if len(user_message) > config.MAX_MESSAGE_LENGTH:
            logger.warning(f"Message too long: {len(user_message)} chars (max: {config.MAX_MESSAGE_LENGTH})")
            return jsonify({"error": f"Message too long (max {config.MAX_MESSAGE_LENGTH} characters)"}), 400
                
        logger.info(f"Received message (length {len(user_message)}): {user_message[:30]}...")
        
        # --- Call Service Layer ---
        rag_service: RAGService = get_rag_service() # Get service instance 
        result = rag_service.process_query(user_message)
        # --------------------------
        
        logger.info(f"Message processed successfully in {result.get('processing_time', -1):.3f}s")
        # Ensure response is JSON with correct headers
        response = jsonify(result)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response
        
    except Exception as e:
        # Catch-all for unexpected errors in the route handler
        logger.error(f"Unexpected error in chat endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        # Return generic 500 error
        return jsonify({"error": "Internal server error"}), 500

# Direct Gemini API endpoint - bypasses RAG
@api_bp.route('/gemini', methods=['POST'])
def gemini_chat():
    """
    Processes user queries directly with Gemini API.
    Bypasses RAG processing for direct LLM access.
    """
    try:
        # Similar validation as the main chat endpoint
        try:
            data = request.get_json()
            if not data:
                raise ValueError("Request body is empty")
        except Exception as e:
            logger.warning(f"Failed to parse request body: {e}")
            return jsonify({"error": "Invalid request body. Expecting valid JSON."}), 400
        
        # Validate required fields
        user_message = data.get('message')
        if not user_message:
            logger.warning("Invalid request: missing 'message' field")
            return jsonify({"error": "'message' field is required"}), 400
            
        if len(user_message) > config.MAX_MESSAGE_LENGTH:
            logger.warning(f"Message too long: {len(user_message)} chars (max: {config.MAX_MESSAGE_LENGTH})")
            return jsonify({"error": f"Message too long (max {config.MAX_MESSAGE_LENGTH} characters)"}), 400
                
        logger.info(f"Gemini endpoint received message: {user_message[:30]}...")
        
        # Call Gemini service directly
        gemini_service = get_gemini_service()
        result = gemini_service.generate_response(user_message)
        
        # Return response
        logger.info(f"Gemini message processed in {result.get('processing_time', -1):.3f}s")
        response = jsonify(result)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response
        
    except Exception as e:
        logger.error(f"Unexpected error in gemini endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": "Internal server error"}), 500 