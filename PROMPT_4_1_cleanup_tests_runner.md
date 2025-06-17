# פרומט 4.1: ניקוי src/tests/backend/tests_runner.py

## מטרה

המרת print statements לשימוש ב-logger וניקוי הדפסות מיותרות.

## שינויים נדרשים:

### 1. הוספת logger בראש הקובץ:

```python
import logging
logger = logging.getLogger(__name__)
```

### 2. החלפת print statements עיקריים ב-logger:

החלף print statements אלה ב-logger:

- שורות 190-192: סיכום תוצאות → `logger.info`
- שורות 221-222: ניתוח failures → `logger.warning`
- שורות 293-313: סטטיסטיקות כלליות → `logger.info`
- שורות 357-362: התחלת test suite → `logger.info`

### 3. הסרת print statements של formatting:

הסר print statements אלה (קווי חלוקה וקישוטים):

- `print("=" * 80)`
- `print("-" * 50)`
- `print("🔍 FAILURE ANALYSIS SUMMARY")`
- וכל ההדפסות עם emoji וקווי חלוקה

### 4. שמירת print statements חיוניים:

שמור רק:

- שורות 328-344: רשימת test suites זמינים (זה מועיל למשתמש)
- שורות 383: הרצת pytest (זה מועיל לדיבוג)

### 5. החלפת structured output:

במקום הדפסות מפורטות, צור structured output:

```python
def print_summary(self):
    """Print a clean summary of test results"""
    total = self.total_stats.get('total', 0)
    if total == 0:
        print("No tests were run")
        return

    passed = self.total_stats.get('passed', 0)
    failed = self.total_stats.get('failed', 0)

    print(f"Tests: {passed}/{total} passed, {failed} failed")
    if failed > 0:
        print("Failed tests:")
        for failure in self.failed_tests_details:
            print(f"  - {failure['test_name']}: {failure['failure_reason']}")
```

## אחרי השינויים:

- פחות noise בלוגים
- שימוש נכון ב-logger במקום print
- output נקי ומובנה
- שמירה על מידע חיוני למשתמש
