"""
Afeka ChatBot - Minimal AI Service (v2.0)

מטרת השירות המופחת:
1. Health checks ובדיקות בריאות השירות  
2. Key management status עבור DatabaseKeyManager
3. תמיכה בארכיטקטורה היברידית עם Backend החדש

הערה: רוב הפונקציונליות של RAG ו-Chat עברה לBackend החדש
שמשתמש ישירות במודולים מ-src/ai/services/ ללא HTTP calls.
השירות הזה נשמר רק עבור key management ובדיקות בריאות.
"""

from flask import Flask, request, jsonify
import os
import logging
import time
import dotenv
from flask_cors import CORS

# Load environment variables
dotenv.load_dotenv(override=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
# Enable CORS support
CORS(app, resources={r"/*": {"origins": "*"}})

# Get environment settings
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

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
        "version": "2.0-minimal",
        "note": "Minimal service for key management and health checks only"
    })

@app.route('/status')
@app.route('/api/key-status')
def key_status():
    """Simple key management status endpoint for DatabaseKeyManager"""
    try:
        # Simple solution: call backend API instead of handling database directly
        import requests
        backend_url = os.environ.get("BACKEND_URL", "http://localhost:8000")
        
        response = requests.get(f"{backend_url}/api/keys/", timeout=10)
        
        if response.status_code == 200:
            backend_data = response.json()
            return jsonify(backend_data)
        else:
            return jsonify({
                "status": "error",
                "error": f"Backend API returned {response.status_code}",
                "key_management": {
                    "current_key_index": 0,
                    "total_keys": 0,
                    "available_keys": 0
                }
            }), 500
            
    except Exception as e:
        logger.error(f"Status endpoint error: {str(e)}")
        return jsonify({
            "status": "error", 
            "error": str(e),
            "key_management": {
                "current_key_index": 0,
                "total_keys": 0,
                "available_keys": 0
            }
        }), 500

if __name__ == '__main__':
    # Set up server start time for uptime tracking
    app.start_time = time.time()
    
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 5000))
    
    # Run the Flask app
    logger.info(f"Starting minimal AI service on port {port}")
    logger.info("Service provides: health checks + key management status")
    logger.info("For full RAG functionality, use the Backend service directly")
    app.run(
        host='0.0.0.0', 
        port=port, 
        debug=DEBUG,
        threaded=True
    ) 