import os
from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
from dotenv import load_dotenv
from typing import Dict, Any, List, Optional
import json
import logging
from supabase import create_client, Client
from fastapi.security import APIKeyHeader
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import time
import secrets
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Afeka ChatBot API",
    description="Backend API for Afeka College Regulations ChatBot",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Define allowed origins for CORS
ALLOWED_ORIGINS = os.environ.get(
    "ALLOWED_ORIGINS", 
    "http://localhost:5173,http://localhost:80,http://localhost,http://frontend:3000,http://frontend"
).split(",")

logger.info(f"Configured CORS with allowed origins: {ALLOWED_ORIGINS}")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-API-Key"],
    max_age=600  # 10 minutes cache for preflight requests
)

# Add trusted host middleware for production
if os.environ.get("ENV", "development") == "production":
    ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost").split(",")
    app.add_middleware(
        TrustedHostMiddleware, allowed_hosts=ALLOWED_HOSTS
    )
    logger.info(f"Added TrustedHostMiddleware with hosts: {ALLOWED_HOSTS}")

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

# Rate limiting setup
API_RATE_LIMIT = int(os.environ.get("API_RATE_LIMIT", "100"))  # Requests per minute
rate_limit_data = {}

# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Get client IP
    client_ip = request.client.host if request.client else "unknown"
    
    # Skip rate limiting for certain paths
    if request.url.path in ["/api/health", "/", "/api/docs", "/api/redoc", "/api/openapi.json"]:
        return await call_next(request)
    
    current_time = time.time()
    minute_window = int(current_time / 60)
    
    # Initialize or reset rate limit data for new minute window
    if client_ip not in rate_limit_data or rate_limit_data[client_ip]["window"] != minute_window:
        rate_limit_data[client_ip] = {"window": minute_window, "count": 0}
    
    # Increment request count for this IP
    rate_limit_data[client_ip]["count"] += 1
    
    # Check if rate limit exceeded
    if rate_limit_data[client_ip]["count"] > API_RATE_LIMIT:
        logger.warning(f"Rate limit exceeded for IP {client_ip}")
        return JSONResponse(
            status_code=429,
            content={"error": "Too many requests. Please try again later."}
        )
    
    # Add rate limit headers
    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(API_RATE_LIMIT)
    response.headers["X-RateLimit-Remaining"] = str(max(0, API_RATE_LIMIT - rate_limit_data[client_ip]["count"]))
    response.headers["X-RateLimit-Reset"] = str((minute_window + 1) * 60)
    
    return response

# Initialize Supabase client
try:
    supabase_url = os.environ.get("SUPABASE_URL", "https://wzvyibgtfwvmbfaybmqx.supabase.co")
    supabase_key = os.environ.get("SUPABASE_KEY")
    
    if not supabase_key:
        logger.warning("SUPABASE_KEY environment variable not set. Supabase features will not work.")
        supabase = None
    else:
        supabase: Client = create_client(supabase_url, supabase_key)
        logger.info("Supabase client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Supabase client: {e}")
    supabase = None

# AI Service configuration
AI_SERVICE_URL = os.environ.get("AI_SERVICE_URL", "http://localhost:5000")
logger.info(f"AI service URL set to: {AI_SERVICE_URL}")

# Security - API key for internal API calls
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Generate random API key if not in environment
INTERNAL_API_KEY = os.environ.get("INTERNAL_API_KEY", secrets.token_urlsafe(32))

# Input validation pattern for document IDs
ID_PATTERN = re.compile(r"^\d+$")

# Models
class ChatRequest(BaseModel):
    message: str
    user_id: str = "anonymous"

class ChatResponse(BaseModel):
    response: Dict[str, Any]

class Document(BaseModel):
    title: str
    content: str
    category: Optional[str] = None
    tags: Optional[List[str]] = None

@app.get("/")
async def root():
    """Root endpoint that confirms the API is running"""
    return {"message": "Afeka ChatBot API is running"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "ok"}

