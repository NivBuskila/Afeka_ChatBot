"""
Test Runner and Utilities
Main test execution script with reporting and utilities
"""
import argparse
import pytest
import sys
import json
import time
import os
import tempfile
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict
from unittest.mock import patch, MagicMock
from fastapi import status, HTTPException
from fastapi.testclient import TestClient
import httpx

# הוסף את תיקיות הפרויקט ל-Python path
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent  # מ-src/tests/backend למעלה ל-Apex/Afeka_ChatBot
src_dir = project_root / "src"

sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_dir))

# Set test environment variables FIRST - before any validation
os.environ["ENVIRONMENT"] = "test"
os.environ["JWT_SECRET"] = "test-jwt-secret-key-for-testing-only"
os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_KEY"] = "test-key"
os.environ["AI_SERVICE_URL"] = "http://localhost:5000"
os.environ["INTERNAL_API_KEY"] = "test-internal-api-key"

# Available test suites with their descriptions
TEST_SUITES = {
    "auth": {
        "file": "tests_01_auth.py",
        "description": "Authentication and authorization tests",
        "test_count": 11
    },
    "chat": {
        "file": "tests_02_chat_sessions.py", 
        "description": "Chat session management tests",
        "test_count": 14
    },
    "messages": {
        "file": "tests_03_messages.py",
        "description": "Message handling and processing tests", 
        "test_count": 6
    },
    "ai": {
        "file": "tests_04_ai_integration.py",
        "description": "AI service integration tests",
        "test_count": 15
    },
    "documents": {
        "file": "tests_05_documents.py",
        "description": "Document management and RAG tests",
        "test_count": 6
    },
    "security": {
        "file": "tests_06_security.py",
        "description": "Security and middleware tests",
        "test_count": 9
    },
    "errors": {
        "file": "tests_07_errors.py",
        "description": "Error handling and edge cases",
        "test_count": 13
    },
    "e2e": {
        "file": "tests_08_e2e.py",
        "description": "End-to-end integration tests",
        "test_count": 3
    },
    "performance": {
        "file": "tests_09_performance.py",
        "description": "Performance and load tests",
        "test_count": 6
    },
    "keymanager": {
        "file": "tests_10_key_manager.py",
        "description": "Key manager and embedding tests",
        "test_count": 5
    }
}


