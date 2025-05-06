import requests
import json
import re

def extract_section_metadata(section_content):
    """
    Extract metadata about a section, including its number and level.
    
    Args:
        section_content: Text content of the section
        
    Returns:
        Dictionary with metadata
    """
    # Try to extract section numbers (like 4.3, 5.1, etc.)
    section_pattern = re.compile(r'^\s*#+\s*([\d\.]+)\s*(.*?)$', re.MULTILINE)
    match = section_pattern.search(section_content)
    
    if match:
        section_number = match.group(1)
        section_title = match.group(2).strip()
        level = len(section_number.split('.'))
        return {
            "section_number": section_number,
            "section_title": section_title,
            "section_level": level
        }
    return {}

url = 'http://localhost:5000/api/documents/load'
headers = {'Content-Type': 'application/json'}

# הגדרות מטא-דאטה משופרות למסמך התקנון
metadata = {
    'source': 'מסמך תקנון אפקה הרשמי',
    'title': 'תקנון אפקה',
    'doc_type': 'תקנון',
    'category': 'אקדמי',
    'audience': 'סטודנטים',
    'language': 'he',  # Hebrew language code
    'description': 'תקנון מכללת אפקה להנדסה שמפרט את הכללים, הזכויות והחובות של סטודנטים במכללה',
    'keywords': 'תקנון, זכויות סטודנטים, חובות סטודנטים, בחינות, מבחנים, מועדי בחינה, ערעורים, מועד מיוחד, השלמות, נוכחות, משמעת'
}

data = {
    'file_path': 'data/docs/afeka_takanon.txt',
    'metadata': metadata,
    'chunk_size': 500,  # smaller chunks for better retrieval of specific sections
    'chunk_overlap': 100,  # sufficient overlap to maintain context
    'extract_section_metadata': True  # Use this flag to signal our special metadata extraction
}

response = requests.post(url, json=data)
print(response.status_code)
print(response.text) 