from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.services.chat_service import ChatService
from app.schemas.chat_session import (
    ChatSessionCreate,
    ChatSessionResponse,
    ChatSessionListResponse
)
from app.dependencies import get_chat_service

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/sessions", response_model=ChatSessionResponse)
async def create_chat_session(
    session_data: ChatSessionCreate,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Create a new chat session"""
    try:
        session = await chat_service.create_session(session_data)
        return ChatSessionResponse.from_domain(session)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/sessions", response_model=ChatSessionListResponse)
async def get_user_sessions(
    user_id: str,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Get all sessions for a user"""
    sessions = await chat_service.get_user_sessions(user_id)
    return ChatSessionListResponse(
        sessions=[ChatSessionResponse.from_domain(s) for s in sessions],
        total=len(sessions)
    )