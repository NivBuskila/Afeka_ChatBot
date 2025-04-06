from fastapi import APIRouter

router = APIRouter()

@router.get("/", tags=["General"])
async def root():
    """Root endpoint that confirms the API is running"""
    return {"message": "Afeka ChatBot API is running"}

@router.get("/api/health", tags=["General"])
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "ok"} 