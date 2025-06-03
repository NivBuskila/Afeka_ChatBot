# Hybrid Search Setup Instructions

This document explains how to set up the hybrid search functionality for the Afeka_ChatBot project. Hybrid search combines semantic (vector) search with traditional keyword search to provide more accurate search results, especially for Hebrew text.

## What is Hybrid Search?

Hybrid search combines two powerful search techniques:
1. **Semantic Search**: Using vector embeddings to find similar content based on meaning
2. **Keyword Search**: Using traditional text search to find exact term matches

This combined approach improves search results by:
- Finding conceptually similar content even when exact keywords aren't present
- Prioritizing exact keyword matches when they are relevant
- Working effectively with Hebrew text

## Setup Instructions

### Option 1: Automatic Setup (Preferred)

Run the automatic setup script:

```bash
# On Windows
.\apply_hybrid_search.bat

# On Linux/Mac
python src/backend/apply_hybrid_search.py
```

The script will attempt to apply the hybrid search function to your Supabase database. If successful, it will also run a test to verify the function works correctly.

### Option 2: Manual Setup via Supabase SQL Editor

If the automatic setup fails, you can apply the SQL manually:

1. Login to your Supabase dashboard
2. Go to the SQL Editor
3. Create a new query
4. Copy and paste the contents of `src/supabase/manual_migration.sql`
5. Run the query

The SQL creates:
- `hybrid_search_documents` function for hybrid search
- `insert_document_chunk_basic` function for adding document chunks
- Helper functions for checking if the setup is complete

### Option 3: Manual SQL Application via API

If you have direct database access, you can run the SQL directly using psql or another PostgreSQL client:

```bash
psql -h your-supabase-db-host -U postgres -d postgres -f src/supabase/manual_migration.sql
```

## Verifying the Setup

To verify that the hybrid search function is working correctly:

1. Run the test script:
```bash
python src/backend/test_rag_search.py
```

2. Or manually test via the SQL editor with:
```sql
SELECT * FROM hybrid_search_documents(
  array_fill(0::float, ARRAY[768]), -- Dummy embedding
  'סטודנט',                        -- Test query
  0.5,                              -- Lower threshold for testing
  5                                 -- Limit results
);
```

## Troubleshooting

If you encounter issues:

1. **Function Not Found**: Ensure the SQL was executed successfully without errors
2. **No Results**: Check that you have documents with Hebrew text and embeddings in your database
3. **Error in Execution**: Check the PostgreSQL logs for specific error messages
4. **Permission Issues**: Ensure your Supabase user has permission to create functions

For further assistance, check the logs in the console or contact the development team.

## Technical Details

The hybrid search function combines:
- Vector similarity using the `<=>` operator for semantic search
- PostgreSQL's full-text search with `to_tsvector` and `plainto_tsquery` for keyword search
- Weights (default: 60% semantic, 40% keyword) that can be adjusted at query time

The function signature is:
```sql
hybrid_search_documents(
  query_embedding vector(768),
  query_text text,
  match_threshold float DEFAULT 0.70,
  match_count int DEFAULT 10,
  semantic_weight float DEFAULT 0.6,
  keyword_weight float DEFAULT 0.4
)
``` 