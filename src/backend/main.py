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
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables - force reload from .env file in current directory
load_dotenv(override=True)

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
    "http://localhost:5173,http://localhost:80,http://localhost,http://frontend:3000,http://frontend,http://192.168.56.1:5173,http://172.16.16.179:5173,http://172.20.224.1:5173"
).split(",")

logger.info(f"Configured CORS with allowed origins: {ALLOWED_ORIGINS}")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
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
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

    logger.info(f"SUPABASE_URL exists: {SUPABASE_URL is not None}")
    logger.info(f"SUPABASE_KEY exists: {SUPABASE_KEY is not None}")
    
    # Print the values for debugging (Be sure to remove/redact in production)
    logger.info(f"SUPABASE_URL value first 20 chars: {SUPABASE_URL[:20] if SUPABASE_URL else 'None'}")
    logger.info(f"AI_SERVICE_URL from env: {os.environ.get('AI_SERVICE_URL')}")

    if SUPABASE_URL and SUPABASE_KEY:
        try:
            # הסרת פרמטר ה-proxy שגורם לשגיאה
            supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            supabase_client = None
    else:
        logger.warning("SUPABASE_KEY or SUPABASE_URL not set, Supabase features will not work")
        supabase_client = None
except Exception as e:
    logger.error(f"Failed to initialize Supabase client: {e}")
    supabase_client = None

# AI Service configuration
AI_SERVICE_URL = "http://localhost:5000"  # Force localhost for local development
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
    # Also check Supabase connection
    supabase_status = "connected" if supabase_client else "disconnected"
    return {"status": "ok", "supabase": supabase_status}

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
        if not supabase_client:
            raise HTTPException(status_code=503, detail="Supabase connection not available")
        
        # Query documents from Supabase
        response = supabase_client.table('documents').select('*').execute()
        
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
        
        if not supabase_client:
            raise HTTPException(status_code=503, detail="Supabase connection not available")
        
        # Query the specific document
        response = supabase_client.table('documents').select('*').eq('id', doc_id).execute()
        
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
        if not supabase_client:
            raise HTTPException(status_code=503, detail="Supabase connection not available")
            
        # Validate document length
        if len(document.content) > 100000:
            raise HTTPException(status_code=400, detail="Document content too large (max 100KB)")
            
        # Create document in Supabase
        doc_data = document.model_dump()
        doc_data["created_at"] = "now()"
        
        response = supabase_client.table('documents').insert(doc_data).execute()
            
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

# Proxy routes for Supabase
@app.post("/api/proxy/chat_sessions")
async def proxy_create_chat_session(request: Request):
    """Proxy endpoint for creating chat sessions"""
    if not supabase_client:
        raise HTTPException(status_code=503, detail="Supabase connection not available")
    
    try:
        body = await request.json()
        result = supabase_client.table("chat_sessions").insert(body).execute()
        
        # Also create a corresponding conversation record if needed
        if result.data:
            conversation_data = {
                "conversation_id": result.data[0]["id"],
                "user_id": body.get("user_id"),
                "title": body.get("title"),
                "created_at": body.get("created_at", result.data[0].get("created_at")),
                "updated_at": body.get("updated_at", result.data[0].get("updated_at")),
                "is_active": True
            }
            
            supabase_client.table("conversations").insert(conversation_data).execute()
            
        return JSONResponse(content=result.data)
    except Exception as e:
        logger.error(f"Error proxying chat session creation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/proxy/chat_sessions")
async def proxy_get_chat_sessions(user_id: str, request: Request):
    """Proxy endpoint for getting chat sessions"""
    if not supabase_client:
        raise HTTPException(status_code=503, detail="Supabase connection not available")
    
    try:
        result = supabase_client.table("chat_sessions").select("*").eq("user_id", user_id).order("updated_at", desc=True).execute()
        return JSONResponse(content=result.data)
    except Exception as e:
        logger.error(f"Error proxying chat sessions retrieval: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/proxy/chat_sessions/{session_id}")
