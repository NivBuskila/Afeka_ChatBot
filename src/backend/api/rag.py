from fastapi import APIRouter, HTTPException, Depends, Query, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging

from services.rag_service import RAGService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/rag", tags=["RAG"])

# Pydantic models
class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="שאילתת החיפוש")
    document_id: Optional[int] = Field(None, description="ID מסמך ספציפי לחיפוש")
    search_method: str = Field("hybrid", description="שיטת חיפוש: semantic, hybrid, contextual")
    max_results: Optional[int] = Field(8, ge=1, le=20, description="מספר תוצאות מקסימלי")

class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000, description="השאלה")
    document_id: Optional[int] = Field(None, description="ID מסמך ספציפי")
    search_method: str = Field("hybrid", description="שיטת חיפוש")
    include_sources: bool = Field(True, description="האם לכלול מקורות")

class ContextualSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    section_filter: Optional[str] = Field(None, description="סינון לפי סעיף")
    content_type_filter: Optional[str] = Field(None, description="סינון לפי סוג תוכן")

# Dependency injection
async def get_rag_service() -> RAGService:
    return RAGService()

@router.post("/search", 
             summary="חיפוש במסמכים", 
             description="ביצוע חיפוש סמנטי או היברידי במסמכים")
async def search_documents(
    request: SearchRequest,
    rag_service: RAGService = Depends(get_rag_service)
) -> JSONResponse:
    """חיפוש במסמכים באמצעות שיטות שונות"""
    try:
        logger.info(f"Search request: {request.query[:50]}... method: {request.search_method}")
        
        if request.search_method == "semantic":
            results = await rag_service.semantic_search(
                query=request.query,
                document_id=request.document_id,
                max_results=request.max_results
            )
        elif request.search_method == "contextual":
            results = await rag_service.contextual_search(
                query=request.query
            )
        else:  # hybrid (default)
            results = await rag_service.hybrid_search(
                query=request.query,
                document_id=request.document_id
            )
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "results": results,
                "total_results": len(results),
                "query": request.query,
                "search_method": request.search_method
            }
        )
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"שגיאה בחיפוש: {str(e)}"
        )

@router.post("/ask",
             summary="שאלה ותשובה RAG",
             description="שאילת שאלה וקבלת תשובה מבוססת על התקנונים")
async def ask_question(
    request: QuestionRequest,
    rag_service: RAGService = Depends(get_rag_service)
) -> JSONResponse:
    """מענה לשאלות באמצעות RAG"""
    try:
        logger.info(f"Question request: {request.question[:50]}...")
        
        answer_data = await rag_service.generate_answer(
            query=request.question,
            search_method=request.search_method,
            document_id=request.document_id
        )
        
        response_content = {
            "success": True,
            "answer": answer_data["answer"],
            "metadata": {
                "search_results_count": answer_data["search_results_count"],
                "response_time_ms": answer_data["response_time_ms"],
                "search_method": answer_data["search_method"]
            }
        }
        
        if request.include_sources:
            response_content["sources"] = answer_data["sources"]
        
        return JSONResponse(
            status_code=200,
            content=response_content
        )
        
    except Exception as e:
        logger.error(f"Question answering error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"שגיאה ביצירת תשובה: {str(e)}"
        )

@router.post("/contextual-search",
             summary="חיפוש מותנה",
             description="חיפוש עם סינונים ספציפיים")
async def contextual_search(
    request: ContextualSearchRequest,
    rag_service: RAGService = Depends(get_rag_service)
) -> JSONResponse:
    """חיפוש מותנה לפי הקשר"""
    try:
        results = await rag_service.contextual_search(
            query=request.query,
            section_filter=request.section_filter,
            content_type_filter=request.content_type_filter
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "results": results,
                "total_results": len(results),
                "filters": {
                    "section": request.section_filter,
                    "content_type": request.content_type_filter
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Contextual search error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"שגיאה בחיפוש מותנה: {str(e)}"
        )

@router.get("/test",
            summary="בדיקת חיפוש פשוט",
            description="בדיקה מהירה של מערכת החיפוש")
async def test_search(
    q: str = Query(..., description="שאילתת בדיקה"),
    method: str = Query("semantic", description="שיטת חיפוש"),
    rag_service: RAGService = Depends(get_rag_service)
) -> JSONResponse:
    """בדיקה מהירה של מערכת החיפוש"""
    try:
        if method == "semantic":
            results = await rag_service.semantic_search(q, max_results=3)
        else:
            results = await rag_service.hybrid_search(q)
        
        simplified_results = []
        for result in results:
            simplified_results.append({
                "id": result.get("id"),
                "similarity_score": result.get("similarity_score", result.get("combined_score")),
                "text_preview": result.get("chunk_text", "")[:100] + "...",
                "source": result.get("document_name", "לא ידוע")
            })
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "test_query": q,
                "method": method,
                "results_count": len(simplified_results),
                "results": simplified_results
            }
        )
        
    except Exception as e:
        logger.error(f"Test search error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"שגיאה בבדיקת החיפוש: {str(e)}"
        )

@router.get("/stats",
            summary="סטטיסטיקות חיפוש",
            description="קבלת נתונים סטטיסטיים על החיפושים")
async def get_search_statistics(
    days: int = Query(30, ge=1, le=365, description="מספר ימים אחורה"),
    rag_service: RAGService = Depends(get_rag_service)
) -> JSONResponse:
    """מחזיר סטטיסטיקות חיפוש"""
    try:
        stats = await rag_service.get_search_statistics(days)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "period_days": days,
                "statistics": stats
            }
        )
        
    except Exception as e:
        logger.error(f"Statistics error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"שגיאה בקבלת סטטיסטיקות: {str(e)}"
        )

@router.get("/health",
            summary="בדיקת בריאות RAG",
            description="בדיקה שהמערכת פעילה ותקינה")
async def health_check() -> JSONResponse:
    """בדיקת בריאות המערכת"""
    try:
        # בדיקה בסיסית שניתן ליצור שירות RAG
        rag_service = RAGService()
        
        # בדיקה שיש חיבור למסד נתונים
        response = rag_service.supabase.table("documents").select("count").limit(1).execute()
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "status": "healthy",
                "message": "מערכת RAG פעילה ותקינה",
                "database_connected": True
            }
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "success": False,
                "status": "unhealthy",
                "message": f"מערכת RAG לא תקינה: {str(e)}",
                "database_connected": False
            }
        ) 