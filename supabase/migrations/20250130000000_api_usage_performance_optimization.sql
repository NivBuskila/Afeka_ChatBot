-- API Usage Performance Optimization
-- Created: 2025-01-30
-- Purpose: Optimize token usage aggregation queries for dashboard performance

-- Drop existing functions if they exist (to handle type changes)
DROP FUNCTION IF EXISTS aggregate_daily_usage(DATE, INTEGER[]);
DROP FUNCTION IF EXISTS aggregate_minute_usage(TIMESTAMPTZ, INTEGER[]);
DROP FUNCTION IF EXISTS get_all_keys_usage_stats(DATE, TIMESTAMPTZ);

-- Function to aggregate daily usage for multiple API keys
CREATE OR REPLACE FUNCTION aggregate_daily_usage(
    target_date DATE,
    key_ids INTEGER[]
)
RETURNS TABLE (
    api_key_id INTEGER,
    total_tokens INTEGER,
    total_requests INTEGER
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        u.api_key_id::INTEGER,
        COALESCE(SUM(u.tokens_used), 0)::INTEGER as total_tokens,
        COALESCE(SUM(u.requests_count), 0)::INTEGER as total_requests
    FROM api_key_usage u
    WHERE 
        u.usage_date = target_date
        AND u.api_key_id = ANY(key_ids)
    GROUP BY u.api_key_id;
END;
$$;

-- Function to aggregate current minute usage for multiple API keys  
CREATE OR REPLACE FUNCTION aggregate_minute_usage(
    target_minute TIMESTAMPTZ,
    key_ids INTEGER[]
)
RETURNS TABLE (
    api_key_id INTEGER,
    total_tokens INTEGER,
    total_requests INTEGER
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        u.api_key_id::INTEGER,
        COALESCE(SUM(u.tokens_used), 0)::INTEGER as total_tokens,
        COALESCE(SUM(u.requests_count), 0)::INTEGER as total_requests
    FROM api_key_usage u
    WHERE 
        u.usage_minute = target_minute
        AND u.api_key_id = ANY(key_ids)
    GROUP BY u.api_key_id;
END;
$$;

-- Function to get comprehensive usage statistics for all keys at once
CREATE OR REPLACE FUNCTION get_all_keys_usage_stats(
    target_date DATE DEFAULT CURRENT_DATE,
    target_minute TIMESTAMPTZ DEFAULT date_trunc('minute', NOW())
)
RETURNS TABLE (
    api_key_id INTEGER,
    daily_tokens INTEGER,
    daily_requests INTEGER,
    minute_tokens INTEGER,
    minute_requests INTEGER
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    WITH daily_stats AS (
        SELECT 
            usage.api_key_id,
            COALESCE(SUM(usage.tokens_used), 0)::INTEGER as tokens,
            COALESCE(SUM(usage.requests_count), 0)::INTEGER as requests
        FROM api_key_usage usage
        WHERE usage.usage_date = target_date
        GROUP BY usage.api_key_id
    ),
    minute_stats AS (
        SELECT 
            usage.api_key_id,
            COALESCE(SUM(usage.tokens_used), 0)::INTEGER as tokens,
            COALESCE(SUM(usage.requests_count), 0)::INTEGER as requests
        FROM api_key_usage usage
        WHERE usage.usage_minute = target_minute
        GROUP BY usage.api_key_id
    ),
    all_keys AS (
        SELECT DISTINCT usage.api_key_id FROM api_key_usage usage
        UNION
        SELECT keys.id as api_key_id FROM api_keys keys WHERE keys.is_active = true
    )
    SELECT 
        ak.api_key_id::INTEGER,
        COALESCE(ds.tokens, 0)::INTEGER as daily_tokens,
        COALESCE(ds.requests, 0)::INTEGER as daily_requests,
        COALESCE(ms.tokens, 0)::INTEGER as minute_tokens,
        COALESCE(ms.requests, 0)::INTEGER as minute_requests
    FROM all_keys ak
    LEFT JOIN daily_stats ds ON ak.api_key_id = ds.api_key_id
    LEFT JOIN minute_stats ms ON ak.api_key_id = ms.api_key_id
    ORDER BY ak.api_key_id;
END;
$$;

-- Add indexes for better performance on common queries
CREATE INDEX IF NOT EXISTS idx_api_key_usage_date_key 
ON api_key_usage(usage_date, api_key_id);

CREATE INDEX IF NOT EXISTS idx_api_key_usage_minute_key 
ON api_key_usage(usage_minute, api_key_id);

-- Add composite index for faster aggregations
CREATE INDEX IF NOT EXISTS idx_api_key_usage_composite
ON api_key_usage(api_key_id, usage_date, usage_minute);

-- Grant execution permissions
GRANT EXECUTE ON FUNCTION aggregate_daily_usage(DATE, INTEGER[]) TO authenticated;
GRANT EXECUTE ON FUNCTION aggregate_minute_usage(TIMESTAMPTZ, INTEGER[]) TO authenticated;  
GRANT EXECUTE ON FUNCTION get_all_keys_usage_stats(DATE, TIMESTAMPTZ) TO authenticated;

-- Comment functions for documentation
COMMENT ON FUNCTION aggregate_daily_usage IS 'Efficiently aggregate daily token/request usage for multiple API keys';
COMMENT ON FUNCTION aggregate_minute_usage IS 'Efficiently aggregate current minute token/request usage for multiple API keys';
COMMENT ON FUNCTION get_all_keys_usage_stats IS 'Get comprehensive usage statistics for all API keys in one query';

-- Performance notes:
-- These functions use aggregation at the database level to reduce data transfer
-- and improve query performance for the token usage dashboard 