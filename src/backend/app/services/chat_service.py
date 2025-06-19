import logging
import json
import sys
import os
from typing import Dict, Any, List, Optional, AsyncGenerator
from fastapi import HTTPException
from pathlib import Path

# Add the backend directory to sys.path to allow importing from services
backend_dir = Path(__file__).parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Add AI path to sys.path
ai_path = Path(__file__).parent.parent.parent.parent / "ai"
if str(ai_path) not in sys.path:
    sys.path.insert(0, str(ai_path))

from ..core.interfaces import IChatService
from ..config.settings import settings
from ..domain.models import ChatMessageHistoryItem
try:
    from src.ai.services.rag_service import RAGService  # Import the new RAG service
    from src.ai.services.document_processor import DocumentProcessor  # Import from ai/services
    RAG_AVAILABLE = True
except ImportError as e:
    RAGService = None
    DocumentProcessor = None
    RAG_AVAILABLE = False

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
from src.ai.core.gemini_key_manager import get_key_manager

# Add Gemini client for streaming
try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

logger = logging.getLogger(__name__)

# Log RAG availability after logger is defined
if RAG_AVAILABLE:
    logger.info("✅ RAG services imported successfully")
else:
    logger.warning("⚠️ RAG services not available")

if GENAI_AVAILABLE:
    logger.info("✅ Google Generative AI available for streaming")
