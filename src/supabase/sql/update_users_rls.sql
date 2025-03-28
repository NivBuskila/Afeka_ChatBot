-- First, remove all existing policies
DROP POLICY IF EXISTS "Users are insertable by authenticated users" ON users;
DROP POLICY IF EXISTS "Users are updatable by authenticated users" ON users;
DROP POLICY IF EXISTS "Users are deletable by authenticated users" ON users;
DROP POLICY IF EXISTS "Users can add their own record" ON users;
DROP POLICY IF EXISTS "Users can update their own record" ON users;
DROP POLICY IF EXISTS "Users can delete their own record" ON users;
DROP POLICY IF EXISTS "Admins can manage all users" ON users;

-- Basic insert policy - authenticated users can insert their own records
CREATE POLICY "Users can insert their own record"
  ON users FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = id);

-- Basic read policy - authenticated users can view all records
CREATE POLICY "Users can view all records"
  ON users FOR SELECT
  TO authenticated
  USING (true);

-- Basic update policy - authenticated users can update only their own records
CREATE POLICY "Users can update their own record"
  ON users FOR UPDATE
  TO authenticated
  USING (auth.uid() = id);

-- Basic delete policy - authenticated users can delete only their own records
CREATE POLICY "Users can delete their own record"
  ON users FOR DELETE
  TO authenticated
  USING (auth.uid() = id);

-- Check if the updated_at trigger exists
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_trigger
    WHERE tgname = 'update_users_updated_at'
  ) THEN
    CREATE TRIGGER update_users_updated_at
      BEFORE UPDATE ON users
      FOR EACH ROW
      EXECUTE FUNCTION update_updated_at_column();
  END IF;
END $$; 