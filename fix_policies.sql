-- Drop existing policies
DROP POLICY IF EXISTS "Enable read access for all users" ON "public"."users";
DROP POLICY IF EXISTS "Enable insert for authenticated users only" ON "public"."users";
DROP POLICY IF EXISTS "Enable update for users based on id" ON "public"."users";
DROP POLICY IF EXISTS "Enable delete for users based on id" ON "public"."users";
DROP POLICY IF EXISTS "Enable read access for all users" ON "public"."documents";
DROP POLICY IF EXISTS "Enable insert for authenticated users only" ON "public"."documents";
DROP POLICY IF EXISTS "Enable update for document owners" ON "public"."documents";
DROP POLICY IF EXISTS "Enable delete for document owners" ON "public"."documents";
DROP POLICY IF EXISTS "Enable read access for all users" ON "public"."admins";
DROP POLICY IF EXISTS "Enable insert for authenticated users only" ON "public"."admins";
DROP POLICY IF EXISTS "Enable update for admins" ON "public"."admins";
DROP POLICY IF EXISTS "Enable delete for admins" ON "public"."admins";

-- Enable RLS
ALTER TABLE "public"."users" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."documents" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."admins" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."conversations" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."messages" ENABLE ROW LEVEL SECURITY;

-- Users policies
CREATE POLICY "Enable read access for all users" ON "public"."users"
FOR SELECT USING (true);

CREATE POLICY "Enable insert for authenticated users only" ON "public"."users"
FOR INSERT WITH CHECK (auth.uid() = id);

CREATE POLICY "Enable update for users based on id" ON "public"."users"
FOR UPDATE USING (auth.uid() = id) WITH CHECK (auth.uid() = id);

CREATE POLICY "Enable delete for users based on id" ON "public"."users"
FOR DELETE USING (auth.uid() = id);

-- Documents policies
CREATE POLICY "Enable read access for all users" ON "public"."documents"
FOR SELECT USING (true);

CREATE POLICY "Enable insert for authenticated users only" ON "public"."documents"
FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Enable update for document owners and admins" ON "public"."documents"
FOR UPDATE USING (
    EXISTS (
        SELECT 1 FROM admins
        WHERE user_id = auth.uid()
    )
);

CREATE POLICY "Enable delete for document owners and admins" ON "public"."documents"
FOR DELETE USING (
    EXISTS (
        SELECT 1 FROM admins
        WHERE user_id = auth.uid()
    )
);

-- Admins policies
CREATE POLICY "Enable read access for all users" ON "public"."admins"
FOR SELECT USING (true);

CREATE POLICY "Enable insert for authenticated users only" ON "public"."admins"
FOR INSERT WITH CHECK (
    auth.jwt() ->> 'email' LIKE '%admin%'
);

CREATE POLICY "Enable update for admins" ON "public"."admins"
FOR UPDATE USING (
    EXISTS (
        SELECT 1 FROM admins
        WHERE user_id = auth.uid()
    )
);

CREATE POLICY "Enable delete for admins" ON "public"."admins"
FOR DELETE USING (
    EXISTS (
        SELECT 1 FROM admins
        WHERE user_id = auth.uid()
    )
);

-- Conversations policies
CREATE POLICY "Enable read access for conversation participants" ON "public"."conversations"
FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Enable insert for authenticated users" ON "public"."conversations"
FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Enable update for conversation owners" ON "public"."conversations"
FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Enable delete for conversation owners" ON "public"."conversations"
FOR DELETE USING (auth.uid() = user_id);

-- Messages policies
CREATE POLICY "Enable read access for conversation participants" ON "public"."messages"
FOR SELECT USING (
    EXISTS (
        SELECT 1 FROM conversations
        WHERE conversations.conversation_id = messages.conversation_id
        AND conversations.user_id = auth.uid()
    )
);

CREATE POLICY "Enable insert for conversation participants" ON "public"."messages"
FOR INSERT WITH CHECK (
    EXISTS (
        SELECT 1 FROM conversations
        WHERE conversations.conversation_id = messages.conversation_id
        AND conversations.user_id = auth.uid()
    )
);

CREATE POLICY "Enable update for message owners" ON "public"."messages"
FOR UPDATE USING (
    EXISTS (
        SELECT 1 FROM conversations
        WHERE conversations.conversation_id = messages.conversation_id
        AND conversations.user_id = auth.uid()
    )
);

CREATE POLICY "Enable delete for message owners" ON "public"."messages"
FOR DELETE USING (
    EXISTS (
        SELECT 1 FROM conversations
        WHERE conversations.conversation_id = messages.conversation_id
        AND conversations.user_id = auth.uid()
    )
);

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon;
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT USAGE ON SCHEMA public TO service_role;

GRANT ALL ON ALL TABLES IN SCHEMA public TO anon;
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;

GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO service_role; 