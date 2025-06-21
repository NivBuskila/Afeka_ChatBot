"""
Context Builder - Handles context assembly and prompt creation
"""

import re
import logging
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)

class ContextBuilder:
    """Service for handling context assembly and prompt creation"""
    
    def __init__(self):
        # Import here to avoid circular imports
        try:
            from ...config.rag_config import get_context_config, get_performance_config
        except ImportError:
            from src.ai.config.rag_config import get_context_config, get_performance_config
        
        self.context_config = get_context_config()
        self.performance_config = get_performance_config()
        logger.info("🔧 ContextBuilder initialized")
    
    def build_context(self, search_results: List[Dict[str, Any]]) -> Tuple[str, List[str], List[Dict[str, Any]]]:
        """בונה קונטקסט מתוצאות החיפוש"""
        context_chunks = []
        citations = []
        included_chunks = []
        total_tokens = 0
        
        max_chunks_for_context = min(
            len(search_results), 
            getattr(self.context_config, 'MAX_CHUNKS_FOR_CONTEXT', 10)
        )
        
        for i, result in enumerate(search_results[:max_chunks_for_context]):
            chunk_content = result.get('chunk_text', result.get('content', ''))
            document_name = result.get('document_name', f'מסמך {i+1}')
            
            # הערכת tokens
            estimated_tokens = len(chunk_content.split()) * getattr(self.performance_config, 'TOKEN_ESTIMATION_MULTIPLIER', 1.3)
            
            max_context_tokens = getattr(self.context_config, 'MAX_CONTEXT_TOKENS', 4000)
            if total_tokens + estimated_tokens > max_context_tokens:
                logger.info(f"Context token limit reached at chunk {i}")
                break
            
            # הוספת מידע על הציון דומיות אם זמין
            similarity_info = ""
            if 'similarity_score' in result:
                similarity_info = f" (דומיות: {result['similarity_score']:.3f})"
            elif 'combined_score' in result:
                similarity_info = f" (ציון: {result['combined_score']:.3f})"
            
            context_chunks.append(f"מקור {len(included_chunks)+1} - {document_name}{similarity_info}:\n{chunk_content}")
            citations.append(document_name)
            included_chunks.append(result)
            total_tokens += estimated_tokens
        
        context = "\n\n".join(context_chunks)
        
        logger.info(f"Built context from {len(context_chunks)} chunks, ~{int(total_tokens)} tokens")
        return context, citations, included_chunks

    def create_rag_prompt(self, query: str, context: str) -> str:
        """יוצר prompt מותאם לשאלות תקנונים"""
        
        has_conversation_history = "היסטוריית השיחה:" in query
        
        conversation_instruction = ""
        if has_conversation_history:
            conversation_instruction = """
🔗 CONVERSATION CONTEXT DETECTED!
- Read the conversation history carefully
- If user refers to previous information (scores, numbers, "you said") - give consistent answer
- Use phrases like "as I mentioned", "with the score you mentioned"
"""

        base_prompt = f"""⚠️ CRITICAL INSTRUCTION - MUST CITE SOURCES! ⚠️
EVERY RESPONSE MUST END WITH: [מקורות: מקור X, מקור Y]
NO EXCEPTIONS! This format is MANDATORY!

אתה עוזר אקדמי של מכללת אפקה.{conversation_instruction}

📚 מידע מהתקנונים:
{context}

❓ שאלה: {query}

INSTRUCTIONS:
1. Read all information above
2. Answer in Hebrew based on the information
3. For scores/ranges - check where the number falls
4. Give detailed accurate answer
5. ⚠️ MANDATORY: End with [מקורות: מקור 1, מקור 2] ⚠️

EXAMPLES OF CORRECT FORMAT:
"הטווח לרמה מתקדמים ב' הוא 120-133. ציון 125 נופל בטווח הזה. [מקורות: מקור 1]"
"שכר הלימוד 5000 ש"ח לסמסטר. [מקורות: מקור 2, מקור 3]"

⚠️ תשובה ללא [מקורות: ...] = תשובה שגויה! ⚠️

תשובה:"""

        return base_prompt

    def extract_cited_sources(self, answer: str) -> List[int]:
        """מחלץ את המקורות שציטט המודל מהתשובה"""
        
        patterns = [
            r'\[מקורות:\s*([^\]]+)\]',
            r'\[מקור:\s*([^\]]+)\]',
            r'מקורות:\s*([^\n\r]+)',
            r'מקור:\s*([^\n\r]+)',
            r'\(מקורות:\s*([^\)]+)\)',
        ]
        
        sources_text = None
        
        for i, pattern in enumerate(patterns):
            match = re.search(pattern, answer, re.IGNORECASE)
            if match:
                sources_text = match.group(1)
                logger.info(f"🔍 מקורות נמצאו עם פטרן #{i+1}: {sources_text}")
                break
        
        if not sources_text:
            logger.error("🚨 לא נמצאו מקורות מצוטטים בתשובה!")
            return []
        
        source_numbers = []
        source_pattern = r'מקור\s*(\d+)'
        source_matches = re.findall(source_pattern, sources_text, re.IGNORECASE)
        
        for match in source_matches:
            try:
                source_num = int(match)
                if 1 <= source_num <= 100:
                    source_numbers.append(source_num)
                else:
                    logger.warning(f"⚠️ מספר מקור לא סביר: {source_num}")
            except ValueError:
                logger.warning(f"⚠️ לא ניתן להמיר למספר: {match}")
                continue
        
        if not source_numbers:
            logger.error(f"🚨 לא נמצאו מספרי מקורות תקינים בטקסט: {sources_text}")
        else:
            logger.info(f"✅ מקורות מצוטטים בהצלחה: {source_numbers}")
        
        return source_numbers

    def get_cited_chunks(self, included_chunks: List[Dict[str, Any]], cited_source_numbers: List[int]) -> List[Dict[str, Any]]:
        """מחזיר את הchunks שבאמת צוטטו על ידי המודל"""
        if not cited_source_numbers:
            logger.warning("⚠️ לא נמצאו ציטוטים מהמודל - מחזיר chunk ראשון")
            return included_chunks[:1] if included_chunks else []
        
        cited_chunks = []
        for source_num in cited_source_numbers:
            index = source_num - 1
            if 0 <= index < len(included_chunks):
                cited_chunks.append(included_chunks[index])
                logger.info(f"✅ מצא מקור מצוטט {source_num}")
            else:
                logger.warning(f"⚠️ מקור {source_num} לא קיים בקונטקסט")
        
        if not cited_chunks:
            logger.warning("⚠️ לא נמצאו chunks תקינים מהציטוטים")
            return included_chunks[:1] if included_chunks else []
        
        return cited_chunks

    def extract_relevant_chunk_segment(self, chunk_text: str, query: str, answer: str, max_length: int = 500) -> str:
        """מחלץ קטע רלוונטי מהchunk"""
        if not chunk_text or len(chunk_text) <= max_length:
            return chunk_text
        
        try:
            query_words = set(query.lower().split())
            answer_words = set(answer.lower().split())
            important_words = query_words.union(answer_words)
            
            sentences = re.split(r'[.!?]\s+', chunk_text)
            
            sentence_scores = []
            for i, sentence in enumerate(sentences):
                sentence_lower = sentence.lower()
                score = 0
                
                for word in important_words:
                    if len(word) > 2 and word in sentence_lower:
                        score += 1
                
                sentence_scores.append((i, sentence, score))
            
            sentence_scores.sort(key=lambda x: x[2], reverse=True)
            
            selected_sentences = []
            current_length = 0
            
            for i, sentence, score in sentence_scores:
                if current_length + len(sentence) <= max_length:
                    selected_sentences.append((i, sentence))
                    current_length += len(sentence)
                else:
                    break
            
            selected_sentences.sort(key=lambda x: x[0])
            
            result = '. '.join([sentence for _, sentence in selected_sentences])
            
            if not result.strip():
                result = chunk_text[:max_length] + "..." if len(chunk_text) > max_length else chunk_text
            
            return result.strip()
            
        except Exception as e:
            logger.error(f"Error extracting relevant segment: {e}")
            return chunk_text[:max_length] + "..." if len(chunk_text) > max_length else chunk_text 