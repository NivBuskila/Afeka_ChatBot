# src/ai/services/gemini_service.py
import logging
import time
import json
import requests
from typing import Dict, Any

from ai.core import config

logger = logging.getLogger(__name__)

class GeminiService:
    """Service for interacting with Google's Gemini API."""
    
    def __init__(self):
        """Initialize the Gemini service with configuration settings."""
        self.api_key = config.GEMINI_API_KEY
        self.api_url = config.GEMINI_API_URL
        self.model = config.GEMINI_MODEL
        self.temperature = config.GEMINI_TEMPERATURE
        self.max_output_tokens = config.GEMINI_MAX_OUTPUT_TOKENS
        logger.info(f"Initializing Gemini Service with model: {self.model}")

    def generate_response(self, message: str) -> Dict[str, Any]:
        """
        Sends a message to Gemini API and returns the response.
        
        Args:
            message: The user's message to send to Gemini
            
        Returns:
            Dict containing the response and metadata
        """
        start_time = time.time()
        logger.info(f"Sending message to Gemini API: {message[:50]}...")
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": message
                }]
            }],
            "generationConfig": {
                "temperature": self.temperature,
                "maxOutputTokens": self.max_output_tokens,
            }
        }
        
        headers = {
            "Content-Type": "application/json", 
            "x-goog-api-key": self.api_key
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                data=json.dumps(payload),
                timeout=30
            )
            
            response.raise_for_status()  # Raise exception for 4xx/5xx responses
            response_data = response.json()
            
            # Extract text response from Gemini API response
            gemini_response = "No response generated."
            if (response_data.get("candidates") and 
                response_data["candidates"][0].get("content") and 
                response_data["candidates"][0]["content"].get("parts")):
                gemini_response = response_data["candidates"][0]["content"]["parts"][0]["text"]
            
            logger.debug(f"Received response from Gemini API")
            
            # Return in the format expected by the API routes
            processing_time = time.time() - start_time
            result = {
                "result": gemini_response,
                "processing_time": round(processing_time, 3),
                "model": self.model,
                "keywords": [],  # Could extract keywords with additional processing
                "sentiment": "neutral",  # Could analyze sentiment with additional processing
            }
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Gemini API: {str(e)}")
            # Return error response in expected format
            return {
                "result": f"Sorry, I encountered an error: {str(e)}",
                "processing_time": round(time.time() - start_time, 3),
                "error": str(e),
                "keywords": [],
                "sentiment": "neutral"
            }

# Singleton instance
_gemini_service_instance = None

def get_gemini_service() -> GeminiService:
    """Returns a singleton instance of the GeminiService."""
    global _gemini_service_instance
    if _gemini_service_instance is None:
        _gemini_service_instance = GeminiService()
    return _gemini_service_instance 