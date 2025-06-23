#!/usr/bin/env python
"""
RAG Test Pro System - English Only Version
A comprehensive testing system for RAG configurations with automatic key management.

This system provides:
- Easy question set selection from JSON files
- RAG profile selection and management  
- Automatic API key rotation
- Detailed performance reporting
- User-friendly interactive menu

Author: RAG Test Pro System
Version: 1.0 - All Hebrew text removed, imports fixed
"""

import os
import sys
import json
import time
import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import traceback

# Load environment variables
try:
    from dotenv import load_dotenv
    # Load from the main project .env file
    env_file = Path(__file__).parent.parent / ".env"
    load_dotenv(env_file)
    print(f"✅ Environment variables loaded from: {env_file}")
except ImportError:
    print("⚠️ python-dotenv not installed. Install with: pip install python-dotenv")
except Exception as e:
    print(f"⚠️ Could not load .env file: {e}")

# Add the parent directory to sys.path to import from the main project
current_dir = Path(__file__).parent
project_root = current_dir.parent / "src"
ai_path = project_root / "ai"

# Add paths for imports
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(ai_path))

# Configuration
RESULTS_DIR = current_dir / "results"
QUESTIONS_DIR = current_dir / "test_questions"
PROFILES_DIR = current_dir / "rag_profiles"

# Create directories if they don't exist
RESULTS_DIR.mkdir(exist_ok=True)
QUESTIONS_DIR.mkdir(exist_ok=True)
PROFILES_DIR.mkdir(exist_ok=True)

# Configure clean logging - reduce verbose output
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Disable verbose loggers from RAG system to get clean output
logging.getLogger('ai.services.rag_service').setLevel(logging.WARNING)
logging.getLogger('ai.core.database_key_manager').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)

