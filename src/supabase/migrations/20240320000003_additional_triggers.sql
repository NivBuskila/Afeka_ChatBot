-- Function to handle document deletion
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

  RETURN OLD;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for document deletion
CREATE TRIGGER on_document_deletion
  BEFORE DELETE ON documents
  FOR EACH ROW
  EXECUTE FUNCTION handle_document_deletion();

-- Function to handle user deletion
CREATE OR REPLACE FUNCTION handle_user_deletion()
RETURNS TRIGGER AS $$
BEGIN
  -- Delete analytics data
  DELETE FROM document_analytics
  WHERE user_id = OLD.id;

  RETURN OLD;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for user deletion
CREATE TRIGGER on_user_deletion
  BEFORE DELETE ON users
  FOR EACH ROW
  EXECUTE FUNCTION handle_user_deletion();

-- Function to validate file size
CREATE OR REPLACE FUNCTION validate_file_size()
RETURNS TRIGGER AS $$
BEGIN
  -- Maximum file size (100MB)
  IF NEW.size > 100 * 1024 * 1024 THEN
    RAISE EXCEPTION 'File size exceeds maximum limit of 100MB';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for file size validation
CREATE TRIGGER validate_document_size
  BEFORE INSERT OR UPDATE ON documents
  FOR EACH ROW
  EXECUTE FUNCTION validate_file_size();

-- Function to log document access
CREATE OR REPLACE FUNCTION get_document_with_logging(doc_id BIGINT)
RETURNS TABLE (
  id BIGINT,
  name TEXT,
  type TEXT,
  size BIGINT,
  url TEXT,
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ
) AS $$
BEGIN
  -- Log the access
  INSERT INTO document_analytics (document_id, user_id, action)
  VALUES (doc_id, auth.uid(), 'view');
  
  -- Return the document data
  RETURN QUERY
  SELECT d.id, d.name, d.type, d.size, d.url, d.created_at, d.updated_at
  FROM documents d
  WHERE d.id = doc_id;
END;
$$ LANGUAGE plpgsql;

-- Create a secure view for accessing documents
CREATE OR REPLACE VIEW documents_with_logging AS
SELECT 
  d.id,
  d.name,
  d.type,
  d.size,
  d.url,
  d.created_at,
  d.updated_at
FROM documents d;

-- Grant access to the view and function
GRANT SELECT ON documents_with_logging TO authenticated;
GRANT EXECUTE ON FUNCTION get_document_with_logging(BIGINT) TO authenticated; 