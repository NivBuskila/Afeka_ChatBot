-- Add an index to the document_id column in the document_chunks table
CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id ON public.document_chunks (document_id);

-- Optional: Add an index to the document_id column in the embeddings table if it also experiences slow deletes
-- CREATE INDEX IF NOT EXISTS idx_embeddings_document_id ON public.embeddings (document_id); 