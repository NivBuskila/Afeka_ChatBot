import logging
import asyncio
from typing import Dict, Any, List, Optional, AsyncGenerator, TypedDict, Annotated
from pathlib import Path
import sys
import json
import re

# Add paths for imports
backend_dir = Path(__file__).parent.parent.parent
ai_path = Path(__file__).parent.parent.parent.parent / "ai"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
if str(ai_path) not in sys.path:
    sys.path.insert(0, str(ai_path))

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage, trim_messages
from langchain_core.messages.utils import count_tokens_approximately
from langchain_core.runnables import RunnableConfig

# LangGraph imports
try:
    from langgraph.graph import StateGraph, START, MessagesState, add_messages
    from langgraph.checkpoint.memory import MemorySaver
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False

# Try to import RAG if available
try:
    from src.ai.services.rag_service import RAGService
    RAG_AVAILABLE = True
except ImportError:
    RAGService = None
    RAG_AVAILABLE = False

from ..config.settings import settings
from ..core.interfaces import IChatService
from ..domain.models import ChatMessageHistoryItem
from src.ai.core.gemini_key_manager import get_key_manager

logger = logging.getLogger(__name__)

class AdvancedChatState(TypedDict):
    """Enhanced state with conversation context and summarization"""
    messages: Annotated[list[BaseMessage], add_messages]
    summary: str  # Running summary of conversation
    user_context: Dict[str, Any]  # User-specific context
    rag_sources: List[Dict[str, Any]]  # RAG sources from last query

