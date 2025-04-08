-- קובץ ליצירת פונקציות הצ'אט החסרות
-- יש להריץ את הקובץ הזה ב-SQL Editor של Supabase

-- מחיקת הפונקציות הקיימות לפני יצירתן מחדש
DROP FUNCTION IF EXISTS create_conversation(UUID, TEXT, TEXT);
DROP FUNCTION IF EXISTS add_message(UUID, UUID, TEXT, TEXT);
DROP FUNCTION IF EXISTS update_response(BIGINT, TEXT, TEXT, INTEGER, JSONB);
DROP FUNCTION IF EXISTS get_user_conversations(UUID, INTEGER, INTEGER);
DROP FUNCTION IF EXISTS get_conversation_messages(UUID, INTEGER, INTEGER);

-- 1. פונקציה ליצירת שיחה חדשה
CREATE OR REPLACE FUNCTION create_conversation(
  p_user_id UUID,
  p_title TEXT DEFAULT NULL,
  p_model TEXT DEFAULT 'default'
) RETURNS UUID AS $$
DECLARE
  new_conversation_id UUID;
BEGIN
  INSERT INTO conversations (
    user_id,
    title,
    model
  ) VALUES (
    p_user_id,
    p_title,
    p_model
  ) RETURNING conversation_id INTO new_conversation_id;
  
  RETURN new_conversation_id;
END;
$$ LANGUAGE plpgsql;

-- 2. פונקציה להוספת הודעה לשיחה
CREATE OR REPLACE FUNCTION add_message(
  p_conversation_id UUID,
  p_user_id UUID,
  p_request TEXT,
  p_request_type TEXT DEFAULT 'TEXT'
) RETURNS BIGINT AS $$
DECLARE
  new_message_id BIGINT;
BEGIN
  -- עדכון זמן ההודעה האחרונה בשיחה
  UPDATE conversations 
  SET last_message_at = NOW()
  WHERE conversation_id = p_conversation_id;

  -- הוספת ההודעה החדשה
  INSERT INTO messages (
    conversation_id,
    user_id,
    request,
    request_type
  ) VALUES (
    p_conversation_id,
    p_user_id,
    p_request,
    p_request_type
  ) RETURNING message_id INTO new_message_id;
  
  RETURN new_message_id;
END;
$$ LANGUAGE plpgsql;

-- 3. פונקציה לעדכון תשובה להודעה
CREATE OR REPLACE FUNCTION update_response(
  p_message_id BIGINT,
  p_response TEXT,
  p_status TEXT DEFAULT 'COMPLETED',
  p_processing_time_ms INTEGER DEFAULT NULL,
  p_response_payload JSONB DEFAULT NULL
) RETURNS BOOLEAN AS $$
BEGIN
  UPDATE messages
  SET 
    response = p_response,
    status = p_status,
    status_updated_at = NOW(),
    processing_end_time = CASE WHEN p_status = 'COMPLETED' THEN NOW() ELSE processing_end_time END,
    processing_time_ms = p_processing_time_ms,
    response_payload = p_response_payload
  WHERE message_id = p_message_id;
  
  RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

-- 4. פונקציה לקבלת היסטוריית שיחות של משתמש
CREATE OR REPLACE FUNCTION get_user_conversations(
  p_user_id UUID,
  p_limit INTEGER DEFAULT 10,
  p_offset INTEGER DEFAULT 0
) RETURNS TABLE (
  conversation_id UUID,
  title TEXT,
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ,
  last_message_at TIMESTAMPTZ,
  is_active BOOLEAN,
  model TEXT,
  message_count BIGINT,
  last_message_text TEXT
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    c.conversation_id,
    c.title,
    c.created_at,
    c.updated_at,
    c.last_message_at,
    c.is_active,
    c.model,
    COUNT(m.message_id)::BIGINT AS message_count,
    (
      SELECT m2.request
      FROM messages m2
      WHERE m2.conversation_id = c.conversation_id
      ORDER BY m2.created_at DESC
      LIMIT 1
    ) AS last_message_text
  FROM conversations c
  LEFT JOIN messages m ON c.conversation_id = m.conversation_id
  WHERE c.user_id = p_user_id
  GROUP BY 
    c.conversation_id,
    c.title,
    c.created_at,
    c.updated_at,
    c.last_message_at,
    c.is_active,
    c.model
  ORDER BY c.last_message_at DESC NULLS LAST
  LIMIT p_limit
  OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;

-- 5. פונקציה לקבלת הודעות של שיחה מסוימת
CREATE OR REPLACE FUNCTION get_conversation_messages(
  p_conversation_id UUID,
  p_limit INTEGER DEFAULT 100,
  p_offset INTEGER DEFAULT 0
) RETURNS TABLE (
  message_id BIGINT,
  request TEXT,
  response TEXT,
  created_at TIMESTAMPTZ,
  status TEXT,
  request_type TEXT
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    m.message_id,
    m.request,
    m.response,
    m.created_at,
    m.status,
    m.request_type
  FROM messages m
  WHERE m.conversation_id = p_conversation_id
  ORDER BY m.created_at ASC
  LIMIT p_limit
  OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;

-- לאחר יצירת הפונקציות, יש להעניק הרשאות ביצוע
GRANT EXECUTE ON FUNCTION create_conversation(UUID, TEXT, TEXT) TO authenticated, anon;
GRANT EXECUTE ON FUNCTION add_message(UUID, UUID, TEXT, TEXT) TO authenticated, anon;
GRANT EXECUTE ON FUNCTION update_response(BIGINT, TEXT, TEXT, INTEGER, JSONB) TO authenticated, anon;
GRANT EXECUTE ON FUNCTION get_user_conversations(UUID, INTEGER, INTEGER) TO authenticated, anon;
GRANT EXECUTE ON FUNCTION get_conversation_messages(UUID, INTEGER, INTEGER) TO authenticated, anon; 