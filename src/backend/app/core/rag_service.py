import logging
import time
import os
import sys
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import asyncio
from pathlib import Path

# Add the backend directory to sys.path to allow importing from services
backend_dir = Path(__file__).parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Import DocumentProcessor from the correct location
from services.document_processor import DocumentProcessor
from sentence_transformers import CrossEncoder # Ensure this is installed

import google.generativeai as genai # For the call_llm part

from langchain_community.vectorstores import SupabaseVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_experimental.text_splitter import SemanticChunker
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

logger = logging.getLogger(__name__)

async def call_llm_placeholder(prompt: str, model_name: str = "gemini-1.5-flash-latest") -> str:
    try:
        # API key configuration for genai is assumed to be done globally at app startup.
        model = genai.GenerativeModel(model_name)
        response = await model.generate_content_async(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Error calling LLM ({model_name}): {str(e)}")
        return f"Error in LLM response: {str(e)}"

class RAGService:
    _pool = ThreadPoolExecutor(max_workers=int(os.getenv("RERANK_THREADS", "4")))

    def __init__(self, doc_processor: DocumentProcessor, *, 
                 # enable_reranking: bool = True, # Replaced by env var based logic
                 default_search_limit: int = 6, 
                 default_search_threshold: float = 0.72,
                 cross_encoder_model_name: str = 'cross-encoder/ms-marco-MiniLM-L-6-v2',
                 llm_model_name: str = "gemini-1.5-flash-latest"):
        self.dp = doc_processor
        self.default_search_limit = default_search_limit
        self.default_search_threshold = default_search_threshold
        
        # Reranking configuration
        self._globally_enable_rerank = os.getenv("ENABLE_RERANK", "true").lower() == "true"
        self.should_rerank = self._globally_enable_rerank # Actual state, can be changed dynamically
        self._latency_cap_s = float(os.getenv("RERANK_LATENCY_CAP_S", "1.5")) # Default 1.5 seconds
        self._last_rerank_latency_s = 0.0

        self.cross_encoder = None
        self.llm_model_name = llm_model_name

        if self.should_rerank: # Initial check based on global env var
            try:
                self.cross_encoder = CrossEncoder(cross_encoder_model_name)
                logger.info(f"CrossEncoder model '{cross_encoder_model_name}' loaded successfully. Reranking enabled globally.")
            except ImportError:
                logger.error("sentence_transformers library not found. Install it to enable reranking. Reranking will be disabled.")
                self.should_rerank = False # Disable if library not found
                self._globally_enable_rerank = False # Also update global flag if essential lib is missing
            except Exception as e:
                logger.error(f"Failed to load CrossEncoder model '{cross_encoder_model_name}': {e}. Reranking disabled.")
                self.should_rerank = False # Disable on any other loading error
                self._globally_enable_rerank = False # Also update global flag if model loading fails
        else:
            logger.info("Reranking is globally disabled via ENABLE_RERANK environment variable or due to previous init failure.")
        
        # For statistics - initialize per instance
        self._search_time_total_s = 0.0
        self._rerank_time_total_s = 0.0
        self._llm_time_total_s = 0.0
        self._requests_processed_count = 0

    async def search(self, query: str, limit: Optional[int] = None, threshold: Optional[float] = None, use_hybrid: bool = False) -> List[Dict[str, Any]]:
        start_time = time.monotonic()
        search_limit = limit if limit is not None else self.default_search_limit
        search_threshold = threshold if threshold is not None else self.default_search_threshold
        logger.info(f"RAGService: Performing search for query ('{query[:30]}...') with limit={search_limit}, threshold={search_threshold}, hybrid={use_hybrid}")
        if use_hybrid:
            results = await self.dp.hybrid_search(query, limit=search_limit, threshold=search_threshold)
        else:
            results = await self.dp.search_documents(query, limit=search_limit, threshold=search_threshold)
        elapsed_time = time.monotonic() - start_time
        self._search_time_total_s += elapsed_time
        logger.info(f"RAGService: Search completed in {elapsed_time:.4f}s, found {len(results)} results.")
        return results

    async def rerank_results(self, query: str, search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not self.should_rerank or not self.cross_encoder or not search_results:
            # Add default rerank_score if not present (e.g. from similarity or if reranking is off)
            for r_item in search_results:
                if "rerank_score" not in r_item:
                    r_item["rerank_score"] = r_item.get("similarity", r_item.get("combined_score", 0.0)) 
            # If reranking is off, ensure results are still sorted by some meaningful score if available
            # (e.g. initial similarity from semantic or combined_score from hybrid)
            if not self.should_rerank:
                 return sorted(search_results, key=lambda x: x.get("rerank_score", 0.0), reverse=True)
            return search_results

        start_time = time.monotonic()
        # `chunk_text` from DB should contain header + original_text, which is good for reranking context.
        pairs_for_reranking = [[query, res.get("chunk_text", "")] for res in search_results]
        logger.info(f"RAGService: Reranking {len(pairs_for_reranking)} pairs using ThreadPoolExecutor...")
        
        loop = asyncio.get_running_loop()
        scores = await loop.run_in_executor(
            self._pool, 
            self.cross_encoder.predict, 
            pairs_for_reranking
        )
        
        for result_item, score_val in zip(search_results, scores):
            result_item["rerank_score"] = float(score_val)
        
        # Sort by the new rerank_score
        reranked_items = sorted(search_results, key=lambda x: x.get("rerank_score", 0.0), reverse=True)
        
        elapsed_time = time.monotonic() - start_time
        self._rerank_time_total_s += elapsed_time
        self._last_rerank_latency_s = elapsed_time # Store last rerank latency
        logger.info(f"RAGService: Reranking completed in {elapsed_time:.4f}s.")

        # Dynamic rerank disabling based on latency cap
        if self._globally_enable_rerank and self.should_rerank and self._last_rerank_latency_s > self._latency_cap_s:
            logger.warning(
                f"Reranking latency ({self._last_rerank_latency_s:.2f}s) exceeded cap ({self._latency_cap_s:.2f}s). "
                f"Dynamically disabling reranking for this RAGService instance to maintain performance."
            )
            self.should_rerank = False

        return reranked_items

    def _build_context_string(self, reranked_results: List[Dict[str, Any]], max_tokens_for_context: int = 2000, max_chunks_for_context: int = 3) -> str:
        context_parts_list = []
        approx_token_count = 0 # Using a simple word count for now
        
        # Results are already reranked, so iterate and take top ones that fit constraints
        for i, result_item in enumerate(reranked_results):
            if i >= max_chunks_for_context:
                logger.info(f"RAGService: Context builder hit max_chunks_for_context ({max_chunks_for_context}).")
                break

            # User's format: "[{r['header']}]\n{r['chunk_text']}"
            # `chunk_header` is the clean header. `chunk_text` is header + original_text.
            # This implies the header is repeated if we use both directly in this format.
            # Let's use: "Source [Header Title]:\nOriginal Text... (or full chunk_text if simpler)"
            # The prompt asked: part = f"[{r['header']}]\n{r['chunk_text']}"
            # This requires `header` and `chunk_text` keys in `result_item`.
            # Our DB provides `chunk_header` and `chunk_text` (which includes header).
            
            header_val = result_item.get("chunk_header", "Source") # Fallback if no chunk_header
            full_chunk_text_val = result_item.get("chunk_text", "") # This is header + original
            
            # This format directly uses the user's specification
            context_segment = f"[{header_val}]\n{full_chunk_text_val}"
            
            # Simple token estimation
            segment_tokens = len(context_segment.split())
            if approx_token_count + segment_tokens > max_tokens_for_context:
                logger.info(f"RAGService: Context builder hit max_tokens_for_context ({max_tokens_for_context}) adding chunk {i+1}.")
                break
            
            context_parts_list.append(context_segment)
            approx_token_count += segment_tokens

        logger.info(f"RAGService: Context built with {len(context_parts_list)} parts, approx. {approx_token_count} tokens.")
        return "\n\n---\n\n".join(context_parts_list) if context_parts_list else ""

    async def get_answer(self, query: str, 
                         use_hybrid_search: bool = False, 
                         add_sources_to_response: bool = True,
                         search_limit_override: Optional[int] = None, 
                         search_threshold_override: Optional[float] = None,
                         context_max_tokens: int = 2500, 
                         context_max_chunks: int = 3
                        ) -> Dict[str, Any]:
        self._requests_processed_count += 1
        operation_start_time = time.monotonic()

        raw_search_results = await self.search(query, limit=search_limit_override, threshold=search_threshold_override, use_hybrid=use_hybrid_search)
        reranked_search_results = await self.rerank_results(query, raw_search_results)
        
        # Use top N reranked results for context, actual N determined by _build_context_string
        context_string = self._build_context_string(reranked_search_results, 
                                                    max_tokens_for_context=context_max_tokens, 
                                                    max_chunks_for_context=context_max_chunks)

        # Construct prompt for LLM
        if context_string:
            llm_prompt = f"Context from documents:\n{context_string}\n\nBased on the context above, answer the following question.\nUser Question: {query}\n\nAssistant Answer:"
        else:
            logger.info("RAGService: No context built, proceeding with direct LLM call for the query.")
            llm_prompt = f"User Question: {query}\n\nAssistant Answer:"
        
        logger.info(f"RAGService: Generating LLM answer. Query: '{query[:30]}...'. Context length: {len(context_string)}")
        llm_call_start_time = time.monotonic()
        ai_response_text = await call_llm_placeholder(llm_prompt, model_name=self.llm_model_name)
        self._llm_time_total_s += (time.monotonic() - llm_call_start_time)
        logger.info(f"RAGService: LLM answer generated in {time.monotonic() - llm_call_start_time:.4f}s.")

        final_response = {
            "result": ai_response_text,
            "rag_used": bool(context_string),
            "rag_count": len(raw_search_results),
            "sources": [],
            "processing_time_s": round(time.monotonic() - operation_start_time, 3)
            # Add more debug info if needed
        }

        if add_sources_to_response and reranked_search_results:
            # Add sources from the chunks that likely contributed to context
            # The number of sources should correspond to context_max_chunks or less if token limit was hit earlier.
            num_sources_to_add = min(len(reranked_search_results), context_max_chunks)
            for res_item in reranked_search_results[:num_sources_to_add]:
                source_info = {
                    "section": res_item.get("chunk_header", "N/A"),
                    "page": res_item.get("page_number", "N/A"),
                    # Add any other useful source metadata, like document_id or chunk_id
                    "id": res_item.get("id"), 
                    "document_id": res_item.get("document_id"),
                    "rerank_score": round(res_item.get("rerank_score",0.0), 4) if self.should_rerank else None,
                    "initial_similarity": round(res_item.get("similarity",0.0), 4) if "similarity" in res_item else None
                }
                final_response["sources"].append(source_info)
        
        return final_response

    def get_service_stats(self) -> Dict[str, Any]:
        if self._requests_processed_count == 0:
            return {"message": "No requests processed by RAGService yet."}
        avg_search_time = (self._search_time_total_s * 1000 / self._requests_processed_count) if self._requests_processed_count else 0
        avg_rerank_time = (self._rerank_time_total_s * 1000 / self._requests_processed_count) if self._requests_processed_count and self.should_rerank else 0
        avg_llm_time = (self._llm_time_total_s * 1000 / self._requests_processed_count) if self._requests_processed_count else 0
        return {
            "total_requests_processed": self._requests_processed_count,
            "average_search_time_ms": round(avg_search_time, 2),
            "average_rerank_time_ms": round(avg_rerank_time, 2),
            "average_llm_processing_time_ms": round(avg_llm_time, 2),
            "total_search_time_s": round(self._search_time_total_s, 2),
            "total_rerank_time_s": round(self._rerank_time_total_s, 2),
            "total_llm_processing_time_s": round(self._llm_time_total_s, 2),
        }

    def get_runtime_config(self) -> Dict[str, Any]: # For debug endpoint
        config = {
            "default_search_limit": self.default_search_limit,
            "default_search_threshold": self.default_search_threshold,
            "reranking_globally_enabled_on_init": self._globally_enable_rerank,
            "reranking_currently_active": self.should_rerank,
            "rerank_latency_cap_seconds": self._latency_cap_s,
            "last_rerank_latency_seconds": round(self._last_rerank_latency_s, 4),
            "llm_model_name": self.llm_model_name,
        }
        if self.cross_encoder:
            # Accessing tokenizer.name_or_path might be specific to HuggingFace model wrappers
            # For CrossEncoder from sentence_transformers, it might not directly expose it this way.
            # Let's use the model name provided at init.
             config["cross_encoder_model_name"] = self.cross_encoder.model_name if hasattr(self.cross_encoder, 'model_name') else type(self.cross_encoder).__name__
        else:
            config["cross_encoder_model_name"] = None
        return config 