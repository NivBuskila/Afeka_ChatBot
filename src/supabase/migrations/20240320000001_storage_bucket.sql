-- Create storage bucket for documents
INSERT INTO storage.buckets (id, name, public)
VALUES ('documents', 'documents', true);

-- Create storage policies
CREATE POLICY "Documents are publicly accessible"
  ON storage.objects FOR SELECT
  USING (bucket_id = 'documents');

CREATE POLICY "Documents are uploadable by authenticated users"
  ON storage.objects FOR INSERT
  TO authenticated
  WITH CHECK (bucket_id = 'documents');

CREATE POLICY "Documents are deletable by authenticated users"
  ON storage.objects FOR DELETE
  TO authenticated
  USING (bucket_id = 'documents'); 