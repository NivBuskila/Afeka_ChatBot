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
        try:
            from ...config.rag_config import get_context_config, get_performance_config
        except ImportError:
            from src.ai.config.rag_config import get_context_config, get_performance_config
        
        self.context_config = get_context_config()
        self.performance_config = get_performance_config()
        logger.info("ContextBuilder initialized")
    
    def _clean_document_name(self, document_name: str) -> str:
        """Clean document name for clean and beautiful citation"""
        if not document_name:
            return "מסמך לא ידוע"
        
        clean_name = document_name.split('/')[-1].split('\\')[-1]
        
        extensions = ['.pdf', '.docx', '.doc', '.txt', '.md', '.html', '.rtf']
        for ext in extensions:
            if clean_name.lower().endswith(ext.lower()):
                clean_name = clean_name[:-len(ext)]
                break
        
        unwanted_patterns = [
            r'\s*cleaned\s*\(\d+\)',
            r'\s*cleaned\s*$',
            r'\s*copy\s*\(\d+\)',
            r'\s*copy\s*$',
            r'\s*\(\d+\)\s*$',
            r'\s*-\s*copy\s*$',
            r'\s*_copy\s*$',
        ]
        
        for pattern in unwanted_patterns:
            clean_name = re.sub(pattern, '', clean_name, flags=re.IGNORECASE)
        
        clean_name = re.sub(r'[-_.]+', ' ', clean_name)
        
        clean_name = re.sub(r'\s+', ' ', clean_name).strip()
        
        if not clean_name:
            return "מסמך לא ידוע"
        
        return clean_name

    def build_context(self, search_results: List[Dict[str, Any]]) -> Tuple[str, List[str], List[Dict[str, Any]]]:
        """Build context from search results"""
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
            
            # Estimate tokens
            estimated_tokens = len(chunk_content.split()) * getattr(self.performance_config, 'TOKEN_ESTIMATION_MULTIPLIER', 1.3)
            
            max_context_tokens = getattr(self.context_config, 'MAX_CONTEXT_TOKENS', 4000)
            if total_tokens + estimated_tokens > max_context_tokens:
                logger.info(f"Context token limit reached at chunk {i}")
                break
            
            # Add similarity score if available
            similarity_info = ""
            if 'similarity_score' in result:
                similarity_info = f" (דומיות: {result['similarity_score']:.3f})"
            elif 'combined_score' in result:
                similarity_info = f" (ציון: {result['combined_score']:.3f})"
            
            clean_document_name = self._clean_document_name(document_name)
            context_chunks.append(f"{clean_document_name}{similarity_info}:\n{chunk_content}")
            citations.append(clean_document_name)
            included_chunks.append(result)
            total_tokens += estimated_tokens
        
        context = "\n\n".join(context_chunks)
        
        logger.info(f"Built context from {len(context_chunks)} chunks, ~{int(total_tokens)} tokens")
        return context, citations, included_chunks

    def create_rag_prompt(self, query: str, context: str) -> str:
        """Create tailored prompt for RAG - now using centralized prompts"""
        try:
            from ...config.system_prompts import get_rag_prompt
            return get_rag_prompt(query, context)
        except ImportError:
            try:
                from src.ai.config.system_prompts import get_rag_prompt
                return get_rag_prompt(query, context)
            except ImportError:
                # Fallback if import fails - keep the old prompt structure
                base_prompt = f"""CRITICAL INSTRUCTION - MUST CITE SOURCES!
EVERY RESPONSE MUST END WITH: [מקורות: מקור X, מקור Y]
NO EXCEPTIONS! This format is MANDATORY!

אתה עוזר אקדמי של מכללת אפקה.

מידע מהתקנונים:
{context}

שאלה: {query}

INSTRUCTIONS:
1. Read all information above carefully
2. Answer in Hebrew based ONLY on the information provided in the sources above
3. Use specific details from the sources
4. MANDATORY: End with [מקורות: מקור 1, מקור 2] citing which sources you used

תשובה:"""
                return base_prompt

    def create_rag_prompt_with_conversation_context(self, query: str, context: str, conversation_context: str) -> str:
        """Create RAG prompt with separate conversation context - now using centralized prompts"""
        try:
            from ...config.system_prompts import get_rag_prompt
            return get_rag_prompt(query, context, conversation_context)
        except ImportError:
            try:
                from src.ai.config.system_prompts import get_rag_prompt
                return get_rag_prompt(query, context, conversation_context)
            except ImportError:
                # Fallback if import fails - keep the old prompt structure
                base_prompt = f"""CRITICAL INSTRUCTION - MUST CITE SOURCES!
EVERY RESPONSE MUST END WITH: [מקורות: מקור X, מקור Y]
NO EXCEPTIONS! This format is MANDATORY!

אתה עוזר אקדמי של מכללת אפקה.

{conversation_context}

מידע מהתקנונים:
{context}

השאלה הנוכחית: {query}

INSTRUCTIONS:
1. Read all information from the sources carefully
2. Answer the current question based ONLY on the information provided in the sources above
3. MANDATORY: End with [מקורות: מקור 1, מקור 2] citing which sources you used

תשובה:"""
                return base_prompt

    def extract_cited_sources(self, answer: str, available_citations: Optional[List[str]] = None) -> List[str]:
        """Extract sources cited by the model from the answer"""
        
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
                logger.info(f"Found sources with pattern #{i+1}: {sources_text}")
                break
        
        if not sources_text:
            logger.error("No sources found in the answer!")
            return []
        
        cited_sources = []
        
        potential_sources = [s.strip() for s in sources_text.split(',')]
        
        for source in potential_sources:
            clean_source = source.strip()
            
            clean_source = re.sub(r'^(מקור\s*\d*\s*[-:]?\s*)', '', clean_source, flags=re.IGNORECASE)
            clean_source = clean_source.strip()
            
            if clean_source:
                cited_sources.append(clean_source)
                logger.info(f"Cited source: {clean_source}")
        
        if not cited_sources and available_citations:
            logger.warning("No valid sources found - returning first source")
            return [available_citations[0]]
        
        if not cited_sources:
            logger.error(f"No valid sources found in text: {sources_text}")
        else:
            logger.info(f"Successfully cited sources: {cited_sources}")
        
        return cited_sources

    def get_cited_chunks(self, included_chunks: List[Dict[str, Any]], cited_source_names: List[str], available_citations: List[str]) -> List[Dict[str, Any]]:
        """Return the chunks that were actually cited by the model"""
        if not cited_source_names:
            logger.warning("No sources found in the model - returning first chunk")
            return included_chunks[:1] if included_chunks else []
        
        cited_chunks = []
        for cited_name in cited_source_names:
            best_match_index = -1
            best_match_score = 0
            
            for i, available_citation in enumerate(available_citations):
                similarity = self._calculate_citation_similarity(cited_name, available_citation)
                
                if similarity > best_match_score and similarity > 0.3:
                    best_match_score = similarity
                    best_match_index = i
            
            if best_match_index >= 0 and best_match_index < len(included_chunks):
                cited_chunks.append(included_chunks[best_match_index])
                logger.info(f"Found cited source: {cited_name} -> {available_citations[best_match_index]}")
            else:
                logger.warning(f"Source {cited_name} not found in context")
        
        if not cited_chunks:
            logger.warning("No valid chunks found from citations")
            return included_chunks[:1] if included_chunks else []
        
        return cited_chunks
    
    def _calculate_citation_similarity(self, cited_name: str, available_citation: str) -> float:
        """Calculate similarity between cited source name and available citation"""
        cited_words = set(cited_name.lower().split())
        available_words = set(available_citation.lower().split())
        
        if not cited_words or not available_words:
            return 0.0
        
        intersection = cited_words.intersection(available_words)
        union = cited_words.union(available_words)
        
        return len(intersection) / len(union) if union else 0.0

    def extract_relevant_chunk_segment(self, chunk_text: str, query: str, answer: str, max_length: int = 500) -> str:
        """Extract relevant segment from chunk"""
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