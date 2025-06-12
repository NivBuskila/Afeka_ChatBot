-- יצירת טבלת API Keys
CREATE TABLE api_keys (
  id BIGSERIAL PRIMARY KEY,
  key_name TEXT NOT NULL UNIQUE,
  api_key TEXT NOT NULL,
  provider TEXT NOT NULL DEFAULT 'gemini',
  is_active BOOLEAN NOT NULL DEFAULT true,
  daily_limit_tokens INTEGER DEFAULT 1000000,
  daily_limit_requests INTEGER DEFAULT 1500,
  minute_limit_requests INTEGER DEFAULT 15,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- יצירת טבלת מעקב שימוש
CREATE TABLE api_key_usage (
  id BIGSERIAL PRIMARY KEY,
  api_key_id BIGINT NOT NULL REFERENCES api_keys(id) ON DELETE CASCADE,
  usage_date DATE NOT NULL DEFAULT CURRENT_DATE,
  usage_minute TIMESTAMP WITH TIME ZONE NOT NULL,
  tokens_used INTEGER NOT NULL DEFAULT 0,
  requests_count INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- יצירת אינדקסים
CREATE INDEX idx_api_keys_provider ON api_keys(provider);
CREATE INDEX idx_api_keys_active ON api_keys(is_active);
CREATE INDEX idx_api_key_usage_key_date ON api_key_usage(api_key_id, usage_date);
CREATE INDEX idx_api_key_usage_minute ON api_key_usage(usage_minute);

-- הפעלת RLS
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_key_usage ENABLE ROW LEVEL SECURITY;

-- יצירת מדיניות גישה
CREATE POLICY "API keys are viewable by authenticated users"
  ON api_keys FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "API key usage is viewable by authenticated users"
  ON api_key_usage FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "API key usage is insertable by authenticated users"
  ON api_key_usage FOR INSERT
  TO authenticated
  WITH CHECK (true);

CREATE POLICY "API key usage is updatable by authenticated users"
  ON api_key_usage FOR UPDATE
  TO authenticated
  USING (true);

