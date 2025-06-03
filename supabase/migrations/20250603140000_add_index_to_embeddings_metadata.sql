-- Add a GIN index to the metadata column in the embeddings table to speed up lookups.
-- This is crucial for the handle_document_deletion trigger.
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_embeddings_metadata_gin ON public.embeddings USING gin (metadata jsonb_path_ops); 