class AdvancedChatService(IChatService):
    """
    Next-generation chat service using LangGraph with advanced memory management:
    - Persistent conversation state across sessions
    - Automatic conversation summarization for long chats
    - Smart context trimming to manage token limits
    - Cross-thread memory for user-specific context
    - RAG integration with source tracking
    """
    
    def __init__(self):
        self.llm = None
        self.graph = None
        self.checkpointer = None
        self.store = None
        
        # Initialize LLM
        self._init_llm()
        
        # Initialize LangGraph if available
        if LANGGRAPH_AVAILABLE:
            self._init_langgraph()
        else:
            logger.warning("⚠️ LangGraph not available, using fallback mode")
        
        logger.info("✅ AdvancedChatService initialized")

    def _init_llm(self):
        """Initialize the Gemini LLM"""
        if not settings.GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY not found")
            return
            
        try:
            self.llm = ChatGoogleGenerativeAI(
                api_key=settings.GEMINI_API_KEY,
                model=settings.GEMINI_MODEL_NAME,
                temperature=settings.GEMINI_TEMPERATURE,
                max_tokens=settings.GEMINI_MAX_TOKENS
            )
            logger.info(f"🤖 LLM initialized: {settings.GEMINI_MODEL_NAME}")
        except Exception as e:
            logger.error(f"Error initializing LLM: {e}")

    def _init_langgraph(self):
        """Initialize LangGraph with in-memory persistence for now"""
        try:
            # Use in-memory storage for now
            self.checkpointer = MemorySaver()
            logger.info("🗄️ Using in-memory storage")

            # Build the advanced conversation graph
            self._build_conversation_graph()
            
        except Exception as e:
            logger.error(f"Error initializing LangGraph: {e}")

    def _build_conversation_graph(self):
        """Build the LangGraph conversation workflow"""
        workflow = StateGraph(AdvancedChatState)
        
        # Add nodes
        workflow.add_node("analyze_input", self._analyze_input_node)
        workflow.add_node("manage_context", self._manage_context_node)
        workflow.add_node("rag_search", self._rag_search_node)
        workflow.add_node("generate_response", self._generate_response_node)
        workflow.add_node("summarize_if_needed", self._summarize_if_needed_node)
        
        # Add edges
        workflow.add_edge(START, "analyze_input")
        workflow.add_edge("analyze_input", "manage_context")
        workflow.add_edge("manage_context", "rag_search")
        workflow.add_edge("rag_search", "generate_response")
        workflow.add_edge("generate_response", "summarize_if_needed")
        
        # Compile with persistence
        self.graph = workflow.compile(
            checkpointer=self.checkpointer
        )
        
        logger.info("🔗 LangGraph workflow compiled successfully")

    async def _analyze_input_node(self, state: AdvancedChatState, config: RunnableConfig) -> Dict[str, Any]:
        """Analyze user input and determine processing strategy"""
        last_message = state["messages"][-1] if state["messages"] else None
        
        if not last_message:
            return {"user_context": {"input_type": "empty"}}
        
        content = last_message.content.lower() if hasattr(last_message, 'content') else ""
        
        # בדיקה מתקדמת לסוג הקלט
        input_type = "information_request"  # Default
        requires_rag = True  # Default to True for most cases
        
        # אם יש היסטוריית שיחה בהודעה - בוודאי צריך RAG
        if "היסטוריית השיחה:" in content:
            input_type = "contextual_information_request"
            requires_rag = True
        # דפוסים כלליים להתייחסות למידע קודם
        elif any(re.search(pattern, content) for pattern in [
            r"הציון שלי", r"המספר שלי", r"הטווח שלי",
            r"ציון \d+", r"\d+ זה", r"עם הציון", r"עם המספר",
            r"הציון הזה", r"המספר הזה"
        ]):
            input_type = "reference_question"
            requires_rag = True
        # ביטויים להתייחסות למידע קודם
        elif any(phrase in content for phrase in [
            "אמרת", "ציינת", "למה", "איך זה יכול", "איך יכול להיות",
            "לא הבנתי", "סתירה", "אבל קודם", "אבל אמרת", "אבל ציינת",
            "כתבת", "הסברת", "נאמר", "קודם אמרת", "בתשובה הקודמת"
        ]):
            input_type = "contextual_reference"
            requires_rag = True
        # ביטויים לנושאים אקדמיים
        elif any(term in content for term in [
            "ציון", "רמה", "רמות", "טווח", "טווחים", "דרגה", "קטגוריה",
            "באנגלית", "ברמה", "מתקדמים", "בסיסי", "בינוני", "גבוה",
            "מבחן", "בחינה", "הערכה", "פסיכומטרי", "אמיר"
        ]):
            input_type = "academic_question"
            requires_rag = True
        # זיהוי מספרים (ציונים אפשריים)
        elif re.search(r'\b\d{2,3}\b', content):
            input_type = "numerical_question"
            requires_rag = True
        # ברכות פשוטות
        elif any(word in content for word in ["שלום", "היי", "hello", "hi"]):
            input_type = "greeting"
            requires_rag = False
        # מידע אישי (שם)
        elif any(word in content for word in ["שמי", "קוראים לי", "my name"]):
            input_type = "personal_info"
            requires_rag = False
        # תודה
        elif any(word in content for word in ["תודה", "thanks", "thank you"]):
            input_type = "gratitude"
            requires_rag = False
        
        return {
            "user_context": {
                "input_type": input_type,
                "requires_rag": requires_rag,
                "content_length": len(content)
            }
        }

    async def _manage_context_node(self, state: AdvancedChatState, config: RunnableConfig) -> Dict[str, Any]:
        """Smart context management with trimming and summarization"""
        messages = state.get("messages", [])
        summary = state.get("summary", "")
        
        # Count tokens in current conversation
        total_tokens = count_tokens_approximately(messages)
        max_context_tokens = getattr(settings, 'MAX_CONTEXT_TOKENS', 8000)
        
        logger.info(f"📊 Context: {len(messages)} messages, ~{total_tokens} tokens")
        
        # If we're approaching token limit, apply smart trimming
        if total_tokens > max_context_tokens * 0.8:  # 80% threshold
            logger.info("🔄 Applying smart context trimming...")
            
            # Keep system message, recent messages, and create summary if needed
            trimmed_messages = trim_messages(
                messages,
                strategy="last",
                token_counter=count_tokens_approximately,
                max_tokens=max_context_tokens // 2,  # Keep half for current context
                start_on="human",
                include_system=True,
                allow_partial=False
            )
            
            # If we trimmed significant content, update summary
            if len(trimmed_messages) < len(messages) - 2:
                summary = await self._generate_summary(messages[:-10], summary)
                logger.info(f"📝 Updated conversation summary (trimmed {len(messages) - len(trimmed_messages)} messages)")
            
            return {
                "messages": trimmed_messages,
                "summary": summary,
                "user_context": {**state.get("user_context", {}), "trimmed": True}
            }
        
        return {"user_context": {**state.get("user_context", {}), "trimmed": False}}

    async def _rag_search_node(self, state: AdvancedChatState, config: RunnableConfig) -> Dict[str, Any]:
        """Perform RAG search if needed"""
        user_context = state.get("user_context", {})
        
        if not user_context.get("requires_rag", False) or not RAG_AVAILABLE:
            return {"rag_sources": []}
        
        try:
            last_message = state["messages"][-1]
            query = last_message.content if hasattr(last_message, 'content') else ""
            
            # 🔥 תיקון קריטי: העברת היסטוריית השיחה ל-RAG ב-Advanced Chat
            conversation_history = state.get("messages", [])
            
            if len(conversation_history) > 1:  # יש היסטוריה
                context_messages = []
                for msg in conversation_history[-10:]:  # רק 10 הודעות אחרונות
                    if hasattr(msg, 'content'):
                        if msg.__class__.__name__ == 'HumanMessage':
                            context_messages.append(f"משתמש: {msg.content}")
                        elif msg.__class__.__name__ == 'AIMessage':
                            context_messages.append(f"מערכת: {msg.content}")
                
                if context_messages:
                    conversation_context = "\n".join(context_messages[:-1])  # הכל חוץ מההודעה האחרונה
                    enhanced_query = f"היסטוריית השיחה:\n{conversation_context}\n\nשאלה נוכחית: {query}"
                    logger.info(f"🔗 [ADVANCED-CHAT] Enhanced query with {len(context_messages)-1} context messages")
                else:
                    enhanced_query = query
            else:
                enhanced_query = query
            
            rag_service = RAGService()
            rag_response = await rag_service.generate_answer(enhanced_query, search_method="hybrid")
            
            if rag_response and rag_response.get("sources"):
                logger.info(f"🔍 RAG found {len(rag_response['sources'])} sources")
                return {
                    "rag_sources": rag_response.get("sources", []),
                    "user_context": {**user_context, "rag_answer": rag_response.get("answer", "")}
                }
                
        except Exception as e:
            logger.warning(f"RAG search error: {e}")
        
        return {"rag_sources": []}

    async def _generate_response_node(self, state: AdvancedChatState, config: RunnableConfig) -> Dict[str, Any]:
        """Generate response using LLM with full context"""
        messages = state.get("messages", [])
        summary = state.get("summary", "")
        user_context = state.get("user_context", {})
        rag_sources = state.get("rag_sources", [])
        
        # Prepare system prompt with context
        system_content = settings.GEMINI_SYSTEM_PROMPT
        
        # Add summary if available
        if summary:
            system_content += f"\n\nסיכום קודם של השיחה: {summary}"
        
        # Add RAG context if available
        if user_context.get("rag_answer"):
            system_content += f"\n\nמידע רלוונטי מהמערכת: {user_context['rag_answer']}"
        
        # Add user context insights
        input_type = user_context.get("input_type", "information_request")
        if input_type == "greeting":
            system_content += "\n\nהמשתמש מברך - הגב בחום ובמענה אישי."
        elif input_type == "personal_info":
            system_content += "\n\nהמשתמש משתף מידע אישי - זכור את זה לעתיד."
        
        # Prepare final messages for LLM
        final_messages = [SystemMessage(content=system_content)] + messages
        
        try:
            # Track token usage
            await self._track_token_usage(
                messages[-1].content if messages else "", 
                "", 
                "preparing"
            )
            
            # Generate response
            response = await self.llm.ainvoke(final_messages)
            
            # Track final token usage
            await self._track_token_usage(
                messages[-1].content if messages else "",
                response.content,
                "advanced_chat"
            )
            
            logger.info(f"🤖 Generated response ({len(response.content)} chars)")
            
            return {"messages": [response]}
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            fallback_response = AIMessage(content="מצטער, אירעה שגיאה בעיבוד הבקשה. אנא נסה שוב.")
            return {"messages": [fallback_response]}

    async def _summarize_if_needed_node(self, state: AdvancedChatState, config: RunnableConfig) -> Dict[str, Any]:
        """Create or update conversation summary if the conversation is getting long"""
        messages = state.get("messages", [])
        summary = state.get("summary", "")
        
        # Check if we need to summarize (every 20 messages or so)
        if len(messages) % 20 == 0 and len(messages) > 10:
            try:
                new_summary = await self._generate_summary(messages[-20:], summary)
                logger.info("📋 Generated conversation summary")
                return {"summary": new_summary}
            except Exception as e:
                logger.warning(f"Summarization error: {e}")
        
        # אם לא נדרש סיכום, החזר את הסיכום הקיים כדי לעמוד בדרישות LangGraph
        return {"summary": summary}

    async def _generate_summary(self, messages: List[BaseMessage], existing_summary: str = "") -> str:
        """Generate a conversation summary"""
        try:
            summary_prompt = f"""
            סכם את השיחה הבאה בצורה קצרה ומדויקת. התמקד בנקודות המפתח ומידע חשוב שהמשתמש שיתף.
            
            {f"סיכום קודם: {existing_summary}" if existing_summary else ""}
            
            הודעות אחרונות:
            {chr(10).join([f"{msg.type}: {msg.content}" for msg in messages[-10:]])}
            
            סיכום מעודכן:
            """
            
            summary_response = await self.llm.ainvoke([HumanMessage(content=summary_prompt)])
            return summary_response.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return existing_summary

    async def _track_token_usage(self, user_message: str, ai_response: str, method: str = "advanced_chat"):
        """Track token usage"""
        try:
            # Estimate tokens
            input_tokens = len(user_message) // 4
            output_tokens = len(ai_response) // 4
            total_tokens = input_tokens + output_tokens + 100  # System overhead
            
            key_manager = get_key_manager()
            if hasattr(key_manager, 'record_usage'):
                current_key = await key_manager.get_available_key()
                if current_key and current_key.get('id'):
                    await key_manager.record_usage(current_key['id'], total_tokens, 1)
            elif hasattr(key_manager, 'track_usage'):
                key_manager.track_usage(total_tokens)
                
            logger.debug(f"📊 Tracked {total_tokens} tokens for {method}")
        except Exception as e:
            logger.warning(f"Token tracking error: {e}")

    async def process_chat_message(
        self,
        user_message: str,
        user_id: str = "anonymous",
        history: Optional[List[ChatMessageHistoryItem]] = None
    ) -> Dict[str, Any]:
        """Process chat message using advanced LangGraph workflow"""
        logger.info(f"🚀 [ADVANCED-CHAT] Processing message for user: {user_id}")
        
        if not LANGGRAPH_AVAILABLE or not self.graph:
            # Fallback to simple processing
            return await self._fallback_processing(user_message, user_id, history)
        
        try:
            # Prepare initial state
            initial_messages = []
            
            # Convert history to messages if provided
            if history:
                for msg in history[-20:]:  # Limit recent history
                    if msg.type == 'user':
                        initial_messages.append(HumanMessage(content=msg.content))
                    elif msg.type == 'bot':
                        initial_messages.append(AIMessage(content=msg.content))
            
            # Add current user message
            initial_messages.append(HumanMessage(content=user_message))
            
            # Configuration for the graph
            config = {
                "configurable": {
                    "thread_id": f"user_{user_id}",
                    "user_id": user_id
                }
            }
            
            # Run the advanced workflow
            result = await self.graph.ainvoke(
                {
                    "messages": initial_messages,
                    "summary": "",
                    "user_context": {},
                    "rag_sources": []
                },
                config
            )
            
            # Extract response
            final_messages = result.get("messages", [])
            last_response = final_messages[-1] if final_messages else None
            
            if last_response and hasattr(last_response, 'content'):
                response_content = last_response.content
                sources = result.get("rag_sources", [])
                
                logger.info(f"✅ [ADVANCED-CHAT] Response generated with {len(sources)} sources")
                
                return {
                    "response": response_content,
                    "sources": sources,
                    "chunks": len(sources),
                    "summary": result.get("summary", ""),
                    "context_trimmed": result.get("user_context", {}).get("trimmed", False)
                }
            else:
                raise Exception("No valid response generated")
                
        except Exception as e:
            logger.error(f"❌ [ADVANCED-CHAT] Error: {e}")
            return {
                "response": "מצטער, אירעה שגיאה בעיבוד הבקשה. אנא נסה שוב.",
                "sources": [],
                "chunks": 0
            }

    async def _fallback_processing(
        self,
        user_message: str,
        user_id: str = "anonymous",
        history: Optional[List[ChatMessageHistoryItem]] = None
    ) -> Dict[str, Any]:
        """Fallback processing without LangGraph"""
        logger.info(f"🔄 [FALLBACK] Processing message for user: {user_id}")
        
        try:
            # Simple context management
            messages = []
            if history:
                for msg in history[-10:]:  # Keep last 10 messages
                    if msg.type == 'user':
                        messages.append(HumanMessage(content=msg.content))
                    elif msg.type == 'bot':
                        messages.append(AIMessage(content=msg.content))
            
            messages.append(HumanMessage(content=user_message))
            
            # System prompt
            system_msg = SystemMessage(content=settings.GEMINI_SYSTEM_PROMPT + "\n\nזכור את ההקשר של השיחה ותן מענים רציפים.")
            final_messages = [system_msg] + messages
            
            # Generate response
            response = await self.llm.ainvoke(final_messages)
            
            await self._track_token_usage(user_message, response.content, "fallback")
            
            return {
                "response": response.content,
                "sources": [],
                "chunks": 0
            }
            
        except Exception as e:
            logger.error(f"❌ [FALLBACK] Error: {e}")
            return {
                "response": "מצטער, אירעה שגיאה בעיבוד הבקשה. אנא נסה שוב.",
                "sources": [],
                "chunks": 0
            }

    async def process_chat_message_stream(
        self,
        user_message: str,
        user_id: str = "anonymous",
        history: Optional[List[ChatMessageHistoryItem]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Process streaming chat message - fallback to regular processing for now"""
        
        # For now, process normally and yield the result
        # TODO: Implement true streaming with LangGraph
        result = await self.process_chat_message(user_message, user_id, history)
        
        # Simulate streaming by yielding chunks
        response_content = result.get("response", "")
        chunk_size = 50
        
        for i in range(0, len(response_content), chunk_size):
            chunk = response_content[i:i + chunk_size]
            yield {
                "type": "chunk",
                "content": chunk,
                "accumulated": response_content[:i + len(chunk)]
            }
            # Small delay to simulate real streaming
            await asyncio.sleep(0.1)
        
        # Final completion
        yield {
            "type": "complete",
            "content": response_content,
            "sources": result.get("sources", []),
            "chunks": result.get("chunks", 0)
        }