async def proxy_get_chat_session(session_id: str, request: Request):
    """Proxy endpoint for getting a specific chat session"""
    if not supabase_client:
        raise HTTPException(status_code=503, detail="Supabase connection not available")
    
    try:
        # Get the session
        session_result = supabase_client.table("chat_sessions").select("*").eq("id", session_id).single().execute()
        
        if not session_result.data:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        # Get messages for this session
        messages_result = supabase_client.table("messages").select("*").eq("conversation_id", session_id).order("created_at").execute()
        
        # Combine the data
        result = {
            **session_result.data,
            "messages": messages_result.data or []
        }
        
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error proxying chat session retrieval: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/proxy/messages")
async def proxy_create_message(request: Request):
    """Proxy endpoint for creating messages"""
    if not supabase_client:
        raise HTTPException(status_code=503, detail="Supabase connection not available")
    
    try:
        body = await request.json()
        result = supabase_client.table("messages").insert(body).execute()
        return JSONResponse(content=result.data)
    except Exception as e:
        logger.error(f"Error proxying message creation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/proxy/documents")
async def proxy_get_documents(request: Request):
    """Proxy endpoint for retrieving documents"""
    if not supabase_client:
        raise HTTPException(status_code=503, detail="Supabase connection not available")
    
    try:
        result = supabase_client.table("documents").select("*").order("created_at", desc=True).execute()
        return JSONResponse(content=result.data)
    except Exception as e:
        logger.error(f"Error proxying documents retrieval: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/proxy/documents/{document_id}")
async def proxy_get_document(document_id: int, request: Request):
    """Proxy endpoint for retrieving a specific document"""
    if not supabase_client:
        raise HTTPException(status_code=503, detail="Supabase connection not available")
    
    try:
        result = supabase_client.table("documents").select("*").eq("id", document_id).single().execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Document not found")
        return JSONResponse(content=result.data)
    except Exception as e:
        logger.error(f"Error proxying document retrieval: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/proxy/documents")
async def proxy_create_document(request: Request):
    """Proxy endpoint for creating documents"""
    if not supabase_client:
        raise HTTPException(status_code=503, detail="Supabase connection not available")
    
    try:
        body = await request.json()
        # Use RPC function if it exists, otherwise fall back to direct insert
        try:
            result = supabase_client.rpc("create_document", {
                "name": body.get("name"),
                "type": body.get("type"),
                "size": body.get("size"),
                "url": body.get("url"),
                "user_id": body.get("user_id")
            }).execute()
            
            # Get the newly created document
            if result.data:
                doc_result = supabase_client.table("documents").select("*").eq("id", result.data).single().execute()
                return JSONResponse(content=doc_result.data)
            else:
                raise HTTPException(status_code=500, detail="Document creation failed")
        except Exception as rpc_err:
            logger.warning(f"RPC method failed, falling back to direct insert: {rpc_err}")
            result = supabase_client.table("documents").insert(body).execute()
            return JSONResponse(content=result.data[0] if result.data else None)
    except Exception as e:
        logger.error(f"Error proxying document creation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/proxy/documents/{document_id}")
async def proxy_delete_document(document_id: int, request: Request):
    """Proxy endpoint for deleting documents"""
    if not supabase_client:
        raise HTTPException(status_code=503, detail="Supabase connection not available")
    
    try:
        # Get document info before deletion
        doc_result = supabase_client.table("documents").select("*").eq("id", document_id).single().execute()
        if not doc_result.data:
            raise HTTPException(status_code=404, detail="Document not found")
            
        # Delete from database
        result = supabase_client.table("documents").delete().eq("id", document_id).execute()
        
        # Try to delete from storage if URL exists
        if doc_result.data.get("url"):
            try:
                url = doc_result.data.get("url")
                
                # Extract storage path from URL
                # This is a simplified version - we might need more complex logic based on URL format
                parts = url.split("/")
                filename = parts[-1].split("?")[0]
                
                # Try to delete the file - silently fail if it doesn't work
                supabase_client.storage.from_("documents").remove([filename])
            except Exception as storage_err:
                logger.warning(f"Failed to delete file from storage: {storage_err}")
                
        return JSONResponse(content={"success": True})
    except Exception as e:
        logger.error(f"Error proxying document deletion: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/api/proxy/chat_session/{session_id}")
async def proxy_update_chat_session(session_id: str, request: Request):
    """Proxy endpoint for updating a chat session"""
    if not supabase_client:
        raise HTTPException(status_code=503, detail="Supabase connection not available")
    
    try:
        body = await request.json()
        
        # Ensure we have the updated timestamp
        if 'updated_at' not in body:
            body['updated_at'] = datetime.now().isoformat()
            
        result = supabase_client.table("chat_sessions").update(body).eq("id", session_id).execute()
        
        # Also update conversation if it exists
        try:
            conversation_update = {
                'updated_at': body.get('updated_at'),
                'last_message_at': body.get('updated_at')
            }
            if 'title' in body:
                conversation_update['title'] = body['title']
                
            supabase_client.table("conversations").update(conversation_update).eq("conversation_id", session_id).execute()
        except Exception as conv_err:
            logger.warning(f"Error updating conversation: {conv_err}")
        
        return JSONResponse(content={"success": True, "data": result.data})
    except Exception as e:
        logger.error(f"Error proxying chat session update: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/api/proxy/chat_sessions/{session_id}")
