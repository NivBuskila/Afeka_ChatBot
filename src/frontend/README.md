# Afeka ChatBot

מערכת ניהול מסמכים עם תמיכה בצ'אטבוט חכם.

## התקנה

1. התקן את החבילות הנדרשות:

```bash
npm install
```

2. צור קובץ `.env` בהתבסס על `.env.example`:

```bash
cp .env.example .env
```

3. עדכן את משתני הסביבה בקובץ `.env` עם הפרטים שלך מ-Supabase:

- `REACT_APP_SUPABASE_URL`: כתובת ה-URL של פרויקט Supabase שלך
- `REACT_APP_SUPABASE_ANON_KEY`: מפתח האנונימי של פרויקט Supabase שלך

## פיתוח

הפעל את השרת המקומי:

```bash
npm start
```

האפליקציה תהיה זמינה בכתובת [http://localhost:3000](http://localhost:3000).

## בנייה

בנה את האפליקציה לייצור:

```bash
npm run build
```

## מבנה הפרויקט

```
src/
  ├── components/         # קומפוננטות React
  │   ├── Dashboard/     # קומפוננטות לוח הבקרה
  │   └── Chat/          # קומפוננטות צ'אט
  ├── config/            # קבצי תצורה
  ├── i18n/              # קבצי תרגום
  ├── services/          # שירותים
  └── types/             # הגדרות טיפוסים
```

## טכנולוגיות

- React
- TypeScript
- Tailwind CSS
- Supabase
- i18next
- React Dropzone

## תכונות

- ניהול מסמכים (העלאה, הורדה, מחיקה)
- סטטיסטיקות שימוש
- תמיכה בשפות (עברית ואנגלית)
- ממשק משתמש מודרני ומותאם למובייל
- אבטחה עם Supabase
