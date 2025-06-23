"""
Afeka ChatBot API - Main Application Entry Point

A clean, production-ready FastAPI application for the Afeka ChatBot system.
Uses modular architecture with separate routers and services.
"""

from dotenv import load_dotenv
from pathlib import Path

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

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.backend.app.core.app import create_application

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def background_document_processor():
    """Run document processor in background thread"""
    import asyncio
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
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
    logger.info("Starting Afeka ChatBot API...")
    
    try:
        logger.info("Starting automatic document processing service...")
        
        processor_thread = threading.Thread(target=background_document_processor, daemon=True)
        processor_thread.start()
        logger.info("Document processor thread started successfully")
        
    except Exception as e:
        logger.warning(f"Background document processor initialization warning: {e}")
    
    logger.info("Application startup complete")
    
    yield
    
    logger.info("Shutting down Afeka ChatBot API...")
    logger.info("Application shutdown complete")

app = create_application(lifespan=lifespan)

@app.get("/api/health")
async def health_check():
    """Simple health check endpoint"""
    return {
        "status": "healthy",
        "service": "Afeka ChatBot API",
        "version": "2.0.0"
    }

@app.get("/")
async def root():
    """Root endpoint confirming API is running"""
    return {
        "message": "Afeka ChatBot API is running",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"Starting server on {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=os.getenv("RELOAD", "false").lower() == "true",
        log_level="info"
    )