from flask import Flask, request, jsonify, Response
import nltk
import os
import logging
import traceback
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import json
import time
from functools import wraps
import secrets
import threading
import re

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

# Security settings
INTERNAL_API_KEY = os.environ.get('INTERNAL_API_KEY', secrets.token_urlsafe(32))
API_KEY_HEADER = 'X-API-Key'
TRUSTED_PROXIES = os.environ.get('TRUSTED_PROXIES', '127.0.0.1').split(',')

# Rate limiting
ip_rate_limits = {}
rate_limit_lock = threading.Lock()

# Input validation - prevent potential code injection or command injection
UNSAFE_PATTERN = re.compile(r'[;<>`|&$]')

# Download NLTK resources on startup
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    logger.info("NLTK resources downloaded successfully")
except Exception as e:
    logger.error(f"Failed to download NLTK resources: {e}")

# Load keyword mapping from file
try:
    with open('keywords.json', 'r', encoding='utf-8') as file:
        KEYWORD_MAPPING = json.load(file)
    logger.info(f"Loaded {len(KEYWORD_MAPPING)} keyword mappings")
except FileNotFoundError:
    logger.error("keywords.json file not found. Using empty mapping.")
    KEYWORD_MAPPING = {}
except json.JSONDecodeError:
    logger.error("Invalid JSON in keywords.json file. Using empty mapping.")
    KEYWORD_MAPPING = {}
except Exception as e:
    logger.error(f"Error loading keywords.json: {e}")
    KEYWORD_MAPPING = {}

# Security decorator for internal API endpoints
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get(API_KEY_HEADER)
        if app.debug:  # Bypass in debug mode but log it
            if api_key != INTERNAL_API_KEY:
                logger.warning("API key validation bypassed in debug mode")
            return f(*args, **kwargs)
            
        if api_key != INTERNAL_API_KEY:
            logger.warning(f"Unauthorized API request blocked")
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function

