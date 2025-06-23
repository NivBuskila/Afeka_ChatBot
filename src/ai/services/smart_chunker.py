"""
Smart Chunking module for Afeka College regulations
Implements the second stage of the strategic plan: Advanced hierarchical chunking algorithm
"""

import re
import logging
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
import unicodedata

# Import configuration
try:
    from ..config.rag_config import get_performance_config
except ImportError:
    from src.ai.config.rag_config import get_performance_config

logger = logging.getLogger(__name__)

@dataclass
class ChunkMetadata:
    """Full metadata for each chunk"""
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
    """Processed chunk with all metadata"""
    text: str
    metadata: ChunkMetadata
    size: int
    overlap_with_previous: int
    token_count: int

class SmartChunker:
    """Smart chunker for Afeka College regulations with advanced hierarchical detection and metadata"""
    
    def __init__(self):
        self.performance_config = get_performance_config()
        # Section and chapter patterns
        self.section_patterns = [
            r'^\s*(\d+(?:\.\d+)*)\s*[.\-]?\s*(.+?)(?:\n|$)',  # 1.2.3 כותרת
            r'^\s*סעיף\s+(\d+(?:\.\d+)*)\s*[:\-]?\s*(.+?)(?:\n|$)',  # סעיף 1.2.3:
            r'^\s*פרק\s+([א-ת]+|\d+)\s*[:\-]?\s*(.+?)(?:\n|$)',  # פרק ראשון:
        ]
        
        # Cross-reference patterns
        self.cross_ref_patterns = [
            r'כמפורט בסעיף\s+(\d+(?:\.\d+)*)',
            r'בהתאם לסעיף\s+(\d+(?:\.\d+)*)',
            r'לפי סעיף\s+(\d+(?:\.\d+)*)',
            r'ראה סעיף\s+(\d+(?:\.\d+)*)',
            r'סעיף\s+(\d+(?:\.\d+)*)\s+לעיל',
            r'סעיף\s+(\d+(?:\.\d+)*)\s+להלן',
        ]
        
        # Critical keywords for content type identification
        self.content_type_keywords = {
            'rule': ['חובה', 'אסור', 'יש', 'אין', 'רשאי', 'חייב', 'מותר'],
            'procedure': ['בקשה', 'תהליך', 'הליך', 'מועד', 'הגשה', 'אישור'],
            'definition': ['פירוש', 'משמעות', 'הגדרה', 'כוונתו', 'לעניין'],
            'penalty': ['עונש', 'פיטורין', 'הרחקה', 'קנס', 'משמעת', 'עבירה'],
            'temporal': ['מועד', 'תאריך', 'שנה', 'סמסטר', 'חודש', 'יום', 'שעה']
        }
        
        # Advanced temporal keywords
        self.temporal_keywords = [
            r'\d+\s*ימים?', r'\d+\s*שבועות?', r'\d+\s*חודשים?',
            r'סמסטר\s+[אב]', r'שנת\s+לימודים', r'מועד\s+[אב]',
            r'עד\s+\d+\.\d+\.\d+', r'החל\s+מ\-?\d+\.\d+',
            r'תוך\s+\d+\s+ימים', r'לא\s+יאוחר\s+מ'
        ]

    def normalize_hebrew_text(self, text: str) -> str:
        """Cleaning and normalizing Hebrew text"""
        # Remove diacritics
        text = unicodedata.normalize('NFD', text)
        text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
        
        # Clean special characters but preserve numbers and important punctuation
        text = re.sub(r'[^\u05D0-\u05EA\u0590-\u05FF0-9a-zA-Z\s\.\-:()"]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()

    def extract_section_info(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract section number and title - improved section detection"""
        
        # Enhanced section detection patterns
        enhanced_patterns = [
            # Regular pattern: section number with title
            r'^\s*(\d+(?:\.\d+)*)\s*[.\-:]?\s*(.+?)(?:\n|$)',
            # Explicit section: "סעיף 1.5.1:"
            r'^\s*סעיף\s+(\d+(?:\.\d+)*)\s*[:\-]?\s*(.+?)(?:\n|$)',
            # Section number at the beginning of a line even without a title
            r'^\s*(\d+(?:\.\d+)*)\s*[.\-:]\s*(.*)$',
            # Detection within text: "לפי סעיף 1.5.1"
            r'סעיף\s+(\d+(?:\.\d+)*)\s*[:\-]?\s*([^\n]*)',
            # Chapter with number
            r'^\s*פרק\s+([א-ת]+|\d+)\s*[:\-]?\s*(.+?)(?:\n|$)',
            # Simple number at the beginning of a line
            r'^\s*(\d+(?:\.\d+)*)\s+([^\n]+?)(?:\n|$)',
        ]
        
        # Test the existing patterns
        for pattern in self.section_patterns + enhanced_patterns:
            match = re.search(pattern, text[:500], re.MULTILINE | re.UNICODE)  # Search in the first 500 characters
            if match:
                section_number = match.group(1)
                section_title = match.group(2).strip() if len(match.groups()) > 1 else ""
                
                # Clean the title from extra characters
                section_title = re.sub(r'^[:\-\.\s]+', '', section_title)
                section_title = re.sub(r'[:\-\.\s]+$', '', section_title)
                
                return section_number, section_title
        
        # Additional attempt - search for section numbers in the entire text
        section_number_pattern = r'\b(\d+(?:\.\d+){1,3})\b'
        matches = re.findall(section_number_pattern, text[:200])
        if matches:
            # Select the first number that looks like a section number
            for match in matches:
                if '.' in match:  # This looks like a section number
                    # Try to extract the title from the first sentence
                    first_line = text.split('\n')[0][:100]
                    title = re.sub(r'\d+(?:\.\d+)*\s*[:\-\.]?\s*', '', first_line).strip()
                    return match, title if title else ""
        
        return None, None

    def find_cross_references(self, text: str) -> List[str]:
        """Detect nested references to other sections"""
        cross_refs = []
        for pattern in self.cross_ref_patterns:
            matches = re.findall(pattern, text, re.UNICODE)
            cross_refs.extend(matches)
        return list(set(cross_refs))  # Remove duplicates

    def extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords"""
        keywords = []
        normalized_text = self.normalize_hebrew_text(text.lower())
        
        # Important keywords
        important_words = [
            'נוכחות', 'ציון', 'מעבר', 'נקודות זכות', 'תוכנית לימודים',
            'מעבדה', 'פרויקט', 'עבודה', 'מטלה', 'בחינה', 'מבחן',
            'הרשמה', 'ביטול', 'פטור', 'שוויון', 'תלמיד', 'סטודנט'
        ]
        
        for word in important_words:
            if word in normalized_text:
                keywords.append(word)
        
        # Detect percentages and grades
        percentages = re.findall(r'\d+%|\d+\s+אחוז', text)
        keywords.extend(percentages)
        
        # Detect grades
        grades = re.findall(r'\d+\s+ומעלה|\d+\s+נקודות', text)
        keywords.extend(grades)
        
        return keywords

    def classify_content_type(self, text: str) -> str:
        """Classify content type"""
        normalized_text = self.normalize_hebrew_text(text.lower())
        
        # Check by keywords
        type_scores = {content_type: 0 for content_type in self.content_type_keywords}
        
        for content_type, keywords in self.content_type_keywords.items():
            for keyword in keywords:
                if keyword in normalized_text:
                    type_scores[content_type] += 1
        
        # Return the type with the highest score
        max_score = max(type_scores.values())
        if max_score > 0:
            return max(type_scores.keys(), key=lambda k: type_scores[k])
        
        return 'rule'  # Default

    def is_temporal_content(self, text: str) -> bool:
        """Check if the content contains temporal information"""
        for pattern in self.temporal_keywords:
            if re.search(pattern, text, re.UNICODE):
                return True
        return False

    def build_hierarchical_path(self, section_number: str, chapter: str = "") -> str:
        """Build hierarchical path"""
        if not section_number:
            return chapter if chapter else ""
        
        parts = section_number.split('.')
        path_parts = []
        
        # Build hierarchical path
        for i in range(len(parts)):
            path_parts.append('.'.join(parts[:i+1]))
        
        if chapter:
            return f"{chapter} > " + " > ".join(path_parts)
        return " > ".join(path_parts)

    def smart_split_text(self, text: str, max_chunk_size: int = 600, overlap: int = 100) -> List[Tuple[str, int]]:
        """Smart text splitting by real size while preserving coherence"""
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
            
            # If the sentence is too long, split it
            if sentence_size > max_chunk_size:
                if current_chunk:
                    chunks.append((current_chunk.strip(), overlap if len(chunks) > 0 else 0))
                    current_chunk = ""
                    current_size = 0
                
                # Split long sentence
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
            
            # Check if adding the sentence would exceed the maximum size
            if current_size + sentence_size + 1 > max_chunk_size:
                if current_chunk:
                    chunks.append((current_chunk.strip(), overlap if len(chunks) > 0 else 0))
                
                # Start a new chunk with overlap
                overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
                current_chunk = overlap_text + " " + sentence if overlap_text else sentence
                current_size = len(current_chunk)
            else:
                current_chunk += " " + sentence if current_chunk else sentence
                current_size += sentence_size + (1 if current_chunk else 0)
        
        # Add the last chunk
        if current_chunk.strip():
            chunks.append((current_chunk.strip(), overlap if len(chunks) > 0 else 0))
        
        return chunks

    def process_document(self, 
                        document_text: str, 
                        document_name: str = "", 
                        document_version: str = "",
                        max_chunk_size: int = 600,
                        overlap: int = 100) -> List[ProcessedChunk]:
        """Process full document into smart chunks with full metadata"""
        
        logger.info(f"Starting document processing: {document_name}")
        
        processed_chunks = []
        
        # First split into chapters/sections
        sections = self._split_into_sections(document_text)
        
        for section_text, section_info in sections:
            # Extract section information
            section_number, section_title = self.extract_section_info(section_text)
            
            # Identify chapter
            chapter = self._identify_chapter(section_text, section_info)
            
            # Smart split into chunks
            text_chunks = self.smart_split_text(section_text, max_chunk_size, overlap)
            
            for i, (chunk_text, chunk_overlap) in enumerate(text_chunks):
                # Create full metadata
                metadata = ChunkMetadata(
                    document_name=document_name,
                    document_version=document_version,
                    chapter=chapter,
                    section_number=section_number or "",
                    section_title=section_title or "",
                    hierarchical_path=self.build_hierarchical_path(section_number or "", chapter),
                    parent_context=section_info.get('parent_context', ''),
                    cross_references=self.find_cross_references(chunk_text),
                    keywords=self.extract_keywords(chunk_text),
                    content_type=self.classify_content_type(chunk_text),
                    is_temporal=self.is_temporal_content(chunk_text),
                    chunk_type='primary' if i == 0 else 'secondary'
                )
                
                # Create processed chunk
                processed_chunk = ProcessedChunk(
                    text=chunk_text,
                    metadata=metadata,
                    size=len(chunk_text),
                    overlap_with_previous=chunk_overlap,
                    token_count=self._estimate_token_count(chunk_text)
                )
                
                processed_chunks.append(processed_chunk)
        
        logger.info(f"Document processing completed: {document_name} - {len(processed_chunks)} chunks created")
        return processed_chunks

    def _split_into_sections(self, text: str) -> List[Tuple[str, Dict]]:
        """Initial split into sections - improved small section detection"""
        
        # Multiple section detection patterns
        section_patterns = [
            # Main sections: 1. 2. 3.
            r'(?:^|\n)\s*(\d+)\.?\s+([^\n]*(?:\n(?!\s*\d+\.)[^\n]*)*)',
            # Sub-sections: 1.1, 1.2, etc.
            r'(?:^|\n)\s*(\d+\.\d+)\.?\s+([^\n]*(?:\n(?!\s*\d+\.)[^\n]*)*)',
            # Sub-sub-sections: 1.1.1, 1.2.3, etc. 
            r'(?:^|\n)\s*(\d+\.\d+\.\d+)\.?\s+([^\n]*(?:\n(?!\s*\d+\.)[^\n]*)*)',
            # Sections with "סעיף": סעיף 1.5.1
            r'(?:^|\n)\s*סעיף\s+(\d+(?:\.\d+)*)\s*[:\-]?\s*([^\n]*(?:\n(?!\s*(?:סעיף\s+)?\d+\.)[^\n]*)*)',
            # Additional sections that can be in the document
            r'(\d+(?:\.\d+){0,3})\s*[:\-]\s*([^\n]*(?:\n(?!\s*\d+\.)[^\n]*)*)',
        ]
        
        all_sections = []
        used_positions = set()
        
        # Search by all patterns
        for pattern in section_patterns:
            matches = list(re.finditer(pattern, text, re.MULTILINE | re.UNICODE))
            for match in matches:
                start_pos = match.start()
                end_pos = match.end()
                
                # Check if the position is not already captured
                if not any(start_pos <= pos <= end_pos for pos in used_positions):
                    section_number = match.group(1)
                    section_content = match.group(2)
                    full_text = match.group(0).strip()
                    
                    section_info = {
                        'type': 'section',
                        'number': section_number,
                        'start_pos': start_pos,
                        'end_pos': end_pos
                    }
                    
                    all_sections.append((full_text, section_info))
                    
                    # Mark the range as captured
                    for pos in range(start_pos, end_pos + 1):
                        used_positions.add(pos)
        
        # If no sections found, simple split by paragraphs
        if not all_sections:
            paragraphs = text.split('\n\n')
            result = []
            for i, para in enumerate(paragraphs):
                if para.strip():
                    section_info = {'type': 'paragraph', 'number': str(i+1)}
                    result.append((para.strip(), section_info))
            return result if result else [(text, {'type': 'full_document'})]
        
        # Sort by position in the document
        all_sections.sort(key=lambda x: x[1]['start_pos'])
        
        # Remove duplicates by section number
        seen_numbers = set()
        unique_sections = []
        for section_text, section_info in all_sections:
            section_number = section_info.get('number', '')
            if section_number not in seen_numbers:
                seen_numbers.add(section_number)
                unique_sections.append((section_text, section_info))
        
        logger.info(f"Found {len(unique_sections)} identified sections: {[s[1].get('number') for s in unique_sections]}")
        
        return unique_sections

    def _identify_chapter(self, text: str, section_info: Dict) -> str:
        """Identify chapter from text"""
        chapter_patterns = [
            r'פרק\s+([א-ת]+|\d+)\s*[:\-]?\s*(.+?)(?:\n|$)',
            r'חלק\s+([א-ת]+|\d+)\s*[:\-]?\s*(.+?)(?:\n|$)'
        ]
        
        for pattern in chapter_patterns:
            match = re.search(pattern, text[:200], re.UNICODE)  # Search only at the beginning of the text
            if match:
                return f"פרק {match.group(1)} - {match.group(2).strip()}"
        
        return "לא זוהה פרק"

    def _estimate_token_count(self, text: str) -> int:
        """Estimate token count in Hebrew text"""
        # Rough estimate: 1 token per word in Hebrew according to the settings
        words = len(text.split())
        return int(words * self.performance_config.HEBREW_TOKEN_RATIO) 