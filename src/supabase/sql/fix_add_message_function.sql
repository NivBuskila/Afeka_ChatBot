-- קובץ לפתרון בעיית פונקציית add_message
-- אין התאמה חד משמעית של פונקציית add_message בגלל פרמטר p_is_placeholder

-- מחיקת כל גרסאות הפונקציה הקיימות
DROP FUNCTION IF EXISTS add_message(UUID, UUID, TEXT, TEXT);
DROP FUNCTION IF EXISTS add_message(UUID, UUID, TEXT, TEXT, BOOLEAN);

-- יצירת פונקציה חדשה שתומכת בפרמטר הנוסף
CREATE OR REPLACE FUNCTION add_message(
  p_conversation_id UUID,
  p_user_id UUID,
  p_request TEXT,
  p_request_type TEXT DEFAULT 'TEXT',
  p_is_placeholder BOOLEAN DEFAULT FALSE
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
    request_type,
    metadata
  ) VALUES (
    p_conversation_id,
    p_user_id,
    p_request,
    p_request_type,
    CASE WHEN p_is_placeholder THEN '{"is_placeholder": true}'::JSONB ELSE '{}'::JSONB END
  ) RETURNING message_id INTO new_message_id;
  
  RETURN new_message_id;
END;
$$ LANGUAGE plpgsql;

-- הענקת הרשאות ביצוע
GRANT EXECUTE ON FUNCTION add_message(UUID, UUID, TEXT, TEXT, BOOLEAN) TO authenticated, anon; 