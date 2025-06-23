-- Fix document deletion trigger to also delete embeddings

-- Drop existing trigger to replace it
DROP TRIGGER IF EXISTS on_document_deletion ON documents;

-- Update the function
CREATE OR REPLACE FUNCTION handle_document_deletion()
RETURNS TRIGGER AS $$
DECLARE
  storage_path TEXT;
BEGIN
  -- Extract the storage path from the URL
  -- The URL is usually in format: https://domain.com/storage/v1/object/public/documents/filename.ext
  storage_path := substring(OLD.url from '/documents/(.*)$');
  
  IF storage_path IS NULL THEN
    -- Fallback: try to extract just the filename
    storage_path := substring(OLD.url from '[^/]+$');
    IF storage_path IS NOT NULL THEN
      storage_path := 'documents/' || storage_path;
    END IF;
  ELSE
    storage_path := 'documents/' || storage_path;
  END IF;
  
  -- Log the path we're trying to delete for debugging
  RAISE NOTICE 'Attempting to delete storage object: %', storage_path;
  
  -- Delete the file from storage
  DELETE FROM storage.objects
  WHERE bucket_id = 'documents'
  AND (name = storage_path OR path = storage_path OR name = OLD.url OR path = OLD.url);

  -- Delete analytics data
  DELETE FROM document_analytics
  WHERE document_id = OLD.id;
  
  -- Delete embeddings associated with this document
  -- Important: Delete embeddings first before document_chunks to maintain referential integrity
  DELETE FROM embeddings
  WHERE id IN (
    SELECT embedding_id FROM document_chunks
    WHERE document_id = OLD.id
  );
  
  -- Delete document chunks
  DELETE FROM document_chunks
  WHERE document_id = OLD.id;

  RETURN OLD;
END;
$$ LANGUAGE plpgsql;

-- Recreate the trigger
CREATE TRIGGER on_document_deletion
  BEFORE DELETE ON documents
  FOR EACH ROW
  EXECUTE FUNCTION handle_document_deletion(); 