@app.post("/api/chat")
async def chat(request: Request):
    """
    Process chat messages - currently a placeholder for future RAG implementation
    
    Takes user message and returns a placeholder response
    """
    try:
        # Log request headers for debugging
        logger.info(f"Request headers: {request.headers.get('content-type', 'Not specified')}")
        
        # Parse incoming request body with explicit UTF-8 encoding
        try:
            body_bytes = await request.body()
            body_str = body_bytes.decode('utf-8', errors='replace')
            logger.info(f"Raw request body (first 100 chars): {body_str[:100]}...")
            
            import json
            body = json.loads(body_str)
        except Exception as json_err:
            logger.error(f"Error parsing JSON: {json_err}")
            # Fallback to default JSON parsing
            body = await request.json()
            
        user_message = body.get("message", "")
        
        if not user_message:
            raise HTTPException(status_code=400, detail="Message is required")
            
        # Validate message length
        if len(user_message) > 1000:
            raise HTTPException(status_code=400, detail="Message too long (max 1000 characters)")
            
        logger.info(f"Received chat request with message (length {len(user_message)}): {user_message[:50]}...")
        
        # Forward the request to the AI service if it's available
        try:
            async with httpx.AsyncClient() as client:
                logger.info(f"Sending to AI service: {user_message[:50]}...")
                
                # Prepare request with explicit encoding
                json_data = json.dumps({"message": user_message}, ensure_ascii=False)
                headers = {
                    "Content-Type": "application/json; charset=utf-8",
                    "Accept": "application/json; charset=utf-8"
                }
                
                response = await client.post(
                    f"{AI_SERVICE_URL}/chat",
                    content=json_data.encode('utf-8'),
                    headers=headers
                )
                
                logger.info(f"AI service response status: {response.status_code}")
                
                # Try to get response in different ways
                try:
                    response_json = response.json()
                except Exception as json_err:
                    logger.error(f"Error parsing AI service response as JSON: {json_err}")
                    # Try manual JSON parsing
                    response_text = response.text
                    logger.info(f"Raw AI response: {response_text[:100]}...")
                    
                    import json
                    response_json = json.loads(response_text)
                
                return JSONResponse(
                    content=response_json,
                    headers={"Content-Type": "application/json; charset=utf-8"}
                )
        except httpx.RequestError as e:
            logger.error(f"Error communicating with AI service: {e}")
            return JSONResponse(
                content={
                    "error": "AI service is currently unavailable",
                    "message": "This is a placeholder response. Future implementation will use RAG to query document knowledge base."
                },
                headers={"Content-Type": "application/json; charset=utf-8"}
            )
            
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in request: {e}")
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid JSON in request body"},
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
    except Exception as e:
        import traceback
        logger.error(f"Unexpected error in chat endpoint: {e}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "message": str(e)},
            headers={"Content-Type": "application/json; charset=utf-8"}
        )

@app.get("/api/documents")
async def get_documents():
    """
    Retrieve available documents from Supabase storage
    
    Returns a list of documents with their metadata
    """
    try:
        if not supabase:
            raise HTTPException(status_code=503, detail="Supabase connection not available")
        
        # Query documents from Supabase
        response = supabase.table('documents').select('*').execute()
        
        if hasattr(response, 'data'):
            logger.info(f"Retrieved {len(response.data)} documents from Supabase")
            return response.data
        else:
            logger.warning("No data returned from Supabase query")
            return []
            
    except Exception as e:
        logger.error(f"Error retrieving documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve documents")

@app.get("/api/documents/{document_id}")
async def get_document(document_id: str):
    """
    Retrieve a specific document by ID
    
    Args:
        document_id: The ID of the document to retrieve
        
    Returns:
        Document data including URL for download
    """
    try:
        # Validate document_id format for security
        if not ID_PATTERN.match(document_id):
            raise HTTPException(status_code=400, detail="Invalid document ID format")
            
        doc_id = int(document_id)
        
        if not supabase:
            raise HTTPException(status_code=503, detail="Supabase connection not available")
        
        # Query the specific document
        response = supabase.table('documents').select('*').eq('id', doc_id).execute()
        
        if not response.data or len(response.data) == 0:
            logger.warning(f"Document with ID {doc_id} not found")
            raise HTTPException(status_code=404, detail="Document not found")
            
        logger.info(f"Retrieved document with ID {doc_id}")
        return response.data[0]
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document ID format")
    except Exception as e:
        logger.error(f"Error retrieving document {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve document")

@app.post("/api/documents", status_code=201)
async def create_document(document: Document, api_key: str = Depends(api_key_header)):
    """
    Create a new document in Supabase
    
    Requires API key for authentication
    """
    # Validate API key
    if api_key != INTERNAL_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key",
            headers={"WWW-Authenticate": "APIKey"}
        )
        
    try:
        if not supabase:
            raise HTTPException(status_code=503, detail="Supabase connection not available")
            
        # Validate document length
        if len(document.content) > 100000:
            raise HTTPException(status_code=400, detail="Document content too large (max 100KB)")
            
        # Create document in Supabase
        doc_data = document.model_dump()
        doc_data["created_at"] = "now()"
        
        response = supabase.table('documents').insert(doc_data).execute()
            
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create document")
            
        logger.info(f"Created new document: {document.title}")
        return {"success": True, "id": response.data[0]["id"], "message": "Document created successfully"}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create document")

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True) 