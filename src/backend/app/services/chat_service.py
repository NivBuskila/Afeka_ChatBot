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
from ..core.rag_service import RAGService
from services.document_processor import DocumentProcessor  # Import from backend/services

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
                doc_processor = DocumentProcessor()
                self.rag_service = RAGService(doc_processor)
                logger.info("RAG service initialized successfully")
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
            # Check if the message is asking about information from previous conversation
            if self._is_conversation_question(user_message) or not self._is_document_question(user_message):
                # Use regular LLM with conversation history for personal questions and general chat
                response_content = await self.conversation_chain.apredict(input=user_message)
                logger.info(f"LangChain (Gemini) - AI response: {response_content[:100]}...")
                return {"response": response_content}
            
            # For document-based questions, try RAG service first
            if self.rag_service and self._is_document_question(user_message):
                logger.info("Using RAG service to answer document-based question")
                try:
                    rag_response = await self.rag_service.get_answer(
                        query=user_message,
                        use_hybrid_search=True,
                        add_sources_to_response=True
                    )
                    
                    # Add the RAG response to memory so it's part of the conversation history
                    self.memory.chat_memory.add_user_message(user_message)
                    self.memory.chat_memory.add_ai_message(rag_response["result"])
                    
                    logger.info(f"RAG service response: {rag_response['result'][:100]}...")
                    return {"response": rag_response["result"], "sources": rag_response.get("sources", [])}
                except Exception as e:
                    logger.error(f"Error using RAG service: {e}. Falling back to regular LLM.")
            
            # If RAG service is not available or failed, use regular LLM
            response_content = await self.conversation_chain.apredict(input=user_message)
            
            logger.info(f"LangChain (Gemini) - AI response: {response_content[:100]}...")
            
            return {"response": response_content}

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
    
    def _is_document_question(self, message: str) -> bool:
        """Determine if a message is likely a document-based question"""
        message = message.lower()
        
        # Skip conversation questions even if they have question indicators
        if self._is_conversation_question(message):
            return False
            
        # Document-specific keywords
        document_keywords = [
            "תקנון", "חוק", "נוהל", "כללים", "חובות", "זכויות", 
            "לימודים", "קורס", "מבחן", "ציון", "סמסטר", "אפקה",
            "regulations", "rules", "course", "exam", "grade", "afeka"
        ]
        
        # Check for document-specific keywords first
        for keyword in document_keywords:
            if keyword in message:
                return True
        
        # If no document keywords, check for general question indicators
        # but be more selective to avoid catching conversation questions
        question_indicators = ["מה זה", "איך עושים", "מתי צריך", "איפה נמצא", "מי אחראי"]
        
        for indicator in question_indicators:
            if indicator in message:
                return True
        
        return False