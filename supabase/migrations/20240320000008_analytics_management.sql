-- Function to get overall analytics
CREATE OR REPLACE FUNCTION get_overall_analytics(days INTEGER DEFAULT 30)
RETURNS TABLE (
  total_documents BIGINT,
  total_users BIGINT,
  total_views BIGINT,
  total_downloads BIGINT,
  active_users BIGINT,
  new_documents BIGINT,
  new_users BIGINT
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    (SELECT COUNT(*) FROM documents) as total_documents,
    (SELECT COUNT(*) FROM users) as total_users,
    COUNT(*) FILTER (WHERE da.action = 'view') as total_views,
    COUNT(*) FILTER (WHERE da.action = 'download') as total_downloads,
    COUNT(DISTINCT da.user_id) as active_users,
    COUNT(DISTINCT d.id) FILTER (WHERE d.created_at >= NOW() - (days || ' days')::INTERVAL) as new_documents,
    COUNT(DISTINCT u.id) FILTER (WHERE u.created_at >= NOW() - (days || ' days')::INTERVAL) as new_users
  FROM document_analytics da
  CROSS JOIN documents d
  CROSS JOIN users u
  WHERE da.created_at >= NOW() - (days || ' days')::INTERVAL;
END;
$$ LANGUAGE plpgsql;

-- Function to get daily analytics
CREATE OR REPLACE FUNCTION get_daily_analytics(days INTEGER DEFAULT 30)
RETURNS TABLE (
  date DATE,
  views BIGINT,
  downloads BIGINT,
  active_users BIGINT,
  new_documents BIGINT,
  new_users BIGINT
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    DATE(da.created_at) as date,
    COUNT(*) FILTER (WHERE da.action = 'view') as views,
    COUNT(*) FILTER (WHERE da.action = 'download') as downloads,
    COUNT(DISTINCT da.user_id) as active_users,
    COUNT(DISTINCT d.id) FILTER (WHERE DATE(d.created_at) = DATE(da.created_at)) as new_documents,
    COUNT(DISTINCT u.id) FILTER (WHERE DATE(u.created_at) = DATE(da.created_at)) as new_users
  FROM document_analytics da
  CROSS JOIN documents d
  CROSS JOIN users u
  WHERE da.created_at >= NOW() - (days || ' days')::INTERVAL
  GROUP BY DATE(da.created_at)
  ORDER BY date DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to get popular documents
CREATE OR REPLACE FUNCTION get_popular_documents(
  days INTEGER DEFAULT 30,
  limit_count INTEGER DEFAULT 10
)
RETURNS TABLE (
  id BIGINT,
  name TEXT,
  views BIGINT,
  downloads BIGINT,
  unique_viewers BIGINT,
  last_viewed TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    d.id,
    d.name,
    COUNT(*) FILTER (WHERE da.action = 'view') as views,
    COUNT(*) FILTER (WHERE da.action = 'download') as downloads,
    COUNT(DISTINCT da.user_id) as unique_viewers,
    MAX(da.created_at) FILTER (WHERE da.action = 'view') as last_viewed
  FROM documents d
  LEFT JOIN document_analytics da ON da.document_id = d.id
  WHERE da.created_at >= NOW() - (days || ' days')::INTERVAL
  GROUP BY d.id, d.name
  ORDER BY views DESC
  LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- Function to get active users
CREATE OR REPLACE FUNCTION get_active_users(
  days INTEGER DEFAULT 30,
  limit_count INTEGER DEFAULT 10
)
RETURNS TABLE (
  id UUID,
  email TEXT,
  total_actions BIGINT,
  last_action TIMESTAMP WITH TIME ZONE,
  documents_viewed BIGINT,
  documents_downloaded BIGINT
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    u.id,
    u.email,
    COUNT(*) as total_actions,
    MAX(da.created_at) as last_action,
    COUNT(*) FILTER (WHERE da.action = 'view') as documents_viewed,
    COUNT(*) FILTER (WHERE da.action = 'download') as documents_downloaded
  FROM users u
  JOIN document_analytics da ON da.user_id = u.id
  WHERE da.created_at >= NOW() - (days || ' days')::INTERVAL
  GROUP BY u.id, u.email
  ORDER BY total_actions DESC
  LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- Function to get document type distribution
CREATE OR REPLACE FUNCTION get_document_type_distribution()
RETURNS TABLE (
  type TEXT,
  count BIGINT,
  total_size BIGINT,
  avg_size BIGINT
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    d.type,
    COUNT(*) as count,
    SUM(d.size) as total_size,
    AVG(d.size)::BIGINT as avg_size
  FROM documents d
  GROUP BY d.type
  ORDER BY count DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to get user engagement metrics
CREATE OR REPLACE FUNCTION get_user_engagement_metrics(days INTEGER DEFAULT 30)
RETURNS TABLE (
  metric TEXT,
  value FLOAT
) AS $$
BEGIN
  RETURN QUERY
  WITH metrics AS (
    SELECT
      COUNT(DISTINCT user_id)::FLOAT as active_users,
      COUNT(DISTINCT document_id)::FLOAT as accessed_documents,
      COUNT(*)::FLOAT as total_actions
    FROM document_analytics
    WHERE created_at >= NOW() - (days || ' days')::INTERVAL
  )
  SELECT 'Average Actions per User' as metric,
         ROUND(total_actions / NULLIF(active_users, 0), 2) as value
  FROM metrics
  UNION ALL
  SELECT 'Average Documents per User' as metric,
         ROUND(accessed_documents / NULLIF(active_users, 0), 2) as value
  FROM metrics
  UNION ALL
  SELECT 'Actions per Document' as metric,
         ROUND(total_actions / NULLIF(accessed_documents, 0), 2) as value
  FROM metrics;
END;
$$ LANGUAGE plpgsql;

-- Function to get retention metrics
CREATE OR REPLACE FUNCTION get_retention_metrics(
  cohort_days INTEGER DEFAULT 30,
  retention_days INTEGER DEFAULT 7
)
RETURNS TABLE (
  cohort_date DATE,
  cohort_size BIGINT,
  retained_users BIGINT,
  retention_rate FLOAT
) AS $$
BEGIN
  RETURN QUERY
  WITH cohorts AS (
    SELECT
      DATE(u.created_at) as cohort_date,
      COUNT(DISTINCT u.id) as cohort_size,
      COUNT(DISTINCT CASE
        WHEN da.created_at >= u.created_at + (retention_days || ' days')::INTERVAL
        THEN u.id
      END) as retained_users
    FROM users u
    LEFT JOIN document_analytics da ON da.user_id = u.id
    WHERE u.created_at >= NOW() - (cohort_days || ' days')::INTERVAL
    GROUP BY DATE(u.created_at)
  )
  SELECT
    c.cohort_date,
    c.cohort_size,
    c.retained_users,
    ROUND((c.retained_users::FLOAT / NULLIF(c.cohort_size, 0)) * 100, 2) as retention_rate
  FROM cohorts c
  ORDER BY c.cohort_date DESC;
END;
$$ LANGUAGE plpgsql; 