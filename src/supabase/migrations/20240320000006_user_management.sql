-- Function to create new user
CREATE OR REPLACE FUNCTION create_user(
  email TEXT,
  is_admin BOOLEAN DEFAULT FALSE,
  name TEXT DEFAULT NULL,
  status TEXT DEFAULT 'active'
)
RETURNS UUID AS $$
DECLARE
  new_user_id UUID;
BEGIN
  -- Insert new user
  INSERT INTO users (email, name, status)
  VALUES (
    email, 
    COALESCE(name, split_part(email, '@', 1)), 
    status
  )
  RETURNING id INTO new_user_id;

  -- If admin, add to admins table
  IF is_admin THEN
    INSERT INTO admins (user_id)
    VALUES (new_user_id);
  END IF;

  -- Log security event
  PERFORM log_security_event(
    'user_created',
    new_user_id,
    jsonb_build_object(
      'email', email,
      'is_admin', is_admin
    )
  );

  RETURN new_user_id;
END;
$$ LANGUAGE plpgsql;

-- Function to update user role
CREATE OR REPLACE FUNCTION update_user_role(
  user_id UUID,
  make_admin BOOLEAN,
  admin_id UUID
)
RETURNS BOOLEAN AS $$
BEGIN
  -- Check if admin has permission
  IF NOT is_admin(admin_id) THEN
    RAISE EXCEPTION 'Only admins can update user roles';
  END IF;

  -- Update user role
  IF make_admin THEN
    -- Add to admins table if not already there
    INSERT INTO admins (user_id)
    VALUES (user_id)
    ON CONFLICT (user_id) DO NOTHING;
  ELSE
    -- Remove from admins table if there
    DELETE FROM admins WHERE user_id = user_id;
  END IF;

  -- Log security event
  PERFORM log_security_event(
    'role_updated',
    admin_id,
    jsonb_build_object(
      'user_id', user_id,
      'is_admin', make_admin
    )
  );

  RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Function to deactivate user
CREATE OR REPLACE FUNCTION deactivate_user(
  user_id UUID,
  admin_id UUID
)
RETURNS BOOLEAN AS $$
BEGIN
  -- Check if admin has permission
  IF NOT is_admin(admin_id) THEN
    RAISE EXCEPTION 'Only admins can deactivate users';
  END IF;

  -- Check if user exists and is not already deactivated
  IF NOT EXISTS (
    SELECT 1 FROM users
    WHERE id = user_id
  ) THEN
    RAISE EXCEPTION 'User not found';
  END IF;

  -- Log security event
  PERFORM log_security_event(
    'user_deactivated',
    admin_id,
    jsonb_build_object(
      'user_id', user_id
    )
  );

  RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Function to get user profile
CREATE OR REPLACE FUNCTION get_user_profile(user_id UUID)
RETURNS TABLE (
  id UUID,
  email TEXT,
  is_admin BOOLEAN,
  name TEXT,
  status TEXT,
  created_at TIMESTAMP WITH TIME ZONE,
  last_activity TIMESTAMP WITH TIME ZONE,
  total_documents_viewed BIGINT,
  total_documents_downloaded BIGINT
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    u.id,
    u.email,
    is_admin(u.id) as is_admin,
    u.name,
    u.status,
    u.created_at,
    MAX(da.created_at) as last_activity,
    COUNT(*) FILTER (WHERE da.action = 'view') as total_documents_viewed,
    COUNT(*) FILTER (WHERE da.action = 'download') as total_documents_downloaded
  FROM users u
  LEFT JOIN document_analytics da ON da.user_id = u.id
  WHERE u.id = $1
  GROUP BY u.id, u.email, u.name, u.status, u.created_at;
END;
$$ LANGUAGE plpgsql;

-- Function to get user activity summary
CREATE OR REPLACE FUNCTION get_user_activity_summary(
  user_id UUID,
  days INTEGER DEFAULT 30
)
RETURNS TABLE (
  total_views BIGINT,
  total_downloads BIGINT,
  unique_documents_viewed BIGINT,
  unique_documents_downloaded BIGINT,
  most_viewed_document TEXT,
  most_viewed_count BIGINT
) AS $$
BEGIN
  RETURN QUERY
  WITH user_stats AS (
    SELECT
      COUNT(*) FILTER (WHERE action = 'view') as total_views,
      COUNT(*) FILTER (WHERE action = 'download') as total_downloads,
      COUNT(DISTINCT document_id) FILTER (WHERE action = 'view') as unique_documents_viewed,
      COUNT(DISTINCT document_id) FILTER (WHERE action = 'download') as unique_documents_downloaded
    FROM document_analytics
    WHERE user_id = $1
    AND created_at >= NOW() - (days || ' days')::INTERVAL
  ),
  most_viewed AS (
    SELECT
      d.name as document_name,
      COUNT(*) as view_count
    FROM document_analytics da
    JOIN documents d ON d.id = da.document_id
    WHERE da.user_id = $1
    AND da.action = 'view'
    AND da.created_at >= NOW() - (days || ' days')::INTERVAL
    GROUP BY d.id, d.name
    ORDER BY view_count DESC
    LIMIT 1
  )
  SELECT
    us.total_views,
    us.total_downloads,
    us.unique_documents_viewed,
    us.unique_documents_downloaded,
    mv.document_name as most_viewed_document,
    mv.view_count as most_viewed_count
  FROM user_stats us
  LEFT JOIN most_viewed mv ON TRUE;
END;
$$ LANGUAGE plpgsql;

-- Function to get user security status
CREATE OR REPLACE FUNCTION get_user_security_status(user_id UUID)
RETURNS TABLE (
  is_active BOOLEAN,
  failed_login_attempts INTEGER,
  last_login TIMESTAMP WITH TIME ZONE,
  suspicious_activity BOOLEAN,
  security_events_count INTEGER
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    EXISTS (
      SELECT 1 FROM users
      WHERE id = $1
    ) as is_active,
    get_failed_login_attempts($1) as failed_login_attempts,
    (
      SELECT MAX(created_at)
      FROM security_events
      WHERE user_id = $1
      AND event_type = 'login_success'
    ) as last_login,
    check_suspicious_activity($1) as suspicious_activity,
    (
      SELECT COUNT(*)
      FROM security_events
      WHERE user_id = $1
      AND created_at >= NOW() - '24 hours'::INTERVAL
    ) as security_events_count;
END;
$$ LANGUAGE plpgsql; 