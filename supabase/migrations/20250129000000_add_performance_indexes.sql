-- Performance optimization indexes migration
-- This migration adds essential indexes to improve query performance

-- Add GIN index for Hebrew text search on document chunks
CREATE INDEX IF NOT EXISTS idx_document_chunks_gin_text 
ON document_chunks USING gin(to_tsvector('hebrew', chunk_text));

-- Add index on section for faster section-based queries
CREATE INDEX IF NOT EXISTS idx_document_chunks_section 
ON document_chunks(section) WHERE section IS NOT NULL;

-- Add index on page_number for faster page-based queries
CREATE INDEX IF NOT EXISTS idx_document_chunks_page_number 
ON document_chunks(page_number) WHERE page_number IS NOT NULL;

-- Add composite index for document_id and chunk_index for faster chunk ordering
CREATE INDEX IF NOT EXISTS idx_document_chunks_doc_id_chunk_index 
ON document_chunks(document_id, chunk_index);

-- Add index on chunk_header for faster header-based searches
CREATE INDEX IF NOT EXISTS idx_document_chunks_chunk_header 
ON document_chunks USING gin(to_tsvector('hebrew', chunk_header)) 
WHERE chunk_header IS NOT NULL;

-- Add index on content_token_count for token-based filtering
CREATE INDEX IF NOT EXISTS idx_document_chunks_token_count 
ON document_chunks(content_token_count) WHERE content_token_count IS NOT NULL;

-- Add index on created_at for documents for faster date-based queries
CREATE INDEX IF NOT EXISTS idx_documents_created_at_desc 
ON documents(created_at DESC);

-- Add partial index for active documents only
CREATE INDEX IF NOT EXISTS idx_documents_active 
ON documents(id, name, created_at) WHERE created_at IS NOT NULL;

-- Add index for user analytics queries
CREATE INDEX IF NOT EXISTS idx_users_created_at_desc 
ON users(created_at DESC) WHERE created_at IS NOT NULL;

-- Add index for admin user queries
CREATE INDEX IF NOT EXISTS idx_admins_user_id_created_at 
ON admins(user_id, created_at);

-- Add indexes for chat session performance
CREATE INDEX IF NOT EXISTS idx_chat_sessions_created_at 
ON chat_sessions(created_at DESC) WHERE created_at IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_messages_created_at 
ON messages(created_at DESC) WHERE created_at IS NOT NULL;

-- Add index for API key usage tracking
CREATE INDEX IF NOT EXISTS idx_api_key_usage_created_at 
ON api_key_usage(created_at DESC, api_key_id);

-- Add comment explaining the performance improvements
COMMENT ON INDEX idx_document_chunks_gin_text IS 'GIN index for fast Hebrew full-text search on chunk content';
COMMENT ON INDEX idx_document_chunks_section IS 'Index for fast section-based filtering';
COMMENT ON INDEX idx_document_chunks_doc_id_chunk_index IS 'Composite index for efficient chunk ordering within documents';
COMMENT ON INDEX idx_documents_created_at_desc IS 'Descending index for recent documents queries';
COMMENT ON INDEX idx_users_created_at_desc IS 'Descending index for recent users analytics'; 