from abc import ABC, abstractmethod
from supabase import Client
from ..utils.common_types import Dict, Any, List, Optional
from ..utils.logger import get_logger
from ..core.exceptions import RepositoryError

logger = get_logger(__name__)

class BaseRepository(ABC):
    """Base repository with common Supabase operations"""
    
    def __init__(self, client: Client, table_name: str):
        """Initialize with Supabase client and table name"""
        self.client = client
        self.table_name = table_name
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
    
    def _handle_supabase_error(self, error: Exception, operation: str) -> None:
        """Common error handling for Supabase operations"""
        error_str = str(error)
        
        # Check for common Supabase errors
        if "PGRST116" in error_str or "0 rows" in error_str:
            raise RepositoryError(f"No data found for {operation}", status_code=404)
        
        # Log and re-raise as RepositoryError
        self.logger.error(f"Error in {operation}: {error_str}")
        raise RepositoryError(f"Failed to {operation}: {error_str}")
    
    def _check_response_data(self, response: Any, operation: str) -> Any:
        """Check if response has data and return it"""
        if hasattr(response, 'data'):
            return response.data
        else:
            self.logger.warning(f"No data returned from {operation}")
            return None
    
    async def safe_execute(self, query_func, operation: str):
        """Safely execute a Supabase query with error handling"""
        try:
            response = query_func()
            return self._check_response_data(response, operation)
        except Exception as e:
            if isinstance(e, RepositoryError):
                raise e
            self._handle_supabase_error(e, operation)
    
    # Common implementations that subclasses can use
    async def get_all_base(self, order_by: Optional[str] = None, desc: bool = True) -> List[Dict[str, Any]]:
        """Base implementation for get_all with common patterns"""
        try:
            query = self.client.table(self.table_name).select('*')
            if order_by:
                query = query.order(order_by, desc=desc)
            
            response = query.execute()
            
            if hasattr(response, 'data') and isinstance(response.data, list):
                return response.data
            else:
                self.logger.warning("No data or unexpected response format")
                return []
                
        except Exception as e:
            self.logger.error(f"Error retrieving records: {e}")
            raise RepositoryError(f"Failed to retrieve records: {e}")
    
    async def get_by_id_base(self, record_id: Any, id_field: str = 'id') -> Dict[str, Any]:
        """Base implementation for get_by_id with common patterns"""
        try:
            response = self.client.table(self.table_name).select('*').eq(id_field, record_id).single().execute()
            
            if hasattr(response, 'data') and response.data:
                return response.data
            else:
                self.logger.warning(f"Record with {id_field} {record_id} not found")
                raise RepositoryError(f"Record {record_id} not found", status_code=404)
                
        except Exception as e:
            if isinstance(e, RepositoryError):
                raise e
            
            # Handle Supabase specific "no rows" error
            error_str = str(e)
            if "PGRST116" in error_str or "0 rows" in error_str or "multiple (or no) rows returned" in error_str:
                self.logger.warning(f"Record with {id_field} {record_id} not found (Supabase: no rows)")
                raise RepositoryError(f"Record {record_id} not found", status_code=404)
                
            self.logger.error(f"Error retrieving record {record_id}: {e}")
            raise RepositoryError(f"Failed to retrieve record: {e}")
    
    @abstractmethod
    async def get_all(self) -> List[Dict[str, Any]]:
        """Get all records - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    async def get_by_id(self, record_id: Any) -> Dict[str, Any]:
        """Get record by ID - must be implemented by subclasses"""
        pass 