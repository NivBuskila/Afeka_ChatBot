#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
מערכת בדיקה מלאה לRAG - מכללת אפקה
=====================================

סקריפט זה מריץ בדיקה מקיפה של מערכת ה-RAG ויוצר דוחות מפורטים.
"""

import os
import sys
import json
import time
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# Add the backend directory to sys.path to allow importing from services
current_dir = Path(__file__).parent
backend_dir = current_dir.parent / "src" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

try:
    from services.rag_service import RAGService
    from app.config.settings import settings
except ImportError as e:
    print(f"שגיאה בייבוא מודולים: {e}")
    print("וודא שאתה מריץ את הסקריפט מהתיקייה הראשית של הפרויקט")
    sys.exit(1)

# הגדרת לוגינג
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('results/test_debug.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

class RAGTester:
    """מחלקה לבדיקת מערכת RAG"""
    
    def __init__(self):
        self.rag_service = None
        self.test_results = []
        self.start_time = None
        self.end_time = None
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # טעינת שאלות בדיקה
        with open('test_questions.json', 'r', encoding='utf-8') as f:
            self.questions = json.load(f)['questions']
    
    async def initialize_services(self):
        """אתחול שירותים"""
        try:
            logger.info("מאתחל שירותי RAG...")
            # 🎯 שימוש בפרופיל מרכזי - ללא hard-coding!
            self.rag_service = RAGService()  # יטען את הפרופיל המרכזי אוטומטית
            logger.info("שירותים אותחלו בהצלחה")
        except Exception as e:
            logger.error(f"שגיאה באתחול שירותים: {e}")
            raise
    
    def extract_current_settings(self) -> Dict[str, Any]:
        """חילוץ הגדרות RAG נוכחיות"""
        return {
            "timestamp": self.timestamp,
            "rag_settings": {
                "max_context_tokens": getattr(self.rag_service, 'max_context_tokens', 'N/A'),
                "similarity_threshold": getattr(self.rag_service, 'similarity_threshold', 'N/A'),
                "max_chunks": getattr(self.rag_service, 'max_chunks', 'N/A'),
                "embedding_model": "models/embedding-001",
                "llm_model": getattr(self.rag_service, 'model', {}).model_name if hasattr(self.rag_service, 'model') else 'N/A'
            },
            "chat_settings": {
                "gemini_model": settings.GEMINI_MODEL_NAME,
                "temperature": settings.GEMINI_TEMPERATURE,
                "max_tokens": settings.GEMINI_MAX_TOKENS,
                "history_window": settings.LANGCHAIN_HISTORY_K
            },
            "system_info": {
                "python_version": sys.version,
                "working_directory": os.getcwd()
            }
        }
    
    async def test_single_question(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """בדיקת שאלה יחידה"""
        logger.info(f"בודק שאלה #{question_data['id']}: {question_data['question']}")
        
        start_time = time.time()
        
        try:
            # ביצוע החיפוש באמצעות RAG service
            rag_result = await self.rag_service.generate_answer(
                query=question_data['question'],
                search_method="hybrid"
            )
            
            response_time = (time.time() - start_time) * 1000  # במילישניות
            
            # ניתוח התוצאות
            chunks_info = []
            if 'chunks_selected' in rag_result:
                for i, chunk in enumerate(rag_result['chunks_selected']):
                    chunk_info = {
                        "chunk_id": chunk.get('chunk_id', f'chunk_{i}'),
                        "similarity_score": chunk.get('similarity_score', chunk.get('combined_score', 0)),
                        "section_detected": chunk.get('section', 'לא זוהה'),
                        "content_preview": chunk.get('chunk_text', '')[:100] + "..." if chunk.get('chunk_text') else '',
                        "metadata": {
                            "document": chunk.get('document_name', 'לא זוהה'),
                            "page": chunk.get('page_number', 'לא זוהה'),
                            "chunk_header": chunk.get('chunk_header', 'לא זוהה')
                        }
                    }
                    chunks_info.append(chunk_info)
            
            # הערכת דיוק
            accuracy = self.assess_accuracy(question_data, rag_result, chunks_info)
            
            result = {
                "question_id": question_data['id'],
                "category": question_data['category'],
                "question": question_data['question'],
                "expected_section": question_data['expected_section'],
                "expected_content": question_data['expected_content'],
                "difficulty": question_data['difficulty'],
                "timestamp": datetime.now().isoformat(),
                "response_time_ms": round(response_time, 2),
                "answer": rag_result.get('answer', 'לא התקבלה תשובה'),
                "chunks_selected": chunks_info,
                "total_chunks_retrieved": len(chunks_info),
                "sources_count": len(rag_result.get('sources', [])),
                "context_tokens_estimated": self.estimate_tokens(rag_result.get('answer', '')),
                "accuracy_assessment": accuracy,
                "raw_rag_result": rag_result  # לצורך דיבוג
            }
            
            return result
            
        except Exception as e:
            logger.error(f"שגיאה בבדיקת שאלה #{question_data['id']}: {e}")
            return {
                "question_id": question_data['id'],
                "category": question_data['category'],
                "question": question_data['question'],
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "response_time_ms": (time.time() - start_time) * 1000
            }
    
    def assess_accuracy(self, question_data: Dict[str, Any], rag_result: Dict[str, Any], chunks_info: List[Dict]) -> Dict[str, Any]:
        """הערכת דיוק התשובה"""
        answer = rag_result.get('answer', '').lower()
        expected_section = question_data['expected_section'].lower()
        
        # בדיקה אם הסעיף הנכון נמצא
        correct_section = False
        if expected_section != 'multiple' and expected_section != 'none':
            correct_section = expected_section in answer
            # בדיקה גם בצ'אנקים
            if not correct_section:
                for chunk in chunks_info:
                    if expected_section in chunk['section_detected'].lower():
                        correct_section = True
                        break
        elif expected_section == 'multiple':
            correct_section = len(chunks_info) > 0  # אם מצא משהו רלוונטי
        elif expected_section == 'none':
            correct_section = len(chunks_info) == 0 or "לא נמצא" in answer or "אין מידע" in answer
        
        # בדיקת שלמות התשובה
        complete_answer = len(answer) > 50 and "לא נמצא" not in answer
        
        # בדיקת רלוונטיות
        relevant_content = len(chunks_info) > 0 and any(
            chunk['similarity_score'] > 0.6 for chunk in chunks_info
        )
        
        # קביעת סוג שגיאה
        error_type = "none"
        if not correct_section:
            error_type = "wrong_section"
        elif not complete_answer:
            error_type = "incomplete"
        elif not relevant_content:
            error_type = "irrelevant"
        
        return {
            "correct_section": correct_section,
            "complete_answer": complete_answer,
            "relevant_content": relevant_content,
            "error_type": error_type,
            "overall_success": correct_section and complete_answer and relevant_content
        }
    
    def estimate_tokens(self, text: str) -> int:
        """הערכת מספר טוקנים"""
        return int(len(text.split()) * 1.3)  # הערכה גסה
    
    async def run_all_tests(self):
        """הרצת כל הבדיקות"""
        logger.info("מתחיל בדיקות RAG...")
        self.start_time = datetime.now()
        
        await self.initialize_services()
        
        for question in self.questions:
            result = await self.test_single_question(question)
            self.test_results.append(result)
            
            # המתנה קצרה בין שאלות
            await asyncio.sleep(0.5)
        
        self.end_time = datetime.now()
        logger.info("בדיקות הושלמו!")
    
    def generate_summary_stats(self) -> Dict[str, Any]:
        """יצירת סטטיסטיקות סיכום"""
        total_questions = len(self.test_results)
        successful_tests = [r for r in self.test_results if 'error' not in r]
        
        if not successful_tests:
            return {"error": "לא הצליחה אף בדיקה"}
        
        # סטטיסטיקות כלליות
        correct_answers = sum(1 for r in successful_tests 
                            if r.get('accuracy_assessment', {}).get('overall_success', False))
        partial_answers = sum(1 for r in successful_tests 
                            if r.get('accuracy_assessment', {}).get('correct_section', False) 
                            and not r.get('accuracy_assessment', {}).get('overall_success', False))
        wrong_answers = total_questions - correct_answers - partial_answers
        
        # זמן תגובה ממוצע
        avg_response_time = sum(r.get('response_time_ms', 0) for r in successful_tests) / len(successful_tests)
        
        # סטטיסטיקות לפי קטגוריה
        categories_stats = {}
        for result in successful_tests:
            category = result.get('category', 'לא זוהה')
            if category not in categories_stats:
                categories_stats[category] = {'total': 0, 'correct': 0}
            categories_stats[category]['total'] += 1
            if result.get('accuracy_assessment', {}).get('overall_success', False):
                categories_stats[category]['correct'] += 1
        
        return {
            "total_questions": total_questions,
            "correct_answers": correct_answers,
            "partial_answers": partial_answers,
            "wrong_answers": wrong_answers,
            "success_rate": (correct_answers / total_questions) * 100,
            "partial_rate": (partial_answers / total_questions) * 100,
            "error_rate": (wrong_answers / total_questions) * 100,
            "avg_response_time_ms": round(avg_response_time, 2),
            "categories_stats": categories_stats,
            "test_duration_seconds": (self.end_time - self.start_time).total_seconds()
        }
    
    def generate_recommendations(self, stats: Dict[str, Any]) -> List[str]:
        """יצירת המלצות לשיפור"""
        recommendations = []
        
        success_rate = stats.get('success_rate', 0)
        avg_response_time = stats.get('avg_response_time_ms', 0)
        
        # המלצות על סמך שיעור הצלחה
        if success_rate < 70:
            recommendations.append("🚨 שיעור הצלחה נמוך - הנמך את סף הדמיון ל-0.5")
            recommendations.append("🔧 הגדל את מספר הצ'אנקים הנשלפים ל-12")
        elif success_rate < 85:
            recommendations.append("⚠️ שיעור הצלחה בינוני - שקול להגדיל את מספר הצ'אנקים בקונטקסט")
        
        # המלצות על סמך זמן תגובה
        if avg_response_time > 3000:
            recommendations.append("⏱️ זמן תגובה איטי - שקול להקטין את מספר הצ'אנקים")
            recommendations.append("🚀 שקול אופטימיזציה של חיפוש במסד הנתונים")
        
        # המלצות ספציפיות לקטגוריות
        categories = stats.get('categories_stats', {})
        for category, cat_stats in categories.items():
            success_rate_cat = (cat_stats['correct'] / cat_stats['total']) * 100 if cat_stats['total'] > 0 else 0
            if success_rate_cat < 60:
                recommendations.append(f"📚 קטגוריה '{category}': שיעור הצלחה נמוך ({success_rate_cat:.1f}%) - שפר זיהוי מילות מפתח")
        
        # בדיקה לגבי שאלות מלכודת
        trap_questions = [r for r in self.test_results if r.get('difficulty') == 'trap']
        trap_success = sum(1 for r in trap_questions if 'לא נמצא' in r.get('answer', '') or 'אין מידע' in r.get('answer', ''))
        if len(trap_questions) > 0 and (trap_success / len(trap_questions)) < 0.5:
            recommendations.append("🪤 בעיה בזיהוי שאלות מלכודת - שפר הנדלינג של תשובות 'לא נמצא'")
        
        if not recommendations:
            recommendations.append("✅ מערכת ה-RAG עובדת בצורה מצוינת!")
        
        return recommendations
    
    def save_detailed_report(self):
        """שמירת דוח מפורט"""
        settings_data = self.extract_current_settings()
        stats = self.generate_summary_stats()
        recommendations = self.generate_recommendations(stats)
        
        # שמירת הגדרות למובן JSON
        with open(f'results/rag_settings_{self.timestamp}.json', 'w', encoding='utf-8') as f:
            json.dump(settings_data, f, ensure_ascii=False, indent=2)
        
        # יצירת דוח טקסט מפורט
        report_content = self.create_detailed_text_report(stats, recommendations)
        with open(f'results/test_report_{self.timestamp}.txt', 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        # שמירת ניתוח צ'אנקים
        chunks_analysis = self.create_chunks_analysis()
        with open(f'results/chunks_analysis_{self.timestamp}.txt', 'w', encoding='utf-8') as f:
            f.write(chunks_analysis)
        
        # שמירת נתונים גולמיים JSON
        with open(f'results/raw_results_{self.timestamp}.json', 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"דוחות נשמרו בתיקיית results/ עם חותמת זמן {self.timestamp}")
    
    def create_detailed_text_report(self, stats: Dict[str, Any], recommendations: List[str]) -> str:
        """יצירת דוח טקסט מפורט"""
        
        report = f"""===============================================
