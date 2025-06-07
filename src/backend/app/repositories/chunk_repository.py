# src/backend/app/repositories/chunk_repository.py
"""Document Chunk repository implementation with vector search capabilities"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
import logging
import time

from .base import BaseRepository
from app.domain.rag import DocumentChunk, SearchResult, SearchType
from app.config.rag_settings import rag_settings
from app.core.rag_exceptions import SearchException, VectorSearchException, EmbeddingException

logger = logging.getLogger(__name__)


class ChunkRepository(BaseRepository[DocumentChunk]):
    """Repository for DocumentChunk entities with vector search capabilities"""
    
    @property
    def table_name(self) -> str:
        return "rag_document_chunks"
    
    @property
    def model_class(self) -> type[DocumentChunk]:
        return DocumentChunk
    
    async def find_by_document_id(self, document_id: UUID) -> List[DocumentChunk]:
        """Find all chunks for a specific document"""
        try:
            return await self.find_by_field("document_id", str(document_id))
        except Exception as e:
            self.logger.error(f"Error finding chunks by document ID {document_id}: {e}")
            raise SearchException(f"Failed to find chunks for document: {str(e)}")
    
    async def semantic_search(self, 
                            query_embedding: List[float], 
                            similarity_threshold: Optional[float] = None,
                            max_results: Optional[int] = None,
                            document_ids: Optional[List[UUID]] = None) -> List[DocumentChunk]:
        """Perform semantic search using vector embeddings"""
        start_time = time.time()
        
        try:
            # Use config defaults if not provided
            threshold = similarity_threshold or rag_settings.search_similarity_threshold
            limit = max_results or rag_settings.search_max_chunks_retrieved
            
            # Validate embedding
            if not query_embedding or len(query_embedding) != rag_settings.embedding_dimension:
                raise VectorSearchException(
                    f"Invalid query embedding dimension: expected {rag_settings.embedding_dimension}, got {len(query_embedding)}",
                    query_embedding_dimension=len(query_embedding)
                )
            
            # Call vector search function
            search_results = await self._execute_vector_search(
                query_embedding=query_embedding,
                similarity_threshold=threshold,
                match_count=limit,
                document_ids=document_ids
            )
            
            # Convert to domain entities and set similarity scores
            chunks = []
            for result in search_results:
                chunk = self._dict_to_entity(result)
                # Set similarity score from search result
                if 'similarity_score' in result:
                    chunk.set_similarity_score(result['similarity_score'])
                chunks.append(chunk)
            
            search_time = int((time.time() - start_time) * 1000)
            self.logger.info(f"Semantic search completed: {len(chunks)} results in {search_time}ms")
            
            return chunks
            
        except VectorSearchException:
            raise
        except Exception as e:
            search_time = int((time.time() - start_time) * 1000)
            self.logger.error(f"Error in semantic search after {search_time}ms: {e}")
            raise VectorSearchException(
                f"Semantic search failed: {str(e)}",
                function_name="semantic_search",
                database_error=str(e)
            )
    
    async def hybrid_search(self,
                          query_embedding: List[float],
                          query_text: str,
                          similarity_threshold: Optional[float] = None,
                          max_results: Optional[int] = None) -> List[DocumentChunk]:
        """Perform hybrid search combining semantic and keyword search"""
        try:
            # Get semantic results
            semantic_results = await self.semantic_search(
                query_embedding=query_embedding,
                similarity_threshold=similarity_threshold,
                max_results=max_results
            )
            
            # Get keyword results (simple text search for now)
            keyword_results = await self.keyword_search(
                query_text=query_text,
                max_results=max_results
            )
            
            # Combine and deduplicate results
            combined_results = self._combine_search_results(
                semantic_results, 
                keyword_results,
                max_results or rag_settings.search_max_chunks_retrieved
            )
            
            return combined_results
            
        except Exception as e:
            self.logger.error(f"Error in hybrid search: {e}")
            raise SearchException(
                f"Hybrid search failed: {str(e)}",
                search_type="hybrid"
            )
    
    async def keyword_search(self, 
                           query_text: str,
                           max_results: Optional[int] = None) -> List[DocumentChunk]:
        """Perform keyword-based text search in chunks"""
        try:
            limit = max_results or rag_settings.search_max_chunks_retrieved
            
            # Get all chunks (in a real implementation, this would use full-text search)
            all_chunks = await self.find_all(limit=limit * 3)  # Get more to filter
            
            # Simple keyword matching
            query_words = query_text.lower().split()
            matching_chunks = []
            
            for chunk in all_chunks:
                chunk_text_lower = chunk.chunk_text.lower()
                
                # Count word matches
                matches = sum(1 for word in query_words if word in chunk_text_lower)
                if matches > 0:
                    # Set a simple relevance score based on matches
                    relevance_score = matches / len(query_words)
                    chunk.set_similarity_score(relevance_score)
                    matching_chunks.append(chunk)
            
            # Sort by relevance and limit results
            matching_chunks.sort(key=lambda c: c.similarity_score or 0.0, reverse=True)
            return matching_chunks[:limit]
            
        except Exception as e:
            self.logger.error(f"Error in keyword search: {e}")
            raise SearchException(
                f"Keyword search failed: {str(e)}",
                query=query_text,
                search_type="keyword"
            )
    
    async def find_similar_chunks(self, 
                                chunk_id: UUID, 
                                similarity_threshold: float = 0.7,
                                max_results: int = 5) -> List[DocumentChunk]:
        """Find chunks similar to a given chunk"""
        try:
            # Get the reference chunk
            reference_chunk = await self.find_by_id(chunk_id)
            if not reference_chunk or not reference_chunk.has_embedding():
                raise SearchException(f"Chunk {chunk_id} not found or has no embedding")
            
            # Search for similar chunks
            similar_chunks = await self.semantic_search(
                query_embedding=reference_chunk.embedding,
                similarity_threshold=similarity_threshold,
                max_results=max_results + 1  # +1 to exclude the reference chunk
            )
            
            # Remove the reference chunk from results
            filtered_chunks = [chunk for chunk in similar_chunks if chunk.id != chunk_id]
            return filtered_chunks[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error finding similar chunks: {e}")
            raise SearchException(f"Failed to find similar chunks: {str(e)}")
    
    async def get_chunks_statistics(self) -> Dict[str, Any]:
        """Get statistics about chunks in the repository"""
        try:
            all_chunks = await self.find_all()
            
            # Calculate statistics
            total_chunks = len(all_chunks)
            chunks_with_embeddings = sum(1 for chunk in all_chunks if chunk.has_embedding())
            unique_documents = len(set(chunk.document_id for chunk in all_chunks))
            
            # Average chunk length
            total_length = sum(len(chunk.chunk_text) for chunk in all_chunks)
            avg_chunk_length = total_length / total_chunks if total_chunks > 0 else 0
            
            return {
                "total_chunks": total_chunks,
                "chunks_with_embeddings": chunks_with_embeddings,
                "embedding_coverage": chunks_with_embeddings / total_chunks if total_chunks > 0 else 0,
                "unique_documents": unique_documents,
                "avg_chunks_per_document": total_chunks / unique_documents if unique_documents > 0 else 0,
                "avg_chunk_length": int(avg_chunk_length)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting chunk statistics: {e}")
            raise SearchException(f"Failed to get chunk statistics: {str(e)}")
    
    async def delete_chunks_by_document_id(self, document_id: UUID) -> int:
        """Delete all chunks for a specific document"""
        try:
            chunks = await self.find_by_document_id(document_id)
            deleted_count = 0
            
            for chunk in chunks:
                success = await self.delete(chunk.id)
                if success:
                    deleted_count += 1
            
            self.logger.info(f"Deleted {deleted_count} chunks for document {document_id}")
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Error deleting chunks for document {document_id}: {e}")
            raise SearchException(f"Failed to delete chunks: {str(e)}")
    
    def _combine_search_results(self, 
                              semantic_results: List[DocumentChunk],
                              keyword_results: List[DocumentChunk],
                              max_results: int) -> List[DocumentChunk]:
        """Combine semantic and keyword search results with deduplication"""
        # Create a map to deduplicate by chunk ID
        combined_map = {}
        
        # Add semantic results with weight
        semantic_weight = 0.7  # Could come from config
        for chunk in semantic_results:
            chunk_id = str(chunk.id)
            score = (chunk.similarity_score or 0.0) * semantic_weight
            combined_map[chunk_id] = (chunk, score)
        
        # Add keyword results with weight
        keyword_weight = 0.3  # Could come from config
        for chunk in keyword_results:
            chunk_id = str(chunk.id)
            score = (chunk.similarity_score or 0.0) * keyword_weight
            
            if chunk_id in combined_map:
                # Combine scores
                existing_chunk, existing_score = combined_map[chunk_id]
                combined_score = existing_score + score
                combined_map[chunk_id] = (existing_chunk, combined_score)
            else:
                combined_map[chunk_id] = (chunk, score)
        
        # Sort by combined score and limit results
        sorted_results = sorted(
            combined_map.values(),
            key=lambda x: x[1],  # Sort by score
            reverse=True
        )
        
        # Extract chunks and update their similarity scores
        final_results = []
        for chunk, score in sorted_results[:max_results]:
            chunk.set_similarity_score(score)
            final_results.append(chunk)
        
        return final_results
    
    async def _execute_vector_search(self, 
                                   query_embedding: List[float],
                                   similarity_threshold: float,
                                   match_count: int,
                                   document_ids: Optional[List[UUID]] = None) -> List[Dict[str, Any]]:
        """Execute vector search using Supabase RPC function"""
        try:
            # Prepare RPC parameters
            rpc_params = {
                "query_embedding": query_embedding,
                "similarity_threshold": similarity_threshold,
                "match_count": match_count
            }
            
            # Add document filter if provided
            if document_ids:
                rpc_params["document_ids"] = [str(doc_id) for doc_id in document_ids]
            
            # Call the vector search function
            response = await self.db.rpc("rag_semantic_search", rpc_params).execute()
            
            if response.data:
                return response.data
            else:
                self.logger.warning("Vector search returned no data")
                return []
                
        except Exception as e:
            self.logger.error(f"Error executing vector search RPC: {e}")
            raise VectorSearchException(
                f"Vector search RPC call failed: {str(e)}",
                function_name="rag_semantic_search",
                database_error=str(e)
            )
    
    def _entity_to_dict(self, entity: DocumentChunk) -> Dict[str, Any]:
        """Convert DocumentChunk entity to dictionary for database storage"""
        data = super()._entity_to_dict(entity)
        
        # Handle datetime serialization
        if 'created_at' in data and isinstance(data['created_at'], datetime):
            data['created_at'] = data['created_at'].isoformat()
        
        # Ensure document_id is string
        if 'document_id' in data and isinstance(data['document_id'], UUID):
            data['document_id'] = str(data['document_id'])
        
        return data
    
    def _dict_to_entity(self, data: Dict[str, Any]) -> DocumentChunk:
        """Convert dictionary from database to DocumentChunk entity"""
        # Handle datetime deserialization
        if 'created_at' in data and isinstance(data['created_at'], str):
            try:
                data['created_at'] = datetime.fromisoformat(data['created_at'])
            except ValueError:
                data['created_at'] = datetime.utcnow()
        
        # Handle UUID conversion
        if 'document_id' in data and isinstance(data['document_id'], str):
            try:
                data['document_id'] = UUID(data['document_id'])
            except ValueError:
                self.logger.warning(f"Invalid document_id UUID: {data['document_id']}")
        
        return super()._dict_to_entity(data)