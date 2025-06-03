-- Fix for hybrid search functionality
-- This migration creates/updates the hybrid_search_documents function that was missing

-- First, drop the function if it exists with any signature to avoid conflicts
DROP FUNCTION IF EXISTS hybrid_search_documents;

-- Create the hybrid_search_documents function with the expected parameters
CREATE OR REPLACE FUNCTION hybrid_search_documents(
  query_embedding vector(768),
  query_text text,
  match_threshold float DEFAULT 0.70, -- Adjusted default threshold for hybrid
  match_count int DEFAULT 10,
  semantic_weight float DEFAULT 0.6, -- semantic part weight
  keyword_weight float DEFAULT 0.4   -- keyword part weight
)
RETURNS TABLE (
  id bigint,              -- Chunk ID
  document_id bigint,     -- ID of the parent document
  document_name text,     -- Name of the parent document
  chunk_text text,        -- Chunk content (header + original text)
  chunk_header text,      -- The specific header for this chunk
  page_number integer,    -- Page number of the chunk
  section text,           -- Section identifier (same as chunk_header)
  similarity float,       -- Semantic similarity score
  text_match_rank float,  -- Keyword search rank score
  combined_score float    -- Weighted combined score
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
    dc.document_id,
    d.name as document_name,
    dc.chunk_text,
    dc.chunk_header,
    dc.page_number,
    dc.section,
    COALESCE(ss.semantic_similarity_score, 0.0) as similarity,
    COALESCE(ks.keyword_rank_score, 0.0) as text_match_rank,
    (
        COALESCE(ss.semantic_similarity_score, 0.0) * semantic_weight +
        COALESCE(ks.keyword_rank_score, 0.0) * keyword_weight
    ) as combined_score
  FROM document_chunks dc
  JOIN documents d ON d.id = dc.document_id
  LEFT JOIN semantic_search ss ON ss.chunk_id = dc.id
  LEFT JOIN keyword_search ks ON ks.chunk_id = dc.id
  -- Filter based on combined logic: semantic match OR keyword match, and combined score above threshold
  WHERE (COALESCE(ss.semantic_similarity_score, 0.0) > match_threshold OR COALESCE(ks.keyword_rank_score, 0.0) > 0) 
  ORDER BY combined_score DESC
  LIMIT match_count;
$$;

-- Also, create a simplified insert function for document chunks that doesn't require all fields
CREATE OR REPLACE FUNCTION insert_document_chunk_basic(
  p_document_id BIGINT,
  p_chunk_text TEXT,
  p_embedding vector(768),
  p_content_token_count INTEGER
)
RETURNS SETOF document_chunks
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  INSERT INTO document_chunks (
    document_id,
    chunk_text,
    embedding,
    content_token_count
  ) VALUES (
    p_document_id,
    p_chunk_text,
    p_embedding,
    p_content_token_count
  )
  RETURNING *;
END;
$$;

-- Add comment about the migration
COMMENT ON FUNCTION hybrid_search_documents IS 'Hybrid search function that combines vector similarity with full-text search for Hebrew documents';
COMMENT ON FUNCTION insert_document_chunk_basic IS 'Simple function to insert a document chunk with basic required fields'; 