# מדריך למפתחים: אינטגרציית Gemini API עם צ'אטבוט AFEKA

מדריך זה מסביר כיצד להגדיר ולהפעיל את מערכת הצ'אטבוט עם אינטגרציית Gemini API.

## דרישות מקדימות

1. **Python 3.9+** מותקן במערכת
2. **Node.js** מותקן במערכת (עבור הפרונטאנד)
3. **Git** מותקן במערכת

## הורדת הקוד מ-GitHub

```bash
git clone https://github.com/NivBuskila/Afeka_ChatBot.git
cd Afeka_ChatBot
git checkout Omri's  # החלף לענף עם האינטגרציה של Gemini
```

## הגדרת API Key של Gemini

יש שתי דרכים להגדיר את מפתח ה-API:

### 1. באמצעות קובץ `.env`

העתק את קובץ `.env.example` ל-`.env` והוסף את מפתח ה-API:

```bash
cp .env.example .env
```

ערוך את הקובץ `.env` והגדר את מפתח ה-API:

```
# AI Configuration
GEMINI_API_KEY=YOUR_API_KEY_HERE
```

### 2. באמצעות משתנה סביבה

**Windows**:

```
set GEMINI_API_KEY=YOUR_API_KEY_HERE
```

**Linux/Mac**:

```
export GEMINI_API_KEY=YOUR_API_KEY_HERE
```

## אפשרויות הפעלה

הפרויקט כולל מספר סקריפטי הפעלה לנוחותך:

### 1. הפעלת המערכת המלאה (פרונטאנד + AI)

הדרך הקלה ביותר להפעיל את המערכת המלאה היא באמצעות הסקריפט:

```
run_frontend.bat  # Windows בלבד
```

סקריפט זה:

- מתקין את כל התלויות הנדרשות
- מפעיל את שירות ה-AI
- מפעיל את הפרונטאנד
- מגדיר את הפרוקסי המתאים

### 2. הפעלת ממשק צ'אט גרפי עצמאי

אם אתה רוצה רק לבדוק את ה-AI ללא הפרונטאנד המלא:

```
run_chat_gui.bat  # Windows בלבד
```

סקריפט זה מפעיל ממשק גרפי פשוט בסיסי שמדבר ישירות עם Gemini API.

### 3. הפעלה ידנית

#### הפעלת שירות ה-AI:

```bash
cd src/ai
pip install -r requirements.txt
pip install google-genai  # אם לא מותקן עדיין
python app.py
```

#### הפעלת הפרונטאנד:

```bash
cd src/frontend
npm install
npm run dev
```

## איך לבדוק שהכל עובד

1. גש לכתובת `http://localhost:5173` בדפדפן
2. התחבר עם פרטי המשתמש (שאל את מנהל המערכת)
3. נווט לעמוד הצ'אט
4. שלח הודעה ובדוק שאתה מקבל תשובה מ-Gemini API

## פתרון בעיות נפוצות

### שגיאת 404 ב-API endpoint

בדוק שהפרוקסי מוגדר נכון בקובץ `vite.config.ts`:

```javascript
proxy: {
  '/api/chat': {
    target: 'http://localhost:5000',
    changeOrigin: true,
    rewrite: (path) => path.replace(/^\/api\/chat/, '/chat')
  }
}
```

### שגיאת API Key לא תקין

ודא שמפתח ה-API שהוגדר הוא תקין ומעודכן. אם השתנה, יש לעדכן אותו בקובץ `.env`.

### בעיית חיבור ל-Gemini API

ודא שיש חיבור אינטרנט ושמגבלות האש (Firewall) לא חוסמות את הגישה ל-API.

## למפתחים מתקדמים: התאמות נוספות

### שינוי מודל Gemini בשימוש

ניתן לשנות את המודל הנמצא בשימוש בקובץ `src/ai/app.py`:

```python
model = "gemini-2.0-flash"  # אפשרויות אחרות: "gemini-1.5-pro", "gemini-1.0-pro", וכו'
```

### התאמת פרמטרי תצוגה

ניתן לשנות את גודל הגופן והצבעים בממשק הצ'אט הגרפי בקובץ `src/ai/simple_chat.py`.

### עבודה עם דוקר

אם ברצונך להפעיל את המערכת עם דוקר:

```bash
docker-compose up --build
```

## משימות עתידיות

הפרויקט הנוכחי הוא אב-טיפוס. להמשך הפיתוח מתוכננות המשימות הבאות:

1. מימוש RAG מלא (Retrieval Augmented Generation)
2. חיבור למסד נתונים לאחסון המסמכים
3. הרחבת ממשק המנהל לניהול מסמכים
4. שיפור ממשק המשתמש וחוויית הצ'אט

---

לשאלות נוספות, ניתן לפנות לעמרי או לעיין בקוד המקור.
