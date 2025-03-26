-- Function to get document statistics
CREATE OR REPLACE FUNCTION get_document_stats(document_id BIGINT)
RETURNS TABLE (
  total_views BIGINT,
  total_downloads BIGINT,
  last_viewed TIMESTAMP WITH TIME ZONE,
  last_downloaded TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    COUNT(*) FILTER (WHERE action = 'view') as total_views,
    COUNT(*) FILTER (WHERE action = 'download') as total_downloads,
    MAX(created_at) FILTER (WHERE action = 'view') as last_viewed,
    MAX(created_at) FILTER (WHERE action = 'download') as last_downloaded
  FROM document_analytics
  WHERE document_id = $1;
END;
$$ LANGUAGE plpgsql;

-- Function to get user activity
CREATE OR REPLACE FUNCTION get_user_activity(user_id UUID)
RETURNS TABLE (
  total_documents_viewed BIGINT,
  total_documents_downloaded BIGINT,
  last_activity TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    COUNT(*) FILTER (WHERE action = 'view') as total_documents_viewed,
    COUNT(*) FILTER (WHERE action = 'download') as total_documents_downloaded,
    MAX(created_at) as last_activity
  FROM document_analytics
  WHERE user_id = $1;
END;
$$ LANGUAGE plpgsql;

-- Function to get recent activity
CREATE OR REPLACE FUNCTION get_recent_activity(limit_count INTEGER DEFAULT 10)
RETURNS TABLE (
  document_id BIGINT,
  document_name TEXT,
  user_email TEXT,
  action TEXT,
  created_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    da.document_id,
    d.name as document_name,
    u.email as user_email,
    da.action,
    da.created_at
  FROM document_analytics da
  JOIN documents d ON d.id = da.document_id
  JOIN users u ON u.id = da.user_id
  ORDER BY da.created_at DESC
  LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- Function to get document usage statistics
CREATE OR REPLACE FUNCTION get_document_usage_stats(days INTEGER DEFAULT 30)
RETURNS TABLE (
  document_id BIGINT,
  document_name TEXT,
  total_views BIGINT,
  total_downloads BIGINT,
  unique_viewers BIGINT,
  unique_downloaders BIGINT
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    d.id as document_id,
    d.name as document_name,
    COUNT(*) FILTER (WHERE da.action = 'view') as total_views,
    COUNT(*) FILTER (WHERE da.action = 'download') as total_downloads,
    COUNT(DISTINCT da.user_id) FILTER (WHERE da.action = 'view') as unique_viewers,
    COUNT(DISTINCT da.user_id) FILTER (WHERE da.action = 'download') as unique_downloaders
  FROM documents d
  LEFT JOIN document_analytics da ON da.document_id = d.id
  WHERE da.created_at >= NOW() - (days || ' days')::INTERVAL
  GROUP BY d.id, d.name
  ORDER BY total_views DESC;
END;
$$ LANGUAGE plpgsql; 