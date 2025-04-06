import logging
import os
from flask import Flask

# Import config and blueprints using absolute paths
from ai.core import config
from ai.api.routes import api_bp

# Configure logging (could also be done within create_app)
logging.basicConfig(
    level=logging.INFO if not config.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Application Factory Function"""
    app = Flask(__name__)
    
    # Load configuration from config object (optional, can access config directly)
    # app.config.from_object(config)
    logger.info(f"Creating Flask app in {config.ENVIRONMENT} mode (Debug: {config.DEBUG})")

    # Register Blueprints
    app.register_blueprint(api_bp) 
    logger.info("Registered API blueprint")

    # Add security headers (can also be done with middleware like Talisman)
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        # Consider a stricter CSP if possible
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        if config.ENVIRONMENT == 'production':
             response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response

    # --- Add other middleware here if needed (e.g., CORS, Rate Limiting) ---
    # Example: from flask_cors import CORS
    # CORS(app) 
    # Example: from flask_limiter import Limiter
    # from flask_limiter.util import get_remote_address
    # limiter = Limiter(get_remote_address, app=app, default_limits=["..."])
    # -----------------------------------------------------------------------

    # Add global error handlers if needed
    # @app.errorhandler(404)
    # def not_found(error):
    #    return jsonify({"error": "Not Found"}), 404
    
    # @app.errorhandler(500)
    # def internal_error(error):
    #    logger.error(f"Server Error: {error}")
    #    return jsonify({"error": "Internal Server Error"}), 500

    return app

# Entry point for running the app directly (e.g., python -m src.ai.app)
# Or using a WSGI server like Gunicorn: gunicorn "src.ai.app:create_app()"
if __name__ == '__main__':
    app = create_app()
    logger.info(f"Starting AI service directly via __main__ on http://{config.HOST}:{config.PORT}")
    # Use debug=config.DEBUG for development reloading
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG) 