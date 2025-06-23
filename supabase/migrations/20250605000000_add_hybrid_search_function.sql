-- Hybrid search function that combines semantic and keyword searching
-- This combines the power of vector similarity search with traditional full-text search

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
  document_name text,     -- Name of the document
  chunk_text text,        -- Text content of the chunk
  chunk_header text,      -- Header/title of the chunk if available
  page_number integer,    -- Page number where the chunk appears
  section text,           -- Section information
  similarity float,       -- Semantic similarity score (0-1)
  text_match_rank float,  -- Text match rank score
  combined_score float    -- Combined score for ranking
) 
LANGUAGE plpgsql
AS $$
BEGIN
  -- Query 1: Semantic search using vector similarity (higher limit to have enough candidates)
  RETURN QUERY
  WITH semantic_results AS (
    SELECT 
      dc.id,
      dc.document_id,
      d.name AS document_name,
      dc.chunk_text,
      dc.chunk_header,
      dc.page_number,
      dc.section,
      1 - (dc.embedding <=> query_embedding) AS similarity,
      0 AS text_match_rank,
      (1 - (dc.embedding <=> query_embedding)) * semantic_weight AS base_score
    FROM document_chunks dc
    JOIN documents d ON d.id = dc.document_id
    WHERE 1 - (dc.embedding <=> query_embedding) > match_threshold
    ORDER BY similarity DESC
    LIMIT (match_count * 2)
  ),
  -- Query 2: Full-text search using PostgreSQL full-text capabilities
  keyword_results AS (
    SELECT 
      dc.id,
      dc.document_id,
      d.name AS document_name,
      dc.chunk_text,
      dc.chunk_header,
      dc.page_number,
      dc.section,
      0 AS similarity,
      ts_rank_cd(to_tsvector('hebrew', dc.chunk_text), plainto_tsquery('hebrew', query_text)) AS text_match_rank,
      ts_rank_cd(to_tsvector('hebrew', dc.chunk_text), plainto_tsquery('hebrew', query_text)) * keyword_weight AS base_score
    FROM document_chunks dc
    JOIN documents d ON d.id = dc.document_id
    WHERE to_tsvector('hebrew', dc.chunk_text) @@ plainto_tsquery('hebrew', query_text)
    ORDER BY text_match_rank DESC
    LIMIT (match_count * 2)
  ),
  -- Combine both result sets
  combined_results AS (
    -- Results from semantic search
    SELECT 
      sr.id, 
      sr.document_id,
      sr.document_name,
      sr.chunk_text,
      sr.chunk_header,
      sr.page_number,
      sr.section,
      sr.similarity,
      COALESCE(kr.text_match_rank, 0) AS text_match_rank,
      sr.base_score + COALESCE(kr.base_score, 0) AS combined_score
    FROM semantic_results sr
    LEFT JOIN keyword_results kr ON sr.id = kr.id
    
    UNION
    
    -- Results from keyword search that weren't in semantic results
    SELECT 
      kr.id, 
      kr.document_id,
      kr.document_name,
      kr.chunk_text,
      kr.chunk_header,
      kr.page_number,
      kr.section,
      COALESCE(sr.similarity, 0) AS similarity,
      kr.text_match_rank,
      kr.base_score + COALESCE(sr.base_score, 0) AS combined_score
    FROM keyword_results kr
    LEFT JOIN semantic_results sr ON kr.id = sr.id
    WHERE sr.id IS NULL
  )
  -- Final results, ordered by combined score
  SELECT 
    cr.id, 
    cr.document_id,
    cr.document_name,
    cr.chunk_text,
    cr.chunk_header,
    cr.page_number,
    cr.section,
    cr.similarity,
    cr.text_match_rank,
    cr.combined_score
  FROM combined_results cr
  WHERE cr.combined_score > (match_threshold * semantic_weight)
  ORDER BY cr.combined_score DESC
  LIMIT match_count;
END;
$$; 