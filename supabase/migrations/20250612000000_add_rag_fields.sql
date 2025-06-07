ALTER TABLE public.document_chunks
  ADD COLUMN IF NOT EXISTS chunk_header TEXT,
  ADD COLUMN IF NOT EXISTS page_number INT,
  ADD COLUMN IF NOT EXISTS section TEXT;
 
ALTER TABLE public.documents
  ADD COLUMN IF NOT EXISTS processing_notes TEXT; 