else:
    logger.warning("⚠️ Google Generative AI not available - streaming disabled")

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
            # Before creating the LLM, get current key from manager
            key_manager = get_key_manager()
            
            # Use environment key for ChatService since it's initialized once
            # The RAG service will use the key manager for dynamic key management
            current_key = settings.GEMINI_API_KEY
            
            if not current_key:
                logger.error("No GEMINI_API_KEY available for ChatService initialization")
                raise ValueError("GEMINI_API_KEY is required for ChatService")

            self.llm = ChatGoogleGenerativeAI(
                google_api_key=current_key,  # Use environment key for stable init
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

    async def _track_token_usage(self, user_message: str, ai_response: str, method: str = "chat"):
        """Track token usage with the key manager"""
        try:
            # 🔍 DEBUG: הוספת לוגים מפורטים
            logger.info(f"🔢 [CHAT-TOKEN-TRACK] ===== TRACKING TOKEN USAGE =====")
            logger.info(f"🔢 [CHAT-TOKEN-TRACK] Method: {method}")
            logger.info(f"🔢 [CHAT-TOKEN-TRACK] User message length: {len(user_message)}")
            logger.info(f"🔢 [CHAT-TOKEN-TRACK] AI response length: {len(ai_response)}")
            
            # Estimate tokens based on text length (rough approximation)
            # Typically ~4 characters per token for mixed content
            input_tokens = len(user_message) // 4
            output_tokens = len(ai_response) // 4
            total_tokens = input_tokens + output_tokens
            
            # Add some overhead for system prompt and context
            system_overhead = 50  # Rough estimate
            total_tokens += system_overhead
            
            logger.info(f"🔢 [CHAT-TOKEN-TRACK] Estimated tokens:")
            logger.info(f"🔢 [CHAT-TOKEN-TRACK] - Input: {input_tokens}")
            logger.info(f"🔢 [CHAT-TOKEN-TRACK] - Output: {output_tokens}")
            logger.info(f"🔢 [CHAT-TOKEN-TRACK] - Overhead: {system_overhead}")
            logger.info(f"🔢 [CHAT-TOKEN-TRACK] - Total: {total_tokens}")
            
            # Smart tracking that works with both key manager types
            try:
                key_manager = get_key_manager()
                logger.info(f"🔢 [CHAT-TOKEN-TRACK] Key manager type: {type(key_manager).__name__}")
                logger.info(f"🔢 [CHAT-TOKEN-TRACK] Has record_usage: {hasattr(key_manager, 'record_usage')}")
                logger.info(f"🔢 [CHAT-TOKEN-TRACK] Has api_keys: {hasattr(key_manager, 'api_keys')}")
                logger.info(f"🔢 [CHAT-TOKEN-TRACK] Has track_usage: {hasattr(key_manager, 'track_usage')}")
                
                # Check if this is DatabaseKeyManager or legacy GeminiKeyManager
                if hasattr(key_manager, 'record_usage') and hasattr(key_manager, 'api_keys'):
                    # DatabaseKeyManager - needs key_id
                    # 🔥 FIX: Ensure keys are loaded by calling get_available_key
                    current_key = await key_manager.get_available_key()
                    if current_key:
                        key_id = current_key.get('id')
                        if key_id:
                            await key_manager.record_usage(key_id, total_tokens, 1)
                            logger.info(f"🔢 [CHAT-TOKEN-TRACK] Successfully tracked {total_tokens} tokens for key {key_id}")
                        else:
                            logger.warning("⚠️ [CHAT-TOKEN-TRACK] No key_id found in current key")
                    else:
                        logger.warning("⚠️ [CHAT-TOKEN-TRACK] No API keys available in DatabaseKeyManager")
                elif hasattr(key_manager, 'track_usage'):
                    # Legacy GeminiKeyManager - accepts only tokens_used
                    key_manager.track_usage(total_tokens)
                    logger.info(f"🔢 [CHAT-TOKEN-TRACK] Successfully tracked {total_tokens} tokens (legacy)")
                else:
                    logger.warning("⚠️ [CHAT-TOKEN-TRACK] Unknown key manager type - no tracking method found")
                    
            except Exception as km_error:
                logger.warning(f"⚠️ [CHAT-TOKEN-TRACK] Key manager tracking failed: {km_error}")
                # Continue without key manager tracking - not critical for ChatService
            
            logger.info(f"🔢 [CHAT-TOKEN-TRACK] ===== TOKEN TRACKING COMPLETE =====")
            
        except Exception as e:
            logger.error(f"❌ [CHAT-TOKEN-ERROR] Error tracking token usage: {e}")
            import traceback
            logger.error(f"❌ [CHAT-TOKEN-ERROR] Traceback: {traceback.format_exc()}")

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
                    if RAG_AVAILABLE and RAGService:
                        from src.ai.config.current_profile import get_current_profile
                        current_profile = get_current_profile()
                        self.current_profile_cache = current_profile
                        
                        # יצירת RAG service חדש
                        self.rag_service = RAGService()
                        logger.debug(f"✅ RAG service ready with profile: {self.current_profile_cache}")
                    else:
                        logger.warning("RAG service not available - imports failed")
                        self.rag_service = None
                        self.current_profile_cache = "unavailable"
                except Exception as e:
                    logger.warning(f"Could not get current profile or create RAG service: {e}")
                    self.current_profile_cache = "error"
                    self.rag_service = None
                    
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

        # 🔍 DEBUG: הוספת לוגים מפורטים
        logger.info(f"🚀 [CHAT-SERVICE-DEBUG] ===== PROCESSING CHAT MESSAGE =====")
        logger.info(f"🚀 [CHAT-SERVICE-DEBUG] User ID: {user_id}")
        logger.info(f"🚀 [CHAT-SERVICE-DEBUG] Message: {user_message[:50]}...")
        logger.info(f"🚀 [CHAT-SERVICE-DEBUG] History provided: {len(history) if history else 0} messages")

        if not self.conversation_chain:
            logger.error("ConversationChain (Gemini) is not initialized. GEMINI_API_KEY might be missing or initialization failed.")
            raise HTTPException(status_code=500, detail="AI Service (Gemini/LangChain) not initialized. Check GEMINI_API_KEY and server logs.")

        logger.debug(f"Processing message for user_id: {user_id} with LangChain (Gemini).")
        logger.debug(f"Incoming user_message: {user_message}")
        
        # Always clear memory at the start of each conversation to ensure session isolation
        logger.debug("Clearing memory to ensure fresh conversation context")
        self.memory.clear()
        
        # Rehydrate memory with provided history if available
        if history and len(history) > 0:
            logger.debug(f"Rehydrating memory with {len(history)} messages from provided history for Gemini.")
            for msg in history:
                if msg.type == 'user':
                    self.memory.chat_memory.add_user_message(msg.content)
                elif msg.type == 'bot':
                    self.memory.chat_memory.add_ai_message(msg.content)
            logger.debug(f"Memory after rehydration for Gemini: {self.memory.chat_memory.messages}")
        else:
            logger.debug("No history provided - starting fresh conversation.")
        
        # Detect if this is a personal conversation vs information request (including conversation history questions)
        is_conversation_question = self._is_conversation_question(user_message)
        
        logger.info(f"📝 Question analysis for '{user_message}': conversation={is_conversation_question}")
        
        if is_conversation_question:
            logger.info(f"🗣️ Treating as conversation question: '{user_message}'")
        else:
            logger.info(f"📚 Treating as information request (will use RAG): '{user_message}'")
        
        # Handle conversation questions with LangChain conversation chain (includes memory)
        if is_conversation_question:
            logger.debug("Using LangChain conversation chain for personal conversation question")
            response_content = self.conversation_chain.predict(input=user_message)
            logger.debug(f"LangChain conversation chain - AI response: {response_content[:100]}...")
            
            # 🔥 TRACK TOKEN USAGE FOR CONVERSATION
            logger.info(f"🎯 [CHAT-SERVICE] Tracking tokens for conversation response")
            await self._track_token_usage(user_message, response_content, "conversation")
            
            return {
                "response": response_content,
                "sources": [],
                "chunks": 0
            }
        
        # For information requests, use RAG
        rag_service = self._get_current_rag_service()
        logger.debug(f"Using RAG service with profile: {self.current_profile_cache}")
        
        try:
            # Get RAG response WITH CONVERSATION HISTORY
            if rag_service:
                logger.info(f"🔍 Calling RAG service for question: '{user_message}'")
                
                # 🔥 תיקון קריטי: העברת היסטוריית השיחה ל-RAG
                conversation_context = ""
                if history and len(history) > 0:
                    context_messages = []
                    for msg in history[-10:]:  # רק 10 הודעות אחרונות למניעת overflow
                        if msg.type == 'user':
                            context_messages.append(f"משתמש: {msg.content}")
                        elif msg.type == 'bot':
                            context_messages.append(f"מערכת: {msg.content}")
                    conversation_context = "\n".join(context_messages)
                    logger.info(f"🔄 העברת {len(history[-10:])} הודעות קונטקסט ל-RAG")
                
                # שליחת השאלה עם קונטקסט השיחה
                if conversation_context:
                    enhanced_query = f"היסטוריית השיחה:\n{conversation_context}\n\nשאלה נוכחית: {user_message}"
                    logger.info(f"🔗 Enhanced query length: {len(enhanced_query)} chars")
                else:
                    enhanced_query = user_message
                    logger.info("📝 No conversation history, using original query")
                
                rag_response = await rag_service.generate_answer(enhanced_query, search_method="hybrid")
                logger.info(f"📋 RAG response received: {rag_response is not None}")
                if rag_response:
                    logger.info(f"📋 RAG response keys: {list(rag_response.keys()) if isinstance(rag_response, dict) else 'Not a dict'}")
            else:
                logger.warning("⚠️ RAG service not available")
                rag_response = None
            
            if rag_response and rag_response.get("answer"):
                sources_count = len(rag_response.get("sources", []))
                chunks_count = len(rag_response.get("chunks_selected", []))
                
                logger.info(f"📊 RAG answer found: sources={sources_count}, chunks={chunks_count}")
                
                if sources_count > 0:
                    logger.info(f"🎯 RAG generated answer with {sources_count} sources, {chunks_count} chunks")
                    
                    # Update memory to preserve conversation context
                    self.memory.chat_memory.add_user_message(user_message)
                    self.memory.chat_memory.add_ai_message(rag_response["answer"])
                    
                    # 🔥 TRACK TOKEN USAGE FOR RAG RESPONSE
                    logger.info(f"🎯 [CHAT-SERVICE] Tracking tokens for RAG response")
                    await self._track_token_usage(user_message, rag_response["answer"], "rag")
                    
                    return {
                        "response": rag_response["answer"],
                        "sources": rag_response.get("sources", []),
                        "chunks": chunks_count
                    }
                else:
                    logger.info("📊 RAG found answer but no sources, falling back")
            else:
                logger.info("❌ RAG service didn't generate answer or answer is empty, falling back to regular LLM")
            
        except Exception as e:
            logger.warning(f"⚠️  RAG service error: {e}")
            logger.debug("Using regular LLM as fallback")
        
        # Fallback to LangChain conversation chain (preserves memory)
        response_content = self.conversation_chain.predict(input=user_message)
        logger.debug(f"LangChain conversation chain fallback - AI response: {response_content[:100]}...")
        
        # 🔥 TRACK TOKEN USAGE FOR FALLBACK RESPONSE
        logger.info(f"🎯 [CHAT-SERVICE] Tracking tokens for fallback response")
        await self._track_token_usage(user_message, response_content, "fallback")
        
        return {
            "response": response_content,
            "sources": [],
            "chunks": 0
        }
    
    def _is_conversation_question(self, message: str) -> bool:
        """Determine if a message is asking about information from previous conversation or general chat"""
        message = message.lower().strip()
        
        # אם ההודעה מתחילה ב"היסטוריית השיחה:" - זה בוודאי מיועד ל-RAG
        if "היסטוריית השיחה:" in message:
            return False  # שלח ל-RAG לא ל-conversation
        
        # זיהוי התייחסויות למידע קודם או מספרים (כללי)
        import re
        
        # דפוסים כלליים להתייחסות למידע קודם
        reference_patterns = [
            r"הציון שלי",
            r"המספר שלי", 
            r"הטווח שלי",
            r"ציון \d+",  # ציון + מספר כלשהו
            r"\d+ זה",   # מספר + "זה"
            r"עם הציון",
            r"עם המספר",
            r"הציון הזה",
            r"המספר הזה"
        ]
        
        # ביטויים להתייחסות למידע קודם
        reference_phrases = [
            "אמרת", "ציינת", "למה", "איך זה יכול", "איך יכול להיות",
            "לא הבנתי", "סתירה", "אבל קודם", "אבל אמרת", "אבל ציינת",
            "כתבת", "הסברת", "נאמר", "קודם אמרת", "בתשובה הקודמת"
        ]
        
        # ביטויים לנושאים אקדמיים שצריכים RAG
        academic_terms = [
            "ציון", "רמה", "רמות", "טווח", "טווחים", "דרגה", "קטגוריה",
            "באנגלית", "ברמה", "מתקדמים", "בסיסי", "בינוני", "גבוה",
            "מבחן", "בחינה", "הערכה", "פסיכומטרי", "אמיר"
        ]
        
        # בדיקת דפוסים בביטויים רגולריים
        for pattern in reference_patterns:
            if re.search(pattern, message):
                return False  # שלח ל-RAG
        
        # בדיקת ביטויי התייחסות
        for phrase in reference_phrases:
            if phrase in message:
                return False  # שלח ל-RAG
        
        # בדיקת מונחים אקדמיים
        for term in academic_terms:
            if term in message:
                return False  # שלח ל-RAG
        
        # זיהוי מספרים בהודעה (כל מספר שיכול להיות ציון)
        if re.search(r'\b\d{2,3}\b', message):  # מספרים של 2-3 ספרות (ציונים אפשריים)
            return False  # שלח ל-RAG
        
        # Very specific conversation questions only
        # Questions about personal information from conversation history
        personal_info_questions = [
            "איך קוראים לי", "מה השם שלי", "איך קוראים לי?", "מה השם שלי?",
            "מי אני", "מה השם", "מה שמי", "קוראים לי",
            "what is my name", "what's my name", "who am i"
        ]
        
        # Simple greetings and personal questions
        simple_greetings = [
            "שלום", "היי", "hello", "hi",
            "מה שלומך", "איך אתה", "how are you"
        ]
        
        # Check for exact matches or very close matches
        for indicator in personal_info_questions:
            if message == indicator or message == indicator + "?":
                return True
        
        # Check for simple greetings
        for greeting in simple_greetings:
            if message == greeting or message == greeting + "?":
                return True
                
        # Only return True for very obvious conversation questions
        return False

    async def process_chat_message_stream(
        self, 
        user_message: str, 
        user_id: str = "anonymous",
        history: Optional[List[ChatMessageHistoryItem]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Process a chat message using streaming Gemini API and return chunks."""
        
        logger.info(f"🚀 [CHAT-STREAM] Processing streaming message for user: {user_id}")
        
        if not GENAI_AVAILABLE:
            logger.error("Google Generative AI not available for streaming")
            yield {"type": "error", "content": "Streaming not available"}
            return
        
        try:
            # Get API key
            key_manager = get_key_manager()
            current_key = settings.GEMINI_API_KEY
            
            if not current_key:
                logger.error("No GEMINI_API_KEY available for streaming")
                yield {"type": "error", "content": "API key not available"}
                return
            
            # Configure Gemini client
            client = genai.Client(api_key=current_key)
            
            # Build conversation for context
            conversation_parts = []
            if history:
                for msg in history:
                    if msg.type == 'user':
                        conversation_parts.append({"role": "user", "parts": [msg.content]})
                    elif msg.type == 'bot':
                        conversation_parts.append({"role": "model", "parts": [msg.content]})
            
            # Add current message
            conversation_parts.append({"role": "user", "parts": [user_message]})
            
            # Use proper conversation format instead of text concatenation
            response = client.models.generate_content_stream(
                model="gemini-2.0-flash-exp",
                contents=conversation_parts  # Use structured conversation format
            )
            
            accumulated_text = ""
            for chunk in response:
                if chunk.text:
                    accumulated_text += chunk.text
                    yield {
                        "type": "chunk",
                        "content": chunk.text,
                        "accumulated": accumulated_text
                    }
            
            # Track usage
            await self._track_token_usage(user_message, accumulated_text, "streaming_conversation")
            
            yield {
                "type": "complete",
                "content": accumulated_text,
                "sources": [],
                "chunks": 0
            }
            
        except Exception as e:
            logger.exception(f"❌ [CHAT-STREAM] Streaming error: {e}")
            yield {"type": "error", "content": f"Streaming error: {str(e)}"}
    
