-- ⚡ Advanced Chat Performance Optimization
-- Target: Reduce chat_sessions queries from 500ms+ to <100ms

-- 🎯 Composite index for chat sessions - most common query pattern
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_updated_desc 
ON chat_sessions(user_id, updated_at DESC) 
WHERE updated_at IS NOT NULL;

-- 🎯 Covering index - includes all commonly selected fields
CREATE INDEX IF NOT EXISTS idx_chat_sessions_covering 
ON chat_sessions(user_id, updated_at DESC) 
INCLUDE (id, title, created_at)
WHERE updated_at IS NOT NULL;

-- 🎯 Messages optimization - conversation lookup
CREATE INDEX IF NOT EXISTS idx_messages_conversation_created_asc 
ON messages(conversation_id, created_at ASC) 
WHERE conversation_id IS NOT NULL;

-- 🎯 Partial index for active sessions only (common pattern)
CREATE INDEX IF NOT EXISTS idx_chat_sessions_active_user 
ON chat_sessions(user_id, updated_at DESC) 
WHERE updated_at > (now() - interval '30 days');

-- 🎯 Message content search optimization
CREATE INDEX IF NOT EXISTS idx_messages_content_gin 
ON messages USING gin(to_tsvector('english', COALESCE(request, '') || ' ' || COALESCE(response, '')))
WHERE (request IS NOT NULL OR response IS NOT NULL);

-- 🎯 User activity tracking for analytics
CREATE INDEX IF NOT EXISTS idx_messages_user_created_desc 
ON messages(user_id, created_at DESC) 
WHERE created_at IS NOT NULL;

-- 🎯 API key usage optimization (reduce from 7s to milliseconds)
CREATE INDEX IF NOT EXISTS idx_api_key_usage_minute_key 
ON api_key_usage(usage_minute, api_key_id) 
WHERE usage_minute IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_api_key_usage_date_key 
ON api_key_usage(usage_date, api_key_id) 
WHERE usage_date IS NOT NULL;

-- Comments for performance tracking
COMMENT ON INDEX idx_chat_sessions_user_updated_desc IS 'Primary chat sessions query optimization - target <100ms';
COMMENT ON INDEX idx_chat_sessions_covering IS 'Covering index to avoid heap lookups';
COMMENT ON INDEX idx_messages_conversation_created_asc IS 'Message loading optimization for chat history';
COMMENT ON INDEX idx_api_key_usage_minute_key IS 'API key minute usage lookup optimization'; 