class TestResultCollector:
    """Collect and format test results"""
    
    def __init__(self):
        self.all_tests = []
        self.category_stats = defaultdict(lambda: {"passed": 0, "failed": 0, "skipped": 0, "error": 0, "total": 0})
        self.total_stats = {"passed": 0, "failed": 0, "skipped": 0, "error": 0, "total": 0}
        self.failed_tests_details = []
    
    def add_test_result(self, category: str, test_name: str, status: str, duration: float = 0.0, error_msg: str = None):
        """Add a test result to the collection"""
        self.all_tests.append({
            "category": category,
            "test_name": test_name,
            "status": status,
            "duration": duration,
            "error_msg": error_msg
        })
        
        # Update statistics
        self.category_stats[category][status] += 1
        self.category_stats[category]["total"] += 1
        self.total_stats[status] += 1
        self.total_stats["total"] += 1
        
        # Store failed test details for analysis
        if status in ["failed", "error"]:
            self.failed_tests_details.append({
                "category": category,
                "test_name": test_name,
                "status": status,
                "error_msg": error_msg,
                "failure_reason": self._extract_failure_reason(error_msg)
            })
    
    def _extract_failure_reason(self, error_msg: str) -> str:
        """Extract concise failure reason from error message"""
        if not error_msg:
            return "Unknown error"
        
        # Common patterns to identify failure types
        failure_patterns = [
            (r"assert (\d+) == (\d+)", "Status code mismatch: expected {}, got {}"),
            (r"AssertionError: assert (\d+) == (\d+)", "Status code assertion failed: {} != {}"),
            (r"Connection.*refused", "Connection refused - service not running"),
            (r"ConnectTimeout", "Connection timeout - service unavailable"),
            (r"404.*Not Found", "404 Not Found - endpoint/resource missing"),
            (r"401.*Unauthorized", "401 Unauthorized - authentication failed"),
            (r"500.*Internal Server Error", "500 Internal Server Error"),
            (r"KeyError.*'(\w+)'", "Missing key in response: '{}'"),
            (r"AttributeError.*'NoneType'", "Null reference error"),
            (r"TypeError.*", "Type error - data format issue"),
            (r"ValidationError", "Data validation failed"),
            (r"JSONDecodeError", "Invalid JSON response"),
            (r"fixture.*not found", "Test fixture missing or misconfigured"),
            (r"ImportError", "Import error - module not found"),
        ]
        
        # Try to match common patterns
        for pattern, template in failure_patterns:
            match = re.search(pattern, error_msg, re.IGNORECASE)
            if match:
                try:
                    return template.format(*match.groups())
                except:
                    return template.replace("{}", "")
        
        # If no pattern matches, return first meaningful line
        lines = [line.strip() for line in error_msg.split('\n') if line.strip()]
        if lines:
            # Look for assert statements or error messages
            for line in lines:
                if any(keyword in line.lower() for keyword in ['assert', 'error:', 'failed', 'exception']):
                    return line[:100] + "..." if len(line) > 100 else line
            # Return first non-empty line if no keywords found
            return lines[0][:100] + "..." if len(lines[0]) > 100 else lines[0]
        
        return "Unknown error"
    
    def parse_pytest_json_report(self, json_file: str, category: str):
        """Parse pytest JSON report and extract test results"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for test in data.get('tests', []):
                test_name = test.get('nodeid', '').split('::')[-1] if '::' in test.get('nodeid', '') else test.get('nodeid', '')
                status = test.get('outcome', 'unknown')
                duration = test.get('call', {}).get('duration', 0.0) if test.get('call') else 0.0
                
                # Get error message if test failed
                error_msg = None
                if status in ['failed', 'error']:
                    call_info = test.get('call', {})
                    if 'longrepr' in call_info:
                        error_msg = str(call_info['longrepr'])
                
                self.add_test_result(category, test_name, status, duration, error_msg)
                
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"⚠️ Could not parse JSON report for {category}: {e}")
    
    def print_detailed_summary(self):
        """Print detailed summary of all test results"""
        print("\n" + "=" * 80)
        print("📊 DETAILED TEST RESULTS SUMMARY")
        print("=" * 80)
        
        # Group tests by category
        tests_by_category = defaultdict(list)
        for test in self.all_tests:
            tests_by_category[test["category"]].append(test)
        
        # Print results for each category
        for category, tests in tests_by_category.items():
            print(f"\n📋 {category.upper()} TESTS:")
            print("-" * 50)
            
            for test in tests:
                status_icon = self._get_status_icon(test["status"])
                duration_str = f"({test['duration']:.3f}s)" if test['duration'] > 0 else ""
                
                print(f"  {status_icon} {test['test_name']} {duration_str}")
            
            # Print category statistics
            stats = self.category_stats[category]
            print(f"\n    📈 {category.upper()} Summary: {stats['total']} total, "
                  f"✅ {stats['passed']} passed, ❌ {stats['failed']} failed, "
                  f"⏭️ {stats['skipped']} skipped, 💥 {stats['error']} errors")
        
        # Print overall statistics
        self._print_overall_statistics()
    
    def print_short_failure_summary(self):
        """Print short summary focused on failures only"""
        print("\n" + "🔍 FAILURE ANALYSIS SUMMARY")
        print("=" * 60)
        
        if not self.failed_tests_details:
            print("✅ No failed tests!")
            return
        
        # Group failures by category
        failures_by_category = defaultdict(list)
        for failure in self.failed_tests_details:
            failures_by_category[failure["category"]].append(failure)
        
        print(f"❌ Total Failed Tests: {len(self.failed_tests_details)}")
        print(f"📊 Success Rate: {((self.total_stats['passed'] / self.total_stats['total']) * 100):.1f}%")
        print()
        
        # Print failures by category
        for category, failures in failures_by_category.items():
            print(f"💥 {category.upper()} FAILURES ({len(failures)}):")
            print("-" * 40)
            
            for failure in failures:
                print(f"  ❌ {failure['test_name']}")
                print(f"     💬 {failure['failure_reason']}")
                print()
    
    def print_failure_patterns_analysis(self):
        """Analyze and print common failure patterns"""
        if not self.failed_tests_details:
            return
        
        print("\n📈 FAILURE PATTERNS ANALYSIS")
        print("=" * 50)
        
        # Count failure types
        failure_types = defaultdict(int)
        for failure in self.failed_tests_details:
            reason = failure['failure_reason']
            if "connection" in reason.lower():
                failure_types["Connection Issues"] += 1
            elif "status code" in reason.lower():
                failure_types["HTTP Status Errors"] += 1
            elif "timeout" in reason.lower():
                failure_types["Timeouts"] += 1
            elif "not found" in reason.lower():
                failure_types["Missing Resources"] += 1
            elif "authentication" in reason.lower() or "401" in reason:
                failure_types["Authentication Issues"] += 1
            elif "validation" in reason.lower():
                failure_types["Data Validation"] += 1
            elif "fixture" in reason.lower():
                failure_types["Test Setup Issues"] += 1
            else:
                failure_types["Other"] += 1
        
        print("🔸 Common failure patterns:")
        for pattern, count in sorted(failure_types.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(self.failed_tests_details)) * 100
            print(f"   {pattern}: {count} ({percentage:.1f}%)")
    
    def _get_status_icon(self, status: str) -> str:
        """Get emoji icon for test status"""
        icons = {
            "passed": "✅",
            "failed": "❌", 
            "skipped": "⏭️",
            "error": "💥"
        }
        return icons.get(status, "❓")
    
    def _print_overall_statistics(self):
        """Print overall test statistics"""
        print(f"\n🎯 OVERALL STATISTICS:")
        print("=" * 50)
        
        total = self.total_stats["total"]
        if total == 0:
            print("No tests were run")
            return
        
        passed = self.total_stats["passed"]
        failed = self.total_stats["failed"]
        skipped = self.total_stats["skipped"]
        error = self.total_stats["error"]
        
        success_rate = (passed / total) * 100
        
        print(f"📊 Total Tests: {total}")
        print(f"✅ Passed: {passed} ({(passed/total)*100:.1f}%)")
        print(f"❌ Failed: {failed} ({(failed/total)*100:.1f}%)")
        print(f"⏭️ Skipped: {skipped} ({(skipped/total)*100:.1f}%)")
        print(f"💥 Errors: {error} ({(error/total)*100:.1f}%)")
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        # Status indicator
        if success_rate >= 90:
            print("🟢 Excellent!")
        elif success_rate >= 75:
            print("🟡 Good")
        elif success_rate >= 50:
            print("🟠 Needs Improvement")
        else:
            print("🔴 Critical Issues")


def list_available_suites():
    """Display all available test suites"""
    print("\n📋 AVAILABLE TEST SUITES:")
    print("=" * 60)
    
    total_tests = 0
    for suite_name, suite_info in TEST_SUITES.items():
        print(f"🔸 {suite_name.upper()}")
        print(f"   📝 {suite_info['description']}")
        print(f"   📊 {suite_info['test_count']} tests")
        print(f"   📁 File: {suite_info['file']}")
        print()
        total_tests += suite_info['test_count']
    
    print(f"📈 Total: {len(TEST_SUITES)} suites, {total_tests} tests")
    print("\n💡 Usage examples:")
    print("   python test_runner.py --suite auth")
    print("   python test_runner.py --suite auth,chat,messages")
    print("   python test_runner.py --all")


def run_single_suite(suite_name: str, verbose: bool = True) -> Dict[str, Any]:
    """Run a single test suite"""
    if suite_name not in TEST_SUITES:
        print(f"❌ Unknown test suite: {suite_name}")
        print(f"Available suites: {', '.join(TEST_SUITES.keys())}")
        return {"success": False, "error": f"Unknown suite: {suite_name}"}
    
    suite_info = TEST_SUITES[suite_name]
    test_file = suite_info["file"]
    
    print(f"\n🚀 Running {suite_name.upper()} Test Suite")
    print("=" * 50)
    print(f"📝 {suite_info['description']}")
    print(f"📁 File: {test_file}")
    print(f"📊 Expected tests: {suite_info['test_count']}")
    print()
    
    # Create temporary file for JSON output
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
        json_file = temp_file.name
    
    try:
        # Prepare pytest arguments
        pytest_args = [
            test_file,
            "--json-report",
            f"--json-report-file={json_file}",
            "--tb=short"
        ]
        
        if verbose:
            pytest_args.extend(["-v", "--tb=short"])
        else:
            pytest_args.append("-q")
        
        # Run pytest
        print(f"⚡ Executing: pytest {' '.join(pytest_args)}")
        start_time = time.time()
        
        exit_code = pytest.main(pytest_args)
        
        duration = time.time() - start_time
        print(f"⏱️ Test suite completed in {duration:.2f}s")
        
        # Parse results
        collector = TestResultCollector()
        collector.parse_pytest_json_report(json_file, suite_name)
        
        # Display results
        if verbose:
            collector.print_detailed_summary()
        else:
            collector.print_short_failure_summary()
        
        return {
            "success": exit_code == 0,
            "suite": suite_name,
            "duration": duration,
            "stats": collector.total_stats,
            "failed_tests": collector.failed_tests_details
        }
        
    except Exception as e:
        print(f"❌ Error running {suite_name} tests: {e}")
        return {"success": False, "error": str(e)}
    
    finally:
        # Clean up temporary file
        try:
            os.unlink(json_file)
        except:
            pass


def run_multiple_suites(suite_names: List[str], verbose: bool = True) -> Dict[str, Any]:
    """Run multiple test suites"""
    print(f"\n🎯 Running Multiple Test Suites: {', '.join(suite_names)}")
    print("=" * 70)
    
    all_results = {}
    total_start_time = time.time()
    
    for suite_name in suite_names:
        print(f"\n📍 Starting {suite_name.upper()} suite...")
        result = run_single_suite(suite_name, verbose=False)  # Less verbose for multiple
        all_results[suite_name] = result
        
        # Quick summary after each suite
        if result["success"]:
            stats = result.get("stats", {})
            print(f"✅ {suite_name.upper()}: {stats.get('passed', 0)}/{stats.get('total', 0)} passed")
        else:
            print(f"❌ {suite_name.upper()}: Failed to run")
    
    total_duration = time.time() - total_start_time
    
    # Overall summary
    print(f"\n📊 MULTIPLE SUITES SUMMARY")
    print("=" * 50)
    
    total_tests = 0
    total_passed = 0
    total_failed = 0
    successful_suites = 0
    
    for suite_name, result in all_results.items():
        if result.get("success"):
            successful_suites += 1
            stats = result.get("stats", {})
            suite_total = stats.get("total", 0)
            suite_passed = stats.get("passed", 0)
            suite_failed = stats.get("failed", 0) + stats.get("error", 0)
            
            total_tests += suite_total
            total_passed += suite_passed
            total_failed += suite_failed
            
            print(f"🔸 {suite_name.upper()}: {suite_passed}/{suite_total} "
                  f"({(suite_passed/suite_total)*100:.1f}% success)")
        else:
            print(f"🔸 {suite_name.upper()}: ❌ Failed to run")
    
    overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n🎯 OVERALL RESULTS:")
    print(f"   📊 Suites run: {successful_suites}/{len(suite_names)}")
    print(f"   📊 Total tests: {total_passed}/{total_tests} passed")
    print(f"   📊 Success rate: {overall_success_rate:.1f}%")
    print(f"   ⏱️ Total duration: {total_duration:.2f}s")
    
    return {
        "success": successful_suites == len(suite_names),
        "suites_results": all_results,
        "total_duration": total_duration,
        "overall_stats": {
            "total_tests": total_tests,
            "total_passed": total_passed,
            "total_failed": total_failed,
            "success_rate": overall_success_rate
        }
    }


def run_all_suites(verbose: bool = True) -> Dict[str, Any]:
    """Run all available test suites"""
    all_suite_names = list(TEST_SUITES.keys())
    return run_multiple_suites(all_suite_names, verbose)


def validate_test_environment() -> bool:
    """Validate that the test environment is properly set up"""
    print("🔍 Validating test environment...")
    
    required_vars = ["JWT_SECRET", "SUPABASE_URL", "SUPABASE_KEY", "AI_SERVICE_URL"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    # Check if test files exist
    missing_files = []
    for suite_name, suite_info in TEST_SUITES.items():
        test_file = Path(__file__).parent / suite_info["file"]
        if not test_file.exists():
            missing_files.append(suite_info["file"])
    
    if missing_files:
        print(f"❌ Missing test files: {', '.join(missing_files)}")
        return False
    
    print("✅ Test environment is valid")
    return True


def create_argument_parser():
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description="Backend Test Suite Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all tests
  python test_runner.py --all
  
  # Run specific suite
  python test_runner.py --suite auth
  
  # Run multiple suites
  python test_runner.py --suite auth,chat,messages
  
  # List available suites
  python test_runner.py --list
  
  # Run with minimal output
  python test_runner.py --suite auth --quiet
  
  # Show only failures
  python test_runner.py --all --failure-only
        """
    )
    
    # Main action arguments (mutually exclusive)
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument(
        "--all", 
        action="store_true",
        help="Run all test suites"
    )
    action_group.add_argument(
        "--suite", 
        type=str,
        help="Run specific test suite(s). Use comma-separated list for multiple suites"
    )
    action_group.add_argument(
        "--list", 
        action="store_true",
        help="List all available test suites"
    )
    action_group.add_argument(
        "--validate", 
        action="store_true",
        help="Validate test environment setup"
    )
    
    # Output control arguments
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Reduce output verbosity"
    )
    parser.add_argument(
        "--failure-only",
        action="store_true", 
        help="Show only failure summary"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Increase output verbosity"
    )
    
    return parser