🧪 דוח בדיקת מערכת RAG - מכללת אפקה
===============================================
📅 תאריך: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}
⏱️ משך בדיקה: {stats.get('test_duration_seconds', 0):.1f} שניות
🔧 גרסת מערכת: v2.1.3

📊 הגדרות RAG נוכחיות:
----------------------------------------
🔸 מקס טוקנים בקונטקסט: {self.rag_service.context_config.MAX_CONTEXT_TOKENS if self.rag_service else 'N/A'}
🔸 סף דמיון: {self.rag_service.search_config.SIMILARITY_THRESHOLD if self.rag_service else 'N/A'}
🔸 מקס צ'אנקים: {self.rag_service.search_config.MAX_CHUNKS_RETRIEVED if self.rag_service else 'N/A'}
🔸 מודל embedding: {self.rag_service.embedding_config.MODEL_NAME if self.rag_service else 'models/embedding-001'}
🔸 מודל LLM: {self.rag_service.llm_config.MODEL_NAME if self.rag_service else 'N/A'}
🔸 טמפרטורה: {self.rag_service.llm_config.TEMPERATURE if self.rag_service else 'N/A'}
🔸 מקס טוקנים: {self.rag_service.llm_config.MAX_OUTPUT_TOKENS if self.rag_service else 'N/A'}

