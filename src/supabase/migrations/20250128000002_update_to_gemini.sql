-- Migration to update existing database for Gemini embeddings
-- This migration handles the transition from OpenAI (1536 dimensions) to Gemini (768 dimensions)

-- Drop existing vector indexes
DROP INDEX IF EXISTS idx_document_chunks_embedding;
DROP INDEX IF EXISTS idx_documents_embedding;

-- Drop existing functions that use the old vector size
DROP FUNCTION IF EXISTS match_documents_semantic(vector, float, int);
DROP FUNCTION IF EXISTS match_documents_hybrid(vector, text, float, int);

-- Update existing tables to use 768-dimension vectors
-- Note: This will clear existing embeddings as vector dimensions cannot be changed
ALTER TABLE documents DROP COLUMN IF EXISTS embedding;
ALTER TABLE documents ADD COLUMN embedding vector(768);

ALTER TABLE document_chunks DROP COLUMN IF EXISTS embedding;
ALTER TABLE document_chunks ADD COLUMN embedding vector(768);

-- Update default embedding model
UPDATE documents SET embedding_model = 'models/embedding-001' WHERE embedding_model = 'text-embedding-ada-002';

-- Recreate indexes for new vector size
CREATE INDEX idx_document_chunks_embedding ON document_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX idx_documents_embedding ON documents USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Recreate functions with correct vector dimensions
CREATE OR REPLACE FUNCTION match_documents_semantic(
  query_embedding vector(768),
  match_threshold float DEFAULT 0.78,
  match_count int DEFAULT 10
)
RETURNS TABLE (
  id bigint,
  name text,
  content text,
  similarity float,
  chunk_index integer,
  document_id bigint
)
LANGUAGE sql STABLE
AS $$
  SELECT
    dc.id,
    d.name,
    dc.chunk_text as content,
    1 - (dc.embedding <=> query_embedding) as similarity,
    dc.chunk_index,
    dc.document_id
  FROM document_chunks dc
  JOIN documents d ON d.id = dc.document_id
  WHERE 1 - (dc.embedding <=> query_embedding) > match_threshold
  ORDER BY dc.embedding <=> query_embedding
  LIMIT match_count;
$$;

CREATE OR REPLACE FUNCTION match_documents_hybrid(
  query_embedding vector(768),
  query_text text,
  match_threshold float DEFAULT 0.78,
  match_count int DEFAULT 10
)
RETURNS TABLE (
  id bigint,
  name text,
  content text,
  similarity float,
  text_rank float,
  combined_score float,
  chunk_index integer,
  document_id bigint
)
LANGUAGE sql STABLE
AS $$
  SELECT
    dc.id,
    d.name,
    dc.chunk_text as content,
    1 - (dc.embedding <=> query_embedding) as similarity,
    ts_rank_cd(to_tsvector('english', dc.chunk_text), to_tsquery('english', query_text)) as text_rank,
    (1 - (dc.embedding <=> query_embedding)) * 0.7 + ts_rank_cd(to_tsvector('english', dc.chunk_text), to_tsquery('english', query_text)) * 0.3 as combined_score,
    dc.chunk_index,
    dc.document_id
  FROM document_chunks dc
  JOIN documents d ON d.id = dc.document_id
  WHERE 
    (1 - (dc.embedding <=> query_embedding) > match_threshold)
    OR 
    (to_tsvector('english', dc.chunk_text) @@ to_tsquery('english', query_text))
  ORDER BY combined_score DESC
  LIMIT match_count;
$$;

-- Reset processing status for documents that need reprocessing
UPDATE documents 
SET processing_status = 'pending', 
    content = NULL,
    embedding = NULL
WHERE processing_status = 'completed';

-- Clear existing chunks (they need to be regenerated with new embeddings)
DELETE FROM document_chunks;

-- Add comment about the migration
COMMENT ON TABLE documents IS 'Updated to use Gemini embeddings (768 dimensions) instead of OpenAI (1536 dimensions)'; 