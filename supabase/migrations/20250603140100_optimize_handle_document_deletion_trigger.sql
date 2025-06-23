CREATE OR REPLACE FUNCTION public.handle_document_deletion()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
AS $function$
BEGIN
    -- Delete related embeddings from the '''embeddings''' table
    -- This will be faster once idx_embeddings_metadata_gin is created
    DELETE FROM embeddings
    WHERE metadata->>'document_id' = OLD.id::text;

    -- Delete related analytics data from '''document_analytics'''
    -- The document_chunks are deleted by the application code before this trigger runs.
    DELETE FROM document_analytics
    WHERE document_id = OLD.id;
    
    RETURN OLD;
END;
$function$;

COMMENT ON FUNCTION public.handle_document_deletion() IS 'Handles cleanup of related data when a document is deleted. Optimized to remove redundant document_chunks deletion.'; 