-- Create security events table
CREATE TABLE security_events (
  id BIGSERIAL PRIMARY KEY,
  event_type TEXT NOT NULL,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  details JSONB NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Create index for security events
CREATE INDEX idx_security_events_user_id ON security_events(user_id);
CREATE INDEX idx_security_events_event_type ON security_events(event_type);
CREATE INDEX idx_security_events_created_at ON security_events(created_at);

-- Enable RLS
ALTER TABLE security_events ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
CREATE POLICY "Security events are viewable by admins only"
  ON security_events FOR SELECT
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM users
      WHERE id = auth.uid()
      AND role = 'admin'
    )
  );

CREATE POLICY "Security events are insertable by system"
  ON security_events FOR INSERT
  TO authenticated
  WITH CHECK (true);

-- Create function to clean old security events
CREATE OR REPLACE FUNCTION clean_old_security_events(days INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
  deleted_count INTEGER;
BEGIN
  DELETE FROM security_events
  WHERE created_at < NOW() - (days || ' days')::INTERVAL
  RETURNING COUNT(*) INTO deleted_count;
  
  RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Create function to get security event statistics
CREATE OR REPLACE FUNCTION get_security_event_stats(days INTEGER DEFAULT 30)
RETURNS TABLE (
  event_type TEXT,
  count BIGINT,
  last_occurrence TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    se.event_type,
    COUNT(*) as count,
    MAX(se.created_at) as last_occurrence
  FROM security_events se
  WHERE se.created_at >= NOW() - (days || ' days')::INTERVAL
  GROUP BY se.event_type
  ORDER BY count DESC;
END;
$$ LANGUAGE plpgsql;

-- Create function to get user security events
CREATE OR REPLACE FUNCTION get_user_security_events(
  user_id UUID,
  limit_count INTEGER DEFAULT 10
)
RETURNS TABLE (
  event_type TEXT,
  details JSONB,
  created_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    se.event_type,
    se.details,
    se.created_at
  FROM security_events se
  WHERE se.user_id = $1
  ORDER BY se.created_at DESC
  LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- Create function to get failed login attempts
CREATE OR REPLACE FUNCTION get_failed_login_attempts(
  user_id UUID,
  minutes INTEGER DEFAULT 15
)
RETURNS INTEGER AS $$
BEGIN
  RETURN (
    SELECT COUNT(*)
    FROM security_events
    WHERE user_id = $1
    AND event_type = 'failed_login'
    AND created_at >= NOW() - (minutes || ' minutes')::INTERVAL
  );
END;
$$ LANGUAGE plpgsql;

-- Create function to check for suspicious activity
CREATE OR REPLACE FUNCTION check_suspicious_activity(user_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
  RETURN (
    -- Check for multiple failed login attempts
    get_failed_login_attempts(user_id) > 5
    OR
    -- Check for rapid document access
    EXISTS (
      SELECT 1
      FROM document_analytics
      WHERE user_id = $1
      AND created_at >= NOW() - '1 minute'::INTERVAL
      GROUP BY document_id
      HAVING COUNT(*) > 10
    )
  );
END;
$$ LANGUAGE plpgsql; 