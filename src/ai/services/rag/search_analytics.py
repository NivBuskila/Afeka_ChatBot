"""
Search Analytics - Handles search analytics and statistics
Extracted from RAGService to reduce coupling and improve maintainability
"""

import logging
from typing import Dict, Any, Optional
from supabase import Client

logger = logging.getLogger(__name__)

class SearchAnalytics:
    """Service for handling search analytics and statistics"""
    
    def __init__(self, supabase: Client):
        self.supabase = supabase
        
        # Import here to avoid circular imports
        try:
            from ...config.rag_config import get_database_config, get_performance_config
            from ...config.current_profile import get_current_profile
        except ImportError:
            from src.ai.config.rag_config import get_database_config, get_performance_config
            from src.ai.config.current_profile import get_current_profile
        
        self.db_config = get_database_config()
        self.performance_config = get_performance_config()
        self.get_current_profile = get_current_profile
        logger.info("📊 SearchAnalytics initialized")
    
    async def log_search_analytics(
        self, 
        query: str, 
        search_type: str, 
        results_count: int,
        top_score: float, 
        response_time_ms: int,
        document_id: Optional[int] = None
    ):
        """רושם נתוני חיפוש לטבלת analytics"""
        try:
            # Check if analytics is enabled
            if not getattr(self.performance_config, 'LOG_SEARCH_ANALYTICS', True):
                logger.debug("🔇 Search analytics logging is disabled")
                return
            
            analytics_data = {
                "query_text": query,
                "search_type": search_type,
                "results_count": results_count,
                "top_score": top_score,
                "response_time_ms": response_time_ms,
                "config_profile": self._get_current_profile_safe(),
            }

            # The document_id is currently an integer and causes a UUID error in the RPC.
            # Temporarily removing it from the log until the DB schema is fixed.
            # if document_id is not None:
            #     analytics_data["document_id"] = document_id

            function_name = getattr(self.db_config, 'LOG_ANALYTICS_FUNCTION', 'log_search_analytics')
            response = self.supabase.rpc(function_name, analytics_data).execute()
            
            # Check for errors in the response
            if hasattr(response, 'data') and response.data is None:
                logger.warning(f"⚠️ Failed to log search analytics: No data returned")
            elif isinstance(response, dict) and response.get('error'):
                logger.warning(f"⚠️ Failed to log search analytics: {response.get('error')}")
            else:
                logger.debug(f"✅ Successfully logged search analytics for query: {query[:50]}...")

        except Exception as e:
            # Handle cases where `response` might not be a standard object
            if "postgrest.exceptions.APIError" in str(type(e)):
                logger.warning(f"⚠️ Failed to log search analytics: {str(e)}")
            else:
                logger.warning(f"⚠️ Failed to log search analytics: {e}")
    
    def _get_current_profile_safe(self) -> str:
        """Safely get current profile with fallback"""
        try:
            return self.get_current_profile()
        except Exception as e:
            logger.warning(f"Failed to get current profile: {e}")
            return 'default'
    
    async def get_search_statistics(self, days_back: int = 30) -> Dict[str, Any]:
        """מחזיר סטטיסטיקות חיפוש"""
        try:
            # בדיקה אם analytics מופעל
            if not getattr(self.performance_config, 'LOG_SEARCH_ANALYTICS', True):
                return {"error": "Analytics disabled in configuration"}
                
            response = self.supabase.rpc('get_search_statistics', {
                'days_back': days_back
            }).execute()
            
            if response.data:
                stats = response.data[0] if isinstance(response.data, list) else response.data
                logger.info(f"📊 Retrieved search statistics for {days_back} days")
                return stats
            else:
                logger.warning("⚠️ No search statistics data returned")
                return {}
            
        except Exception as e:
            logger.error(f"❌ Error getting search statistics: {e}")
            return {"error": str(e)}
    
    async def get_analytics_summary(self, hours_back: int = 24) -> Dict[str, Any]:
        """Get analytics summary for recent period"""
        try:
            response = self.supabase.rpc('get_analytics_summary', {
                'hours_back': hours_back
            }).execute()
            
            if response.data:
                summary = response.data[0] if isinstance(response.data, list) else response.data
                logger.info(f"📊 Retrieved analytics summary for {hours_back} hours")
                return summary
            else:
                logger.warning("⚠️ No analytics summary data returned")
                return {}
                
        except Exception as e:
            logger.error(f"❌ Error getting analytics summary: {e}")
            return {"error": str(e)}
    
    async def get_top_queries(self, limit: int = 10, days_back: int = 7) -> list:
        """Get most frequent queries"""
        try:
            response = self.supabase.rpc('get_top_queries', {
                'query_limit': limit,
                'days_back': days_back
            }).execute()
            
            if response.data:
                logger.info(f"📊 Retrieved top {limit} queries for {days_back} days")
                return response.data
            else:
                logger.warning("⚠️ No top queries data returned")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error getting top queries: {e}")
            return []
    
    async def get_performance_metrics(self, days_back: int = 7) -> Dict[str, Any]:
        """Get performance metrics"""
        try:
            response = self.supabase.rpc('get_performance_metrics', {
                'days_back': days_back
            }).execute()
            
            if response.data:
                metrics = response.data[0] if isinstance(response.data, list) else response.data
                logger.info(f"📊 Retrieved performance metrics for {days_back} days")
                return metrics
            else:
                logger.warning("⚠️ No performance metrics data returned")
                return {}
                
        except Exception as e:
            logger.error(f"❌ Error getting performance metrics: {e}")
            return {"error": str(e)}
    
    def is_analytics_enabled(self) -> bool:
        """Check if analytics logging is enabled"""
        return getattr(self.performance_config, 'LOG_SEARCH_ANALYTICS', True)
    
    def get_analytics_config(self) -> Dict[str, Any]:
        """Get current analytics configuration"""
        return {
            "enabled": self.is_analytics_enabled(),
            "log_function": getattr(self.db_config, 'LOG_ANALYTICS_FUNCTION', 'log_search_analytics'),
            "current_profile": self._get_current_profile_safe()
        } 