📈 סיכום תוצאות:
----------------------------------------
✅ תשובות נכונות: {stats.get('correct_answers', 0)}/{stats.get('total_questions', 0)} ({stats.get('success_rate', 0):.1f}%)
⚠️ תשובות חלקיות: {stats.get('partial_answers', 0)}/{stats.get('total_questions', 0)} ({stats.get('partial_rate', 0):.1f}%)
❌ תשובות שגויות: {stats.get('wrong_answers', 0)}/{stats.get('total_questions', 0)} ({stats.get('error_rate', 0):.1f}%)
⏱️ זמן תגובה ממוצע: {stats.get('avg_response_time_ms', 0):.1f} מילישניות

🎯 דיוק לפי קטגוריות:
----------------------------------------"""
        
        for category, cat_stats in stats.get('categories_stats', {}).items():
            success_rate = (cat_stats['correct'] / cat_stats['total']) * 100 if cat_stats['total'] > 0 else 0
            report += f"\n🔹 {category}: {cat_stats['correct']}/{cat_stats['total']} ({success_rate:.1f}%)"
        
        report += f"""

===============================================
📋 תוצאות מפורטות לכל שאלה:
===============================================
"""
        
        for result in self.test_results:
            if 'error' in result:
                report += f"""
❌ שאלה #{result['question_id']}: "{result['question']}"
----------------------------------------
⚠️ שגיאה: {result['error']}
⏱️ זמן תגובה: {result.get('response_time_ms', 0):.1f} מילישניות

