-- Reset all policies
DO $$ 
DECLARE
    table_name text;
BEGIN
    FOR table_name IN 
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public'
    LOOP
        EXECUTE format('DROP POLICY IF EXISTS "Enable read for all" ON %I', table_name);
        EXECUTE format('DROP POLICY IF EXISTS "Enable insert for authenticated users only" ON %I', table_name);
        EXECUTE format('DROP POLICY IF EXISTS "Enable update for users based on email" ON %I', table_name);
        EXECUTE format('DROP POLICY IF EXISTS "Enable delete for users based on email" ON %I', table_name);
        
        -- Enable RLS
        EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', table_name);
        
        -- Create basic policies
        EXECUTE format('CREATE POLICY "Enable read for all" ON %I FOR SELECT USING (true)', table_name);
        EXECUTE format('CREATE POLICY "Enable insert for authenticated users only" ON %I FOR INSERT WITH CHECK (auth.role() = ''authenticated'')', table_name);
        EXECUTE format('CREATE POLICY "Enable update for authenticated users" ON %I FOR UPDATE USING (auth.role() = ''authenticated'')', table_name);
        EXECUTE format('CREATE POLICY "Enable delete for authenticated users" ON %I FOR DELETE USING (auth.role() = ''authenticated'')', table_name);
    END LOOP;
END $$;

-- Grant permissions to roles
GRANT USAGE ON SCHEMA public TO postgres, anon, authenticated, service_role;
GRANT ALL ON ALL TABLES IN SCHEMA public TO postgres, anon, authenticated, service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO postgres, anon, authenticated, service_role;
GRANT ALL ON ALL ROUTINES IN SCHEMA public TO postgres, anon, authenticated, service_role;

-- Specific policies for users table
DROP POLICY IF EXISTS "Users can update own record" ON users;
CREATE POLICY "Users can update own record" ON users
FOR UPDATE USING (auth.uid() = id);

-- Specific policies for admins table
DROP POLICY IF EXISTS "Admin access" ON admins;
CREATE POLICY "Admin access" ON admins
FOR ALL USING (
    EXISTS (
        SELECT 1 FROM users
        WHERE users.id = auth.uid()
        AND (users.email LIKE '%admin%' OR users.role = 'admin')
    )
);

-- Specific policies for conversations
DROP POLICY IF EXISTS "Users can view own conversations" ON conversations;
CREATE POLICY "Users can view own conversations" ON conversations
FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own conversations" ON conversations;
CREATE POLICY "Users can insert own conversations" ON conversations
FOR INSERT WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own conversations" ON conversations;
CREATE POLICY "Users can update own conversations" ON conversations
FOR UPDATE USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete own conversations" ON conversations;
CREATE POLICY "Users can delete own conversations" ON conversations
FOR DELETE USING (auth.uid() = user_id);

-- Specific policies for messages
DROP POLICY IF EXISTS "Users can view conversation messages" ON messages;
CREATE POLICY "Users can view conversation messages" ON messages
FOR SELECT USING (
    EXISTS (
        SELECT 1 FROM conversations
        WHERE conversations.conversation_id = messages.conversation_id
        AND conversations.user_id = auth.uid()
    )
);

DROP POLICY IF EXISTS "Users can insert conversation messages" ON messages;
CREATE POLICY "Users can insert conversation messages" ON messages
FOR INSERT WITH CHECK (
    EXISTS (
        SELECT 1 FROM conversations
        WHERE conversations.conversation_id = messages.conversation_id
        AND conversations.user_id = auth.uid()
    )
);

-- Reset and recreate functions
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.users (id, email, role)
    VALUES (NEW.id, NEW.email, 
        CASE 
            WHEN NEW.email LIKE '%admin%' THEN 'admin'
            ELSE 'user'
        END
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Recreate trigger
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION handle_new_user();

-- Reset sequences
ALTER SEQUENCE IF EXISTS messages_message_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS documents_id_seq RESTART WITH 1;

-- Verify and fix any broken references
DELETE FROM messages WHERE conversation_id NOT IN (SELECT conversation_id FROM conversations);
DELETE FROM conversations WHERE user_id NOT IN (SELECT id FROM users);

-- Update statistics
ANALYZE users;
ANALYZE conversations;
ANALYZE messages;
ANALYZE documents;
ANALYZE admins; 