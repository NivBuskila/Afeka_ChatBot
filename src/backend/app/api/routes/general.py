from fastapi import APIRouter

router = APIRouter(tags=["General"])

@router.get("/")
async def root():
    """Root endpoint that confirms the API is running"""
    return {"message": "Afeka ChatBot API is running"}

@router.get("/api/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "ok"}