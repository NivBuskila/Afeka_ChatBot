"""
מודול חלוקה חכמה (Smart Chunking) לתקנוני מכללה
מממש את השלב השני בתוכנית האסטרטגית: אלגוריתם חלוקה היררכי מתקדם
"""

import re
import logging
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
import unicodedata

logger = logging.getLogger(__name__)

@dataclass
class ChunkMetadata:
    """מטא-דטה מלא לכל chunk"""
    document_name: str
    document_version: str
    chapter: str
    section_number: str
    section_title: str
    hierarchical_path: str
    parent_context: str
    cross_references: List[str]
    keywords: List[str]
    content_type: str  # rule, procedure, definition, penalty, temporal
    is_temporal: bool
    chunk_type: str  # primary, secondary, context

@dataclass
class ProcessedChunk:
    """chunk מעובד עם כל המטא-דטה"""
    text: str
    metadata: ChunkMetadata
    size: int
    overlap_with_previous: int
    token_count: int

class SmartChunker:
    """מחלק חכם למסמכי תקנון עם זיהוי היררכיה ומטא-דטה מתקדם"""
    
    def __init__(self):
        # דפוסי זיהוי סעיפים ופרקים
        self.section_patterns = [
            r'^\s*(\d+(?:\.\d+)*)\s*[.\-]?\s*(.+?)(?:\n|$)',  # 1.2.3 כותרת
            r'^\s*סעיף\s+(\d+(?:\.\d+)*)\s*[:\-]?\s*(.+?)(?:\n|$)',  # סעיף 1.2.3:
            r'^\s*פרק\s+([א-ת]+|\d+)\s*[:\-]?\s*(.+?)(?:\n|$)',  # פרק ראשון:
        ]
        
        # דפוסי זיהוי הפניות צולבות
        self.cross_ref_patterns = [
            r'כמפורט בסעיף\s+(\d+(?:\.\d+)*)',
            r'בהתאם לסעיף\s+(\d+(?:\.\d+)*)',
            r'לפי סעיף\s+(\d+(?:\.\d+)*)',
            r'ראה סעיף\s+(\d+(?:\.\d+)*)',
            r'סעיף\s+(\d+(?:\.\d+)*)\s+לעיל',
            r'סעיף\s+(\d+(?:\.\d+)*)\s+להלן',
        ]
        
        # מילות מפתח קריטיות לזיהוי סוג תוכן
        self.content_type_keywords = {
            'rule': ['חובה', 'אסור', 'יש', 'אין', 'רשאי', 'חייב', 'מותר'],
            'procedure': ['בקשה', 'תהליך', 'הליך', 'מועד', 'הגשה', 'אישור'],
            'definition': ['פירוש', 'משמעות', 'הגדרה', 'כוונתו', 'לעניין'],
            'penalty': ['עונש', 'פיטורין', 'הרחקה', 'קנס', 'משמעת', 'עבירה'],
            'temporal': ['מועד', 'תאריך', 'שנה', 'סמסטר', 'חודש', 'יום', 'שעה']
        }
        
        # מילות מפתח טמפורליות מתקדמות
        self.temporal_keywords = [
            r'\d+\s*ימים?', r'\d+\s*שבועות?', r'\d+\s*חודשים?',
            r'סמסטר\s+[אב]', r'שנת\s+לימודים', r'מועד\s+[אב]',
            r'עד\s+\d+\.\d+\.\d+', r'החל\s+מ\-?\d+\.\d+',
            r'תוך\s+\d+\s+ימים', r'לא\s+יאוחר\s+מ'
        ]

    def normalize_hebrew_text(self, text: str) -> str:
        """ניקוי ונירמול טקסט עברית"""
        # הסרת ניקוד
        text = unicodedata.normalize('NFD', text)
        text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
        
        # ניקוי תווים מיוחדים אך שמירה על מספרים ופיסוק חשוב
        text = re.sub(r'[^\u05D0-\u05EA\u0590-\u05FF0-9a-zA-Z\s\.\-:()"]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()

    def extract_section_info(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """חילוץ מספר סעיף וכותרת"""
        for pattern in self.section_patterns:
            match = re.search(pattern, text, re.MULTILINE | re.UNICODE)
            if match:
                section_number = match.group(1)
                section_title = match.group(2).strip() if len(match.groups()) > 1 else ""
                return section_number, section_title
        return None, None

    def find_cross_references(self, text: str) -> List[str]:
        """זיהוי הפניות צולבות לסעיפים אחרים"""
        cross_refs = []
        for pattern in self.cross_ref_patterns:
            matches = re.findall(pattern, text, re.UNICODE)
            cross_refs.extend(matches)
        return list(set(cross_refs))  # הסרת כפילויות

    def extract_keywords(self, text: str) -> List[str]:
        """חילוץ מילות מפתח רלוונטיות"""
        keywords = []
        normalized_text = self.normalize_hebrew_text(text.lower())
        
        # מילות מפתח חשובות
        important_words = [
            'נוכחות', 'ציון', 'מעבר', 'נקודות זכות', 'תוכנית לימודים',
            'מעבדה', 'פרויקט', 'עבודה', 'מטלה', 'בחינה', 'מבחן',
            'הרשמה', 'ביטול', 'פטור', 'שוויון', 'תלמיד', 'סטודנט'
        ]
        
        for word in important_words:
            if word in normalized_text:
                keywords.append(word)
        
        # זיהוי אחוזים וציונים
        percentages = re.findall(r'\d+%|\d+\s+אחוז', text)
        keywords.extend(percentages)
        
        # זיהוי ציונים
        grades = re.findall(r'\d+\s+ומעלה|\d+\s+נקודות', text)
        keywords.extend(grades)
        
        return keywords

    def classify_content_type(self, text: str) -> str:
        """סיווג סוג התוכן"""
        normalized_text = self.normalize_hebrew_text(text.lower())
        
        # בדיקה לפי מילות מפתח
        type_scores = {content_type: 0 for content_type in self.content_type_keywords}
        
        for content_type, keywords in self.content_type_keywords.items():
            for keyword in keywords:
                if keyword in normalized_text:
                    type_scores[content_type] += 1
        
        # החזרת הסוג עם הציון הגבוה ביותר
        max_score = max(type_scores.values())
        if max_score > 0:
            return max(type_scores, key=type_scores.get)
        
        return 'rule'  # ברירת מחדל

    def is_temporal_content(self, text: str) -> bool:
        """בדיקה האם התוכן מכיל מידע זמני"""
        for pattern in self.temporal_keywords:
            if re.search(pattern, text, re.UNICODE):
                return True
        return False

    def build_hierarchical_path(self, section_number: str, chapter: str = "") -> str:
        """בניית נתיב היררכי"""
        if not section_number:
            return chapter if chapter else ""
        
        parts = section_number.split('.')
        path_parts = []
        
        # בניית נתיב הדרגתי
        for i in range(len(parts)):
            path_parts.append('.'.join(parts[:i+1]))
        
        if chapter:
            return f"{chapter} > " + " > ".join(path_parts)
        return " > ".join(path_parts)

    def smart_split_text(self, text: str, max_chunk_size: int = 600, overlap: int = 100) -> List[Tuple[str, int]]:
        """חלוקה חכמה של טקסט לפי גודל אמיתי תוך שמירה על קוהרנטיות"""
        if len(text) <= max_chunk_size:
            return [(text, 0)]
        
        chunks = []
        sentences = re.split(r'[.!?]\s+', text)
        
        current_chunk = ""
        current_size = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            sentence_size = len(sentence)
            
            # אם המשפט גדול מדי לבד, נחלק אותו
            if sentence_size > max_chunk_size:
                if current_chunk:
                    chunks.append((current_chunk.strip(), overlap if len(chunks) > 0 else 0))
                    current_chunk = ""
                    current_size = 0
                
                # חלוקת משפט ארוך
                words = sentence.split()
                temp_chunk = ""
                for word in words:
                    if len(temp_chunk + " " + word) > max_chunk_size:
                        if temp_chunk:
                            chunks.append((temp_chunk.strip(), overlap))
                        temp_chunk = word
                    else:
                        temp_chunk += " " + word if temp_chunk else word
                
                if temp_chunk:
                    current_chunk = temp_chunk[-overlap:] if len(temp_chunk) > overlap else temp_chunk
                    current_size = len(current_chunk)
                continue
            
            # בדיקה אם הוספת המשפט תחרוג מהגודל המקסימלי
            if current_size + sentence_size + 1 > max_chunk_size:
                if current_chunk:
                    chunks.append((current_chunk.strip(), overlap if len(chunks) > 0 else 0))
                
                # התחלת chunk חדש עם חפיפה
                overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
                current_chunk = overlap_text + " " + sentence if overlap_text else sentence
                current_size = len(current_chunk)
            else:
                current_chunk += " " + sentence if current_chunk else sentence
                current_size += sentence_size + (1 if current_chunk else 0)
        
        # הוספת ה-chunk האחרון
        if current_chunk.strip():
            chunks.append((current_chunk.strip(), overlap if len(chunks) > 0 else 0))
        
        return chunks

    def process_document(self, 
                        document_text: str, 
                        document_name: str = "", 
                        document_version: str = "",
                        max_chunk_size: int = 600,
                        overlap: int = 100) -> List[ProcessedChunk]:
        """עיבוד מסמך מלא לחלקים חכמים עם מטא-דטה מלא"""
        
        logger.info(f"מתחיל עיבוד מסמך: {document_name}")
        
        processed_chunks = []
        
        # חלוקה ראשונית לפרקים/סעיפים
        sections = self._split_into_sections(document_text)
        
        for section_text, section_info in sections:
            # חילוץ מידע על הסעיף
            section_number, section_title = self.extract_section_info(section_text)
            
            # זיהוי פרק
            chapter = self._identify_chapter(section_text, section_info)
            
            # חלוקה חכמה לחלקים
            text_chunks = self.smart_split_text(section_text, max_chunk_size, overlap)
            
            for i, (chunk_text, chunk_overlap) in enumerate(text_chunks):
                # יצירת מטא-דטה מלא
                metadata = ChunkMetadata(
                    document_name=document_name,
                    document_version=document_version,
                    chapter=chapter,
                    section_number=section_number or "",
                    section_title=section_title or "",
                    hierarchical_path=self.build_hierarchical_path(section_number, chapter),
                    parent_context=section_info.get('parent_context', ''),
                    cross_references=self.find_cross_references(chunk_text),
                    keywords=self.extract_keywords(chunk_text),
                    content_type=self.classify_content_type(chunk_text),
                    is_temporal=self.is_temporal_content(chunk_text),
                    chunk_type='primary' if i == 0 else 'secondary'
                )
                
                # יצירת chunk מעובד
                processed_chunk = ProcessedChunk(
                    text=chunk_text,
                    metadata=metadata,
                    size=len(chunk_text),
                    overlap_with_previous=chunk_overlap,
                    token_count=self._estimate_token_count(chunk_text)
                )
                
                processed_chunks.append(processed_chunk)
        
        logger.info(f"סיים עיבוד מסמך {document_name}: {len(processed_chunks)} chunks נוצרו")
        return processed_chunks

    def _split_into_sections(self, text: str) -> List[Tuple[str, Dict]]:
        """חלוקה ראשונית לסעיפים"""
        # זיהוי סעיפים ראשיים
        section_pattern = r'^(\d+(?:\.\d+)*\.?\s+.+?)(?=^\d+(?:\.\d+)*\.?\s+|\Z)'
        sections = re.findall(section_pattern, text, re.MULTILINE | re.DOTALL | re.UNICODE)
        
        if not sections:
            # אם לא נמצאו סעיפים, נחזיר את כל הטקסט כסעיף אחד
            return [(text, {})]
        
        result = []
        for section in sections:
            section_info = {'type': 'section'}
            result.append((section.strip(), section_info))
        
        return result

    def _identify_chapter(self, text: str, section_info: Dict) -> str:
        """זיהוי פרק מהטקסט"""
        chapter_patterns = [
            r'פרק\s+([א-ת]+|\d+)\s*[:\-]?\s*(.+?)(?:\n|$)',
            r'חלק\s+([א-ת]+|\d+)\s*[:\-]?\s*(.+?)(?:\n|$)'
        ]
        
        for pattern in chapter_patterns:
            match = re.search(pattern, text[:200], re.UNICODE)  # חיפוש רק בתחילת הטקסט
            if match:
                return f"פרק {match.group(1)} - {match.group(2).strip()}"
        
        return "לא זוהה פרק"

    def _estimate_token_count(self, text: str) -> int:
        """הערכת מספר טוקנים בטקסט עברית"""
        # הערכה גסה: כ-0.75 טוקן למילה בעברית
        words = len(text.split())
        return int(words * 0.75) 