"""
                continue
            
            accuracy = result.get('accuracy_assessment', {})
            chunks = result.get('chunks_selected', [])
            
            # אייקון לפי הצלחה
            if accuracy.get('overall_success', False):
                icon = "✅"
            elif accuracy.get('correct_section', False):
                icon = "⚠️"
            else:
                icon = "❌"
            
            report += f"""
{icon} שאלה #{result['question_id']}: "{result['question']}"
----------------------------------------
📂 קטגוריה: {result['category']}
🎯 רמת קושי: {result['difficulty']}
⏱️ זמן תגובה: {result['response_time_ms']:.1f} מילישניות
📍 סעיף מצופה: {result['expected_section']}

🧩 צ'אנקים שנבחרו ({len(chunks)} סה"כ):"""
            
            for i, chunk in enumerate(chunks[:5]):  # מציג רק 5 ראשונים
                report += f"""
  📄 chunk_{i+1} (דמיון: {chunk.get('similarity_score', 0):.2f}) - {chunk.get('section_detected', 'לא זוהה')}"""
            
            if len(chunks) > 5:
                report += f"\n  ... ועוד {len(chunks) - 5} צ'אנקים"
            
            # תוצאות הערכה
            report += f"""

💬 התשובה:
"{result['answer'][:200]}{'...' if len(result['answer']) > 200 else ''}"

✅ הערכת דיוק:
  {'✅' if accuracy.get('correct_section') else '❌'} סעיף נכון: {'כן' if accuracy.get('correct_section') else 'לא'}
  {'✅' if accuracy.get('complete_answer') else '❌'} תוכן מלא: {'כן' if accuracy.get('complete_answer') else 'לא'}
  {'✅' if accuracy.get('relevant_content') else '❌'} רלוונטי: {'כן' if accuracy.get('relevant_content') else 'לא'}
  🎭 סוג שגיאה: {accuracy.get('error_type', 'ללא')}

"""
        
        report += f"""
===============================================
🔧 המלצות לשיפור:
===============================================

🚨 בעיות שזוהו:
"""
        
        # ניתוח בעיות
        wrong_section_count = sum(1 for r in self.test_results 
                                if r.get('accuracy_assessment', {}).get('error_type') == 'wrong_section')
        incomplete_count = sum(1 for r in self.test_results 
                             if r.get('accuracy_assessment', {}).get('error_type') == 'incomplete')
        
        if wrong_section_count > 0:
            report += f"1. בלבול בין סעיפים דומים ({wrong_section_count} שאלות)\n"
        if incomplete_count > 0:
            report += f"2. תשובות חלקיות ({incomplete_count} שאלות)\n"
        if stats.get('avg_response_time_ms', 0) > 2000:
            report += f"3. זמן תגובה איטי ({stats.get('avg_response_time_ms', 0):.1f}ms ממוצע)\n"
        
        report += f"""
💡 הצעות לשיפור:
"""
        for i, rec in enumerate(recommendations, 1):
            report += f"{i}. {rec}\n"
        
        report += "\n===============================================\n"
        
        return report
    
    def create_chunks_analysis(self) -> str:
        """יצירת ניתוח מפורט של צ'אנקים"""
        analysis = f"""===============================================
🔍 ניתוח מפורט של צ'אנקים - {self.timestamp}
===============================================

📊 סטטיסטיקות כלליות:
----------------------------------------
"""
        
        all_chunks = []
        for result in self.test_results:
            if 'chunks_selected' in result:
                all_chunks.extend(result['chunks_selected'])
        
        if not all_chunks:
            return analysis + "❌ לא נמצאו צ'אנקים לניתוח\n"
        
        # סטטיסטיקות דמיון
        similarity_scores = [chunk.get('similarity_score', 0) for chunk in all_chunks]
        avg_similarity = sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0
        max_similarity = max(similarity_scores) if similarity_scores else 0
        min_similarity = min(similarity_scores) if similarity_scores else 0
        
        analysis += f"""
🔸 סה"כ צ'אנקים שנבחרו: {len(all_chunks)}
🔸 ציון דמיון ממוצע: {avg_similarity:.3f}
🔸 ציון דמיון מקסימלי: {max_similarity:.3f}
🔸 ציון דמיון מינימלי: {min_similarity:.3f}
🔸 צ'אנקים מעל סף הדמיון (0.65): {sum(1 for s in similarity_scores if s > 0.65)}

📈 התפלגות ציוני דמיון:
----------------------------------------
"""
        
        # היסטוגרמה של ציוני דמיון
        ranges = [(0, 0.3), (0.3, 0.5), (0.5, 0.7), (0.7, 0.85), (0.85, 1.0)]
        for low, high in ranges:
            count = sum(1 for s in similarity_scores if low <= s < high)
            percentage = (count / len(similarity_scores)) * 100 if similarity_scores else 0
            bar = "█" * int(percentage / 5)  # בר גרפי
            analysis += f"{low:.1f}-{high:.1f}: {count:3d} ({percentage:5.1f}%) {bar}\n"
        
        # ניתוח מסמכים
        doc_analysis = {}
        for chunk in all_chunks:
            doc_name = chunk.get('metadata', {}).get('document', 'לא זוהה')
            if doc_name not in doc_analysis:
                doc_analysis[doc_name] = 0
            doc_analysis[doc_name] += 1
        
        analysis += f"""

📚 התפלגות לפי מסמכים:
----------------------------------------
"""
        for doc, count in sorted(doc_analysis.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(all_chunks)) * 100
            analysis += f"📄 {doc}: {count} צ'אנקים ({percentage:.1f}%)\n"
        
        # ניתוח סעיפים שזוהו
        section_analysis = {}
        for chunk in all_chunks:
            section = chunk.get('section_detected', 'לא זוהה')
            if section not in section_analysis:
                section_analysis[section] = 0
            section_analysis[section] += 1
        
        analysis += f"""

🏷️ סעיפים שזוהו הכי הרבה:
----------------------------------------
"""
        top_sections = sorted(section_analysis.items(), key=lambda x: x[1], reverse=True)[:10]
        for section, count in top_sections:
            analysis += f"📋 {section}: {count} פעמים\n"
        
        return analysis


