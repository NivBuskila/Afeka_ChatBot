-- Function to create new document
CREATE OR REPLACE FUNCTION create_document(
  name TEXT,
  type TEXT,
  size BIGINT,
  url TEXT,
  user_id UUID
)
RETURNS BIGINT AS $$
DECLARE
  new_document_id BIGINT;
BEGIN
  -- Validate file type
  IF NOT validate_file_type(type) THEN
    RAISE EXCEPTION 'Invalid file type';
  END IF;

  -- Insert new document
  INSERT INTO documents (name, type, size, url)
  VALUES (name, type, size, url)
  RETURNING id INTO new_document_id;

  -- Log security event
  PERFORM log_security_event(
    'document_created',
    user_id,
    jsonb_build_object(
      'document_id', new_document_id,
      'name', name,
      'type', type,
      'size', size
    )
  );

  RETURN new_document_id;
END;
$$ LANGUAGE plpgsql;

-- Function to update document
CREATE OR REPLACE FUNCTION update_document(
  document_id BIGINT,
  name TEXT,
  type TEXT,
  size BIGINT,
  url TEXT,
  user_id UUID
)
RETURNS BOOLEAN AS $$
BEGIN
  -- Validate file type
  IF NOT validate_file_type(type) THEN
    RAISE EXCEPTION 'Invalid file type';
  END IF;

  -- Update document
  UPDATE documents
  SET
    name = COALESCE(name, name),
    type = COALESCE(type, type),
    size = COALESCE(size, size),
    url = COALESCE(url, url),
    updated_at = NOW()
  WHERE id = document_id;

  -- Log security event
  PERFORM log_security_event(
    'document_updated',
    user_id,
    jsonb_build_object(
      'document_id', document_id,
      'name', name,
      'type', type,
      'size', size
    )
  );

  RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Function to delete document
CREATE OR REPLACE FUNCTION delete_document(
  document_id BIGINT,
  user_id UUID
)
RETURNS BOOLEAN AS $$
DECLARE
  document_url TEXT;
BEGIN
  -- Get document URL
  SELECT url INTO document_url
  FROM documents
  WHERE id = document_id;

  IF document_url IS NULL THEN
    RAISE EXCEPTION 'Document not found';
  END IF;

  -- Delete document
  DELETE FROM documents
  WHERE id = document_id;

  -- Log security event
  PERFORM log_security_event(
    'document_deleted',
    user_id,
    jsonb_build_object(
      'document_id', document_id,
      'url', document_url
    )
  );

  RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Function to get document details
CREATE OR REPLACE FUNCTION get_document_details(document_id BIGINT)
RETURNS TABLE (
  id BIGINT,
  name TEXT,
  type TEXT,
  size BIGINT,
  url TEXT,
  created_at TIMESTAMP WITH TIME ZONE,
  updated_at TIMESTAMP WITH TIME ZONE,
  total_views BIGINT,
  total_downloads BIGINT,
  last_viewed TIMESTAMP WITH TIME ZONE,
  last_downloaded TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    d.*,
    COUNT(*) FILTER (WHERE da.action = 'view') as total_views,
    COUNT(*) FILTER (WHERE da.action = 'download') as total_downloads,
    MAX(da.created_at) FILTER (WHERE da.action = 'view') as last_viewed,
    MAX(da.created_at) FILTER (WHERE da.action = 'download') as last_downloaded
  FROM documents d
  LEFT JOIN document_analytics da ON da.document_id = d.id
  WHERE d.id = document_id
  GROUP BY d.id;
END;
$$ LANGUAGE plpgsql;

-- Function to get document access history
CREATE OR REPLACE FUNCTION get_document_access_history(
  document_id BIGINT,
  limit_count INTEGER DEFAULT 10
)
RETURNS TABLE (
  user_email TEXT,
  action TEXT,
  created_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    u.email as user_email,
    da.action,
    da.created_at
  FROM document_analytics da
  JOIN users u ON u.id = da.user_id
  WHERE da.document_id = $1
  ORDER BY da.created_at DESC
  LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- Function to get document usage trends
CREATE OR REPLACE FUNCTION get_document_usage_trends(
  document_id BIGINT,
  days INTEGER DEFAULT 30
)
RETURNS TABLE (
  date DATE,
  views BIGINT,
  downloads BIGINT,
  unique_users BIGINT
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    DATE(da.created_at) as date,
    COUNT(*) FILTER (WHERE da.action = 'view') as views,
    COUNT(*) FILTER (WHERE da.action = 'download') as downloads,
    COUNT(DISTINCT da.user_id) as unique_users
  FROM document_analytics da
  WHERE da.document_id = $1
  AND da.created_at >= NOW() - (days || ' days')::INTERVAL
  GROUP BY DATE(da.created_at)
  ORDER BY date DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to search documents
CREATE OR REPLACE FUNCTION search_documents(
  search_query TEXT,
  limit_count INTEGER DEFAULT 10
)
RETURNS TABLE (
  id BIGINT,
  name TEXT,
  type TEXT,
  size BIGINT,
  url TEXT,
  created_at TIMESTAMP WITH TIME ZONE,
  relevance FLOAT
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    d.id,
    d.name,
    d.type,
    d.size,
    d.url,
    d.created_at,
    ts_rank_cd(
      to_tsvector('english', d.name),
      to_tsquery('english', search_query)
    ) as relevance
  FROM documents d
  WHERE to_tsvector('english', d.name) @@ to_tsquery('english', search_query)
  ORDER BY relevance DESC
  LIMIT limit_count;
END;
$$ LANGUAGE plpgsql; 