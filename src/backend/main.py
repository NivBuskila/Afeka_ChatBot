# app/main.py
"""Main application entry point - Clean Architecture"""

from app.create_app import create_application, init_dependencies

# Create application
app = create_application()

# Initialize dependencies
init_dependencies(app)

# For running with uvicorn
if __name__ == "__main__":
    import uvicorn
    from app.config import settings
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level="info" if settings.is_development else "warning"
    )