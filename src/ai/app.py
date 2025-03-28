from flask import Flask, request, jsonify, Response
import os
import logging
import time
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

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
    return jsonify({"status": "ok", "service": "ai-service"})

# Main chat endpoint
@app.route('/chat', methods=['POST'])
def chat():
    """
    Placeholder for future RAG implementation
    Will process user queries against document knowledge base
    """
    request_start_time = time.time()
    
    try:
        # Extract the message from the request
        data = request.get_json()
        if not data or 'message' not in data:
            logger.warning("Invalid request: missing message field")
            return jsonify({
                "error": "Message field is required"
            }), 400
            
        user_message = data['message']
        
        # Validate message length
        if not user_message or len(user_message) > MAX_MESSAGE_LENGTH:
            logger.warning(f"Message too long: {len(user_message)} chars (max: {MAX_MESSAGE_LENGTH})")
            return jsonify({
                "error": f"Message too long (max {MAX_MESSAGE_LENGTH} characters)"
            }), 400
                
        logger.info(f"Received message: {user_message[:30]}...")
        
        # Simple placeholder response
        result = {
            "keywords": [],  # Future: Will contain extracted keywords from query
            "result": "This is a placeholder response. Future implementation will use RAG to query document knowledge base.",
            "sentiment": "neutral"  # Future: Will analyze sentiment
        }
        
        # Add processing time for monitoring
        processing_time = time.time() - request_start_time
        result['processing_time'] = round(processing_time, 3)
        
        logger.info(f"Message processed successfully in {processing_time:.3f}s")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {str(e)}")
        return jsonify({
            "error": "Internal server error"
        }), 500

if __name__ == '__main__':
    # Set up server start time for uptime tracking
    app.start_time = time.time()
    
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