"""
Vector utilities for handling embedding dimensions and conversions
"""
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

def truncate_vector_to_768(vector: List[float]) -> List[float]:
    """
    Truncate vector to 768 dimensions (Gemini embedding size)
    
    Args:
        vector: Vector to truncate
        
    Returns:
        Vector with 768 dimensions
    """
    if not vector:
        logger.warning("Empty vector provided for truncation")
        return []
        
    if len(vector) <= 768:
        # Vector already has 768 dimensions or less
        if len(vector) < 768:
            logger.warning(f"Vector has only {len(vector)} dimensions, padding with zeros to 768")
            return vector + [0.0] * (768 - len(vector))
        return vector
    
    # Truncate to 768 dimensions
    logger.info(f"Truncating vector from {len(vector)} to 768 dimensions")
    return vector[:768]

def validate_vector_dimensions(vector: List[float], expected_dims: int = 768) -> bool:
    """
    Check if the vector has the correct size
    
    Args:
        vector: Vector to check
        expected_dims: Expected number of dimensions (default: 768)
        
    Returns:
        True if the Vector has the correct size
    """
    if not vector:
        logger.error("Empty vector provided for validation")
        return False
        
    if len(vector) != expected_dims:
        logger.error(f"Vector dimension mismatch: got {len(vector)}, expected {expected_dims}")
        return False
        
    return True

def ensure_768_dimensions(vector: List[float]) -> List[float]:
    """
    Verify that the vector has exactly 768 dimensions
    
    Args:
        vector: Vector to process
        
    Returns:
        Vector with exactly 768 dimensions
    """
    if not vector:
        logger.error("Cannot process empty vector")
        return [0.0] * 768  # Return zero vector as fallback
        
    if len(vector) == 768:
        return vector
    elif len(vector) > 768:
        logger.warning(f"Truncating vector from {len(vector)} to 768 dimensions")
        return vector[:768]
    else:
        logger.warning(f"Padding vector from {len(vector)} to 768 dimensions")
        return vector + [0.0] * (768 - len(vector))

def convert_openai_to_gemini_dimensions(openai_vector: List[float]) -> List[float]:
    """
    Convert vector from OpenAI (1536 dims) to Gemini (768 dims)
    
    Args:
        openai_vector: Vector from OpenAI with 1536 dimensions
        
    Returns:
        Vector with 768 dimensions
    """
    if not openai_vector:
        logger.error("Empty OpenAI vector provided")
        return [0.0] * 768
        
    if len(openai_vector) != 1536:
        logger.warning(f"Expected 1536 dimensions for OpenAI vector, got {len(openai_vector)}")
        
    # Simply truncate to the first 768 dimensions
    # Alternatively, do pooling or averaging of every 2 elements
    return ensure_768_dimensions(openai_vector)

def average_pooling_conversion(vector: List[float], target_dims: int = 768) -> List[float]:
    """
    Conversion of vector using average pooling
    
    Args:
        vector: Original vector
        target_dims: Target number of dimensions
        
    Returns:
        Vector with target_dims dimensions
    """
    if not vector:
        return [0.0] * target_dims
        
    if len(vector) <= target_dims:
        return ensure_768_dimensions(vector)
        
    # Calculate window size
    pool_size = len(vector) // target_dims
    remainder = len(vector) % target_dims
    
    pooled = []
    idx = 0
    
    for i in range(target_dims):
        # Current window size
        window_size = pool_size + (1 if i < remainder else 0)
        
        # Calculate average of the window
        window_sum = sum(vector[idx:idx + window_size])
        pooled.append(window_sum / window_size)
        
        idx += window_size
    
    return pooled

def log_vector_info(vector: List[float], name: str = "Vector") -> None:
    """
    Log information about vector for debugging
    
    Args:
        vector: Vector to check
        name: Name of the vector
    """
    if not vector:
        logger.info(f"{name}: Empty vector")
        return
        
    logger.info(f"{name}: {len(vector)} dimensions")
    logger.debug(f"{name} first 5 values: {vector[:5]}")
    logger.debug(f"{name} last 5 values: {vector[-5:]}")
    
    # Check for non-numeric values
    if any(not isinstance(x, (int, float)) for x in vector):
        logger.warning(f"{name}: Contains non-numeric values")
        
    # Check for NaN or infinity values
    import math
    nan_count = sum(1 for x in vector if math.isnan(x) if isinstance(x, (int, float)))
    inf_count = sum(1 for x in vector if math.isinf(x) if isinstance(x, (int, float)))
    
    if nan_count > 0:
        logger.error(f"{name}: Contains {nan_count} NaN values")
    if inf_count > 0:
        logger.error(f"{name}: Contains {inf_count} infinity values") 