# Rate limiting decorator
def rate_limit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip rate limiting in debug mode
        if app.debug:
            return f(*args, **kwargs)
            
        # Get client IP
        client_ip = request.remote_addr
        
        # For better accuracy in production, handle proxy
        if request.headers.get('X-Forwarded-For') and request.remote_addr in TRUSTED_PROXIES:
            client_ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
        
        current_time = int(time.time())
        current_minute = current_time // 60
        
        with rate_limit_lock:
            # Reset rate limit for new time window
            if client_ip not in ip_rate_limits or ip_rate_limits[client_ip]['window'] != current_minute:
                ip_rate_limits[client_ip] = {'window': current_minute, 'count': 1}
            else:
                ip_rate_limits[client_ip]['count'] += 1
                
            request_count = ip_rate_limits[client_ip]['count']
            
        # Return 429 if rate limit exceeded
        if request_count > API_RATE_LIMIT:
            logger.warning(f"Rate limit exceeded for IP {client_ip}: {request_count} requests in minute window")
            response = jsonify({
                'error': 'Too many requests, please try again later.',
                'retry_after': 60 - (current_time % 60)
            })
            response.status_code = 429
            response.headers['Retry-After'] = str(60 - (current_time % 60))
            return response
            
        # Add rate limit headers
        response = f(*args, **kwargs)
        if isinstance(response, tuple):
            response_obj, status_code = response
            response = Response(json.dumps(response_obj), status=status_code, mimetype='application/json')
        elif not isinstance(response, Response):
            response = Response(response, mimetype='application/json')
            
        response.headers['X-RateLimit-Limit'] = str(API_RATE_LIMIT)
        response.headers['X-RateLimit-Remaining'] = str(max(0, API_RATE_LIMIT - request_count))
        response.headers['X-RateLimit-Reset'] = str((current_minute + 1) * 60)
        
        return response
    return decorated_function

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
@rate_limit
def chat():
    """
    Process chat messages and return AI-generated responses
    
    Extracts keywords from the input, matches them against predefined rules,
    and returns relevant information along with sentiment analysis
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
        
        # Check for potentially dangerous content
        if UNSAFE_PATTERN.search(user_message):
            logger.warning(f"Potentially unsafe input detected")
            return jsonify({
                "error": "Input contains invalid characters"
            }), 400
                
        logger.info(f"Received message: {user_message[:30]}...")
        
        # Process the message
        result = process_message(user_message)
        
        # Add processing time for monitoring
        processing_time = time.time() - request_start_time
        result['processing_time'] = round(processing_time, 3)
        
        logger.info(f"Message processed successfully in {processing_time:.3f}s")
        return jsonify(result)
        
    except json.JSONDecodeError:
        logger.error("Failed to decode JSON request")
        return jsonify({
            "error": "Invalid JSON in request body"
        }), 400
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": "Internal server error"
        }), 500

# Admin endpoint for diagnostics - requires API key
@app.route('/admin/stats', methods=['GET'])
@require_api_key
def get_stats():
    """Get system statistics (protected endpoint)"""
    return jsonify({
        "keywords_loaded": len(KEYWORD_MAPPING),
        "rate_limits": {ip: data for ip, data in ip_rate_limits.items()},
        "memory_usage_mb": get_memory_usage(),
        "uptime_seconds": time.time() - app.start_time
    })

def get_memory_usage():
    """Get current memory usage in MB"""
    try:
        import psutil
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
    except ImportError:
        return -1  # psutil not available

def process_message(message):
    """
    Process a user message and generate a response
    
    Args:
        message (str): The user's message text
        
    Returns:
        dict: Response containing keywords, result text, and sentiment
    """
    # Extract keywords from message
    keywords = extract_keywords(message)
    
    # Generate response based on keywords
    response_text = generate_response(keywords, message)
    
    # Analyze sentiment (simplified)
    sentiment = analyze_sentiment(message)
    
    return {
        "keywords": keywords,
        "result": response_text,
        "sentiment": sentiment
    }

def extract_keywords(text):
    """
    Extract important keywords from text
    
    Uses NLTK for tokenization and removes stopwords to identify key terms
    
    Args:
        text (str): Text to extract keywords from
        
    Returns:
        list: List of extracted keywords
    """
    try:
        # Tokenize the text
        tokens = word_tokenize(text.lower())
        
        # Remove stopwords (in multiple languages)
        stop_words = set(stopwords.words('english') + stopwords.words('hebrew'))
        keywords = [word for word in tokens if word.isalnum() and word not in stop_words]
        
        # Return unique keywords
        return list(set(keywords))
        
    except Exception as e:
        logger.error(f"Error extracting keywords: {e}")
        return []

def generate_response(keywords, original_message):
    """
    Generate a response based on extracted keywords
    
    Args:
        keywords (list): Extracted keywords from the message
        original_message (str): The original user message
        
    Returns:
        str: Generated response text
    """
    # Check for keyword matches in our mapping
    for keyword in keywords:
        if keyword in KEYWORD_MAPPING:
            return KEYWORD_MAPPING[keyword]
    
    # Default response if no keywords match
    return "I couldn't find specific information about that. Please try rephrasing your question or ask about admissions, courses, or academic policies."

def analyze_sentiment(text):
    """
    Simple sentiment analysis for the message
    
    Args:
        text (str): Text to analyze
        
    Returns:
        str: Sentiment classification (positive, negative, or neutral)
    """
    # Simple keyword-based sentiment analysis
    # In a production system, this would use a proper ML model
    positive_words = {"good", "great", "excellent", "helpful", "thanks", "thank"}
    negative_words = {"bad", "terrible", "awful", "useless", "problem", "issue", "not"}
    
    text_lower = text.lower()
    words = set(word_tokenize(text_lower))
    
    pos_matches = len(words.intersection(positive_words))
    neg_matches = len(words.intersection(negative_words))
    
    if pos_matches > neg_matches:
        return "positive"
    elif neg_matches > pos_matches:
        return "negative"
    else:
        return "neutral"

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
        # Additional security options
        threaded=True,
        ssl_context=None  # Set to appropriate cert in production
    ) 