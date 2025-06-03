import pytest
import asyncio
import os

# This test requires a RAGService instance, which might depend on
# language models, Supabase client, etc.
# Fixture for rag_service needs to be defined in conftest.py or similar.

# Example: Placeholder for RAGService if not using a fixture
# from src.ai.services.rag_service import RAGService # Adjust import path as needed
# async def get_test_rag_service():
#     # This would initialize RAGService with test configurations
#     # e.g., mock models, test Supabase client
#     service = RAGService(
#         supabase_url=os.getenv("SUPABASE_URL_TEST"), 
#         supabase_key=os.getenv("SUPABASE_SERVICE_KEY_TEST"),
#         # ... other necessary params like model names, etc.
#     )
#     await service.initialize_models() # If there's an async init
#     return service

@pytest.mark.asyncio # Mark as an async test
async def test_get_answer_sources(rag_service_fixture): # Renamed to avoid clash
    """Tests that RAGService.get_answer returns sources with section when add_sources=True."""
    # Ensure rag_service_fixture is an initialized RAGService instance.
    # This test also implies that there is some data in the DB that can be matched.
    # The query "מה רשום בסעיף 1.2?" is specific and might require specific test data.

    # For this test to pass, the underlying RPCs (semantic/hybrid search)
    # must be returning 'section', 'chunk_header', 'page_number' etc.
    # And the RAGService must be correctly processing these fields into the 'sources'.

    out = await rag_service_fixture.get_answer(
        "מה רשום בסעיף 1.2?",
        add_sources=True,
        use_hybrid=False # Testing with semantic search first
    )

    assert "sources" in out, "'sources' key missing from RAGService.get_answer response."
    assert out["sources"], (
        "Expected at least one source, but got none. "
        "Ensure test data exists and is retrievable for the query 'מה רשום בסעיף 1.2?'"
    )
    
    first_source = out["sources"][0]
    assert "section" in first_source, "'section' key missing from the first source."
    assert first_source["section"] is not None, "'section' in the first source should not be None."
    assert isinstance(first_source["section"], str), "'section' in the first source should be a string."
    assert len(first_source["section"]) > 0, "'section' in the first source should not be an empty string. Consider using a placeholder if section is not always present."

    # Optionally, test with use_hybrid=True if your test DB is set up for hybrid search
    out_hybrid = await rag_service_fixture.get_answer(
        "מה רשום בסעיף 1.2?",
        add_sources=True,
        use_hybrid=True
    )
    assert "sources" in out_hybrid, "'sources' key missing from RAGService.get_answer response (hybrid)."
    assert out_hybrid["sources"], (
        "Expected at least one source with hybrid search, but got none. "
        "Ensure test data and hybrid search are correctly configured."
    )
    first_source_hybrid = out_hybrid["sources"][0]
    assert "section" in first_source_hybrid, "'section' key missing from the first source (hybrid)."
    assert first_source_hybrid["section"] is not None, "'section' in the first source (hybrid) should not be None."
    assert isinstance(first_source_hybrid["section"], str), "'section' in the first source (hybrid) should be a string."
    assert len(first_source_hybrid["section"]) > 0, "'section' in the first source (hybrid) should not be an empty string." 