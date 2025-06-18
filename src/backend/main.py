"""
Afeka ChatBot API - Main Application Entry Point

A clean, production-ready FastAPI application for the Afeka ChatBot system.
Uses modular architecture with separate routers and services.
"""

# Load environment variables FIRST before any other imports
from dotenv import load_dotenv
load_dotenv()

import os
import sys
import logging
import uvicorn
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

# Background task for document processing
def run_document_processor():
    """Background task for automatic document processing"""
    try:
        from src.ai.scripts.auto_process_documents import process_all_documents
        process_all_documents()
        logger.info("✅ Document processor completed successfully")
    except Exception as e:
        logger.error(f"❌ Document processor failed: {e}")

@asynccontextmanager
async def lifespan(app):
    """Application lifespan manager for startup and shutdown events"""
    # Startup
    logger.info("🚀 Starting Afeka ChatBot API...")
    
    # Initialize background services
    # try:
    #     # Always start document processor for development
    #     logger.info("📄 Starting automatic document processing...")
    #     
    #     # Import and start the background processor
    #     import threading
    #     from src.ai.scripts.auto_process_documents import run_processor
    #     
    #     def background_processor():
    #         """Run document processor in background thread"""
    #         import asyncio
    #         try:
    #             # Create new event loop for this thread
    #             loop = asyncio.new_event_loop()
    #             asyncio.set_event_loop(loop)
    #             
    #             # Run processor with 30 second intervals
    #             loop.run_until_complete(run_processor(interval=30))
    #         except Exception as e:
    #             logger.error(f"Background processor error: {e}")
    #     
    #     # Start processor in daemon thread
    #     processor_thread = threading.Thread(target=background_processor, daemon=True)
    #     processor_thread.start()
    #     logger.info("✅ Document processor thread started")
    #     
    # except Exception as e:
    #     logger.warning(f"⚠️ Background service initialization warning: {e}")
    
    # Skip background services for now to avoid threading issues
    logger.info("📄 Background document processing disabled for performance optimization")
    
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