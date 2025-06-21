"""
Afeka ChatBot API - Main Application Entry Point

A clean, production-ready FastAPI application for the Afeka ChatBot system.
Uses modular architecture with separate routers and services.
"""

# Load environment variables FIRST before any other imports
from dotenv import load_dotenv
from pathlib import Path

# Load .env from project root (two levels up from this file)
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

import os
import sys
import logging
import uvicorn
import threading
import asyncio
from pathlib import Path
from contextlib import asynccontextmanager

# Add project root to path for proper imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the new modular application
from src.backend.app.core.app import create_application

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Background document processor
def background_document_processor():
    """Run document processor in background thread"""
    import asyncio
    try:
        # Create new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Import and run processor with 30 second intervals
        from src.ai.scripts.auto_process_documents import run_processor
        loop.run_until_complete(run_processor(interval=30))
    except Exception as e:
        logger.error(f"Background document processor error: {e}")
    finally:
        try:
            loop.close()
        except:
            pass

@asynccontextmanager
async def lifespan(app):
    """Application lifespan manager for startup and shutdown events"""
    # Startup
    logger.info("🚀 Starting Afeka ChatBot API...")
    
    # Initialize background document processing service
    try:
        logger.info("📄 Starting automatic document processing service...")
        
        # Start processor in daemon thread
        processor_thread = threading.Thread(target=background_document_processor, daemon=True)
        processor_thread.start()
        logger.info("✅ Document processor thread started successfully")
        
    except Exception as e:
        logger.warning(f"⚠️ Background document processor initialization warning: {e}")
    
    logger.info("✅ Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Afeka ChatBot API...")
    logger.info("✅ Application shutdown complete")

# Create the FastAPI application using the modular factory
app = create_application(lifespan=lifespan)

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Simple health check endpoint"""
    return {
        "status": "healthy",
        "service": "Afeka ChatBot API",
        "version": "2.0.0"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint confirming API is running"""
    return {
        "message": "Afeka ChatBot API is running",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }

# Run the application
if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"🌟 Starting server on {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=os.getenv("RELOAD", "false").lower() == "true",
        log_level="info"
    ) 