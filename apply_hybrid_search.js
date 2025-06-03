// Apply hybrid search SQL to Supabase database
const { createClient } = require('@supabase/supabase-js');
require('dotenv').config();

// Read environment variables
const supabaseUrl = process.env.SUPABASE_URL;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_KEY || process.env.SUPABASE_KEY;

if (!supabaseUrl || !supabaseServiceKey) {
  console.error('Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in environment variables');
  process.exit(1);
}

// Initialize Supabase client
const supabase = createClient(supabaseUrl, supabaseServiceKey);

// SQL to create the hybrid_search_documents function
const hybridSearchSql = `
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
  combined_score float,   -- Weighted combined score
  chunk_index integer
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
    ) as combined_score,
    dc.chunk_index
  FROM document_chunks dc
  JOIN documents d ON d.id = dc.document_id
  LEFT JOIN semantic_search ss ON ss.chunk_id = dc.id
  LEFT JOIN keyword_search ks ON ks.chunk_id = dc.id
  -- Filter based on combined logic: semantic match OR keyword match, and combined score above threshold
  WHERE (COALESCE(ss.semantic_similarity_score, 0.0) > match_threshold OR COALESCE(ks.keyword_rank_score, 0.0) > 0) 
  ORDER BY combined_score DESC
  LIMIT match_count;
$$;
`;

async function applyHybridSearchSql() {
  try {
    console.log('Applying hybrid search SQL to Supabase database...');
    
    // Execute the SQL directly using Supabase's RPC capabilities
    const { data, error } = await supabase.rpc('exec_sql', { sql: hybridSearchSql });
    
    if (error) {
      console.error('Error applying SQL:', error);
      return;
    }
    
    console.log('Hybrid search function created successfully!');
    console.log('Testing the function...');
    
    // Test if the function exists
    const { data: testData, error: testError } = await supabase
      .from('pg_proc')
      .select('proname')
      .eq('proname', 'hybrid_search_documents')
      .limit(1);
    
    if (testError) {
      console.error('Error testing function:', testError);
      return;
    }
    
    if (testData && testData.length > 0) {
      console.log('Function hybrid_search_documents exists in the database!');
    } else {
      console.log('Function hybrid_search_documents was not found in the database.');
    }
  } catch (err) {
    console.error('Unexpected error:', err);
  }
}

// Execute the function
applyHybridSearchSql(); 