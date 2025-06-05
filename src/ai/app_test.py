from flask import Flask, request, jsonify
import os
import logging
import google.generativeai as genai
from flask_cors import CORS
from supabase import create_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple Supabase client setup
def get_supabase_client():
    try:
        supabase_url = os.environ.get('SUPABASE_URL', 'https://cqvicgimmzrffvarlokq.supabase.co')
        supabase_key = os.environ.get('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNxdmljZ2ltbXpyZmZ2YXJsb2txIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDcyNDE0MjgsImV4cCI6MjA2MjgxNzQyOH0.TBCN4icU22HJGHK6ka2_cQjA9tBQ-t3IMCPDstBdaUM')
        
        if not supabase_url or not supabase_key:
            logger.warning("Supabase credentials missing")
            return None
            
        return create_client(supabase_url, supabase_key)
    except Exception as e:
        logger.error(f"Failed to create Supabase client: {e}")
        return None

# Initialize Gemini API
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyBBw-VlqWekqnd_vPXCS7LSuKfrkbOro7s')
genai.configure(api_key=GEMINI_API_KEY)

# Create Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Add security headers
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

# Health endpoints that frontend expects
@app.route('/')
def health_check():
    return jsonify({"status": "ok", "service": "ai-service"})

@app.route('/api/health')
def api_health():
    return jsonify({"status": "ok", "service": "ai-service"})

# Main chat endpoint that frontend calls
@app.route('/api/chat', methods=['POST'])
def api_chat():
    """Chat endpoint that matches frontend expectations"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return jsonify({"error": "Message is required"}), 400
            
        # Use Gemini for response
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content(message)
        
        return jsonify({
            "response": response.text,
            "message": response.text,  # Frontend checks for both
            "status": "success"
        })
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({
            "error": "Internal server error",
            "message": "Sorry, I encountered an error while processing your request."
        }), 500

# Documents endpoint (placeholder)
@app.route('/api/documents')
def api_documents():
    return jsonify({"documents": [], "status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

