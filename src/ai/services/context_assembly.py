"""
מודול בניית קונטקסט מתקדם (Advanced Context Assembly) לתקנוני מכללה
מממש את השלב הרביעי בתוכנית האסטרטגית: Context Assembly מתקדם
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, date
import re
from .retrieval import SearchResult, ContextBundle

logger = logging.getLogger(__name__)

@dataclass
class PromptTemplate:

    background_info: str
    hierarchical_context: str
    main_content: str
    additional_info: str
    cross_references: str
    instructions: str
    question: str

class ContextBuilder:
    """בונה קונטקסט חכם ומותאם לתקנוני מכללה"""
    
    def __init__(self):
        # Temporal settings
        self.current_academic_year = "2024-2025"
        self.current_semester = "ב'"
        self.current_date = date.today().strftime("%d/%m/%Y")

    def build_advanced_context(self, 
                             context_bundle: ContextBundle, 
                             query: str,
                             query_type: str = 'general',
                             max_context_length: int = 4000) -> PromptTemplate:
        
        logger.info(f"Building advanced context for query type: {query_type}")
        
        background_info = self._build_background_info(context_bundle, query_type)
        
        hierarchical_context = self._build_hierarchical_context(context_bundle)
        
        main_content = self._build_main_content(context_bundle)
        
        additional_info = self._build_additional_info(context_bundle)
        
        cross_references = self._build_cross_references(context_bundle)
        
        instructions = self._build_instructions(query_type, query)
        
        total_length = (len(background_info) + len(hierarchical_context) + 
                       len(main_content) + len(additional_info) + 
                       len(cross_references) + len(instructions) + len(query))
        
        if total_length > max_context_length:
            logger.warning(f"Context too long ({total_length} characters), trimming...")
            background_info, main_content, additional_info = self._trim_context(
                background_info, main_content, additional_info, max_context_length - 1000
            )
        
        prompt_template = PromptTemplate(
            background_info=background_info,
            hierarchical_context=hierarchical_context,
            main_content=main_content,
            additional_info=additional_info,
            cross_references=cross_references,
            instructions=instructions,
            question=query
        )
        
        logger.info(f"Context built successfully: {total_length} characters")
        return prompt_template

    def _build_background_info(self, context_bundle: ContextBundle, query_type: str) -> str:
        background_parts = []
        
        if context_bundle.definition_context:
            background_parts.append("הגדרות רלוונטיות:")
            for def_result in context_bundle.definition_context[:3]:
                background_parts.append(f"• {def_result.chunk_text[:200]}...")
        
        # Temporal information
        if query_type == 'temporal':
            background_parts.append(f"מידע זמני עדכני:")
            background_parts.append(f"• שנת לימודים נוכחית: {self.current_academic_year}")
            background_parts.append(f"• סמסטר נוכחי: {self.current_semester}")
            background_parts.append(f"• תאריך נוכחי: {self.current_date}")
        
        return "\n".join(background_parts) if background_parts else ""

    def _build_hierarchical_context(self, context_bundle: ContextBundle) -> str:
        if not context_bundle.main_result.hierarchical_path:
            return ""
        
        hierarchy_parts = []
        hierarchy_parts.append("הקשר היררכי:")
        
        # Hierarchical path
        path = context_bundle.main_result.hierarchical_path
        hierarchy_parts.append(f"מיקום: {path}")
        
        # Upper section context
        if context_bundle.hierarchical_context:
            hierarchy_parts.append("\nהקשר מפרק עליון:")
            for ctx_result in context_bundle.hierarchical_context[:2]:
                hierarchy_parts.append(f"- {ctx_result.section_number}: {ctx_result.section_title}")
        
        return "\n".join(hierarchy_parts)

    def _build_main_content(self, context_bundle: ContextBundle) -> str:
        main_parts = []
        main_result = context_bundle.main_result
        
        main_parts.append("התוכן הרלוונטי:")
        
        # Section title
        if main_result.section_number and main_result.section_title:
            main_parts.append(f"סעיף {main_result.section_number}: {main_result.section_title}")
        
        # Main content
        main_parts.append(main_result.chunk_text)
        
        # Related subsections
        if context_bundle.related_subsections:
            main_parts.append("\nתתי-סעיפים קשורים:")
            for sub_result in context_bundle.related_subsections[:3]:
                if sub_result.section_number:
                    main_parts.append(f"\nסעיף {sub_result.section_number}:")
                main_parts.append(sub_result.chunk_text[:300] + "..." if len(sub_result.chunk_text) > 300 else sub_result.chunk_text)
        
        return "\n".join(main_parts)

    def _build_additional_info(self, context_bundle: ContextBundle) -> str:
        if not context_bundle.cross_referenced_content:
            return ""
        
        additional_parts = []
        additional_parts.append("מידע נוסף קשור:")
        
        for ref_result in context_bundle.cross_referenced_content[:3]:
            if ref_result.section_number:
                additional_parts.append(f"\nמסעיף {ref_result.section_number}:")
            additional_parts.append(ref_result.chunk_text[:250] + "..." if len(ref_result.chunk_text) > 250 else ref_result.chunk_text)
        
        return "\n".join(additional_parts)

    def _build_cross_references(self, context_bundle: ContextBundle) -> str:
        cross_refs = context_bundle.main_result.cross_references
        if not cross_refs:
            return ""
        
        ref_parts = []
        ref_parts.append("הפניות צולבות:")
        
        for ref in cross_refs[:5]:
            ref_parts.append(f"• ראה גם סעיף {ref}")
        
        return "\n".join(ref_parts)

    def _build_instructions(self, query_type: str, query: str) -> str:
        base_instructions = [
            "הוראות למענה:",
            "1. ענה בהתבסס על התקנון בלבד - אל תוסיף מידע חיצוני",
            "2. צטט מספרי סעיפים רלוונטיים בתשובתך",
            "3. אם יש תנאים או מועדים, ציין אותם במדויק",
            "4. אם המידע לא מלא או לא ברור, ציין זאת במפורש",
            "5. השתמש בשפה ברורה ומקצועית"
        ]
        
        # Specific instructions for query type
        if query_type == 'temporal':
            base_instructions.extend([
                "6. לשאלות זמניות: ציין בבירור מועדים ותאריכים",
                "7. אם יש התייחסות לשנת לימודים, הזכר שמדובר בתקנון הנוכחי"
            ])
        elif query_type == 'procedural':
            base_instructions.extend([
                "6. לתהליכים: פרט את השלבים בסדר הנכון",
                "7. ציין גורמים אחראיים ומועדים לכל שלב"
            ])
        elif query_type == 'definitional':
            base_instructions.extend([
                "6. להגדרות: תן הגדרה מדויקת וברורה",
                "7. אם יש דוגמאות בתקנון, כלול אותן"
            ])
        elif query_type == 'comparative':
            base_instructions.extend([
                "6. להשוואות: ציין בבירור את ההבדלים והדמיון",
                "7. השתמש בטבלה או רשימה אם מתאים"
            ])
        
        return "\n".join(base_instructions)

    def _trim_context(self, background: str, main: str, additional: str, max_length: int) -> Tuple[str, str, str]:
        """Trim context when it's too long"""
        
        # Preferences: main_content > background > additional
        if len(main) > max_length * 0.6:
            main = main[:int(max_length * 0.6)] + "..."
        
        remaining_length = max_length - len(main)
        
        if len(background) > remaining_length * 0.6:
            background = background[:int(remaining_length * 0.6)] + "..."
        
        remaining_length -= len(background)
        
        if len(additional) > remaining_length:
            additional = additional[:remaining_length] + "..." if remaining_length > 50 else ""
        
        return background, main, additional

    def format_final_prompt(self, template: PromptTemplate) -> str:
        prompt_parts = []
        
        if template.background_info:
            prompt_parts.append(template.background_info)
            prompt_parts.append("")
        
        if template.hierarchical_context:
            prompt_parts.append(template.hierarchical_context)
            prompt_parts.append("")
        
        prompt_parts.append(template.main_content)
        prompt_parts.append("")
        
        if template.additional_info:
            prompt_parts.append(template.additional_info)
            prompt_parts.append("")
        
        if template.cross_references:
            prompt_parts.append(template.cross_references)
            prompt_parts.append("")
        
        prompt_parts.append(template.instructions)
        prompt_parts.append("")
        prompt_parts.append(f"שאלת המשתמש: {template.question}")
        
        return "\n".join(prompt_parts) 