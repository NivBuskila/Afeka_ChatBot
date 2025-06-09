import logging
import json
import sys
import os
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
# from src.ai.services.rag_service import RAGService  # Import the new RAG service - DISABLED
# from src.ai.services.document_processor import DocumentProcessor  # Import from ai/services - DISABLED

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
        
        # 🎯 Cache חכם עבור RAGService
        self.rag_service = None
        self.current_profile_cache = None
        self.profile_file_mtime = None
        
        # נתיב לקובץ הפרופיל
        try:
            ai_config_path = Path(__file__).parent.parent.parent.parent / "ai" / "config"
            self.profile_file_path = ai_config_path / "current_profile.json"
            logger.debug(f"📁 Profile file path: {self.profile_file_path}")
        except Exception as e:
            logger.warning(f"Could not determine profile file path: {e}")
            self.profile_file_path = None
        
        if not settings.GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY not found in settings. LangChain/Gemini functionalities will be disabled.")
            return

        try:
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
            logger.info("✅ ChatService initialized with LangChain and Google Gemini")
            logger.debug(f"🤖 Using model: {settings.GEMINI_MODEL_NAME}, temp: {settings.GEMINI_TEMPERATURE}, tokens: {settings.GEMINI_MAX_TOKENS}, history: {settings.LANGCHAIN_HISTORY_K}")

        except Exception as e:
            logger.error(f"Error initializing LangChain components with Gemini: {e}", exc_info=True)
            self.llm = None
            self.conversation_chain = None

    def _get_current_rag_service(self) -> Optional[Any]:
        """מחזיר RAGService עם cache חכם שבודק שינויים בפרופיל"""
        try:
            # בדיקה אם קובץ הפרופיל קיים ומה זמן השינוי שלו
            profile_changed = False
            current_mtime = None
            
            if self.profile_file_path and self.profile_file_path.exists():
                current_mtime = self.profile_file_path.stat().st_mtime
                
                # בדיקה אם הקובץ השתנה
                if self.profile_file_mtime != current_mtime:
                    profile_changed = True
                    logger.debug(f"🔄 Profile updated (mtime: {current_mtime} vs cached: {self.profile_file_mtime})")
            else:
                # אין קובץ פרופיל - נשתמש בברירת מחדל
                if self.rag_service is None:
                    profile_changed = True
                    logger.debug("📁 No profile file found - using default RAG service")
            
            # אם אין לנו cache או שהפרופיל השתנה - יצירה חדשה
            if self.rag_service is None or profile_changed:
                logger.debug("🆕 Creating new RAG service...")
                
                # עדכון cache
                if current_mtime:
                    self.profile_file_mtime = current_mtime
                
                # שמירת הפרופיל הנוכחי לcache
                try:
                    from src.ai.config.current_profile import get_current_profile
                    current_profile = get_current_profile()
                    self.current_profile_cache = current_profile
                    logger.debug(f"✅ RAG service ready with profile: {self.current_profile_cache}")
                except Exception as e:
                    logger.warning(f"Could not get current profile: {e}")
                    self.current_profile_cache = "unknown"
                    
            else:
                logger.debug(f"📋 Using cached RAG service with profile: {self.current_profile_cache}")
            
            return self.rag_service
            
        except Exception as e:
            logger.error(f"Error getting RAG service: {e}")
            # במקרה של שגיאה, אם יש לנו instance קיים - נשתמש בו
            if self.rag_service is not None:
                logger.warning("Using existing RAG service instance despite error")
                return self.rag_service
            return None

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
        
        # Rehydrate memory with provided history if available
        if history and len(history) > 0:
            logger.debug(f"Rehydrating memory with {len(history)} messages from provided history for Gemini.")
            self.memory.clear()
            for msg in history:
                if msg.get('user_message'):
                    self.memory.chat_memory.add_user_message(msg['user_message'])
                if msg.get('assistant_message'):
                    self.memory.chat_memory.add_ai_message(msg['assistant_message'])
            logger.debug(f"Memory after rehydration for Gemini: {self.memory.chat_memory.messages}")
        else:
            logger.debug("No history provided and memory is empty. Starting fresh conversation.")
        
        # Detect if this is a personal conversation vs information request
        conversation_prompts = ["how are you", "what's your name", "tell me about yourself", "who are you", "how do you feel"]
        is_conversation_question = any(prompt in user_message.lower() for prompt in conversation_prompts)
        
        logger.debug(f"Question analysis: conversation={is_conversation_question}")
        
        # Handle conversation questions with direct LLM
        if is_conversation_question:
            logger.debug("Using regular LLM for personal conversation question")
            response_content = self.llm.invoke(user_message).content
            logger.debug(f"LangChain (Gemini) - AI response: {response_content[:100]}...")
            self.memory.chat_memory.add_user_message(user_message)
            self.memory.chat_memory.add_ai_message(response_content)
            
            return {
                "response": response_content,
                "sources": [],
                "chunks": 0
            }
        
        # For information requests, use RAG
        logger.debug(f"Using RAG service with profile: {self.current_profile_cache}")
        
        try:
            # Get RAG response
            rag_response = self.rag_service.answer_question(user_message)
            
            if rag_response and rag_response.get("answer"):
                sources_count = len(rag_response.get("sources", []))
                chunks_count = len([chunk for source in rag_response.get("sources", []) for chunk in source.get("chunks", [])])
                
                if sources_count > 0:
                    logger.info(f"🎯 RAG generated answer with {sources_count} sources, {chunks_count} chunks")
                    
                    # Update memory
                    self.memory.chat_memory.add_user_message(user_message)
                    self.memory.chat_memory.add_ai_message(rag_response["answer"])
                    
                    return {
                        "response": rag_response["answer"],
                        "sources": rag_response.get("sources", []),
                        "chunks": chunks_count
                    }
            
            logger.debug("❌ RAG service didn't generate answer, falling back to regular LLM")
            
        except Exception as e:
            logger.warning(f"⚠️  RAG service error: {e}")
            logger.debug("Using regular LLM as fallback")
        
        # Fallback to regular LLM
        response_content = self.llm.invoke(user_message).content
        logger.debug(f"LangChain (Gemini) - AI response: {response_content[:100]}...")
        
        return {
            "response": response_content,
            "sources": [],
            "chunks": 0
        }
    
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
    
