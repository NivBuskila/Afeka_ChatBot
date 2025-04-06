export interface Translations {
  [key: string]: {
    he: string;
    en: string;
  };
}

export const translations: Translations = {
  // Menu Items
  'chatbot.preview': {
    he: 'תצוגה מקדימה של הצ\'אטבוט',
    en: 'Chatbot Preview'
  },
  'analytics': {
    he: 'סטטיסטיקה',
    en: 'Analytics'
  },
  'analytics.overview': {
    he: 'סקירה כללית',
    en: 'Overview'
  },
  'analytics.users': {
    he: 'משתמשים',
    en: 'Users'
  },
  'analytics.admins': {
    he: 'מנהלים',
    en: 'Administrators'
  },
  'documents': {
    he: 'בסיס הידע',
    en: 'Knowledge Base'
  },
  'documents.upload': {
    he: 'העלאת מסמכים',
    en: 'Upload Documents'
  },
  'documents.active': {
    he: 'מסמכים פעילים',
    en: 'Active Documents'
  },
  'settings': {
    he: 'הגדרות',
    en: 'Settings'
  },

  // Analytics
  'analytics.active.users': {
    he: 'משתמשים פעילים',
    en: 'Active Users'
  },
  'analytics.daily.conversations': {
    he: 'שיחות יומיות',
    en: 'Daily Conversations'
  },
  'analytics.active.documents': {
    he: 'מסמכים פעילים',
    en: 'Active Documents'
  },
  'analytics.avg.response': {
    he: 'זמן תגובה ממוצע',
    en: 'Average Response Time'
  },
  'analytics.week.change': {
    he: 'מהשבוע שעבר',
    en: 'from last week'
  },

  // Documents
  'documents.add': {
    he: 'הוספת מסמך',
    en: 'Add Document'
  },
  'documents.drag.drop': {
    he: 'גרור קבצים לכאן או לחץ לבחירת קבצים',
    en: 'Drag files here or click to select files'
  },
  'documents.select.files': {
    he: 'בחירת קבצים',
    en: 'Select Files'
  },
  'documents.search': {
    he: 'חיפוש מסמכים...',
    en: 'Search documents...'
  },
  'documents.all.categories': {
    he: 'כל הקטגוריות',
    en: 'All Categories'
  },
  'documents.status.active': {
    he: 'פעיל',
    en: 'Active'
  },
  'documents.status.archived': {
    he: 'בארכיון',
    en: 'Archived'
  },

  // Table Headers
  'table.document.name': {
    he: 'שם המסמך',
    en: 'Document Name'
  },
  'table.category': {
    he: 'קטגוריה',
    en: 'Category'
  },
  'table.upload.date': {
    he: 'תאריך העלאה',
    en: 'Upload Date'
  },
  'table.size': {
    he: 'גודל',
    en: 'Size'
  },
  'table.status': {
    he: 'סטטוס',
    en: 'Status'
  },
  'table.actions': {
    he: 'פעולות',
    en: 'Actions'
  },

  // Settings
  'settings.language': {
    he: 'שפת ברירת מחדל',
    en: 'Default Language'
  },
  'settings.language.he': {
    he: 'עברית',
    en: 'Hebrew'
  },
  'settings.language.en': {
    he: 'אנגלית',
    en: 'English'
  },

  // Header & Navigation
  'header.search': {
    he: 'חיפוש...',
    en: 'Search...'
  },
  'header.system.admin': {
    he: 'מנהל מערכת',
    en: 'System Admin'
  },
  'nav.logout': {
    he: 'התנתק',
    en: 'Logout'
  },
  'nav.apex.admin': {
    he: 'APEX ניהול',
    en: 'APEX Admin'
  },

  // Upload Modal
  'modal.upload.title': {
    he: 'העלאת מסמך חדש',
    en: 'Upload New Document'
  },
  'modal.upload.document.name': {
    he: 'שם המסמך',
    en: 'Document Name'
  },
  'modal.upload.category': {
    he: 'קטגוריה',
    en: 'Category'
  },
  'modal.upload.file': {
    he: 'קובץ',
    en: 'File'
  },
  'modal.upload.drag.file': {
    he: 'גרור קובץ לכאן או לחץ לבחירה',
    en: 'Drag a file here or click to select'
  },
  'modal.upload.select.file': {
    he: 'בחירת קובץ',
    en: 'Select File'
  },
  'modal.upload.cancel': {
    he: 'ביטול',
    en: 'Cancel'
  },
  'modal.upload.submit': {
    he: 'העלאה',
    en: 'Upload'
  },

  // Delete Modal
  'modal.delete.title': {
    he: 'אישור מחיקה',
    en: 'Confirm Delete'
  },
  'modal.delete.message': {
    he: 'האם אתה בטוח שברצונך למחוק מסמך זה? פעולה זו אינה הפיכה.',
    en: 'Are you sure you want to delete this document? This action cannot be undone.'
  },
  'modal.delete.cancel': {
    he: 'ביטול',
    en: 'Cancel'
  },
  'modal.delete.confirm': {
    he: 'מחיקה',
    en: 'Delete'
  },

  // Categories
  'category.regulations': {
    he: 'תקנונים',
    en: 'Regulations'
  },
  'category.guides': {
    he: 'מדריכים',
    en: 'Guides'
  },
  'category.schedules': {
    he: 'לוחות זמנים',
    en: 'Schedules'
  },

  // צ'אטבוט
  'chatbot.name': {
    he: 'APEX צ\'אטבוט',
    en: 'APEX Chatbot'
  },
  'chatbot.status': {
    he: 'מחובר',
    en: 'Connected'
  },
  'chatbot.welcome': {
    he: 'שלום! אני APEX צ\'אטבוט, כיצד אוכל לעזור לך היום?',
    en: 'Hello! I\'m APEX Chatbot, how can I help you today?'
  },
  'chatbot.input.placeholder': {
    he: 'הקלד הודעה...',
    en: 'Type a message...'
  },
  'chatbot.demo.user.message': {
    he: 'היי! אני רוצה לדעת מה שעות הפתיחה של הספרייה',
    en: 'Hi! I want to know the library opening hours'
  },
  'chatbot.demo.bot.response': {
    he: 'הספרייה פתוחה בימים א\'-ה\' בין השעות 08:00-20:00, ובימי ו\' בין השעות 08:00-13:00. בתקופת מבחנים יש שעות פתיחה מורחבות.',
    en: 'The library is open Sunday-Thursday from 08:00-20:00, and Friday from 08:00-13:00. During exam periods there are extended opening hours.'
  }
}; 