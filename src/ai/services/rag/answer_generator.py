"""
Answer Generator - Handles LLM-based answer generation
"""

import os
import asyncio
import logging
from typing import Dict, Any, Optional
import google.generativeai as genai

logger = logging.getLogger(__name__)

class AnswerGenerator:
    """Service for handling LLM-based answer generation"""
    
    def __init__(self, key_manager=None):
        self.key_manager = key_manager
        self.model = None
        
        try:
            from ...config.rag_config import get_llm_config
        except ImportError:
            from src.ai.config.rag_config import get_llm_config
        
        self.llm_config = get_llm_config()
        self._init_gemini_model()
        logger.info("🤖 AnswerGenerator initialized")
    
    def _init_gemini_model(self):
        """יצירת מודל Gemini עם הגדרות מהפרופיל"""
        fallback_key = os.getenv("GEMINI_API_KEY")
        if fallback_key:
            genai.configure(api_key=fallback_key)
            logger.info("🔑 Using GEMINI_API_KEY from environment for initialization")
        
        generation_config = genai.GenerationConfig(
            temperature=getattr(self.llm_config, 'TEMPERATURE', 0.7),
            max_output_tokens=getattr(self.llm_config, 'MAX_OUTPUT_TOKENS', 2048)
        )
        
        self.model = genai.GenerativeModel(
            model_name=getattr(self.llm_config, 'MODEL_NAME', 'gemini-pro'),
            generation_config=generation_config
        )
        logger.info("✅ Gemini model initialized")

    async def _track_generation_usage(self, prompt: str, response: str, key_id: Optional[int] = None):
        """Track token usage for text generation"""
        input_tokens = len(prompt) // 4
        output_tokens = len(response) // 4
        total_tokens = input_tokens + output_tokens
        logger.info(f"🔢 [GEN-TRACK] Estimated {total_tokens} tokens ({input_tokens} input + {output_tokens} output)")
        
        try:
            if self.key_manager and key_id:
                await self.key_manager.record_usage(key_id, total_tokens, 1)
                logger.info(f"🔢 [GEN-TRACK] Successfully tracked {total_tokens} tokens for key {key_id}")
            else:
                logger.warning("⚠️ [GEN-TRACK] No key_id provided or key_manager not available")
        except Exception as e:
            logger.error(f"❌ [GEN-TRACK] Failed to track usage: {e}")

    async def generate_with_retry(self, prompt: str, max_retries: int = 3) -> str:
        """Generate response with automatic retries and error handling"""
        last_error = None
        
        for attempt in range(max_retries):
            try:
                key_id = None
                if self.key_manager:
                    try:
                        api_key_data = await self.key_manager.get_available_key()
                        if api_key_data and 'key' in api_key_data:
                            genai.configure(api_key=api_key_data['key'])
                            key_id = api_key_data.get('id')
                            logger.debug(f"🔑 Using API key ID: {key_id} for generation (attempt {attempt + 1})")
                        else:
                            fallback_key = os.getenv("GEMINI_API_KEY")
                            if fallback_key:
                                genai.configure(api_key=fallback_key)
                                logger.debug(f"🔑 Using fallback key for generation (attempt {attempt + 1})")
                            else:
                                raise ValueError("No API key available")
                    except Exception as key_error:
                        logger.warning(f"Key manager error: {key_error}")
                        fallback_key = os.getenv("GEMINI_API_KEY")
                        if fallback_key:
                            genai.configure(api_key=fallback_key)
                        else:
                            raise ValueError("No API key available")
                else:
                    fallback_key = os.getenv("GEMINI_API_KEY")
                    if fallback_key:
                        genai.configure(api_key=fallback_key)
                    else:
                        raise ValueError("No API key available")
                
                response = self.model.generate_content(prompt)
                
                if response and hasattr(response, 'text') and response.text:
                    response_text = response.text.strip()
                    
                    if key_id:
                        try:
                            await self._track_generation_usage(prompt, response_text, key_id)
                        except Exception as track_error:
                            logger.warning(f"Failed to track token usage: {track_error}")
                    
                    return response_text
                
                if response and hasattr(response, 'prompt_feedback'):
                    feedback = response.prompt_feedback
                    if hasattr(feedback, 'block_reason'):
                        raise ValueError(f"Content blocked: {feedback.block_reason}")
                
                raise ValueError("Empty or invalid response from Gemini")
                
            except Exception as e:
                last_error = e
                logger.warning(f"Generation attempt {attempt + 1} failed: {str(e)}")
                
                error_str = str(e).lower()
                if any(keyword in error_str for keyword in ['quota', 'rate limit', 'resource_exhausted']):
                    logger.info(f"⚠️ API key quota/rate limit reached: {error_str}")
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                
        error_msg = f"Generation failed after {max_retries} attempts. Last error: {str(last_error)}"
        logger.error(error_msg)
        raise Exception(error_msg)

    async def generate_answer(self, prompt: str) -> str:
        """Generate answer using the configured model"""
        try:
            return await self.generate_with_retry(prompt)
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            raise

    def get_model_config(self) -> Dict[str, Any]:
        """Return current model configuration"""
        return {
            "model_name": getattr(self.llm_config, 'MODEL_NAME', 'gemini-pro'),
            "temperature": getattr(self.llm_config, 'TEMPERATURE', 0.7),
            "max_output_tokens": getattr(self.llm_config, 'MAX_OUTPUT_TOKENS', 2048)
        } 