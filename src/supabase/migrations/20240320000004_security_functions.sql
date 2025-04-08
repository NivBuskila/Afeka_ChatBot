-- Function to check if user is admin
CREATE OR REPLACE FUNCTION is_admin(user_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM admins
    WHERE user_id = $1
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to validate file type
CREATE OR REPLACE FUNCTION validate_file_type(file_type TEXT)
RETURNS BOOLEAN AS $$
BEGIN
  RETURN file_type IN (
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'text/plain'
  );
END;
$$ LANGUAGE plpgsql;

-- Function to generate secure file name
CREATE OR REPLACE FUNCTION generate_secure_filename(original_name TEXT)
RETURNS TEXT AS $$
DECLARE
  file_extension TEXT;
  secure_name TEXT;
BEGIN
  -- Extract file extension
  file_extension := LOWER(SPLIT_PART(original_name, '.', 2));
  
  -- Generate secure name using UUID and timestamp
  secure_name := CONCAT(
    gen_random_uuid(),
    '_',
    EXTRACT(EPOCH FROM NOW())::BIGINT,
    '.',
    file_extension
  );
  
  RETURN secure_name;
END;
$$ LANGUAGE plpgsql;

-- Function to check document access
CREATE OR REPLACE FUNCTION check_document_access(
  document_id BIGINT,
  user_id UUID
)
RETURNS BOOLEAN AS $$
BEGIN
  -- Admins have full access
  IF is_admin(user_id) THEN
    RETURN TRUE;
  END IF;
  
  -- Check if user has viewed or downloaded the document
  RETURN EXISTS (
    SELECT 1 FROM document_analytics
    WHERE document_id = $1
    AND user_id = $2
    AND action IN ('view', 'download')
  );
END;
$$ LANGUAGE plpgsql;

-- Function to get user permissions
CREATE OR REPLACE FUNCTION get_user_permissions(user_id UUID)
RETURNS TABLE (
  can_upload BOOLEAN,
  can_delete BOOLEAN,
  can_edit BOOLEAN,
  can_view_analytics BOOLEAN
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    TRUE as can_upload,
    is_admin(user_id) as can_delete,
    is_admin(user_id) as can_edit,
    is_admin(user_id) as can_view_analytics;
END;
$$ LANGUAGE plpgsql;

-- Function to validate user session
CREATE OR REPLACE FUNCTION validate_user_session(session_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM auth.sessions
    WHERE id = session_id
    AND expires_at > NOW()
  );
END;
$$ LANGUAGE plpgsql;

-- Function to log security events
CREATE OR REPLACE FUNCTION log_security_event(
  event_type TEXT,
  user_id UUID,
  details JSONB
)
RETURNS VOID AS $$
BEGIN
  INSERT INTO security_events (event_type, user_id, details)
  VALUES (event_type, user_id, details);
END;
$$ LANGUAGE plpgsql; 