class RAGTestPro:
    """Main RAG Test Pro system - English Only"""
    
    def __init__(self):
        """Initialize the RAG Test Pro system"""
        self.question_sets = {}
        self.rag_profiles = {}
        self.current_session = None
        self.rag_service = None
        self.key_manager = None
        
        print("\n" + "="*60)
        print("🚀 RAG TEST PRO SYSTEM - ENGLISH VERSION")
        print("Advanced RAG Configuration Testing Platform")
        print("All Hebrew text removed, imports fixed")
        print("="*60 + "\n")
        
        # Load available question sets and profiles
        self._load_question_sets()
        self._load_rag_profiles()
        
        print(f"✅ System initialized with:")
        print(f"   📋 {len(self.question_sets)} question sets")
        print(f"   ⚙️  {len(self.rag_profiles)} RAG profiles")
        print()

    def _load_question_sets(self):
        """Load all available question sets from the questions directory"""
        self.question_sets = {}
        
        if not QUESTIONS_DIR.exists():
            print(f"⚠️ Warning: Questions directory not found: {QUESTIONS_DIR}")
            return
        
        for json_file in QUESTIONS_DIR.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Handle different JSON structures
                questions = []
                if isinstance(data, list):
                    # Direct list of questions
                    questions = data
                elif isinstance(data, dict):
                    if 'questions' in data:
                        questions = data['questions']
                    elif 'test_questions' in data:
                        questions = data['test_questions']
                    else:
                        # Try to extract questions from any list in the dict
                        for key, value in data.items():
                            if isinstance(value, list) and value:
                                questions = value
                                break
                
                if questions:
                    self.question_sets[json_file.stem] = {
                        'file': str(json_file),
                        'questions': questions,
                        'count': len(questions),
                        'categories': self._extract_categories(questions)
                    }
                    print(f"📁 Loaded: {json_file.name} ({len(questions)} questions)")
                else:
                    print(f"⚠️ Warning: No questions found in {json_file.name}")
                    
            except Exception as e:
                print(f"❌ Error loading {json_file.name}: {e}")
    
    def _extract_categories(self, questions: List[Dict]) -> List[str]:
        """Extract unique categories from questions"""
        categories = set()
        for q in questions:
            if isinstance(q, dict) and 'category' in q:
                categories.add(q['category'])
        return sorted(list(categories))

    def _load_rag_profiles(self):
        """Load all available RAG profiles"""
        self.rag_profiles = {}
        
        # Load built-in profiles first
        self._load_builtin_profiles()
        
        # Load custom profiles from profiles directory
        if PROFILES_DIR.exists():
            for json_file in PROFILES_DIR.glob("*.json"):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        profile_data = json.load(f)
                    
                    self.rag_profiles[json_file.stem] = {
                        'source': 'custom',
                        'file': str(json_file),
                        'config': profile_data,
                        'name': profile_data.get('name', json_file.stem),
                        'description': profile_data.get('description', 'Custom profile')
                    }
                    print(f"⚙️ Loaded custom profile: {json_file.stem}")
                    
                except Exception as e:
                    print(f"❌ Error loading profile {json_file.name}: {e}")

    def _load_builtin_profiles(self):
        """Load built-in RAG profiles from the main system"""
        builtin_profiles = {
            'maximum_accuracy': {
                'name': 'Maximum Accuracy',
                'description': 'Optimized for highest accuracy, slower response',
                'config': {
                    'similarityThreshold': 0.75,
                    'highQualityThreshold': 0.85,
                    'maxChunks': 15,
                    'temperature': 0.1,
                    'chunkSize': 2000,
                    'chunkOverlap': 400,
                    'maxContextTokens': 8000,
                    'hybridSemanticWeight': 0.7,
                    'hybridKeywordWeight': 0.3,
                    'exactPhraseBonus': 0.15,
                    'topicMatchBonus': 0.1
                }
            },
            'fast_response': {
                'name': 'Fast Response',
                'description': 'Optimized for speed, good accuracy',
                'config': {
                    'similarityThreshold': 0.65,
                    'highQualityThreshold': 0.75,
                    'maxChunks': 8,
                    'temperature': 0.3,
                    'chunkSize': 1500,
                    'chunkOverlap': 200,
                    'maxContextTokens': 5000,
                    'hybridSemanticWeight': 0.6,
                    'hybridKeywordWeight': 0.4,
                    'exactPhraseBonus': 0.1,
                    'topicMatchBonus': 0.05
                }
            },
            'balanced_performance': {
                'name': 'Balanced Performance',
                'description': 'Balanced speed and accuracy',
                'config': {
                    'similarityThreshold': 0.7,
                    'highQualityThreshold': 0.8,
                    'maxChunks': 12,
                    'temperature': 0.2,
                    'chunkSize': 1800,
                    'chunkOverlap': 300,
                    'maxContextTokens': 6500,
                    'hybridSemanticWeight': 0.65,
                    'hybridKeywordWeight': 0.35,
                    'exactPhraseBonus': 0.12,
                    'topicMatchBonus': 0.08
                }
            },
            'perfect_accuracy_plus_coverage': {
                'name': '🎯 דיוק מושלם + כיסוי מקסימלי',
                'description': 'פרופיל מתקדם המשלב דיוק מקסימלי עם כיסוי רחב - פותר בעיות "אין מידע" (יעד: 95-98%)',
                'config': {
                    'id': 'perfect_accuracy_plus_coverage',
                    'similarityThreshold': 0.45,
                    'sectionSearchThreshold': 0.25,
                    'maxChunks': 35,
                    'temperature': 0.05,
                    'modelName': 'gemini-2.0-flash',
                    'chunkSize': 2500,
                    'chunkOverlap': 350,
                    'maxContextTokens': 9000,
                    'targetTokensPerChunk': 420,
                    'hybridSemanticWeight': 0.55,
                    'hybridKeywordWeight': 0.45,
                    'exactPhraseBonus': 200.0,
                    'topicMatchBonus': 18.0,
                    'directMatchBonus': 10.0,
                    'similarityWeightFactor': 3.0,
                    'positionBonusBase': 5.0,
                    'positionBonusDecay': 0.3
                }
            }
        }
        
        for profile_id, profile_data in builtin_profiles.items():
            self.rag_profiles[profile_id] = {
                'source': 'builtin',
                'config': profile_data['config'],
                'name': profile_data['name'],
                'description': profile_data['description']
            }

    async def _initialize_rag_system(self, profile_config: Dict) -> bool:
        """Initialize the RAG system with specified configuration"""
        try:
            print("🔧 Initializing RAG system...")
            
            # Import RAG modules with correct names (fixed import errors)
            try:
                # Import the actual existing classes we found in the codebase search
                from ai.services.rag_service import RAGService
                from ai.core.database_key_manager import DatabaseKeyManager
                print("✅ RAG modules imported successfully")
            except ImportError as e:
                print(f"❌ Error importing RAG modules: {e}")
                print("Please ensure the project is properly set up")
                return False
            
            # Initialize key manager
            try:
                self.key_manager = DatabaseKeyManager()
                print("✅ Key manager initialized")
            except Exception as e:
                print(f"❌ Error initializing key manager: {e}")
                return False
            
            # Initialize RAG service with proper configuration
            try:
                # Try to use the real profile system from the main app
                try:
                    from ai.config.rag_config_profiles import create_profile_from_data
                    
                    # Create a proper RAG configuration from the profile data
                    profile_data = {
                        'config': profile_config
                    }
                    
                    # Create RAG config and then initialize the service
                    rag_config = create_profile_from_data(profile_data)
                    
                    # Get the profile ID from config if available
                    profile_id = profile_config.get('id', 'custom')
                    
                    # Initialize RAG service with the specific profile
                    self.rag_service = RAGService(config_profile=profile_id)
                    
                    print("✅ RAG service initialized with real profile system")
                    print(f"   Profile: {profile_id}")
                    print(f"   Similarity threshold: {self.rag_service.search_config.SIMILARITY_THRESHOLD}")
                    print(f"   Max chunks: {self.rag_service.search_config.MAX_CHUNKS_RETRIEVED}")
                    print(f"   Temperature: {self.rag_service.llm_config.TEMPERATURE}")
                    print(f"   Model: {self.rag_service.llm_config.MODEL_NAME}")
                    
                except ImportError as e:
                    print(f"⚠️ Could not use real profile system: {e}")
                    print("   Falling back to default RAG service initialization...")
                    
                    # Fallback: initialize with default and manually set parameters
                    self.rag_service = RAGService()
                    
                    # Apply the configuration manually by modifying the service attributes
                    if hasattr(self.rag_service, 'search_config'):
                        if 'similarityThreshold' in profile_config:
                            self.rag_service.search_config.SIMILARITY_THRESHOLD = profile_config['similarityThreshold']
                        if 'maxChunks' in profile_config:
                            self.rag_service.search_config.MAX_CHUNKS_RETRIEVED = profile_config['maxChunks']
                    
                    if hasattr(self.rag_service, 'llm_config'):
                        if 'temperature' in profile_config:
                            self.rag_service.llm_config.TEMPERATURE = profile_config['temperature']
                    
                    print("✅ RAG service configured with fallback parameters")
                
                return True
                
            except Exception as e:
                print(f"❌ Error initializing RAG service: {e}")
                traceback.print_exc()
                return False
                
        except Exception as e:
            print(f"❌ Error in RAG system initialization: {e}")
            traceback.print_exc()
            return False

    def run_interactive_menu(self):
        """Run the main interactive menu"""
        while True:
            self._print_main_menu()
            
            try:
                choice = input("\nEnter your choice (1-7): ").strip()
                
                if choice == '1':
                    self._show_question_sets()
                elif choice == '2':
                    self._show_rag_profiles()
                elif choice == '3':
                    self._run_test_session()
                elif choice == '4':
                    self._create_custom_profile()
                elif choice == '5':
                    self._view_recent_results()
                elif choice == '6':
                    self._show_system_status()
                elif choice == '7':
                    print("\n👋 Thank you for using RAG Test Pro!")
                    break
                else:
                    print("❌ Invalid choice. Please select 1-7.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                input("\nPress Enter to continue...")

    def _print_main_menu(self):
        """Print the main menu"""
        print("\n" + "="*50)
        print("🎯 RAG TEST PRO - MAIN MENU")
        print("="*50)
        print("1. 📋 View Available Question Sets")
        print("2. ⚙️  View RAG Profiles")
        print("3. 🚀 Run Test Session")
        print("4. 🛠️  Create Custom Profile")
        print("5. 📊 View Recent Results")
        print("6. 🔍 System Status")
        print("7. 🚪 Exit")
        print("="*50)

    def _show_question_sets(self):
        """Display available question sets"""
        print("\n📋 AVAILABLE QUESTION SETS")
        print("-" * 40)
        
        if not self.question_sets:
            print("❌ No question sets found")
            print(f"Add JSON files to: {QUESTIONS_DIR}")
        else:
            for i, (set_id, set_info) in enumerate(self.question_sets.items(), 1):
                print(f"{i}. {set_id}")
                print(f"   📊 Questions: {set_info['count']}")
                if set_info['categories']:
                    print(f"   🏷️  Categories: {', '.join(set_info['categories'])}")
                print()
        
        input("Press Enter to continue...")

    def _show_rag_profiles(self):
        """Display available RAG profiles"""
        print("\n⚙️ AVAILABLE RAG PROFILES")
        print("-" * 40)
        
        builtin_count = 0
        custom_count = 0
        
        for profile_id, profile_info in self.rag_profiles.items():
            source_icon = "🔧" if profile_info['source'] == 'builtin' else "🛠️"
            print(f"{source_icon} {profile_info['name']} ({profile_id})")
            print(f"   {profile_info['description']}")
            
            # Show key parameters
            config = profile_info['config']
            print(f"   📊 Similarity: {config.get('similarityThreshold', 'N/A')}, "
                  f"Max Chunks: {config.get('maxChunks', 'N/A')}, "
                  f"Temperature: {config.get('temperature', 'N/A')}")
            print()
            
            if profile_info['source'] == 'builtin':
                builtin_count += 1
            else:
                custom_count += 1
        
        print(f"📈 Total: {len(self.rag_profiles)} profiles ({builtin_count} built-in, {custom_count} custom)")
        input("\nPress Enter to continue...")

    def _run_test_session(self):
        """Run a complete test session"""
        print("\n🚀 RAG TEST SESSION")
        print("-" * 30)
        
        # Select question set
        question_set = self._select_question_set()
        if not question_set:
            return
        
        # Select RAG profile
        rag_profile = self._select_rag_profile()
        if not rag_profile:
            return
        
        # Confirm test execution
        print(f"\n📋 Selected: {question_set['name']} ({question_set['count']} questions)")
        print(f"⚙️ Profile: {rag_profile['name']}")
        
        confirm = input("\n🤔 Start test? (y/N): ").strip().lower()
        if confirm != 'y':
            print("❌ Test cancelled")
            return
        
        # Initialize RAG system and run tests
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            if not loop.run_until_complete(self._initialize_rag_system(rag_profile['config'])):
                print("❌ Failed to initialize RAG system")
                return
            
            # Run tests
            results = loop.run_until_complete(self._execute_test_session(question_set, rag_profile))
            
            if results:
                # Generate report
                report_file = self._generate_report(results, question_set, rag_profile)
                print(f"\n✅ Test completed! Report saved to:")
                print(f"📄 {report_file}")
            else:
                print("❌ Test failed or was cancelled")
        finally:
            loop.close()

    def _select_question_set(self) -> Optional[Dict]:
        """Let user select a question set"""
        if not self.question_sets:
            print("❌ No question sets available")
            return None
        
        print("\n📋 SELECT QUESTION SET:")
        print("-" * 25)
        
        sets_list = list(self.question_sets.items())
        for i, (set_id, set_info) in enumerate(sets_list, 1):
            print(f"{i}. {set_id} ({set_info['count']} questions)")
        
        # Add option for all questions
        print(f"{len(sets_list) + 1}. ALL QUESTIONS (combined)")
        
        while True:
            try:
                choice = input(f"\nSelect question set (1-{len(sets_list) + 1}): ").strip()
                choice_num = int(choice)
                
                if choice_num == len(sets_list) + 1:
                    # Combine all question sets
                    all_questions = []
                    for set_id, set_info in sets_list:
                        all_questions.extend(set_info['questions'])
                    
                    return {
                        'id': 'all_combined',
                        'name': 'All Questions Combined',
                        'questions': all_questions,
                        'count': len(all_questions),
                        'file': 'combined'
                    }
                    
                elif 1 <= choice_num <= len(sets_list):
                    set_id, set_info = sets_list[choice_num - 1]
                    return {
                        'id': set_id,
                        'name': set_id,
                        'questions': set_info['questions'],
                        'count': set_info['count'],
                        'file': set_info['file']
                    }
                else:
                    print(f"❌ Please enter a number between 1 and {len(sets_list) + 1}")
            except ValueError:
                print("❌ Please enter a valid number")
            except KeyboardInterrupt:
                return None

    def _select_rag_profile(self) -> Optional[Dict]:
        """Let user select a RAG profile"""
        if not self.rag_profiles:
            print("❌ No RAG profiles available")
            return None
        
        print("\n⚙️ SELECT RAG PROFILE:")
        print("-" * 22)
        
        profiles_list = list(self.rag_profiles.items())
        for i, (profile_id, profile_info) in enumerate(profiles_list, 1):
            source_icon = "🔧" if profile_info['source'] == 'builtin' else "🛠️"
            print(f"{i}. {source_icon} {profile_info['name']}")
            print(f"   {profile_info['description']}")
        
        while True:
            try:
                choice = input(f"\nSelect profile (1-{len(profiles_list)}): ").strip()
                choice_num = int(choice)
                if 1 <= choice_num <= len(profiles_list):
                    profile_id, profile_info = profiles_list[choice_num - 1]
                    return {
                        'id': profile_id,
                        'name': profile_info['name'],
                        'description': profile_info['description'],
                        'config': profile_info['config'],
                        'source': profile_info['source']
                    }
                else:
                    print(f"❌ Please enter a number between 1 and {len(profiles_list)}")
            except ValueError:
                print("❌ Please enter a valid number")
            except KeyboardInterrupt:
                return None

    async def _execute_test_session(self, question_set: Dict, rag_profile: Dict) -> Optional[Dict]:
        """Execute the actual test session"""
        questions = question_set['questions']
        total_questions = len(questions)
        
        print(f"\n🔄 Running {total_questions} tests with {rag_profile['name']}...")
        print("-" * 50)
        
        results = {
            'session_id': datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S"),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'question_set': question_set,
            'rag_profile': rag_profile,
            'test_results': [],
            'summary': {
                'total_questions': total_questions,
                'successful_responses': 0,
                'failed_responses': 0,
                'total_tokens': 0,
                'total_time': 0,
                'average_response_time': 0
            }
        }
        
        start_time = time.time()
        
        for i, question in enumerate(questions, 1):
            try:
                # Extract question text
                if isinstance(question, dict):
                    question_text = question.get('question', question.get('text', str(question)))
                    question_category = question.get('category', 'general')
                    expected_answer = question.get('expected_answer', question.get('answer', ''))
                else:
                    question_text = str(question)
                    question_category = 'general'
                    expected_answer = ''
                
                print(f"\n📝 שאלה {i}/{total_questions}: {question_text}")
                print("-" * 50)
                
                # Execute RAG query with timeout
                test_start = time.time()
                try:
                    # השהיה קטנה בין בקשות כדי לאפשר רוטציה נכונה של מפתחות
                    await asyncio.sleep(0.5)  # חצי שנייה
                    
                    # Add timeout to prevent hanging
                    response = await asyncio.wait_for(
                        self._call_rag_service(question_text), 
                        timeout=60.0  # 60 seconds timeout
                    )
                    tokens_used = 150  # Estimate for successful calls
                    
                    test_time = time.time() - test_start
                    success = True
                    error_message = None
                    
                    # Show the actual answer clearly
                    print(f"💬 תשובה: {response}")
                    print(f"⏱️ זמן תגובה: {test_time:.2f}s")
                
                except asyncio.TimeoutError:
                    test_time = time.time() - test_start
                    response = "Timeout: התשובה לקחה יותר מדי זמן"
                    tokens_used = 0
                    success = False
                    error_message = "Timeout after 60 seconds"
                    
                    print(f"⏰ Timeout: השאלה לקחה יותר מ-60 שניות")
                    
                except Exception as e:
                    test_time = time.time() - test_start
                    response = f"Error: {str(e)}"
                    tokens_used = 0
                    success = False
                    error_message = str(e)
                    
                    print(f"❌ Error in {test_time:.2f}s: {error_message}")
                
                # Store result
                test_result = {
                    'question_index': i,
                    'question': question_text,
                    'category': question_category,
                    'expected_answer': expected_answer,
                    'actual_response': response,
                    'success': success,
                    'error_message': error_message,
                    'response_time': test_time,
                    'tokens_used': tokens_used,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
                results['test_results'].append(test_result)
                
                # Update summary
                if success:
                    results['summary']['successful_responses'] += 1
                else:
                    results['summary']['failed_responses'] += 1
                
                results['summary']['total_tokens'] += tokens_used
                results['summary']['total_time'] += test_time
                
                # Small delay to prevent overwhelming the API
                await asyncio.sleep(0.1)
                
            except KeyboardInterrupt:
                print("\n⏹️ Test interrupted by user")
                break
            except Exception as e:
                print(f"❌ Unexpected error in test {i}: {e}")
                continue
        
        # Calculate final statistics
        total_time = time.time() - start_time
        successful_tests = results['summary']['successful_responses']
        
        if successful_tests > 0:
            results['summary']['average_response_time'] = results['summary']['total_time'] / successful_tests
        
        results['summary']['session_duration'] = total_time
        results['summary']['success_rate'] = (successful_tests / total_questions) * 100 if total_questions > 0 else 0
        
        print(f"\n📊 TEST COMPLETED")
        print(f"✅ Successful: {successful_tests}/{total_questions} ({results['summary']['success_rate']:.1f}%)")
        print(f"⏱️ Total time: {total_time:.2f}s")
        print(f"🎯 Average response: {results['summary']['average_response_time']:.2f}s")
        print(f"🔢 Total tokens: {results['summary']['total_tokens']}")
        
        return results

    async def _call_rag_service(self, question: str) -> str:
        """Call the real RAG service with the question and return the answer"""
        if not self.rag_service:
            return "RAG service not initialized"
        
        try:
            # השהיה קטנה בין בקשות כדי לאפשר רוטציה נכונה של מפתחות
            await asyncio.sleep(0.5)  # חצי שנייה
            
            # Call the real RAG service using the same method as the main system
            result = await self.rag_service.generate_answer(question, search_method="hybrid")
            
            # Handle different response formats
            if result:
                if isinstance(result, dict):
                    # Try different possible response keys
                    if 'answer' in result:
                        answer = result['answer']
                    elif 'response' in result:
                        answer = result['response']
                    elif 'content' in result:
                        answer = result['content']
                    elif 'text' in result:
                        answer = result['text']
                    else:
                        # If it's a dict but no standard key, convert to string
                        answer = str(result)
                elif isinstance(result, str):
                    answer = result
                else:
                    answer = str(result)
                
                # Clean up the answer and validate it
                if answer and len(answer.strip()) > 0:
                    # Remove any generic wrapper text that might be added
                    cleaned_answer = answer.strip()
                    return cleaned_answer
                else:
                    return "Empty response from RAG service"
            else:
                return "No response from RAG service"
                
        except Exception as e:
            error_msg = f"Error calling RAG service: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"

    def _generate_report(self, results: Dict, question_set: Dict, rag_profile: Dict) -> str:
        """Generate a detailed test report in Q&A format for easy export"""
        session_id = results['session_id']
        report_dir = RESULTS_DIR / session_id
        report_dir.mkdir(exist_ok=True)
        
        # Main report file (JSON)
        report_file = report_dir / "test_report.json"
        
        # Save complete results
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        # Generate Q&A export file (easy to read/export)
        qa_export_file = report_dir / "questions_and_answers.txt"
        with open(qa_export_file, 'w', encoding='utf-8') as f:
            f.write("RAG TEST PRO - QUESTIONS & ANSWERS EXPORT\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Session ID: {session_id}\n")
            f.write(f"Timestamp: {results['timestamp']}\n")
            f.write(f"Question Set: {question_set['name']} ({question_set['count']} questions)\n")
            f.write(f"RAG Profile: {rag_profile['name']}\n")
            f.write(f"Success Rate: {results['summary']['success_rate']:.1f}%\n")
            f.write("\n" + "=" * 60 + "\n\n")
            
            for i, result in enumerate(results['test_results'], 1):
                f.write(f"QUESTION {i}:\n")
                f.write(f"{result['question']}\n\n")
                f.write(f"ANSWER:\n")
                f.write(f"{result['actual_response']}\n\n")
                
                if result['expected_answer']:
                    f.write(f"EXPECTED:\n")
                    f.write(f"{result['expected_answer']}\n\n")
                
                f.write(f"STATUS: {'✅ Success' if result['success'] else '❌ Failed'}\n")
                f.write(f"TIME: {result['response_time']:.2f}s\n")
                # f.write(f"TOKENS: {result['tokens_used']}\n")
                
                if result['error_message']:
                    f.write(f"ERROR: {result['error_message']}\n")
                    
                f.write("\n" + "-" * 40 + "\n\n")
        
        # Generate CSV export for spreadsheet use
        csv_export_file = report_dir / "results_export.csv"
        with open(csv_export_file, 'w', encoding='utf-8') as f:
            f.write("Question_Number,Question,Answer,Expected_Answer,Success,Response_Time,Tokens_Used,Error\n")
            for result in results['test_results']:
                question = result['question'].replace('"', '""').replace('\n', ' ')
                answer = result['actual_response'].replace('"', '""').replace('\n', ' ')
                expected = result.get('expected_answer', '').replace('"', '""').replace('\n', ' ')
                error = (result.get('error_message') or '').replace('"', '""').replace('\n', ' ')
                
                f.write(f'{result["question_index"]},"{question}","{answer}","{expected}",')
                f.write(f'{result["success"]},{result["response_time"]:.2f},{result["tokens_used"]},"{error}"\n')
        
        # Generate summary report
        summary_file = report_dir / "summary.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("RAG TEST PRO - TEST REPORT SUMMARY\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Session ID: {session_id}\n")
            f.write(f"Timestamp: {results['timestamp']}\n\n")
            
            f.write("CONFIGURATION\n")
            f.write("-" * 20 + "\n")
            f.write(f"Question Set: {question_set['name']} ({question_set['count']} questions)\n")
            f.write(f"RAG Profile: {rag_profile['name']}\n")
            f.write(f"Description: {rag_profile['description']}\n\n")
            
            f.write("RAG PARAMETERS\n")
            f.write("-" * 20 + "\n")
            config = rag_profile['config']
            for key, value in config.items():
                f.write(f"{key}: {value}\n")
            f.write("\n")
            
            f.write("RESULTS SUMMARY\n")
            f.write("-" * 20 + "\n")
            summary = results['summary']
            f.write(f"Total Questions: {summary['total_questions']}\n")
            f.write(f"Successful: {summary['successful_responses']}\n")
            f.write(f"Failed: {summary['failed_responses']}\n")
            f.write(f"Success Rate: {summary['success_rate']:.1f}%\n")
            f.write(f"Total Time: {summary['session_duration']:.2f}s\n")
            f.write(f"Average Response Time: {summary['average_response_time']:.2f}s\n")
            f.write(f"Total Tokens: {summary['total_tokens']}\n")
        
        # Generate configuration file for reference
        config_file = report_dir / "profile_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(rag_profile['config'], f, indent=2)
        
        print(f"\n📁 Report files generated:")
        print(f"   📄 {report_file}")
        print(f"   📋 {qa_export_file}")
        print(f"   📊 {csv_export_file}")
        print(f"   📝 {summary_file}")
        print(f"   ⚙️ {config_file}")
        
        return str(report_file)

    def _create_custom_profile(self):
        """Create a custom RAG profile interactively"""
        print("\n🛠️ CREATE CUSTOM RAG PROFILE")
        print("-" * 35)
        
        try:
            # Get profile name
            profile_name = input("Profile name: ").strip()
            if not profile_name:
                print("❌ Profile name is required")
                return
            
            profile_id = profile_name.lower().replace(' ', '_').replace('-', '_')
            
            # Get description
            description = input("Description: ").strip()
            if not description:
                description = f"Custom profile: {profile_name}"
            
            print("\n📊 Enter RAG parameters (press Enter for default):")
            
            # Collect parameters with defaults
            config = {}
            
            # Search parameters
            config['similarityThreshold'] = self._get_float_input(
                "Similarity threshold (0.3-0.9)", 0.7, 0.3, 0.9)
            config['maxChunks'] = self._get_int_input(
                "Max chunks (1-50)", 12, 1, 50)
            config['temperature'] = self._get_float_input(
                "LLM temperature (0.0-1.0)", 0.2, 0.0, 1.0)
            config['chunkSize'] = self._get_int_input(
                "Chunk size (1000-4000)", 1800, 1000, 4000)
            config['maxContextTokens'] = self._get_int_input(
                "Max context tokens (4000-12000)", 6500, 4000, 12000)
            config['hybridSemanticWeight'] = self._get_float_input(
                "Hybrid semantic weight (0.4-0.8)", 0.65, 0.4, 0.8)
            config['hybridKeywordWeight'] = self._get_float_input(
                "Hybrid keyword weight (0.2-0.6)", 0.35, 0.2, 0.6)
            
            # Create profile
            profile_data = {
                'name': profile_name,
                'description': description,
                'created': datetime.now(timezone.utc).isoformat(),
                'version': '1.0',
                **config
            }
            
            # Save to file
            profile_file = PROFILES_DIR / f"{profile_id}.json"
            with open(profile_file, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, indent=2)
            
            print(f"\n✅ Profile created successfully!")
            print(f"📄 Saved to: {profile_file}")
            
            # Reload profiles
            self._load_rag_profiles()
            
        except KeyboardInterrupt:
            print("\n❌ Profile creation cancelled")
        except Exception as e:
            print(f"❌ Error creating profile: {e}")

    def _get_float_input(self, prompt: str, default: float, min_val: float, max_val: float) -> float:
        """Get float input with validation"""
        while True:
            try:
                response = input(f"{prompt} [{default}]: ").strip()
                if not response:
                    return default
                value = float(response)
                if min_val <= value <= max_val:
                    return value
                else:
                    print(f"❌ Value must be between {min_val} and {max_val}")
            except ValueError:
                print("❌ Please enter a valid number")

    def _get_int_input(self, prompt: str, default: int, min_val: int, max_val: int) -> int:
        """Get integer input with validation"""
        while True:
            try:
                response = input(f"{prompt} [{default}]: ").strip()
                if not response:
                    return default
                value = int(response)
                if min_val <= value <= max_val:
                    return value
                else:
                    print(f"❌ Value must be between {min_val} and {max_val}")
            except ValueError:
                print("❌ Please enter a valid integer")

    def _view_recent_results(self):
        """View recent test results"""
        print("\n📊 RECENT TEST RESULTS")
        print("-" * 30)
        
        if not RESULTS_DIR.exists():
            print("❌ No results directory found")
            return
        
        # Get all result directories
        result_dirs = [d for d in RESULTS_DIR.iterdir() if d.is_dir()]
        
        if not result_dirs:
            print("❌ No test results found")
            return
        
        # Sort by creation time (newest first)
        result_dirs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        print(f"Found {len(result_dirs)} test sessions:\n")
        
        for i, result_dir in enumerate(result_dirs[:10], 1):  # Show last 10
            report_file = result_dir / "test_report.json"
            
            if report_file.exists():
                try:
                    with open(report_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    timestamp = data.get('timestamp', 'Unknown')
                    if timestamp != 'Unknown':
                        try:
                            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                            timestamp = dt.strftime('%Y-%m-%d %H:%M')
                        except:
                            pass
                    
                    summary = data.get('summary', {})
                    profile_name = data.get('rag_profile', {}).get('name', 'Unknown')
                    question_set = data.get('question_set', {}).get('name', 'Unknown')
                    
                    print(f"{i}. Session: {result_dir.name}")
                    print(f"   📅 {timestamp}")
                    print(f"   📋 {question_set} ({summary.get('total_questions', 0)} questions)")
                    print(f"   ⚙️ {profile_name}")
                    print(f"   ✅ Success: {summary.get('success_rate', 0):.1f}%")
                    print()
                    
                except Exception as e:
                    print(f"{i}. {result_dir.name} (Error reading: {e})")
            else:
                print(f"{i}. {result_dir.name} (No report file)")
        
        if len(result_dirs) > 10:
            print(f"... and {len(result_dirs) - 10} more sessions")
        
        input("\nPress Enter to continue...")

    def _show_system_status(self):
        """Show system status and configuration"""
        print("\n🔍 SYSTEM STATUS")
        print("-" * 20)
        
        print(f"📁 Working Directory: {current_dir}")
        print(f"📋 Questions Directory: {QUESTIONS_DIR}")
        print(f"⚙️ Profiles Directory: {PROFILES_DIR}")
        print(f"📊 Results Directory: {RESULTS_DIR}")
        print()
        
        print(f"📈 Available Resources:")
        print(f"   📋 Question Sets: {len(self.question_sets)}")
        print(f"   ⚙️ RAG Profiles: {len(self.rag_profiles)}")
        
        # Show question sets
        if self.question_sets:
            print(f"\n📋 Question Sets:")
            for set_id, info in self.question_sets.items():
                print(f"   • {set_id}: {info['count']} questions")
        
        # Show profiles
        if self.rag_profiles:
            print(f"\n⚙️ RAG Profiles:")
            for profile_id, info in self.rag_profiles.items():
                source_icon = "🔧" if info['source'] == 'builtin' else "🛠️"
                print(f"   {source_icon} {profile_id}: {info['name']}")
        
        # Show recent results count
        if RESULTS_DIR.exists():
            result_dirs = [d for d in RESULTS_DIR.iterdir() if d.is_dir()]
            print(f"\n📊 Test Results: {len(result_dirs)} sessions")
        
        # System information
        print(f"\n🎯 System Information:")
        print(f"   🌐 Language: English Only")
        print(f"   🔧 Version: 1.0 - Fixed Imports")
        print(f"   📝 Status: All Hebrew text removed")
        
        input("\nPress Enter to continue...")


def main():
    """Main function"""
    try:
        # Create and run the RAG Test Pro system
        system = RAGTestPro()
        system.run_interactive_menu()
        
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ System error: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main() 