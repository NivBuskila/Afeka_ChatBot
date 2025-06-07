# src/backend/app/repositories/base.py
"""Base repository implementation"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, TypeVar, Generic, Any
from uuid import UUID
import logging

# Import from domain - use the correct class name
from app.domain.base import BaseEntity

# Create type variable for entity types
EntityType = TypeVar('EntityType', bound=BaseEntity)

logger = logging.getLogger(__name__)


class BaseRepository(ABC, Generic[EntityType]):
    """Abstract base repository class"""
    
    def __init__(self, database_client):
        self.db = database_client
        self.logger = logger
    
    @property
    @abstractmethod
    def table_name(self) -> str:
        """Return the table name for this repository"""
        pass
    
    @property
    @abstractmethod
    def model_class(self) -> type[EntityType]:
        """Return the model class for this repository"""
        pass
    
    async def create(self, entity: EntityType) -> Optional[EntityType]:
        """Create a new entity"""
        try:
            data = self._entity_to_dict(entity)
            response = await self._execute_create(data)
            
            if response and response.data:
                return self._dict_to_entity(response.data[0])
            return None
            
        except Exception as e:
            self.logger.error(f"Error creating entity in {self.table_name}: {e}")
            raise
    
    async def find_by_id(self, entity_id: UUID) -> Optional[EntityType]:
        """Find entity by ID"""
        try:
            response = await self._execute_select({"id": str(entity_id)})
            
            if response and response.data:
                return self._dict_to_entity(response.data[0])
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding entity by ID in {self.table_name}: {e}")
            raise
    
    async def find_all(self, limit: int = 100) -> List[EntityType]:
        """Find all entities with optional limit"""
        try:
            response = await self._execute_select_all(limit)
            
            if response and response.data:
                return [self._dict_to_entity(item) for item in response.data]
            return []
            
        except Exception as e:
            self.logger.error(f"Error finding all entities in {self.table_name}: {e}")
            raise
    
    async def update(self, entity_id: UUID, updates: Dict[str, Any]) -> Optional[EntityType]:
        """Update entity by ID"""
        try:
            response = await self._execute_update(entity_id, updates)
            
            if response and response.data:
                return self._dict_to_entity(response.data[0])
            return None
            
        except Exception as e:
            self.logger.error(f"Error updating entity in {self.table_name}: {e}")
            raise
    
    async def delete(self, entity_id: UUID) -> bool:
        """Delete entity by ID"""
        try:
            response = await self._execute_delete(entity_id)
            return response is not None
            
        except Exception as e:
            self.logger.error(f"Error deleting entity in {self.table_name}: {e}")
            raise
    
    async def find_by_field(self, field_name: str, field_value: Any) -> List[EntityType]:
        """Find entities by field value"""
        try:
            response = await self._execute_select({field_name: field_value})
            
            if response and response.data:
                return [self._dict_to_entity(item) for item in response.data]
            return []
            
        except Exception as e:
            self.logger.error(f"Error finding entities by field in {self.table_name}: {e}")
            raise
    
    def _entity_to_dict(self, entity: EntityType) -> Dict[str, Any]:
        """Convert entity to dictionary for database storage"""
        if hasattr(entity, '__dict__'):
            data = entity.__dict__.copy()
            # Convert UUID to string
            if 'id' in data and isinstance(data['id'], UUID):
                data['id'] = str(data['id'])
            return data
        else:
            # Handle dataclass entities
            import dataclasses
            if dataclasses.is_dataclass(entity):
                data = dataclasses.asdict(entity)
                if 'id' in data and isinstance(data['id'], UUID):
                    data['id'] = str(data['id'])
                return data
            else:
                raise ValueError(f"Cannot convert entity of type {type(entity)} to dict")
    
    def _dict_to_entity(self, data: Dict[str, Any]) -> EntityType:
        """Convert dictionary from database to entity"""
        # Convert string ID back to UUID
        if 'id' in data and isinstance(data['id'], str):
            try:
                data['id'] = UUID(data['id'])
            except ValueError:
                pass  # Keep as string if not a valid UUID
        
        # Create entity instance
        model_class = self.model_class()
        
        # Handle dataclass entities
        import dataclasses
        if dataclasses.is_dataclass(model_class):
            return model_class(**data)
        else:
            # Handle regular class entities
            entity = model_class()
            for key, value in data.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
            return entity
    
    # Database-specific methods to be implemented by concrete repositories
    async def _execute_create(self, data: Dict[str, Any]):
        """Execute create operation - to be implemented by concrete repositories"""
        if hasattr(self.db, 'table'):
            return await self.db.table(self.table_name).insert(data).execute()
        else:
            raise NotImplementedError("Database client does not support table operations")
    
    async def _execute_select(self, filters: Dict[str, Any]):
        """Execute select operation - to be implemented by concrete repositories"""
        if hasattr(self.db, 'table'):
            query = self.db.table(self.table_name).select("*")
            for key, value in filters.items():
                query = query.eq(key, value)
            return await query.execute()
        else:
            raise NotImplementedError("Database client does not support table operations")
    
    async def _execute_select_all(self, limit: int):
        """Execute select all operation"""
        if hasattr(self.db, 'table'):
            return await self.db.table(self.table_name).select("*").limit(limit).execute()
        else:
            raise NotImplementedError("Database client does not support table operations")
    
    async def _execute_update(self, entity_id: UUID, updates: Dict[str, Any]):
        """Execute update operation"""
        if hasattr(self.db, 'table'):
            return await self.db.table(self.table_name).update(updates).eq("id", str(entity_id)).execute()
        else:
            raise NotImplementedError("Database client does not support table operations")
    
    async def _execute_delete(self, entity_id: UUID):
        """Execute delete operation"""
        if hasattr(self.db, 'table'):
            return await self.db.table(self.table_name).delete().eq("id", str(entity_id)).execute()
        else:
            raise NotImplementedError("Database client does not support table operations")