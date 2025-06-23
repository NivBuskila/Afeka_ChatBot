-- Fix Hebrew Full-Text Search
-- This migration fixes the hybrid_search_documents function to work properly with Hebrew text

-- Drop the existing function
DROP FUNCTION IF EXISTS hybrid_search_documents;

-- Create improved hybrid search function that works with Hebrew
CREATE OR REPLACE FUNCTION hybrid_search_documents(
  query_embedding vector(768),
  query_text text,
  match_threshold float DEFAULT 0.70,
  match_count int DEFAULT 10,
  semantic_weight float DEFAULT 0.6,
  keyword_weight float DEFAULT 0.4
)
RETURNS TABLE (
  id bigint,
  document_id bigint,
  document_name text,
  chunk_text text,
  chunk_header text,
  page_number integer,
  section text,
  similarity float,
  text_match_rank float,
  combined_score float
)
LANGUAGE sql STABLE
AS $$
  WITH semantic_search AS (
    SELECT
      dc.id as chunk_id,
      1 - (dc.embedding <=> query_embedding) AS semantic_similarity_score
    FROM document_chunks dc
  ),
  keyword_search AS (
    SELECT
      dc.id as chunk_id,
      CASE 
        -- Exact phrase match gets highest score
        WHEN dc.chunk_text ILIKE '%' || query_text || '%' THEN 1.0
        -- Individual word matches get good scores
        WHEN dc.chunk_text ILIKE '%' || split_part(query_text, ' ', 1) || '%' 
          OR dc.chunk_text ILIKE '%' || split_part(query_text, ' ', 2) || '%'
          OR dc.chunk_text ILIKE '%' || split_part(query_text, ' ', 3) || '%' THEN 0.8
        -- Partial matches get lower scores
        WHEN dc.chunk_text ILIKE '%' || left(query_text, length(query_text)/2) || '%' THEN 0.6
        -- Fall back to PostgreSQL full-text search for other languages
        ELSE GREATEST(
          ts_rank_cd(to_tsvector('simple', dc.chunk_text), plainto_tsquery('simple', query_text)),
          ts_rank_cd(to_tsvector('english', dc.chunk_text), plainto_tsquery('english', query_text))
        )
      END AS keyword_rank_score
    FROM document_chunks dc
    WHERE 
      -- Hebrew text matching (ILIKE)
      dc.chunk_text ILIKE '%' || query_text || '%'
      OR dc.chunk_text ILIKE '%' || split_part(query_text, ' ', 1) || '%'
      OR dc.chunk_text ILIKE '%' || split_part(query_text, ' ', 2) || '%'
      OR dc.chunk_text ILIKE '%' || split_part(query_text, ' ', 3) || '%'
      OR dc.chunk_text ILIKE '%' || left(query_text, length(query_text)/2) || '%'
      -- English/other language full-text search
      OR to_tsvector('simple', dc.chunk_text) @@ plainto_tsquery('simple', query_text)
      OR to_tsvector('english', dc.chunk_text) @@ plainto_tsquery('english', query_text)
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
  -- Accept results with either semantic similarity OR keyword match
  WHERE (COALESCE(ss.semantic_similarity_score, 0.0) > match_threshold OR COALESCE(ks.keyword_rank_score, 0.0) > 0) 
  ORDER BY combined_score DESC
  LIMIT match_count;
$$;

-- Create a simple ILIKE-based search function for Hebrew text
CREATE OR REPLACE FUNCTION search_hebrew_text(
  query_text text,
  match_count int DEFAULT 10
)
RETURNS TABLE (
  id bigint,
  document_id bigint,
  document_name text,
  chunk_text text,
  chunk_header text,
  page_number integer,
  section text,
  match_score float
)
LANGUAGE sql STABLE
AS $$
  SELECT
    dc.id,
    dc.document_id,
    d.name as document_name,
    dc.chunk_text,
    dc.chunk_header,
    dc.page_number,
    dc.section,
    CASE 
      WHEN dc.chunk_text ILIKE '%' || query_text || '%' THEN 1.0
      WHEN dc.chunk_text ILIKE '%' || split_part(query_text, ' ', 1) || '%' THEN 0.8
      WHEN dc.chunk_text ILIKE '%' || split_part(query_text, ' ', 2) || '%' THEN 0.8
      ELSE 0.5
    END as match_score
  FROM document_chunks dc
  JOIN documents d ON d.id = dc.document_id
  WHERE 
    dc.chunk_text ILIKE '%' || query_text || '%'
    OR dc.chunk_text ILIKE '%' || split_part(query_text, ' ', 1) || '%'
    OR dc.chunk_text ILIKE '%' || split_part(query_text, ' ', 2) || '%'
  ORDER BY match_score DESC, dc.id
  LIMIT match_count;
$$;

-- Add comments
COMMENT ON FUNCTION hybrid_search_documents IS 'Improved hybrid search function with Hebrew text support using ILIKE matching';
COMMENT ON FUNCTION search_hebrew_text IS 'Simple Hebrew text search using ILIKE pattern matching'; 