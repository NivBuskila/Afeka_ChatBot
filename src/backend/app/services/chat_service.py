import logging
import json
import sys
from typing import Dict, Any, List, Optional
from fastapi import HTTPException
from pathlib import Path

# Add the backend directory to sys.path to allow importing from services
backend_dir = Path(__file__).parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from ..core.interfaces import IChatService
from ..config.settings import settings
from ..domain.models import ChatMessageHistoryItem
from src.ai.services.rag_service import RAGService  # Import the new RAG service
from src.ai.services.document_processor import DocumentProcessor  # Import from ai/services

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationChain
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

logger = logging.getLogger(__name__)

class ChatService(IChatService):
    """Implementation of chat service interface using LangChain with Google Gemini."""
    
    def __init__(self):
        self.llm = None
        self.conversation_chain = None
        self.rag_service = None
        
        if not settings.GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY not found in settings. LangChain/Gemini functionalities will be disabled.")
            return

        try:
            # Initialize RAG service
            try:
                # 🎯 שימוש בפרופיל מרכזי - ללא hard-coding!
                self.rag_service = RAGService()  # יטען את הפרופיל המרכזי אוטומטית
                logger.info("✅ RAG service initialized successfully with central profile")
            except Exception as e:
                logger.error(f"Error initializing RAG service: {e}")
                self.rag_service = None

            self.llm = ChatGoogleGenerativeAI(
                google_api_key=settings.GEMINI_API_KEY,
                model=settings.GEMINI_MODEL_NAME,
                temperature=settings.GEMINI_TEMPERATURE,
                max_output_tokens=settings.GEMINI_MAX_TOKENS
            )
            
            prompt_template = ChatPromptTemplate.from_messages([
                SystemMessagePromptTemplate.from_template(settings.GEMINI_SYSTEM_PROMPT),
                MessagesPlaceholder(variable_name="chat_history_buffer"),
                HumanMessagePromptTemplate.from_template("{input}")
            ])

            self.memory = ConversationBufferWindowMemory(
                k=settings.LANGCHAIN_HISTORY_K,
                return_messages=True, 
                memory_key="chat_history_buffer"
            )
            
            self.conversation_chain = ConversationChain(
                llm=self.llm,
                prompt=prompt_template,
                memory=self.memory,
                verbose=settings.LANGCHAIN_VERBOSE 
            )
            logger.info("ChatService initialized successfully with LangChain and Google Gemini.")
            logger.info(f"Using Gemini model: {settings.GEMINI_MODEL_NAME}, Temperature: {settings.GEMINI_TEMPERATURE}, Max Tokens: {settings.GEMINI_MAX_TOKENS}, History Window: {settings.LANGCHAIN_HISTORY_K}")

        except Exception as e:
            logger.error(f"Error initializing LangChain components with Gemini: {e}", exc_info=True)
            self.llm = None
            self.conversation_chain = None

    async def process_chat_message(
        self, 
        user_message: str, 
        user_id: str = "anonymous", 
        history: Optional[List[ChatMessageHistoryItem]] = None
    ) -> Dict[str, Any]:
        """Process a chat message using LangChain with Gemini and return an AI response."""

        if not self.conversation_chain:
            logger.error("ConversationChain (Gemini) is not initialized. GEMINI_API_KEY might be missing or initialization failed.")
            raise HTTPException(status_code=500, detail="AI Service (Gemini/LangChain) not initialized. Check GEMINI_API_KEY and server logs.")

        logger.debug(f"Processing message for user_id: {user_id} with LangChain (Gemini).")
        logger.debug(f"Incoming user_message: {user_message}")
        
        if history:
            logger.info(f"Rehydrating memory with {len(history)} messages from provided history for Gemini.")
            self.memory.clear()
            for item in history:
                if item.type == 'user':
                    self.memory.chat_memory.add_user_message(item.content)
                elif item.type == 'bot' or item.type == 'ai':
                    self.memory.chat_memory.add_ai_message(item.content)
            logger.debug(f"Memory after rehydration for Gemini: {self.memory.chat_memory.messages}")
        elif not self.memory.chat_memory.messages:
            logger.debug("No history provided and memory is empty. Starting fresh conversation.")

        try:
            # Check if this is a personal conversation question
            is_conversation_question = self._is_conversation_question(user_message)
            
            logger.info(f"Question analysis: conversation={is_conversation_question}")
            
            # For personal conversation questions, use regular LLM directly
            if is_conversation_question:
                logger.info("Using regular LLM for personal conversation question")
                response_content = await self.conversation_chain.apredict(input=user_message)
                logger.info(f"LangChain (Gemini) - AI response: {response_content[:100]}...")
                return {
                    "response": response_content,
                    "source_type": "conversation",
                    "source_description": "תשובה מבוססת על השיחה הנוכחית"
                }
            
            # For all other questions, try RAG service first
            if self.rag_service:
                logger.info("Trying RAG service first for potential document question")
                try:
                    rag_response = await self.rag_service.generate_answer(
                        query=user_message,
                        search_method="hybrid"
                    )
                    
                    # Check if RAG found relevant results
                    # בדיקה מעודכנת - יש לבדוק גם chunks_selected וגם sources
                    has_sources = rag_response.get("sources") and len(rag_response["sources"]) > 0
                    has_chunks = rag_response.get("chunks_selected") and len(rag_response["chunks_selected"]) > 0
                    
                    if has_sources or has_chunks:
                        # RAG found relevant information
                        self.memory.chat_memory.add_user_message(user_message)
                        self.memory.chat_memory.add_ai_message(rag_response["answer"])
                        
                        sources_count = len(rag_response.get("sources", []))
                        chunks_count = len(rag_response.get("chunks_selected", []))
                        logger.info(f"🎯 RAG service found {sources_count} sources, {chunks_count} chunks - using RAG response")
                        return {
                            "response": rag_response["answer"], 
                            "sources": rag_response.get("sources", []),
                            "source_type": "rag",
                            "source_description": f"תשובה מבוססת על {sources_count} מקורות מהתקנונים",
                            "chunks_count": chunks_count,
                            "sources_count": sources_count
                        }
                    else:
                        # RAG didn't find relevant information, fall back to regular LLM
                        logger.info("❌ RAG service didn't find relevant sources/chunks, falling back to regular LLM")
                except Exception as e:
                    logger.error(f"Error using RAG service: {e}. Falling back to regular LLM.")
            
            # Fallback to regular LLM (no RAG service or RAG didn't find relevant results)
            logger.info("Using regular LLM as fallback")
            response_content = await self.conversation_chain.apredict(input=user_message)
            
            logger.info(f"LangChain (Gemini) - AI response: {response_content[:100]}...")
            
            return {
                "response": response_content,
                "source_type": "llm",
                "source_description": "תשובה כללית (לא נמצא מידע רלוונטי בתקנונים)"
            }

        except Exception as e:
            logger.error(f"Error during LangChain (Gemini) conversation prediction: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error processing message with AI (Gemini): {e}")
    
    def _is_conversation_question(self, message: str) -> bool:
        """Determine if a message is asking about information from previous conversation"""
        message = message.lower()
        conversation_indicators = [
            "איך קוראים לי", "מה השם שלי", "איך קוראים לי?", "מה השם שלי?",
            "מי אני", "איך קוראים לי?", "מה השם", "מה שמי",
            "what is my name", "what's my name", "who am i"
        ]
        
        # Check if the message is asking about personal information from conversation
        for indicator in conversation_indicators:
            if indicator in message:
                return True
        
        return False
    
