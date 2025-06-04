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

-- Recreate functions with correct vector dimensions and new fields
CREATE OR REPLACE FUNCTION match_documents_semantic(
  query_embedding vector(768),
  match_threshold float DEFAULT 0.78,
  match_count int DEFAULT 10
)
RETURNS TABLE (
  id bigint,              -- Chunk ID
  document_name text,     -- Name of the parent document
  chunk_text text,        -- Chunk content (header + original text)
  chunk_header text,      -- The specific header for this chunk
  page_number integer,    -- Page number of the chunk
  section text,           -- Section identifier (same as chunk_header)
  similarity float,
  chunk_index integer,
  document_id bigint      -- ID of the parent document
)
LANGUAGE sql STABLE
AS $$
  SELECT
    dc.id,
    d.name as document_name,
    dc.chunk_text,        -- This is already header + original
    dc.chunk_header,
    dc.page_number,
    dc.section,
    1 - (dc.embedding <=> query_embedding) as similarity, -- Higher is better
    dc.chunk_index,
    dc.document_id
  FROM document_chunks dc
  JOIN documents d ON d.id = dc.document_id
  WHERE 1 - (dc.embedding <=> query_embedding) > match_threshold
  ORDER BY similarity DESC -- Order by calculated similarity
  LIMIT match_count;
$$;

CREATE OR REPLACE FUNCTION match_documents_hybrid(
  query_embedding vector(768),
  query_text text,
  match_threshold float DEFAULT 0.70, -- Adjusted default threshold for hybrid
  match_count int DEFAULT 10,
  semantic_weight float DEFAULT 0.6, -- semantic part weight
  keyword_weight float DEFAULT 0.4   -- keyword part weight
)
RETURNS TABLE (
  id bigint,              -- Chunk ID
  document_name text,     -- Name of the parent document
  chunk_text text,        -- Chunk content (header + original text)
  chunk_header text,      -- The specific header for this chunk
  page_number integer,    -- Page number of the chunk
  section text,           -- Section identifier (same as chunk_header)
  similarity float,       -- Semantic similarity score
  text_rank float,        -- Keyword search rank score
  combined_score float,   -- Weighted combined score
  chunk_index integer,
  document_id bigint      -- ID of the parent document
)
LANGUAGE sql STABLE
AS $$
  WITH semantic_search AS (
    SELECT
      dc.id as chunk_id,
      1 - (dc.embedding <=> query_embedding) AS semantic_similarity_score
    FROM document_chunks dc
    -- No WHERE clause here to allow ranking even below threshold for combining with keyword results
  ),
  keyword_search AS (
    SELECT
      dc.id as chunk_id,
      ts_rank_cd(to_tsvector('hebrew', dc.chunk_text), plainto_tsquery('hebrew', query_text)) AS keyword_rank_score
    FROM document_chunks dc
    WHERE to_tsvector('hebrew', dc.chunk_text) @@ plainto_tsquery('hebrew', query_text)
  )
  SELECT
    dc.id,
    d.name as document_name,
    dc.chunk_text,
    dc.chunk_header,
    dc.page_number,
    dc.section,
    COALESCE(ss.semantic_similarity_score, 0.0) as similarity,
    COALESCE(ks.keyword_rank_score, 0.0) as text_rank,
    (
        COALESCE(ss.semantic_similarity_score, 0.0) * semantic_weight +
        COALESCE(ks.keyword_rank_score, 0.0) * keyword_weight
    ) as combined_score,
    dc.chunk_index,
    dc.document_id
  FROM document_chunks dc
  JOIN documents d ON d.id = dc.document_id
  LEFT JOIN semantic_search ss ON ss.chunk_id = dc.id
  LEFT JOIN keyword_search ks ON ks.chunk_id = dc.id
  -- Filter based on combined logic: semantic match OR keyword match, and combined score above threshold
  WHERE (COALESCE(ss.semantic_similarity_score, 0.0) > match_threshold OR COALESCE(ks.keyword_rank_score, 0.0) > 0) 
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