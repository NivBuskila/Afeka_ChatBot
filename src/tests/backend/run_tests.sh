#!/bin/bash

# Afeka ChatBot Backend Test Runner Script
# This script runs the complete test suite with proper environment setup

echo "🚀 Afeka ChatBot Backend Test Suite"
echo "=================================="

# Check if we're in the right directory
if [ ! -f "conftest.py" ]; then
    echo "❌ Error: Please run this script from the tests/backend directory"
    exit 1
fi

# Set test environment variables
export ENVIRONMENT=test
export JWT_SECRET=test-jwt-secret-key-for-testing-only
export SUPABASE_URL=https://test.supabase.co
export SUPABASE_KEY=test-key
export AI_SERVICE_URL=http://localhost:5000
export INTERNAL_API_KEY=test-internal-api-key

echo "✅ Environment variables set"

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "❌ Error: pytest is not installed. Please install it with: pip install pytest"
    exit 1
fi

# Install required dependencies if not present
echo "📦 Checking dependencies..."
pip install -q pytest pytest-asyncio httpx fastapi faker

# Function to run specific test category
run_category() {
    local category=$1
    local test_file=$2
    
    echo ""
    echo "📋 Running $category tests..."
    echo "----------------------------------------"
    
    if [ -f "$test_file" ]; then
        pytest "$test_file" -v --tb=short
        local exit_code=$?
        
        if [ $exit_code -eq 0 ]; then
            echo "✅ $category tests passed"
        else
            echo "❌ $category tests failed"
        fi
        
        return $exit_code
    else
        echo "⚠️  Test file $test_file not found"
        return 1
    fi
}

# Parse command line arguments
case "$1" in
    "auth")
        run_category "Authentication" "test_01_auth.py"
        ;;
    "chat")
        run_category "Chat Sessions" "test_02_chat_sessions.py"
        ;;
    "messages")
        run_category "Messages" "test_03_messages.py"
        ;;
    "ai")
        run_category "AI Integration" "test_04_ai_integration.py"
        ;;
    "documents")
        run_category "Documents" "test_05_documents.py"
        ;;
    "security")
        run_category "Security" "test_06_security.py"
        ;;
    "errors")
        run_category "Error Handling" "test_07_errors.py"
        ;;
    "e2e")
        run_category "End-to-End" "test_08_e2e.py"
        ;;
    "performance")
        run_category "Performance" "test_09_performance.py"
        ;;
    "all"|"")
        echo "🔄 Running all test categories..."
        
        failed_tests=0
        
        run_category "Authentication" "test_01_auth.py" || ((failed_tests++))
        run_category "Chat Sessions" "test_02_chat_sessions.py" || ((failed_tests++))
        run_category "Messages" "test_03_messages.py" || ((failed_tests++))
        run_category "AI Integration" "test_04_ai_integration.py" || ((failed_tests++))
        run_category "Documents" "test_05_documents.py" || ((failed_tests++))
        run_category "Security" "test_06_security.py" || ((failed_tests++))
        run_category "Error Handling" "test_07_errors.py" || ((failed_tests++))
        run_category "End-to-End" "test_08_e2e.py" || ((failed_tests++))
        run_category "Performance" "test_09_performance.py" || ((failed_tests++))
        
        echo ""
        echo "=================================="
        echo "📊 Test Suite Summary"
        echo "=================================="
        
        if [ $failed_tests -eq 0 ]; then
            echo "🎉 All tests passed!"
            exit 0
        else
            echo "❌ $failed_tests test categories failed"
            exit 1
        fi
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [category]"
        echo ""
        echo "Available categories:"
        echo "  auth         - Authentication tests"
        echo "  chat         - Chat session tests"
        echo "  messages     - Message tests"
        echo "  ai           - AI integration tests"
        echo "  documents    - Document management tests"
        echo "  security     - Security tests"
        echo "  errors       - Error handling tests"
        echo "  e2e          - End-to-end tests"
        echo "  performance  - Performance tests"
        echo "  all          - Run all tests (default)"
        echo ""
        echo "Examples:"
        echo "  $0           # Run all tests"
        echo "  $0 auth      # Run only authentication tests"
        echo "  $0 e2e       # Run only end-to-end tests"
        ;;
    *)
        echo "❌ Unknown test category: $1"
        echo "Use '$0 help' to see available options"
        exit 1
        ;;
esac