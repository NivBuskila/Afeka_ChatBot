-- 1. עדכון טבלת המשתמשים עם השדות החסרים
ALTER TABLE users
  ADD COLUMN IF NOT EXISTS name TEXT,
  ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'active',
  ADD COLUMN IF NOT EXISTS last_sign_in TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS preferred_language TEXT DEFAULT 'he',
  ADD COLUMN IF NOT EXISTS timezone TEXT DEFAULT 'Asia/Jerusalem',
  ADD COLUMN IF NOT EXISTS subscription_plan TEXT DEFAULT 'free',
  ADD COLUMN IF NOT EXISTS subscription_expiry TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}';

-- 2. יצירת טבלת שיחות
CREATE TABLE IF NOT EXISTS conversations (
  conversation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  last_message_at TIMESTAMPTZ,
  model TEXT DEFAULT 'default',
  metadata JSONB DEFAULT '{}'
);

-- 3. יצירת טבלת הודעות
CREATE TABLE IF NOT EXISTS messages (
  message_id BIGSERIAL PRIMARY KEY,
  conversation_id UUID NOT NULL REFERENCES conversations(conversation_id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  request TEXT,
  response TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  status TEXT NOT NULL DEFAULT 'RECEIVED',
  status_updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  error_message TEXT,
  request_type TEXT DEFAULT 'TEXT',
  request_payload JSONB,
  response_payload JSONB,
  status_code INTEGER,
  processing_start_time TIMESTAMPTZ,
  processing_end_time TIMESTAMPTZ,
  processing_time_ms INTEGER,
  is_sensitive BOOLEAN DEFAULT FALSE,
  metadata JSONB DEFAULT '{}'
);

-- 4. יצירת אינדקסים
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_updated_at ON conversations(updated_at);
CREATE INDEX IF NOT EXISTS idx_conversations_last_message_at ON conversations(last_message_at);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);
CREATE INDEX IF NOT EXISTS idx_messages_status ON messages(status);

-- 5. יצירת טריגרים לעדכון שדות updated_at
CREATE OR REPLACE FUNCTION update_conversation_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_conversations_updated_at
  BEFORE UPDATE ON conversations
  FOR EACH ROW
  EXECUTE FUNCTION update_conversation_updated_at();

-- 6. הגדרת Row Level Security (RLS)
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

-- 7. יצירת פוליסות אבטחה עבור טבלת שיחות
CREATE POLICY "User can view own conversations"
  ON conversations FOR SELECT
  TO authenticated
  USING (user_id = auth.uid());

CREATE POLICY "User can insert own conversations"
  ON conversations FOR INSERT
  TO authenticated
  WITH CHECK (user_id = auth.uid());

CREATE POLICY "User can update own conversations"
  ON conversations FOR UPDATE
  TO authenticated
  USING (user_id = auth.uid());

CREATE POLICY "User can delete own conversations"
  ON conversations FOR DELETE
  TO authenticated
  USING (user_id = auth.uid());

-- 8. יצירת פוליסות אבטחה עבור טבלת הודעות
CREATE POLICY "User can view own messages"
  ON messages FOR SELECT
  TO authenticated
  USING (user_id = auth.uid());

CREATE POLICY "User can insert own messages"
  ON messages FOR INSERT
  TO authenticated
  WITH CHECK (user_id = auth.uid());

CREATE POLICY "User can update own messages"
  ON messages FOR UPDATE
  TO authenticated
  USING (user_id = auth.uid());

CREATE POLICY "User can delete own messages"
  ON messages FOR DELETE
  TO authenticated
  USING (user_id = auth.uid());

-- 9. פונקציה ליצירת שיחה חדשה
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

-- 10. פונקציה להוספת הודעה לשיחה
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

-- 11. פונקציה לעדכון תשובה להודעה
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

-- 12. פונקציה לקבלת היסטוריית שיחות של משתמש
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

-- 13. פונקציה לקבלת הודעות של שיחה מסוימת
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

-- 14. פונקציה לקבלת סטטיסטיקות שיחות של משתמש
CREATE OR REPLACE FUNCTION get_user_chat_statistics(
  p_user_id UUID
) RETURNS TABLE (
  total_conversations BIGINT,
  total_messages BIGINT,
  avg_messages_per_conversation NUMERIC,
  last_conversation_at TIMESTAMPTZ,
  active_conversations BIGINT
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    COUNT(DISTINCT c.conversation_id)::BIGINT AS total_conversations,
    COUNT(m.message_id)::BIGINT AS total_messages,
    ROUND(AVG(message_counts.count), 2) AS avg_messages_per_conversation,
    MAX(c.last_message_at) AS last_conversation_at,
    COUNT(DISTINCT c.conversation_id) FILTER (WHERE c.is_active = TRUE)::BIGINT AS active_conversations
  FROM conversations c
  LEFT JOIN messages m ON c.conversation_id = m.conversation_id
  LEFT JOIN (
    SELECT 
      conversation_id,
      COUNT(message_id) AS count
    FROM messages
    GROUP BY conversation_id
  ) message_counts ON c.conversation_id = message_counts.conversation_id
  WHERE c.user_id = p_user_id;
END;
$$ LANGUAGE plpgsql; 