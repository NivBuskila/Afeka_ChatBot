#!/usr/bin/env python
"""
סקריפט הפעלה ראשי למערכת RAG

סקריפט זה מנתב לסקריפט ההפעלה בספריית הבקאנד
ומאפשר להפעיל את המערכת בקלות מתיקיית השורש של הפרויקט.
"""

import os
import sys
import importlib.util
from pathlib import Path

def main():
    """פונקציה ראשית"""
    # בדיקה שאנחנו בתיקייה הנכונה
    project_root = Path(__file__).parent.resolve()
    
    # בדיקה שתיקיית הבקאנד קיימת
    backend_dir = project_root / "src" / "backend"
    if not backend_dir.exists() or not backend_dir.is_dir():
        print("שגיאה: לא נמצאה תיקיית הבקאנד בנתיב", backend_dir)
        sys.exit(1)
    
    # בדיקה שקובץ הסקריפט קיים
    server_script = backend_dir / "run_server.py"
    if not server_script.exists():
        print("שגיאה: לא נמצא סקריפט ההפעלה בנתיב", server_script)
        sys.exit(1)
    
    # טעינה והרצה של הסקריפט
    try:
        print(f"מפעיל את שרת RAG מתיקיית {backend_dir}...")
        
        # שינוי הספרייה הנוכחית לתיקיית הבקאנד
        os.chdir(backend_dir)
        
        # הרצת הסקריפט
        sys.path.insert(0, str(backend_dir))
        spec = importlib.util.spec_from_file_location("run_server", server_script)
        server_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(server_module)
        server_module.main()
        
    except KeyboardInterrupt:
        print("\nהשרת הופסק ידנית")
    except Exception as e:
        print(f"שגיאה בהפעלת השרת: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 