async def main():
    """פונקציה ראשית"""
    print("🚀 מתחיל בדיקת מערכת RAG...")
    print("=" * 50)
    
    try:
        tester = RAGTester()
        await tester.run_all_tests()
        
        print("\n📊 יוצר דוחות...")
        tester.save_detailed_report()
        
        # הצגת סיכום מהיר
        stats = tester.generate_summary_stats()
        print(f"""
✅ בדיקה הושלמה בהצלחה!
📈 תוצאות:
   - שאלות נבדקו: {stats.get('total_questions', 0)}
   - שיעור הצלחה: {stats.get('success_rate', 0):.1f}%
   - זמן ממוצע: {stats.get('avg_response_time_ms', 0):.1f}ms
   
📁 הדוחות נשמרו בתיקיית: RAG_test/results/
   - test_report_{tester.timestamp}.txt (דוח מפורט)
   - rag_settings_{tester.timestamp}.json (הגדרות)
   - chunks_analysis_{tester.timestamp}.txt (ניתוח צ'אנקים)
   - raw_results_{tester.timestamp}.json (נתונים גולמיים)
""")
        
        recommendations = tester.generate_recommendations(stats)
        if recommendations:
            print("💡 המלצות עיקריות:")
            for rec in recommendations[:3]:  # מציג 3 ראשונות
                print(f"   {rec}")
        
    except Exception as e:
        logger.error(f"שגיאה בביצוע בדיקה: {e}", exc_info=True)
        print(f"❌ שגיאה: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    # הרצת הבדיקה
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 