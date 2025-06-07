#!/usr/bin/env python3
"""Phase 1 Foundation Verification Script"""

import sys
import traceback
from datetime import datetime

def test_section(name: str):
    """Print test section header"""
    print(f"\n🧪 {name}")
    print("-" * 50)

def test_imports():
    """Test all Phase 1 imports"""
    test_section("Testing Imports")
    
    try:
        # Existing imports
        from app.domain.base import DomainEntity, TimestampedEntity
        from app.domain.user import User
        from app.domain.chat import ChatSession, ChatMessage  
        from app.domain.document import Document
        print("✅ Existing domain models imported successfully")
        
        # New RAG imports
        from app.domain.base import BaseEntity, BaseValueObject
        from app.domain.rag import Document as RAGDocument, ProcessingStatus, DocumentChunk
        from app.config.rag_settings import rag_settings
        from app.core.rag_exceptions import RAGException
        print("✅ New RAG foundation imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        traceback.print_exc()
        return False

def test_existing_functionality():
    """Test existing models still work"""
    test_section("Testing Existing Functionality")
    
    try:
        from app.domain.user import User
        from app.domain.chat import ChatSession
        from app.domain.document import Document
        
        # Create existing models
        user = User(email="test@afeka.ac.il", name="Test User")
        assert user.email == "test@afeka.ac.il"
        assert user.display_name == "Test User"
        print(f"✅ User model works: {user.display_name}")
        
        # ✅ FIXED: Use correct size calculation
        # 0.001 MB = 0.001 * 1024 * 1024 = 1048.576 bytes ≈ 1049 bytes
        doc = Document(name="test.pdf", type="application/pdf", size=1049, url="http://test.com/doc.pdf")
        assert doc.name == "test.pdf"
        assert abs(doc.size_mb - 0.001) < 0.0001  # Use approximate comparison for floating point
        print(f"✅ Document model works: {doc.name}")
        
        session = ChatSession(user_id=user.id, title="Test Session")
        assert session.title == "Test Session"
        print(f"✅ Chat session works: {session.title}")
        
        return True
    except Exception as e:
        print(f"❌ Existing functionality failed: {e}")
        traceback.print_exc()
        return False

def test_rag_foundation():
    """Test new RAG foundation"""
    test_section("Testing RAG Foundation")
    
    try:
        from app.domain.rag import Document as RAGDocument, ProcessingStatus, DocumentChunk
        from app.config.rag_settings import rag_settings
        
        # Test RAG document
        rag_doc = RAGDocument(title="Test RAG Doc", content="Test content for RAG")
        assert rag_doc.title == "Test RAG Doc"
        assert rag_doc.processing_status == ProcessingStatus.PENDING
        print(f"✅ RAG Document works: {rag_doc.title}")
        
        # Test chunk
        chunk = DocumentChunk(document_id=rag_doc.id, chunk_text="Sample chunk")
        assert chunk.chunk_text == "Sample chunk"
        assert chunk.document_id == rag_doc.id
        print(f"✅ Document chunk works: {len(chunk.chunk_text)} chars")
        
        # Test settings
        assert hasattr(rag_settings, 'embedding_model')
        assert hasattr(rag_settings, 'search_similarity_threshold')
        print(f"✅ RAG settings work: {rag_settings.embedding_model}")
        
        return True
    except Exception as e:
        print(f"❌ RAG foundation failed: {e}")
        traceback.print_exc()
        return False

def test_exception_handling():
    """Test RAG exception handling"""
    test_section("Testing Exception Handling")
    
    try:
        from app.core.rag_exceptions import RAGException, DocumentProcessingException
        
        # Test exception creation
        exc = RAGException("Test error", error_code="TEST_ERROR")
        assert str(exc) == "Test error"
        assert exc.error_code == "TEST_ERROR"
        print("✅ RAG exceptions work")
        
        # Test specific exception
        doc_exc = DocumentProcessingException("Doc error", document_id="test-123")
        assert doc_exc.document_id == "test-123"
        print("✅ Document processing exceptions work")
        
        return True
    except Exception as e:
        print(f"❌ Exception handling failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all Phase 1 tests"""
    print("🔍 Phase 1 Foundation Verification")
    print("=" * 60)
    print(f"Timestamp: {datetime.now()}")
    
    tests = [
        ("Import Verification", test_imports),
        ("Existing Functionality", test_existing_functionality), 
        ("RAG Foundation", test_rag_foundation),
        ("Exception Handling", test_exception_handling)
    ]
    
    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    test_section("Results Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Phase 1 foundation is working correctly")
        print("✅ Ready for Phase 2 implementation")
        print("\n🚀 Next steps:")
        print("1. Run your application: python main.py")
        print("2. Test API endpoints")
        print("3. Proceed with Phase 2: Repository Layer")
    else:
        print("\n❌ SOME TESTS FAILED!")
        print("⚠️  Please fix issues before proceeding")
    
    return passed == total

if __name__ == "__main__":
    # Ensure we're in the right directory
    import os
    if not os.path.exists("app"):
        print("❌ ERROR: Run this script from src/backend directory")
        print("Usage: cd src/backend && python test_phase1.py")
        sys.exit(1)
    
    success = main()
    sys.exit(0 if success else 1)