-- This function bypasses RLS to get all users and admins for the dashboard
DROP FUNCTION IF EXISTS get_all_users_and_admins();

CREATE OR REPLACE FUNCTION get_all_users_and_admins()
RETURNS SETOF JSON AS $$
BEGIN
    -- Return all users with is_admin flag instead of role
    RETURN QUERY
    SELECT json_build_object(
        'id', u.id,
        'email', u.email,
        'name', u.name,
        'created_at', u.created_at,
        'is_admin', a.id IS NOT NULL,
        'department', a.department
    )
    FROM users u
    LEFT JOIN admins a ON u.id = a.user_id
    ORDER BY u.created_at DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Ensure this function is accessible without RLS
GRANT EXECUTE ON FUNCTION get_all_users_and_admins() TO authenticated;
COMMENT ON FUNCTION get_all_users_and_admins() IS 'Gets all users and admins for dashboard display, bypassing RLS';

-- This function counts rows in any table, bypassing RLS
CREATE OR REPLACE FUNCTION count_rows(table_name TEXT)
RETURNS INTEGER AS $$
DECLARE
    count_query TEXT;
    row_count INTEGER;
BEGIN
    -- Construct and execute dynamic SQL to count rows
    count_query := 'SELECT COUNT(*) FROM ' || quote_ident(table_name);
    
    EXECUTE count_query INTO row_count;
    
    RETURN row_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Ensure this function is accessible without RLS
GRANT EXECUTE ON FUNCTION count_rows(TEXT) TO authenticated;
COMMENT ON FUNCTION count_rows(TEXT) IS 'Counts rows in any table, bypassing RLS'; 