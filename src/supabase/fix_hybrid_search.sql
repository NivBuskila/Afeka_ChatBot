-- Fix for hybrid search function with Hebrew support
-- This file fixes the "syntax error in tsquery" issue and adds better Hebrew language support

-- First, drop the function if it exists with any signature to avoid conflicts
DROP FUNCTION IF EXISTS hybrid_search_documents;

-- Create the hybrid_search_documents function with Hebrew text search support
CREATE OR REPLACE FUNCTION hybrid_search_documents(
  query_embedding vector(768),
  query_text text,
  match_threshold float DEFAULT 0.70,
  match_count int DEFAULT 10,
  semantic_weight float DEFAULT 0.6,
  keyword_weight float DEFAULT 0.4
)
RETURNS TABLE (
  id bigint,              -- Chunk ID
  document_id bigint,     -- ID of the parent document
  document_name text,     -- Name of the parent document
  document_status text,   -- Status of the parent document
  document_created_at timestamptz, -- When the document was created
  chunk_text text,        -- The text content of the chunk
  content_token_count int, -- Token count of the chunk
  similarity float,       -- Combined similarity score
  semantic_similarity float, -- Semantic (vector) similarity component
  keyword_similarity float   -- Keyword (text) similarity component
) 
LANGUAGE plpgsql
AS $$
BEGIN
  -- Limit to 500 candidates from vector search to improve performance
  RETURN QUERY
  WITH semantic_results AS (
    -- Get the top semantic matches with a hard limit to avoid timeouts
    SELECT 
      dc.id,
      1 - (dc.embedding <=> query_embedding) as semantic_similarity
    FROM 
      document_chunks dc
    WHERE 
      1 - (dc.embedding <=> query_embedding) > 0.5 -- Lower threshold to get more candidates
    ORDER BY 
      semantic_similarity DESC
    LIMIT 500 -- Hard limit to avoid timeouts
  ),
  keyword_results AS (
    -- Get keyword matches using simple text matching for each word in the query
    SELECT
      dc.id,
      -- Calculate a simple keyword score based on how many query words are found
      -- This is a basic approach; more advanced scoring could be used.
      (
        SELECT SUM(CASE WHEN dc.chunk_text ILIKE '%' || unnest_word || '%' THEN 1 ELSE 0 END)
        FROM unnest(string_to_array(trim(lower(query_text)), ' ')) AS unnest_word
        WHERE unnest_word <> '' -- ignore empty strings from multiple spaces
      )::float / GREATEST(array_length(string_to_array(trim(lower(query_text)), ' '), 1), 1)::float -- Normalize by number of words
      AS keyword_similarity
    FROM
      document_chunks dc
    INNER JOIN
      semantic_results sr ON dc.id = sr.id
    WHERE
      query_text IS NOT NULL AND query_text <> '' AND query_text ~ '\S' -- Ensure query_text has non-whitespace
  ),
  combined_results AS (
    -- Combine both similarity scores
    SELECT 
      sr.id,
      (sr.semantic_similarity * semantic_weight) + 
      COALESCE((kr.keyword_similarity * keyword_weight), 0.0::float) as similarity,
      sr.semantic_similarity,
      COALESCE(kr.keyword_similarity, 0.0::float) as keyword_similarity
    FROM 
      semantic_results sr
    LEFT JOIN 
      keyword_results kr ON sr.id = kr.id
    WHERE 
      (sr.semantic_similarity * semantic_weight) + 
      COALESCE((kr.keyword_similarity * keyword_weight), 0.0::float) >= match_threshold
    ORDER BY 
      similarity DESC
    LIMIT match_count
  )
  -- Join with document_chunks and documents to get full result
  SELECT 
    dc.id,
    dc.document_id,
    d.name as document_name,
    d.status as document_status,
    d.created_at as document_created_at,
    dc.chunk_text,
    dc.content_token_count,
    cr.similarity,
    cr.semantic_similarity,
    cr.keyword_similarity
  FROM 
    combined_results cr
  JOIN 
    document_chunks dc ON cr.id = dc.id
  JOIN 
    documents d ON dc.document_id = d.id
  ORDER BY 
    cr.similarity DESC
  LIMIT match_count;
END;
$$;

-- Add indexes to improve performance if they don't exist
DO $$
BEGIN
  -- Check if index on embedding exists
  IF NOT EXISTS (
    SELECT 1 FROM pg_indexes 
    WHERE tablename = 'document_chunks' AND indexname = 'idx_document_chunks_embedding'
  ) THEN
    CREATE INDEX idx_document_chunks_embedding ON document_chunks USING ivfflat (embedding vector_l2_ops);
  END IF;
  
  -- Check if index on document_id exists
  IF NOT EXISTS (
    SELECT 1 FROM pg_indexes 
    WHERE tablename = 'document_chunks' AND indexname = 'idx_document_chunks_document_id'
  ) THEN
    CREATE INDEX idx_document_chunks_document_id ON document_chunks(document_id);
  END IF;
  
  -- Check if text search index exists
  IF NOT EXISTS (
    SELECT 1 FROM pg_indexes 
    WHERE tablename = 'document_chunks' AND indexname = 'idx_document_chunks_chunk_text'
  ) THEN
    CREATE INDEX idx_document_chunks_chunk_text ON document_chunks(chunk_text text_pattern_ops);
  END IF;
END;
$$;

-- Also, create a simplified insert function for document chunks that doesn't require all fields
DROP FUNCTION IF EXISTS insert_document_chunk_basic;

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

-- Add comments about the functions
COMMENT ON FUNCTION hybrid_search_documents IS 'Hybrid search function that combines vector similarity with simple text matching for Hebrew documents';
COMMENT ON FUNCTION insert_document_chunk_basic IS 'Simple function to insert a document chunk with basic required fields';

-- Add a note to test the function
-- SELECT * FROM hybrid_search_documents(array_fill(0::float, ARRAY[768]), 'בדיקה', 0.5, 5); 