async def proxy_update_chat_sessions_plural(session_id: str, request: Request):
    """Alias for proxy_update_chat_session to maintain backwards compatibility"""
    return await proxy_update_chat_session(session_id, request)

@app.get("/api/proxy/messages_schema")
async def proxy_get_messages_schema(request: Request):
    """Proxy endpoint for getting the message table schema"""
    if not supabase_client:
        raise HTTPException(status_code=503, detail="Supabase connection not available")
    
    try:
        # Get a single message to determine schema
        result = supabase_client.table("messages").select("*").limit(1).execute()
        
        if not result.data or len(result.data) == 0:
            # Create a dummy message with all possible fields
            dummy_schema = {
                "message_id": 0,
                "conversation_id": "",
                "user_id": "",
                "request": "",
                "response": "",
                "created_at": "",
                "status": "",
                "status_updated_at": "",
                "error_message": "",
                "request_type": "",
                "request_payload": {},
                "response_payload": {},
                "status_code": 0,
                "processing_start_time": "",
                "processing_end_time": "",
                "processing_time_ms": 0,
                "is_sensitive": False,
                "metadata": {},
                "chat_session_id": ""
            }
            return JSONResponse(content={"columns": list(dummy_schema.keys())})
        
        # Return the column names
        columns = list(result.data[0].keys())
        return JSONResponse(content={"columns": columns})
    except Exception as e:
        logger.error(f"Error proxying message schema retrieval: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/proxy/message")
