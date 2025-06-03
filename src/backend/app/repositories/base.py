# app/repositories/base.py
"""Base repository implementation"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic
from uuid import UUID
import logging
from supabase import Client
from app.domain.base import DomainEntity

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=DomainEntity)

class BaseRepository(Generic[T], ABC):
    """Base repository class with common CRUD operations"""
    
    def __init__(self, supabase_client: Optional[Client] = None):
        self.supabase_client = supabase_client
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @property
    @abstractmethod
    def table_name(self) -> str:
        """The name of the table in the database"""
        pass
    
    @property
    @abstractmethod
    def model_class(self) -> Type[T]:
        """The domain model class for this repository"""
        pass
    
    def _check_connection(self) -> bool:
        """Check if Supabase connection is available"""
        if not self.supabase_client:
            self.logger.warning(f"Supabase connection not available for {self.table_name}")
            return False
        return True
    
    def _handle_supabase_response(self, response: Any, operation: str) -> Any:
        """Handle Supabase response and extract data"""
        try:
            if hasattr(response, 'data'):
                self.logger.info(f"{operation} successful on {self.table_name}")
                return response.data
            else:
                self.logger.warning(f"No data returned from {operation} on {self.table_name}")
                return None
        except Exception as e:
            self.logger.error(f"Error handling {operation} response on {self.table_name}: {e}")
            raise
    
    async def find_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[T]:
        """Retrieve all records from the table"""
        if not self._check_connection():
            return []
        
        try:
            # Test if table exists
            test_query = self.supabase_client.table(self.table_name).select("count").limit(1)
            test_query.execute()
            
            # Build query
            query = self.supabase_client.table(self.table_name).select("*")
            
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)
                
            response = query.execute()
            data = self._handle_supabase_response(response, "find_all")
            
            if data:
                return [self.model_class(**item) for item in data]
            return []
            
        except Exception as e:
            self.logger.error(f"Error finding all records in {self.table_name}: {e}")
            return []
    
    async def find_by_id(self, id: Any) -> Optional[T]:
        """Find a record by ID"""
        if not self._check_connection():
            return None
            
        try:
            response = self.supabase_client.table(self.table_name).select("*").eq("id", id).single().execute()
            data = self._handle_supabase_response(response, f"find_by_id({id})")
            
            if data:
                return self.model_class(**data)
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding record by ID {id} in {self.table_name}: {e}")
            return None
    
    async def create(self, entity: T) -> Optional[T]:
        """Create a new record"""
        if not self._check_connection():
            return None
            
        try:
            # Convert to dictionary, removing None values
            data = entity.model_dump(exclude_none=True)
            
            # Remove id if it's None (let database generate it)
            if 'id' in data and data['id'] is None:
                del data['id']
                
            response = self.supabase_client.table(self.table_name).insert(data).execute()
            result_data = self._handle_supabase_response(response, "create")
            
            if result_data and len(result_data) > 0:
                return self.model_class(**result_data[0])
            return None
            
        except Exception as e:
            self.logger.error(f"Error creating record in {self.table_name}: {e}")
            return None
    
    async def update(self, id: Any, updates: Dict[str, Any]) -> Optional[T]:
        """Update a record by ID"""
        if not self._check_connection():
            return None
            
        try:
            # Remove None values from updates
            clean_updates = {k: v for k, v in updates.items() if v is not None}
            
            response = self.supabase_client.table(self.table_name).update(clean_updates).eq("id", id).execute()
            result_data = self._handle_supabase_response(response, f"update({id})")
            
            if result_data and len(result_data) > 0:
                return self.model_class(**result_data[0])
            return None
            
        except Exception as e:
            self.logger.error(f"Error updating record {id} in {self.table_name}: {e}")
            return None
    
    async def delete(self, id: Any) -> bool:
        """Delete a record by ID"""
        if not self._check_connection():
            return False
            
        try:
            response = self.supabase_client.table(self.table_name).delete().eq("id", id).execute()
            self._handle_supabase_response(response, f"delete({id})")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting record {id} from {self.table_name}: {e}")
            return False
    
    async def find_by_field(self, field: str, value: Any) -> List[T]:
        """Find records by a specific field value"""
        if not self._check_connection():
            return []
            
        try:
            response = self.supabase_client.table(self.table_name).select("*").eq(field, value).execute()
            data = self._handle_supabase_response(response, f"find_by_field({field}={value})")
            
            if data:
                return [self.model_class(**item) for item in data]
            return []
            
        except Exception as e:
            self.logger.error(f"Error finding records by {field}={value} in {self.table_name}: {e}")
            return []
    
    async def count(self) -> int:
        """Count total records in the table"""
        if not self._check_connection():
            return 0
            
        try:
            response = self.supabase_client.table(self.table_name).select("*", count="exact").execute()
            
            if hasattr(response, 'count') and response.count is not None:
                return response.count
            return 0
            
        except Exception as e:
            self.logger.error(f"Error counting records in {self.table_name}: {e}")
            return 0