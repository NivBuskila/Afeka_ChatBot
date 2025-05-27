#!/usr/bin/env python
"""
סקריפט הפעלה לשרת הRAG

הסקריפט בודק שכל המשתנים הסביבתיים הנדרשים קיימים, 
ואז מפעיל את השרת בצורה נכונה
"""

import os
import sys
import dotenv
import subprocess
import logging
from pathlib import Path

# הגדרת לוגר
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_environment():
    """בדיקת משתני סביבה הכרחיים"""
    dotenv.load_dotenv(override=True)
    
    required_vars = {
        "SUPABASE_URL": "כתובת שרת Supabase",
        "SUPABASE_KEY": "מפתח API של Supabase (או SUPABASE_SERVICE_KEY)",
        "GEMINI_API_KEY": "מפתח API של Gemini"
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var) and not (var == "SUPABASE_KEY" and os.getenv("SUPABASE_SERVICE_KEY")):
            missing_vars.append(f"{var} ({description})")
    
    if missing_vars:
        logger.error("חסרים משתני סביבה הכרחיים:")
        for var in missing_vars:
            logger.error(f"  - {var}")
        logger.error("אנא וודא שקובץ .env מכיל את כל המשתנים הנדרשים")
        return False
    
    # בדיקה נוספת למפתח Gemini
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        logger.info(f"GEMINI_API_KEY נמצא (אורך: {len(gemini_key)})")
    
    return True

def run_server():
    """הפעלת השרת"""
    logger.info("מפעיל את שרת RAG...")
    
    # מציאת הנתיב הנכון
    backend_dir = Path(__file__).parent.resolve()
    
    # שינוי ספרייה לתיקיית הבקאנד
    os.chdir(backend_dir)
    
    # הפעלת השרת
    cmd = ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
    logger.info(f"מריץ פקודה: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        logger.info("השרת הופסק ידנית")
    except Exception as e:
        logger.error(f"שגיאה בהפעלת השרת: {str(e)}")

def main():
    """פונקציה ראשית"""
    logger.info("בדיקת הגדרות סביבה...")
    
    if not check_environment():
        logger.error("לא ניתן להפעיל את השרת בגלל בעיות בהגדרות הסביבה")
        sys.exit(1)
    
    logger.info("הגדרות הסביבה תקינות")
    run_server()

if __name__ == "__main__":
    main() 