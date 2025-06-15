#!/usr/bin/env python3
"""Simple RAG import checker"""
import sys
import os
from pathlib import Path

print("🔍 Simple RAG Import Test")
print("=" * 50)

# Setup paths
ai_path = Path("Apex/Afeka_ChatBot/src/ai")
backend_path = Path("Apex/Afeka_ChatBot/src/backend")

print(f"AI Path: {ai_path}")
print(f"Backend Path: {backend_path}")

# Add to sys.path
sys.path.insert(0, str(ai_path))
sys.path.insert(0, str(backend_path))

print(f"Current working directory: {os.getcwd()}")
print(f"Python path includes: {sys.path[:3]}...")

# Test environment variables
env_vars = ['GEMINI_API_KEY', 'SUPABASE_URL', 'SUPABASE_KEY', 'SUPABASE_SERVICE_KEY']
print("\n📋 Environment Variables:")
for var in env_vars:
    value = os.getenv(var)
    if value:
        print(f"✅ {var}: Set (length: {len(value)})")
    else:
        print(f"❌ {var}: Missing")

print("\n🔧 Testing imports one by one:")

# Test 1: Basic dependencies
try:
    import google.generativeai as genai
    print("✅ google.generativeai")
except Exception as e:
    print(f"❌ google.generativeai: {e}")

try:
    from supabase import create_client
    print("✅ supabase")
except Exception as e:
    print(f"❌ supabase: {e}")

try:
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    print("✅ langchain_google_genai")
except Exception as e:
    print(f"❌ langchain_google_genai: {e}")

try:
    from langchain_experimental.text_splitter import SemanticChunker
    print("✅ langchain_experimental")
except Exception as e:
    print(f"❌ langchain_experimental: {e}")

# Test 2: RAG services (direct import)
print("\n🎯 Testing RAG services:")

try:
    from services.document_processor import DocumentProcessor
    print("✅ DocumentProcessor")
    
    # Try to instantiate
    doc_proc = DocumentProcessor()
    print("✅ DocumentProcessor instantiated")
    
except Exception as e:
    print(f"❌ DocumentProcessor: {e}")
    import traceback
    traceback.print_exc()

try:
    from services.enhanced_processor import EnhancedProcessor
    print("✅ EnhancedProcessor")
except Exception as e:
    print(f"❌ EnhancedProcessor: {e}")

try:
    from services.rag_service import RAGService
    print("✅ RAGService")
except Exception as e:
    print(f"❌ RAGService: {e}")

print("\n🎯 File existence check:")
files_to_check = [
    ai_path / "services" / "document_processor.py",
    ai_path / "services" / "enhanced_processor.py", 
    ai_path / "services" / "rag_service.py",
    ai_path / "config" / "rag_config.py"
]

for file_path in files_to_check:
    if file_path.exists():
        print(f"✅ {file_path.name}: Found")
    else:
        print(f"❌ {file_path.name}: Not found")

print("\n" + "=" * 50)
print("🔍 RAG Import Test Complete") 