async def proxy_update_message(request: Request):
    """Proxy endpoint for adding a message with custom ID"""
    if not supabase_client:
        raise HTTPException(status_code=503, detail="Supabase connection not available")
    
    try:
        # קריאת גוף הבקשה ורישום לוג
        body_bytes = await request.body()
        body_str = body_bytes.decode('utf-8', errors='replace')
        logger.info(f"Raw message request body: {body_str[:200]}...")
        
        try:
            body = json.loads(body_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON body: {e}")
            return JSONResponse(
                status_code=400, 
                content={"error": f"Invalid JSON in request body: {str(e)}"}
            )
        
        logger.info(f"Parsed message data: {str(body)[:200]}...")
        
        # וידוי שהשדות הנדרשים קיימים
        required_fields = ["user_id", "conversation_id"]
        missing_fields = [field for field in required_fields if not body.get(field)]
        
        if missing_fields:
            logger.error(f"Missing required fields: {missing_fields}")
            return JSONResponse(
                status_code=400,
                content={"error": f"Missing required fields: {', '.join(missing_fields)}"}
            )
        
        # Generate ID if not provided
        if 'message_id' not in body and 'id' not in body:
            # Generate timestamp-based numeric ID
            import time
            import random
            body['message_id'] = int(time.time() * 1000) * 1000 + random.randint(0, 999)
        
        # Ensure created_at is set
        if 'created_at' not in body:
            body['created_at'] = datetime.now().isoformat()
            
        # נקה שדות null, undefined או ריקים
        cleaned_body = {}
        for key, value in body.items():
            if value is not None and value != "" and key != "":
                # המר ערכי JSON לפי הצורך
                if key in ['request_payload', 'response_payload', 'metadata'] and isinstance(value, dict):
                    try:
                        cleaned_body[key] = json.dumps(value)
                    except Exception as e:
                        logger.warning(f"Could not serialize JSON field {key}: {e}")
                        # השתמש בערך מקורי אם ההמרה נכשלת
                        cleaned_body[key] = str(value)
                else:
                    cleaned_body[key] = value
        
        # וידוא שהמזהים הם מחרוזות, הערכים שאינם מחרוזות יומרו
        if 'conversation_id' in cleaned_body and not isinstance(cleaned_body['conversation_id'], str):
            cleaned_body['conversation_id'] = str(cleaned_body['conversation_id'])
            
        if 'user_id' in cleaned_body and not isinstance(cleaned_body['user_id'], str):
            cleaned_body['user_id'] = str(cleaned_body['user_id'])
        
        logger.info(f"Cleaned message data for insert: {str(cleaned_body)[:200]}...")
        
        try:
            # נסה להוסיף את ההודעה לטבלה
            result = supabase_client.table("messages").insert(cleaned_body).execute()
            
            if hasattr(result, 'data') and result.data:
                logger.info(f"Message insert success, returned data: {str(result.data)[:200]}...")
                # החזר את הנתונים כפי שהוחזרו מסופאבייס
                return JSONResponse(content=result.data[0])
            else:
                # אם אין נתונים בתשובה, החזר את המזהה והזמן שיצרנו
                logger.warning("No data returned from message insert")
                response_data = {
                    "id": cleaned_body.get('message_id', cleaned_body.get('id', 'unknown')),
                    "created_at": cleaned_body.get('created_at', datetime.now().isoformat()),
                    "conversation_id": cleaned_body.get('conversation_id', ""),
                    "user_id": cleaned_body.get('user_id', "")
                }
                logger.info(f"Generating fallback response: {response_data}")
                return JSONResponse(content=response_data)
        except Exception as insert_err:
            # רישום כל הפרטים של שגיאת ההוספה לבסיס הנתונים
            logger.error(f"Database insertion error: {insert_err}", exc_info=True)
            # בדוק אם זו שגיאת דופליקט
            error_str = str(insert_err).lower()
            if "duplicate" in error_str or "unique constraint" in error_str:
                return JSONResponse(
                    status_code=409,
                    content={"error": "Message ID already exists", "detail": str(insert_err)}
                )
            # החזר שגיאה מפורטת
            return JSONResponse(
                status_code=500,
                content={"error": "Database error", "detail": str(insert_err)}
            )
            
    except Exception as e:
        # רישום כל הפרטים של השגיאה הכללית
        logger.error(f"Error proxying message creation: {e}", exc_info=True)
        # החזר שגיאה מובנת יותר למשתמש
        return JSONResponse(
            status_code=500, 
            content={"error": "Internal server error", "detail": str(e)}
        )

@app.get("/api/proxy/search_chat_sessions")
async def proxy_search_chat_sessions(user_id: str, search_term: str, request: Request):
    """Proxy endpoint for searching chat sessions"""
    if not supabase_client:
        raise HTTPException(status_code=503, detail="Supabase connection not available")
    
    try:
        # First search for chat sessions with matching titles
        title_result = supabase_client.table("chat_sessions").select("*").eq("user_id", user_id).ilike("title", f"%{search_term}%").execute()
        
        # Then search for messages with matching content in request or response fields
        message_result = supabase_client.table("messages").select("conversation_id").eq("user_id", user_id).or_(f"request.ilike.%{search_term}%,response.ilike.%{search_term}%").execute()
        
        # Get unique session IDs from message matches
        session_ids = []
        if message_result.data:
            session_ids = list(set([msg.get("conversation_id") for msg in message_result.data]))
        
        # If we have matching session IDs from messages, fetch those sessions
        content_match_sessions = []
        if session_ids:
            content_result = supabase_client.table("chat_sessions").select("*").eq("user_id", user_id).in_("id", session_ids).execute()
            content_match_sessions = content_result.data or []
        
        # Combine and deduplicate results
        all_sessions = title_result.data + content_match_sessions if title_result.data else content_match_sessions
        
        # Remove duplicates by creating a dictionary with session ID as key
        unique_sessions = {}
        for session in all_sessions:
            if session.get("id") not in unique_sessions:
                unique_sessions[session.get("id")] = session
        
        # Convert back to a list and sort by updated_at (newest first)
        result = list(unique_sessions.values())
        result.sort(key=lambda x: x.get("updated_at", x.get("created_at", "")), reverse=True)
        
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error searching chat sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/proxy/chat_session/{session_id}")
async def proxy_delete_chat_session(session_id: str, request: Request):
    """Proxy endpoint for deleting a chat session"""
    if not supabase_client:
        raise HTTPException(status_code=503, detail="Supabase connection not available")
    
    try:
        # First delete all messages in the session
        messages_result = supabase_client.table("messages").delete().eq("conversation_id", session_id).execute()
        
        # Delete the conversation record if it exists
        try:
            conversation_result = supabase_client.table("conversations").delete().eq("conversation_id", session_id).execute()
        except Exception as conv_err:
            logger.warning(f"Error deleting conversation: {conv_err}")
        
        # Then delete the session itself
        session_result = supabase_client.table("chat_sessions").delete().eq("id", session_id).execute()
        
        return JSONResponse(content={"success": True})
    except Exception as e:
        logger.error(f"Error deleting chat session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True) 