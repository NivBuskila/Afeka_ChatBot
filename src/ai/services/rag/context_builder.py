"""
Context Builder - Handles context assembly and prompt creation
"""

import re
import logging
from typing import List, Dict, Any, Tuple, Optional

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
            
            # Clean document name for citation
            clean_document_name = document_name.replace('.pdf', '').replace('_', ' ')
            context_chunks.append(f"{clean_document_name}{similarity_info}:\n{chunk_content}")
            citations.append(clean_document_name)
            included_chunks.append(result)
            total_tokens += estimated_tokens
        
        context = "\n\n".join(context_chunks)
        
        logger.info(f"Built context from {len(context_chunks)} chunks, ~{int(total_tokens)} tokens")
        return context, citations, included_chunks

    def create_rag_prompt(self, query: str, context: str) -> str:
        """יוצר prompt מותאם לשאלות תקנונים - now using centralized prompts"""
        try:
            from ...config.system_prompts import get_rag_prompt
            return get_rag_prompt(query, context)
        except ImportError:
            try:
                from src.ai.config.system_prompts import get_rag_prompt
                return get_rag_prompt(query, context)
            except ImportError:
                # Fallback if import fails - keep the old prompt structure
                base_prompt = f"""⚠️ CRITICAL INSTRUCTION - MUST CITE SOURCES! ⚠️
EVERY RESPONSE MUST END WITH: [מקורות: מקור X, מקור Y]
NO EXCEPTIONS! This format is MANDATORY!

אתה עוזר אקדמי של מכללת אפקה.

📚 מידע מהתקנונים:
{context}

❓ שאלה: {query}

INSTRUCTIONS:
1. Read all information above carefully
2. Answer in Hebrew based ONLY on the information provided in the sources above
3. Use specific details from the sources
4. ⚠️ MANDATORY: End with [מקורות: מקור 1, מקור 2] citing which sources you used ⚠️

תשובה:"""
                return base_prompt

    def create_rag_prompt_with_conversation_context(self, query: str, context: str, conversation_context: str) -> str:
        """יוצר prompt מותאם עם קונטקסט שיחה נפרד - now using centralized prompts"""
        try:
            from ...config.system_prompts import get_rag_prompt
            return get_rag_prompt(query, context, conversation_context)
        except ImportError:
            try:
                from src.ai.config.system_prompts import get_rag_prompt
                return get_rag_prompt(query, context, conversation_context)
            except ImportError:
                # Fallback if import fails - keep the old prompt structure
                base_prompt = f"""⚠️ CRITICAL INSTRUCTION - MUST CITE SOURCES! ⚠️
EVERY RESPONSE MUST END WITH: [מקורות: מקור X, מקור Y]
NO EXCEPTIONS! This format is MANDATORY!

אתה עוזר אקדמי של מכללת אפקה.

{conversation_context}

📚 מידע מהתקנונים:
{context}

❓ השאלה הנוכחית: {query}

INSTRUCTIONS:
1. Read all information from the sources carefully
2. Answer the current question based ONLY on the information provided in the sources above
3. ⚠️ MANDATORY: End with [מקורות: מקור 1, מקור 2] citing which sources you used ⚠️

תשובה:"""
                return base_prompt

    def extract_cited_sources(self, answer: str, available_citations: Optional[List[str]] = None) -> List[str]:
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
        
        cited_sources = []
        
        # Split by commas and clean up source names
        potential_sources = [s.strip() for s in sources_text.split(',')]
        
        for source in potential_sources:
            # Clean up the source name
            clean_source = source.strip()
            
            # Remove common prefixes
            clean_source = re.sub(r'^(מקור\s*\d*\s*[-:]?\s*)', '', clean_source, flags=re.IGNORECASE)
            clean_source = clean_source.strip()
            
            if clean_source:
                cited_sources.append(clean_source)
                logger.info(f"✅ מקור מצוטט: {clean_source}")
        
        if not cited_sources and available_citations:
            logger.warning("⚠️ לא נמצאו מקורות תקינים - מחזיר את המקור הראשון")
            return [available_citations[0]]
        
        if not cited_sources:
            logger.error(f"🚨 לא נמצאו מקורות תקינים בטקסט: {sources_text}")
        else:
            logger.info(f"✅ מקורות מצוטטים בהצלחה: {cited_sources}")
        
        return cited_sources

    def get_cited_chunks(self, included_chunks: List[Dict[str, Any]], cited_source_names: List[str], available_citations: List[str]) -> List[Dict[str, Any]]:
        """מחזיר את הchunks שבאמת צוטטו על ידי המודל"""
        if not cited_source_names:
            logger.warning("⚠️ לא נמצאו ציטוטים מהמודל - מחזיר chunk ראשון")
            return included_chunks[:1] if included_chunks else []
        
        cited_chunks = []
        for cited_name in cited_source_names:
            # Find matching citation
            best_match_index = -1
            best_match_score = 0
            
            for i, available_citation in enumerate(available_citations):
                # Calculate similarity between cited name and available citation
                similarity = self._calculate_citation_similarity(cited_name, available_citation)
                
                if similarity > best_match_score and similarity > 0.3:  # Minimum similarity threshold
                    best_match_score = similarity
                    best_match_index = i
            
            if best_match_index >= 0 and best_match_index < len(included_chunks):
                cited_chunks.append(included_chunks[best_match_index])
                logger.info(f"✅ מצא מקור מצוטט: {cited_name} -> {available_citations[best_match_index]}")
            else:
                logger.warning(f"⚠️ מקור {cited_name} לא נמצא בקונטקסט")
        
        if not cited_chunks:
            logger.warning("⚠️ לא נמצאו chunks תקינים מהציטוטים")
            return included_chunks[:1] if included_chunks else []
        
        return cited_chunks
    
    def _calculate_citation_similarity(self, cited_name: str, available_citation: str) -> float:
        """מחשב דמיון בין שם מקור מצוטט למקור זמין"""
        cited_words = set(cited_name.lower().split())
        available_words = set(available_citation.lower().split())
        
        if not cited_words or not available_words:
            return 0.0
        
        intersection = cited_words.intersection(available_words)
        union = cited_words.union(available_words)
        
        return len(intersection) / len(union) if union else 0.0

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