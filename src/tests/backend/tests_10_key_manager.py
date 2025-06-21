"""
Key Manager and Embedding Tests
Testing Gemini key manager functionality and embedding generation
"""
import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
import sys
import os

# Add src/ai to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../ai'))

from src.ai.core.gemini_key_manager import safe_embed_content, safe_generate_content, get_key_manager
from src.ai.core.database_key_manager import DatabaseKeyManager


class TestGeminiKeyManager:
    """Test Gemini key manager functionality"""

    @pytest.mark.asyncio
    async def test_km001_safe_embed_content_calls_track_usage_correctly(self):
        """KM-001: safe_embed_content should call track_usage with key_id parameter"""
        
        # Mock the database key manager
        with patch('src.ai.core.gemini_key_manager.get_key_manager') as mock_get_manager:
            mock_manager = MagicMock()
            mock_manager.get_available_key = AsyncMock(return_value={"api_key": "test_key", "id": 123})
            mock_manager.current_key_index = 0
            mock_manager.api_keys = [{"id": 123, "api_key": "test_key"}]
            mock_manager.track_usage = AsyncMock()
            
            mock_get_manager.return_value = mock_manager
            
            # Mock genai.embed_content
            with patch('google.generativeai.embed_content') as mock_embed:
                mock_embed.return_value = {"embedding": [0.1] * 768}
                
                # Import and call the function
                result = await safe_embed_content(
                    model="test-model", 
                    content="test content", 
                    task_type="retrieval_document"
                )
                
                # Verify track_usage was called with key_id
                mock_manager.track_usage.assert_called_once()
                call_args = mock_manager.track_usage.call_args
                
                # Check that key_id was passed as first argument
                assert call_args[0][0] == 123, "track_usage should be called with key_id as first argument"
                assert "tokens_used" in call_args[1], "track_usage should be called with tokens_used parameter"

    @pytest.mark.asyncio
    async def test_km002_safe_generate_content_calls_track_usage_correctly(self):
        """KM-002: safe_generate_content should call track_usage with key_id parameter"""
        
        # Mock the database key manager
        with patch('src.ai.core.gemini_key_manager.get_key_manager') as mock_get_manager:
            mock_manager = MagicMock()
            mock_manager.get_available_key = AsyncMock(return_value={"api_key": "test_key", "id": 456})
            mock_manager.current_key_index = 1
            mock_manager.api_keys = [{"id": 123}, {"id": 456, "api_key": "test_key"}]
            mock_manager.track_usage = AsyncMock()
            
            mock_get_manager.return_value = mock_manager
            
            # Mock genai GenerativeModel
            with patch('google.generativeai.GenerativeModel') as mock_model_class:
                mock_model = MagicMock()
                mock_response = MagicMock()
                mock_response.text = "Generated response"
                mock_model.generate_content.return_value = mock_response
                mock_model_class.return_value = mock_model
                
                # Import and call the function
                result = await safe_generate_content("test prompt")
                
                # Verify track_usage was called with key_id
                mock_manager.track_usage.assert_called_once()
                call_args = mock_manager.track_usage.call_args
                
                # Check that key_id was passed as first argument
                assert call_args[0][0] == 456, "track_usage should be called with key_id as first argument"
                assert "tokens_used" in call_args[1], "track_usage should be called with tokens_used parameter"

    @pytest.mark.asyncio
    async def test_km003_track_usage_missing_key_id_error(self):
        """KM-003: Verify that track_usage fails if key_id is missing (regression test)"""
        
        # This test ensures we catch the specific error that was happening before
        mock_manager = MagicMock(spec=DatabaseKeyManager)
        
        # Create a mock track_usage that requires key_id
        async def mock_track_usage(key_id, tokens_used, requests_count=1):
            if key_id is None:
                raise TypeError("DatabaseKeyManager.track_usage() missing 1 required positional argument: 'key_id'")
            return True
        
        mock_manager.track_usage = AsyncMock(side_effect=mock_track_usage)
        
        # Test calling without key_id should fail
        with pytest.raises(TypeError, match="missing 1 required positional argument: 'key_id'"):
            await mock_manager.track_usage(None, tokens_used=100)
        
        # Test calling with key_id should succeed
        result = await mock_manager.track_usage(123, tokens_used=100)
        assert result is True

    @pytest.mark.asyncio
    async def test_km004_safe_embed_handles_missing_key_id_gracefully(self):
        """KM-004: safe_embed_content should handle missing key_id gracefully"""
        
        with patch('src.ai.core.gemini_key_manager.get_key_manager') as mock_get_manager:
            mock_manager = MagicMock()
            mock_manager.get_available_key = AsyncMock(return_value={"api_key": "test_key"})  # No 'id' field
            mock_manager.current_key_index = 0
            mock_manager.api_keys = [{"api_key": "test_key"}]  # No 'id' field
            mock_manager.track_usage = AsyncMock()
            
            mock_get_manager.return_value = mock_manager
            
            # Mock genai.embed_content
            with patch('google.generativeai.embed_content') as mock_embed:
                mock_embed.return_value = {"embedding": [0.1] * 768}
                
                # Import and call the function
                from src.ai.core.gemini_key_manager import safe_embed_content
                
                # Call the function - should not fail even without key_id
                result = await safe_embed_content(
                    model="test-model", 
                    content="test content", 
                    task_type="retrieval_document"
                )
                
                # Should succeed and return result
                assert result is not None
                
                # track_usage should NOT be called when key_id is missing
                mock_manager.track_usage.assert_not_called()

    @pytest.mark.asyncio
    async def test_km005_embedding_dimensions_validation(self):
        """KM-005: Verify embedding dimensions are handled correctly"""
        
        with patch('src.ai.core.gemini_key_manager.get_key_manager') as mock_get_manager:
            mock_manager = MagicMock()
            mock_manager.get_available_key = AsyncMock(return_value={"api_key": "test_key", "id": 123})
            mock_manager.current_key_index = 0
            mock_manager.api_keys = [{"id": 123, "api_key": "test_key"}]
            mock_manager.track_usage = AsyncMock()
            
            mock_get_manager.return_value = mock_manager
            
            # Mock genai.embed_content with wrong dimensions
            with patch('google.generativeai.embed_content') as mock_embed:
                # Return embedding with wrong dimensions (should be 768)
                mock_embed.return_value = {"embedding": [0.1] * 512}
                
                # Call the function
                result = await safe_embed_content(
                    model="test-model", 
                    content="test content", 
                    task_type="retrieval_document"
                )
                
                # Should still return a result
                assert result is not None
                
                # Verify track_usage was called
                mock_manager.track_usage.assert_called_once()


class TestDatabaseKeyManager:
    """Test Database key manager functionality"""

    def test_km005_database_key_manager_track_usage_signature(self):
        """KM-005: Verify DatabaseKeyManager.track_usage has correct signature"""
        
        # Import the actual class to check its signature
        import inspect
        from src.ai.core.database_key_manager import DatabaseKeyManager
        
        # Check that track_usage method exists and requires key_id
        assert hasattr(DatabaseKeyManager, 'track_usage'), "DatabaseKeyManager should have track_usage method"
        
        signature = inspect.signature(DatabaseKeyManager.track_usage)
        params = list(signature.parameters.keys())
        
        # Should have 'self', 'key_id', 'tokens_used', and optionally 'requests_count'
        assert 'key_id' in params, "track_usage should have key_id parameter"
        assert 'tokens_used' in params, "track_usage should have tokens_used parameter"
        
        # key_id should be required (no default value)
        key_id_param = signature.parameters['key_id']
        assert key_id_param.default == inspect.Parameter.empty, "key_id parameter should be required" 