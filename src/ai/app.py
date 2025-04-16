from flask import Flask, request, jsonify, Response
import os
import logging
import time
from functools import wraps
from google import genai

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Gemini API
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyBBw-VlqWekqnd_vPXCS7LSuKfrkbOro7s')
# ביצירת מופע Client במקום להשתמש בפונקציית configure
genai_client = genai.Client(api_key=GEMINI_API_KEY)

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
        
        # Use Gemini API to generate a response
        try:
            # שימוש ב-client ובמתודה generate_content לפי הגרסה החדשה
            gemini_response = genai_client.models.generate_content(
                model="gemini-2.0-flash",
                contents=user_message
            )
            ai_response = gemini_response.text
            logger.info(f"Gemini API response received: {ai_response[:30]}...")
        except Exception as gemini_error:
            logger.error(f"Gemini API error: {str(gemini_error)}")
            ai_response = "מצטער, אירעה שגיאה בעת עיבוד הבקשה שלך. אנא נסה שוב מאוחר יותר."
        
        # Prepare the response
        result = {
            "result": ai_response,
            "processing_time": round(time.time() - request_start_time, 3)
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
    app.run(
        host='0.0.0.0', 
        port=port, 
        debug=DEBUG,
        threaded=True
    ) 