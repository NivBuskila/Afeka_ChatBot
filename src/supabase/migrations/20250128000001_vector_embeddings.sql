-- Create RAG (Retrieval Augmented Generation) related tables

-- First, add columns to documents table if they don't exist
ALTER TABLE documents 
  ADD COLUMN IF NOT EXISTS content TEXT,
  ADD COLUMN IF NOT EXISTS embedding_model TEXT,
  ADD COLUMN IF NOT EXISTS processing_status TEXT DEFAULT 'pending';

-- Create document_chunks table if it doesn't exist  
CREATE TABLE IF NOT EXISTS document_chunks (
  id BIGSERIAL PRIMARY KEY,
  document_id BIGINT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  chunk_text TEXT NOT NULL,
  chunk_index INTEGER,
  embedding vector(768),
  content_token_count INTEGER,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Create indexes for document_chunks
CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id ON document_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_document_chunks_chunk_index ON document_chunks(chunk_index);

-- Create embeddings table for backwards compatibility
CREATE TABLE IF NOT EXISTS embeddings (
  id BIGSERIAL PRIMARY KEY,
  content TEXT NOT NULL,
  metadata JSONB,
  embedding vector(768),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Create indexes for embeddings
CREATE INDEX IF NOT EXISTS idx_embeddings_created_at ON embeddings(created_at);

-- Create vector indexes if they don't exist
CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding ON document_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_embeddings_embedding ON embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Add RLS policies for the new tables
ALTER TABLE document_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE embeddings ENABLE ROW LEVEL SECURITY;

-- Document chunks policies
CREATE POLICY "Document chunks are viewable by authenticated users"
  ON document_chunks FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Document chunks are insertable by authenticated users"
  ON document_chunks FOR INSERT
  TO authenticated
  WITH CHECK (true);

-- Embeddings policies
CREATE POLICY "Embeddings are viewable by authenticated users"
  ON embeddings FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Embeddings are insertable by authenticated users"
  ON embeddings FOR INSERT
  TO authenticated
  WITH CHECK (true);

-- Function to get document processing status
CREATE OR REPLACE FUNCTION get_document_processing_status(document_id BIGINT)
RETURNS TABLE (
  id BIGINT,
  status TEXT,
  model TEXT,
  chunk_count BIGINT
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    d.id,
    d.processing_status as status,
    d.embedding_model as model,
    COUNT(dc.id) as chunk_count
  FROM documents d
  LEFT JOIN document_chunks dc ON dc.document_id = d.id
  WHERE d.id = document_id
  GROUP BY d.id;
END;
$$ LANGUAGE plpgsql;

-- Function to get document status counts
CREATE OR REPLACE FUNCTION get_document_status_counts()
RETURNS TABLE (
  status TEXT,
  count BIGINT
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    processing_status,
    COUNT(*) as count
  FROM documents
  GROUP BY processing_status;
END;
$$ LANGUAGE plpgsql; 