def main():
    """Main entry point"""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    print("🧪 Backend Test Suite Runner")
    print("=" * 40)
    
    # Handle list command
    if args.list:
        list_available_suites()
        return 0
    
    # Handle validate command
    if args.validate:
        success = validate_test_environment()
        return 0 if success else 1
    
    # Validate environment before running tests
    if not validate_test_environment():
        print("❌ Environment validation failed. Please fix the issues above.")
        return 1
    
    # Determine verbosity
    verbose = not args.quiet
    if args.verbose:
        verbose = True
    
    # Run tests based on arguments
    try:
        if args.all:
            # Run all suites
            result = run_all_suites(verbose=verbose)
            
        elif args.suite:
            # Parse suite names
            suite_names = [name.strip() for name in args.suite.split(',')]
            
            # Validate suite names
            invalid_suites = [name for name in suite_names if name not in TEST_SUITES]
            if invalid_suites:
                print(f"❌ Invalid suite names: {', '.join(invalid_suites)}")
                print(f"Available suites: {', '.join(TEST_SUITES.keys())}")
                return 1
            
            # Run suites
            if len(suite_names) == 1:
                result = run_single_suite(suite_names[0], verbose=verbose)
            else:
                result = run_multiple_suites(suite_names, verbose=verbose)
        
        # Handle failure-only output
        if args.failure_only and "suites_results" in result:
            print(f"\n🔍 FAILURE-ONLY SUMMARY")
            print("=" * 40)
            
            for suite_name, suite_result in result["suites_results"].items():
                failed_tests = suite_result.get("failed_tests", [])
                if failed_tests:
                    print(f"\n💥 {suite_name.upper()} FAILURES:")
                    for failure in failed_tests:
                        print(f"  ❌ {failure['test_name']}")
                        print(f"     💬 {failure['failure_reason']}")
        
        # Return appropriate exit code
        return 0 if result.get("success", False) else 1
        
    except KeyboardInterrupt:
        print("\n👋 Tests interrupted by user")
        return 130
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)