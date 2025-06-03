# Hybrid Search Implementation Summary

This document summarizes the implementation of hybrid search functionality for the Afeka_ChatBot project.

## What is Hybrid Search?

Hybrid search combines semantic vector search with traditional keyword-based search to provide more accurate search results, especially for Hebrew language documents. By combining these two approaches, we can:

1. Find semantically relevant results (similar meaning) even when the exact words aren't used
2. Find exact keyword matches for high precision 
3. Combine both results using weighted scoring for optimal retrieval

## Implementation Details

The hybrid search functionality is implemented through:

1. **SQL Functions in Supabase**:
   - `hybrid_search_documents`: The main function that combines vector similarity with full-text search
   - Optimized version with performance improvements to prevent timeouts

2. **Frontend Integration**:
   - The ChatWindow component uses the hybrid search for querying documents

3. **Backend Support**:
   - The document processor creates vector embeddings for document chunks
   - Backend API exposes endpoints that utilize hybrid search

## Performance Optimization

The hybrid search function has been optimized to prevent timeouts and handle larger document collections:

1. **Query Optimization**:
   - Limited the initial vector search to 500 candidates
   - Reduced computational complexity by limiting joins
   - Applied indexes for faster retrieval

2. **Database Indexes**:
   - Added vector index: `idx_document_chunks_embedding`
   - Added document ID index: `idx_document_chunks_document_id`
   - Added text search index: `idx_document_chunks_chunk_text`

3. **Chunking Parameters**:
   - Increased chunk size from 800 to 2000 characters
   - Limited maximum vectors per document to 500 (down from 1000)

## Migration and Setup

The hybrid search functionality can be applied to a Supabase database in multiple ways:

1. **Automated Script**:
   - Run `python src/backend/apply_hybrid_search.py` to apply migrations programmatically

2. **Manual SQL Application**:
   - Execute the SQL in `src/supabase/manual_migration.sql` through the Supabase SQL Editor

3. **Batch File**:
   - Run `apply_fixed_hybrid_search.bat` on Windows systems

## Verification

To verify that the hybrid search functionality is working correctly:

1. Run `python verify_hybrid_search.py` which tests if the function exists and returns results
2. Or manually run a test query in SQL Editor:
   ```sql
   SELECT * FROM hybrid_search_documents(array_fill(0::float, ARRAY[768]), 'test', 0.5, 5);
   ```

## Troubleshooting

If you experience timeouts when running hybrid search:

1. Ensure you're using the latest optimized version of the function
2. Check that proper indexes are created on the `document_chunks` table
3. Consider reducing the number of chunks by increasing chunk size
4. See `readme-fix-deletion.md` for detailed troubleshooting steps

## References

- The SQL implementation is based on Supabase's [Vector Toolkit](https://github.com/supabase/vector-toolkit)
- Text search uses PostgreSQL's full-text search capabilities
- Vector search uses pgvector's cosine similarity (`<=>` operator)

## Benefits of Hybrid Search

- **Improved Recall**: Find more relevant documents by combining semantic and keyword search
- **Better Ranking**: Results are ranked by a weighted combination of semantic similarity and keyword relevance
- **Enhanced Hebrew Support**: Properly handles Hebrew text through PostgreSQL's text search capabilities
- **Adjustable Weights**: The semantic_weight and keyword_weight parameters can be adjusted at query time

## Performance Considerations

The hybrid search function performs two types of searches and combines the results, which may be more resource-intensive than pure semantic search. However, for most use cases, the improved relevance is worth the additional computational cost. 