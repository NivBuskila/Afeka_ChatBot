import requests
import json
import os

# וודא שהתיקייה הנוכחית היא התיקייה הנכונה
current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)

url = 'http://localhost:5000/api/documents/load'
headers = {'Content-Type': 'application/json'}

# הגדרות מטא-דאטה למסמך נוהל המילואים
metadata = {
    'source': 'נוהל זכויות סטודנטים המשרתים במילואים',
    'title': 'נוהל זכויות סטודנטים במילואים',
    'doc_type': 'נוהל',
    'category': 'מילואים',
    'audience': 'סטודנטים',
    'language': 'he',  # Hebrew language code
    'description': 'נוהל זכויות סטודנטים המשרתים במילואים המפרט את ההקלות וההטבות לסטודנטים',
    'keywords': 'מילואים, זכויות סטודנטים, הקלות, התאמות, בחינות, מועד מיוחד, נוכחות, היעדרות'
}

# מיקום קובץ המילואים (הנתיב המוחלט לקובץ)
miluim_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))), 'נוהל-זכויות-סטודנטים-המשרתים-בשירות-מילואיםcleaned.pdf')

# וודא שהקובץ קיים
if not os.path.exists(miluim_file_path):
    print(f"הקובץ לא נמצא בנתיב: {miluim_file_path}")
    # נסה למצוא את הקובץ בנתיב אחר
    miluim_file_path = "C:/Users/omti9/Afeka_ChatBot/נוהל-זכויות-סטודנטים-המשרתים-בשירות-מילואיםcleaned.pdf"
    if not os.path.exists(miluim_file_path):
        print(f"הקובץ לא נמצא גם בנתיב: {miluim_file_path}")
        exit(1)
    else:
        print(f"הקובץ נמצא בנתיב: {miluim_file_path}")
else:
    print(f"הקובץ נמצא בנתיב: {miluim_file_path}")

data = {
    'file_path': miluim_file_path,
    'metadata': metadata,
    'chunk_size': 500,  # קטעים קטנים לשיפור החיפוש
    'chunk_overlap': 100,  # חפיפה מספקת לשמירה על הקשר
    'extract_section_metadata': True  # חילוץ מטא-דאטה של סעיפים
}

response = requests.post(url, json=data)
print(response.status_code)
print(response.text) 