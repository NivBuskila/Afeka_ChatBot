import logging
import json
import sys
import os
from typing import Dict, Any, List, Optional, AsyncGenerator
from fastapi import HTTPException
from pathlib import Path
from pydantic import SecretStr
import asyncio

backend_dir = Path(__file__).parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

ai_path = Path(__file__).parent.parent.parent.parent / "ai"
if str(ai_path) not in sys.path:
    sys.path.insert(0, str(ai_path))

from ..core.interfaces import IChatService
from ..config.settings import settings
from ..domain.models import ChatMessageHistoryItem
try:
    from ....ai.services.rag_service import RAGService
    from ....ai.services.document_processor import DocumentProcessor
    rag_available = True
except ImportError as e:
    RAGService = None
    DocumentProcessor = None
    rag_available = False

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
from ....ai.core.gemini_key_manager import get_key_manager

try:
    from google import genai
    genai_available = True
except ImportError:
    genai = None
    genai_available = False

logger = logging.getLogger(__name__)

if rag_available:
    logger.info("RAG services imported successfully")
else:
    logger.warning("RAG services not available")

if genai_available:
    logger.info("Google Generative AI available for streaming")
else:
    logger.warning("Google Generative AI not available - streaming disabled")

class ChatService(IChatService):
    """Implementation of chat service interface using LangChain with Google Gemini."""
    
    def __init__(self):
        self.llm = None
        self.conversation_chain = None
        
        self.rag_service = None
        self.current_profile_cache = None
        
        self.MAX_HISTORY_LENGTH = 5
        
        if not settings.GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY not found in settings. LangChain/Gemini functionalities will be disabled.")
            return

        try:
            key_manager = get_key_manager()
            
            current_key = settings.GEMINI_API_KEY
            
            if not current_key:
                logger.error("No GEMINI_API_KEY available for ChatService initialization")
                raise ValueError("GEMINI_API_KEY is required for ChatService")

            self.llm = ChatGoogleGenerativeAI(
                api_key=SecretStr(current_key),
                model=settings.GEMINI_MODEL_NAME,
                temperature=settings.GEMINI_TEMPERATURE,
                max_tokens=settings.GEMINI_MAX_TOKENS
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
            logger.info("ChatService initialized with LangChain and Google Gemini")
            logger.debug(f"Using model: {settings.GEMINI_MODEL_NAME}, temp: {settings.GEMINI_TEMPERATURE}, tokens: {settings.GEMINI_MAX_TOKENS}, history: {settings.LANGCHAIN_HISTORY_K}")

        except Exception as e:
            logger.error(f"Error initializing LangChain components with Gemini: {e}", exc_info=True)
            self.llm = None
            self.conversation_chain = None

    async def _track_token_usage(self, user_message: str, ai_response: str, method: str = "chat"):
        """Track token usage with the key manager"""
        try:
            input_tokens = len(user_message) // 4
            output_tokens = len(ai_response) // 4
            total_tokens = input_tokens + output_tokens + 50
            
            logger.debug(f"Token usage {method}: {total_tokens} tokens")
            
            try:
                key_manager = get_key_manager()
                
                if hasattr(key_manager, 'record_usage') and hasattr(key_manager, 'api_keys'):
                    current_key = await key_manager.get_available_key()
                    if current_key and current_key.get('id'):
                        await key_manager.record_usage(key_id=current_key['id'], tokens_used=total_tokens, requests_count=1)
                        logger.debug(f"Tracked {total_tokens} tokens for key {current_key['id']}")
                    
            except Exception as km_error:
                logger.debug(f"Key manager tracking failed: {km_error}")
            
        except Exception as e:
            logger.debug(f"Error in token tracking: {e}")

    def _get_current_rag_service(self) -> Optional[Any]:
        """Returns RAGService with direct check from Supabase each time"""
        try:
            profile_changed = False
            current_profile = None
            
            try:
                from ....ai.config.current_profile import get_current_profile
                current_profile = get_current_profile()
                logger.debug(f"Current profile from Supabase: '{current_profile}'")
                
                if self.rag_service is None or self.current_profile_cache != current_profile:
                    profile_changed = True
                    logger.info(f"Profile update detected: '{self.current_profile_cache}' → '{current_profile}'")
            except Exception as e:
                logger.warning(f"Could not get current profile from Supabase: {e}")
                if self.rag_service is None:
                    profile_changed = True
                    logger.debug("No profile found - using default RAG service")
            
            if self.rag_service is None or profile_changed:
                logger.debug("Creating new RAG service...")
                
                try:
                    if rag_available and RAGService:
                        if current_profile:
                            self.current_profile_cache = current_profile
                        else:
                            from ....ai.config.current_profile import get_current_profile
                            current_profile = get_current_profile()
                            self.current_profile_cache = current_profile
                        
                        logger.info(f"Creating RAG service with profile: {current_profile}")
                        self.rag_service = RAGService(config_profile=current_profile)
                        logger.debug(f"RAG service ready with profile: {current_profile}")
                        
                        logger.debug(f"   Actual similarity threshold: {self.rag_service.search_config.SIMILARITY_THRESHOLD}")
                        logger.debug(f"   Actual max chunks: {self.rag_service.search_config.MAX_CHUNKS_RETRIEVED}")
                        logger.debug(f"   Actual temperature: {self.rag_service.llm_config.TEMPERATURE}")
                        
                    else:
                        logger.warning("RAG service not available - imports failed")
                        self.rag_service = None
                        self.current_profile_cache = "unavailable"
                except Exception as e:
                    logger.warning(f"Could not get current profile or create RAG service: {e}")
                    if rag_available and RAGService:
                        try:
                            self.rag_service = RAGService(config_profile="balanced")
                            self.current_profile_cache = "balanced"
                            logger.info("Created RAG service with balanced profile as fallback")
                        except Exception as fallback_error:
                            logger.error(f"Failed to create fallback RAG service: {fallback_error}")
                            self.rag_service = None
                            self.current_profile_cache = "error"
                    else:
                        logger.warning("RAG service not available - imports failed")
                        self.rag_service = None
                        self.current_profile_cache = "unavailable"
                    
            else:
                logger.debug(f"Using cached RAG service with profile: {self.current_profile_cache}")
            
            return self.rag_service
            
        except Exception as e:
            logger.error(f"Error getting RAG service: {e}")
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

        logger.info(f"[CHAT-SERVICE] Processing: '{user_message[:50]}...' for {user_id}")
        logger.info(f"[CHAT-SERVICE] History: {len(history) if history else 0} messages")

        if not self.conversation_chain:
            logger.error("ConversationChain (Gemini) is not initialized. GEMINI_API_KEY might be missing or initialization failed.")
            raise HTTPException(status_code=500, detail="AI Service (Gemini/LangChain) not initialized. Check GEMINI_API_KEY and server logs.")

        self.memory.clear()
        
        if history and len(history) > 0:
            limited_history = history[-self.MAX_HISTORY_LENGTH:]
            logger.debug(f"Rehydrating memory with {len(limited_history)} of {len(history)} messages (max: {self.MAX_HISTORY_LENGTH})")
            
            for msg in limited_history:
                if msg.type == 'user':
                    self.memory.chat_memory.add_user_message(msg.content)
                elif msg.type == 'bot':
                    self.memory.chat_memory.add_ai_message(msg.content)
        
        is_conversation_question = self._is_conversation_question(user_message)
        
        logger.info(f"Question analysis: conversation={is_conversation_question}")
        
        if is_conversation_question:
            logger.info(f"Treating as conversation question")
        else:
            logger.info(f"Treating as information request (will use RAG)")
        
        if is_conversation_question:
            logger.debug("Using LangChain conversation chain for personal conversation question")
            
            try:
                from src.ai.config.system_prompts import get_enhanced_conversation_prompt
                enhanced_conversation_prompt = get_enhanced_conversation_prompt(user_message)
            except ImportError:
                enhanced_conversation_prompt = f"""אתה עוזר ידידותי ומקצועי של מכללת אפקה.
ענה בחמימות ובאופן טבעי לשאלה: {user_message}"""
            
            response_content = self.conversation_chain.predict(input=enhanced_conversation_prompt)
            logger.debug(f"LangChain conversation response: {response_content[:100]}...")
            
            logger.info(f"[CHAT-SERVICE] Tracking tokens for conversation response")
            await self._track_token_usage(user_message, response_content, "conversation")
            
            return {
                "response": response_content,
                "sources": [],
                "chunks": 0
            }
        
        rag_service = self._get_current_rag_service()
        logger.debug(f"Using RAG service with profile: {self.current_profile_cache}")
        
        try:
            if rag_service:
                logger.info(f"Calling RAG service for question: '{user_message}'")
                
                conversation_context = ""
                if history and len(history) > 0:
                    limited_history = history[-self.MAX_HISTORY_LENGTH:]
                    
                    context_messages = []
                    for msg in limited_history:
                        if msg.type == 'user':
                            context_messages.append(f"משתמש: {msg.content}")
                        elif msg.type == 'bot':
                            context_messages.append(f"מערכת: {msg.content}")
                    
                    if context_messages:
                        conversation_context = "\n".join(context_messages)
                        logger.debug(f"Built conversation context with {len(limited_history)} messages for LLM")
                
                search_query = user_message
                previous_context = ""
                
                if conversation_context and len(conversation_context.strip()) > 0:
                    last_context = ""
                    context_lines = conversation_context.split('\n')
                    for line in reversed(context_lines):
                        if line.startswith('משתמש:') and line != f"משתמש: {user_message}":
                            last_context = line.replace('משתמש: ', '').strip()
                            break
                    
                    if last_context and len(last_context) > 10:
                        previous_context = f"בהקשר של השאלה הקודמת: {last_context}"
                        
                        if len(user_message.strip()) < 100:
                            try:
                                context_lines = conversation_context.split('\n')
                                user_messages = []
                                for line in context_lines:
                                    if line.startswith('משתמש:'):
                                        clean_message = line.replace('משתמש: ', '').strip()
                                        if clean_message != user_message and len(clean_message) > 5:
                                            user_messages.append(clean_message)
                                
                                cumulative_context = '\n'.join(user_messages[-4:])
                                
                                if cumulative_context and len(cumulative_context.strip()) > 10:
                                    summary_prompt = f"""בהקשר של השיחה הבאה, תן סיכום מצטבר של הנושאים העיקריים ב-5-12 מילות מפתח בעברית:

היסטוריית השיחה:
{cumulative_context}

השאלה הנוכחית: {user_message}

תן תשובה קצרה עם מילות המפתח שמתארות את כל הנושאים בשיחה, מופרדות בפסיקים.
דוגמאות:
- שיחה על חנייה → "חנייה, קנסות, עבירות תנועה, פעמים חוזרות"
- שיחה על לימודים → "ציונים, מתמטיקה, קורסים, בחינות, דרישות"  
- שיחה על מילואים → "מילואים, זכויות סטודנטים, היעדרויות, הכרה"
"""

                                    if self.llm:
                                        cumulative_summary = self.llm.invoke(summary_prompt).content.strip()
                                        if cumulative_summary and len(cumulative_summary) < 80 and len(cumulative_summary) > 8:
                                            enhanced_query = f"{cumulative_summary}. {user_message}"
                                            search_query = enhanced_query
                                            logger.info(f"[CUMULATIVE-AI] Search query: '{search_query}' (GEMINI cumulative summary: '{cumulative_summary}')")
                                        else:
                                            logger.info(f"[SEARCH] Using original query: '{search_query}' (cumulative summary not suitable: '{cumulative_summary}')")
                                    else:
                                        logger.info(f"[SEARCH] Using original query: '{search_query}' (no LLM available for cumulative summarization)")
                                else:
                                    if last_context:
                                        summary_prompt = f"""סכם בקצרה (מקסימום 8 מילים) את הנושא המרכזי מהשאלה הבאה:
"{last_context}"

תן תשובה קצרה עם מילות המפתח העיקריות בלבד (למשל: "חנייה קנסות", "לימודים ציונים", "מילואים זכויות")."""

                                        if self.llm:
                                            context_summary = self.llm.invoke(summary_prompt).content.strip()
                                            if context_summary and len(context_summary) < 50 and len(context_summary) > 5:
                                                enhanced_query = f"{context_summary} {user_message}"
                                                search_query = enhanced_query
                                                logger.info(f"[SINGLE-AI] Search query: '{search_query}' (GEMINI single summary: '{context_summary}')")
                                            else:
                                                logger.info(f"[SEARCH] Using original query: '{search_query}' (single summary not suitable: '{context_summary}')")
                                        else:
                                            logger.info(f"[SEARCH] Using original query: '{search_query}' (no LLM available)")
                            except Exception as e:
                                logger.warning(f"Failed to generate cumulative AI context summary: {e}")
                                logger.info(f"[SEARCH] Using original query: '{search_query}' (fallback due to error)")
                        else:
                            logger.info(f"[SEARCH] Using original query: '{search_query}' (long question, no enhancement needed)")
                        
                        logger.info(f"[CONTEXT] Enhanced prompt context: '{previous_context[:100]}...'")
                    else:
                        logger.debug(f"[CONTEXT] No meaningful previous context found")
                        logger.info(f"[SEARCH] Using original query: '{search_query}'")
                else:
                    logger.debug(f"[CONTEXT] No conversation history available")
                    logger.info(f"[SEARCH] Using original query: '{search_query}'")
                
                rag_response = await rag_service.generate_answer_with_context(
                    query=search_query, 
                    conversation_context=previous_context,
                    search_method="hybrid"
                )
                
                logger.info(f"RAG response received: {rag_response is not None}")
                if rag_response:
                    logger.debug(f"RAG response keys: {list(rag_response.keys()) if isinstance(rag_response, dict) else 'Not a dict'}")
                    logger.debug(f"RAG response answer: {bool(rag_response.get('answer'))}")
                    logger.debug(f"RAG response sources: {rag_response.get('sources', [])}")
                    logger.debug(f"RAG response sources type: {type(rag_response.get('sources', []))}")
                    logger.debug(f"RAG response sources length: {len(rag_response.get('sources', []))}")
            else:
                logger.warning("RAG service not available")
                rag_response = None
            
            if rag_response and rag_response.get("answer"):
                sources_count = len(rag_response.get("sources", []))
                chunks_count = len(rag_response.get("chunks_selected", []))
                
                logger.info(f"RAG answer found: sources={sources_count}, chunks={chunks_count}")
                logger.debug(f"[DEBUG] RAG Response structure:")
                logger.debug(f"    Answer: '{rag_response.get('answer', '')[:100]}...'")
                logger.debug(f"    Sources: {rag_response.get('sources', [])}")
                logger.debug(f"    Chunks: {len(rag_response.get('chunks_selected', []))}")
                
                if sources_count > 0:
                    logger.info(f"RAG generated answer with {sources_count} sources, {chunks_count} chunks")
                    
                    self.memory.chat_memory.add_user_message(user_message)
                    self.memory.chat_memory.add_ai_message(rag_response["answer"])
                    
                    await self._track_token_usage(user_message, rag_response["answer"], "rag")
                    
                    return {
                        "response": rag_response["answer"],
                        "sources": rag_response.get("sources", []),
                        "chunks": chunks_count
                    }
                else:
                    logger.info("RAG found answer but no sources, falling back")
            else:
                logger.info("RAG service didn't generate answer or answer is empty, falling back to regular LLM")
            
        except Exception as e:
            logger.warning(f"RAG service error: {e}")
            logger.debug("Using regular LLM as fallback")
        
        try:
            from src.ai.config.system_prompts import get_fallback_prompt
            enhanced_prompt = get_fallback_prompt(user_message)
        except ImportError:
            enhanced_prompt = f"""
אתה עוזר אקדמי של מכללת אפקה שעונה על שאלות תלמידים.
אם אין לך מידע מדויק ממסמכי המכללה, תן תשובה כללית מועילה.
שאלה: {user_message}
"""
        
        response_content = self.conversation_chain.predict(input=enhanced_prompt)
        
        logger.info(f"LangChain fallback response generated (length: {len(response_content)})")
        
        await self._track_token_usage(user_message, response_content, "fallback")
        
        return {
            "response": response_content,
            "sources": [],
            "chunks": 0
        }
    
    def _is_conversation_question(self, message: str) -> bool:
        """Smart detection: conversation vs information requests"""
        message = message.lower().strip()
        
        academic_keywords = [
            "מגיע לי", "זכאי", "זכויות", "תנאים", "נדרש", "חובה", "הכרה", 
            "קבלה", "רישום", "בחינה", "מועד", "קורס", "תואר", "לימודים",
            "מילואים", "שירות", "צבא", "משוחרר", "חייל", "רפואי", "פטור",
            "מלגה", "שכר לימוד", "תשלום", "הנחה", "מועדון", "דרישות",
            "ציון", "נקודות", "שעות", "סמסטר", "מטלה", "פרוייקט", "עבודה",
            "מרצה", "מחלקה", "פקולטה", "דקאן", "מזכירות", "רכזת", "יועץ",
            "איך ל", "איפה ל", "מתי ל", "האם אפשר", "האם ניתן", "האם יש",
            "מה הליך", "מה התהליך", "מה הדרישות", "איך מקבלים", "איך נרשמים"
        ]
        
        for keyword in academic_keywords:
            if keyword in message:
                return False
        
        conversation_indicators = [
            "שלום", "היי", "hello", "hi", "בוקר טוב", "ערב טוב",
            "איך קוראים לך", "מה השם שלך", "מי אתה", 
            "מה שלומך", "איך אתה", "how are you", "תודה", "thanks", "תודה רבה",
            "כן", "לא", "אוקיי", "טוב", "yes", "no", "ok", "okay"
        ]
        
        for indicator in conversation_indicators:
            if indicator in message:
                return True
        
        if len(message) <= 3:
            return True
            
        return False

    async def process_chat_message_stream(
        self, 
        user_message: str, 
        user_id: str = "anonymous",
        history: Optional[List[ChatMessageHistoryItem]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Process a chat message using streaming - with RAG support!"""
        
        logger.info(f"[CHAT-STREAM] Processing streaming message for user: {user_id}")
        
        is_conversation_question = self._is_conversation_question(user_message)
        
        logger.info(f"[STREAM] Question analysis for '{user_message}': conversation={is_conversation_question}")
        
        if is_conversation_question:
            logger.info(f"[STREAM] Treating as conversation question")
            
            if not genai_available:
                yield {"type": "error", "content": "Streaming not available"}
                return
            
            try:
                current_key = settings.GEMINI_API_KEY
                if not current_key:
                    yield {"type": "error", "content": "API key not available"}
                    return
                
                if genai is None:
                    yield {"type": "error", "content": "Streaming not available - genai not imported"}
                    return
                
                client = genai.Client(api_key=current_key)
                
                conversation_text = ""
                if history:
                    limited_history = history[-self.MAX_HISTORY_LENGTH:]
                    for msg in limited_history:
                        if msg.type == 'user':
                            conversation_text += f"משתמש: {msg.content}\n"
                        elif msg.type == 'bot':
                            conversation_text += f"עוזר: {msg.content}\n"
                
                try:
                    from src.ai.config.system_prompts import get_enhanced_conversation_prompt
                    enhanced_conversation_prompt = get_enhanced_conversation_prompt(user_message)
                except ImportError:
                    enhanced_conversation_prompt = f"""אתה עוזר ידידותי ומקצועי של מכללת אפקה.
ענה בחמימות ובאופן טבעי לשאלה: {user_message}"""
                
                full_prompt = f"{conversation_text}משתמש: {enhanced_conversation_prompt}\nעוזר:"
                
                response = client.models.generate_content_stream(
                    model="gemini-2.0-flash-exp",
                    contents=full_prompt
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
                
                await self._track_token_usage(user_message, accumulated_text, "streaming_conversation")
                
                yield {
                    "type": "complete",
                    "content": accumulated_text,
                    "sources": [],
                    "chunks": 0
                }
                
            except Exception as e:
                logger.exception(f"[CHAT-STREAM] Conversation streaming error: {e}")
                yield {"type": "error", "content": f"Streaming error: {str(e)}"}
                
        else:
            logger.info(f"[STREAM] Treating as information request (will use RAG)")
            
            try:
                rag_result = await self.process_chat_message(user_message, user_id, history)
                
                response_content = rag_result.get("response", "")
                sources = rag_result.get("sources", [])
                chunks_count = rag_result.get("chunks", 0)
                
                chunk_size = 50
                for i in range(0, len(response_content), chunk_size):
                    chunk = response_content[i:i + chunk_size]
                    yield {
                        "type": "chunk",
                        "content": chunk,
                        "accumulated": response_content[:i + len(chunk)]
                    }
                
                yield {
                    "type": "complete",
                    "content": response_content,
                    "sources": sources,
                    "chunks": chunks_count
                }
                
                logger.info(f"[STREAM] RAG-based streaming complete with {len(sources)} sources")
                
            except Exception as e:
                logger.exception(f"[CHAT-STREAM] RAG streaming error: {e}")
                yield {"type": "error", "content": f"Error processing your request: {str(e)}"}