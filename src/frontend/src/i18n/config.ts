import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

const resources = {
  he: {
    translation: {
      // Hebrew translations
      common: {
        search: 'חיפוש',
        filter: 'סינון',
        add: 'הוספה',
        edit: 'עריכה',
        delete: 'מחיקה',
        save: 'שמירה',
        cancel: 'ביטול',
        close: 'סגירה',
        upload: 'העלאה',
        download: 'הורדה',
        language: 'שפה',
        submit: 'שליחה',
        loading: 'טוען...',
        success: 'הצלחה!',
        error: 'שגיאה',
        confirm: 'אישור',
        yes: 'כן',
        no: 'לא',
      },
      analytics: {
        title: 'ניתוח נתונים',
        overview: 'סקירה כללית',
        users: 'משתמשים',
        documents: 'מסמכים',
        questions: 'שאלות',
        activeUsers: 'משתמשים פעילים',
        activeAdmins: 'מנהלים פעילים',
        totalAdmins: 'סך הכל מנהלים',
        activeDocuments: 'מסמכים פעילים',
        knowledgeBase: 'מאגר ידע',
        usersOverTime: 'משתמשים לאורך זמן',
        documentsOverTime: 'מסמכים לאורך זמן',
        questionsOverTime: 'שאלות לאורך זמן',
        totalUsers: 'סך משתמשים',
        totalDocuments: 'סך מסמכים',
        totalQuestions: 'סך שאלות',
      },
      documents: {
        title: 'ניהול מסמכים',
        upload: 'העלאת מסמכים',
        manage: 'ניהול מסמכים',
        add: 'הוספת מסמך',
        edit: 'עריכת מסמך',
        delete: 'מחיקת מסמך',
        name: 'שם מסמך',
        type: 'סוג מסמך',
        size: 'גודל מסמך',
        date: 'תאריך העלאה',
        actions: 'פעולות',
        uploadSuccess: 'המסמך הועלה בהצלחה',
        uploadError: 'שגיאה בהעלאת המסמך',
        deleteSuccess: 'המסמך נמחק בהצלחה',
        deleteError: 'שגיאה במחיקת המסמך',
        confirmDelete: 'האם אתה בטוח שברצונך למחוק מסמך זה?',
        activeDocuments: 'מסמכים פעילים',
        uploadInstructions: 'גרור ושחרר קבצים כאן, או לחץ לבחירת קבצים',
        supportedFormats: 'פורמטים נתמכים: PDF, DOCX, TXT',
        dropHere: 'שחרר כאן',
        supportedTypes: 'סוגי קבצים נתמכים',
        search: 'חיפוש מסמכים...',
      },
      admin: {
        sidebar: {
          title: 'לוח בקרה',
          dashboard: 'לוח בקרה',
          analytics: 'ניתוח נתונים',
          overview: 'סקירה כללית',
          users: 'משתמשים',
          administrators: 'מנהלים',
          knowledgeBase: 'מאגר ידע',
          uploadDocuments: 'העלאת מסמכים',
          activeDocuments: 'מסמכים פעילים',
          settings: 'הגדרות',
          logout: 'התנתקות',
          chatbotPreview: 'תצוגת צ׳אטבוט',
        },
        topbar: {
          activeDocuments: 'מסמכים פעילים',
          notifications: 'התראות',
        }
      },
      auth: {
        login: 'התחברות',
        register: 'הרשמה',
        email: 'דואר אלקטרוני',
        password: 'סיסמה',
        forgotPassword: 'שכחת סיסמה?',
        loginSuccess: 'התחברת בהצלחה',
        loginError: 'שגיאה בהתחברות',
        registerSuccess: 'נרשמת בהצלחה',
        registerError: 'שגיאה בהרשמה',
      },
      settings: {
        title: 'הגדרות',
        profile: 'פרופיל',
        account: 'חשבון',
        notifications: 'התראות',
        language: 'שפה',
        'language.he': 'עברית',
        'language.en': 'אנגלית',
        theme: 'ערכת נושא',
        'theme.light': 'בהיר',
        'theme.dark': 'כהה',
      },
    }
  },
  en: {
    translation: {
      common: {
        search: 'Search',
        filter: 'Filter',
        add: 'Add',
        edit: 'Edit',
        delete: 'Delete',
        save: 'Save',
        cancel: 'Cancel',
        close: 'Close',
        upload: 'Upload',
        download: 'Download',
        language: 'Language',
        submit: 'Submit',
        loading: 'Loading...',
        success: 'Success!',
        error: 'Error',
        confirm: 'Confirm',
        yes: 'Yes',
        no: 'No',
      },
      analytics: {
        title: 'Analytics',
        overview: 'Overview',
        users: 'Users',
        documents: 'Documents',
        questions: 'Questions',
        activeUsers: 'Active Users',
        activeAdmins: 'Active Administrators',
        totalAdmins: 'Total Administrators',
        activeDocuments: 'Active Documents',
        knowledgeBase: 'Knowledge Base',
        usersOverTime: 'Users Over Time',
        documentsOverTime: 'Documents Over Time',
        questionsOverTime: 'Questions Over Time',
        totalUsers: 'Total Users',
        totalDocuments: 'Total Documents',
        totalQuestions: 'Total Questions',
      },
      documents: {
        title: 'Document Management',
        upload: 'Upload Documents',
        manage: 'Manage Documents',
        add: 'Add Document',
        edit: 'Edit Document',
        delete: 'Delete Document',
        name: 'Document Name',
        type: 'Document Type',
        size: 'Document Size',
        date: 'Upload Date',
        actions: 'Actions',
        uploadSuccess: 'Document uploaded successfully',
        uploadError: 'Error uploading document',
        deleteSuccess: 'Document deleted successfully',
        deleteError: 'Error deleting document',
        confirmDelete: 'Are you sure you want to delete this document?',
        activeDocuments: 'Active Documents',
        uploadInstructions: 'Drag and drop files here, or click to select files',
        supportedFormats: 'Supported formats: PDF, DOCX, TXT',
        dropHere: 'Drop here',
        supportedTypes: 'Supported File Types',
        search: 'Search For Documents...',
      },
      admin: {
        sidebar: {
          title: 'Dashboard',
          dashboard: 'Dashboard',
          analytics: 'Analytics',
          overview: 'Overview',
          users: 'Users',
          administrators: 'Administrators',
          knowledgeBase: 'Knowledge Base',
          uploadDocuments: 'Upload Documents',
          activeDocuments: 'Active Documents',
          settings: 'Settings',
          logout: 'Logout',
          chatbotPreview: 'Chatbot Preview',
        },
        topbar: {
          activeDocuments: 'Active Documents',
          notifications: 'Notifications',
        }
      },
      auth: {
        login: 'Login',
        register: 'Register',
        email: 'Email',
        password: 'Password',
        forgotPassword: 'Forgot Password?',
        loginSuccess: 'Logged in successfully',
        loginError: 'Error logging in',
        registerSuccess: 'Registered successfully',
        registerError: 'Error registering',
      },
      settings: {
        title: 'Settings',
        profile: 'Profile',
        account: 'Account',
        notifications: 'Notifications',
        language: 'Language',
        'language.he': 'Hebrew',
        'language.en': 'English',
        theme: 'Theme',
        'theme.light': 'Light',
        'theme.dark': 'Dark',
      },
    }
  }
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: document.documentElement.lang === 'he' ? 'he' : 'en', // Use document language if specified, otherwise default to en
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false
    }
  });

export const changeLanguage = (lang: 'he' | 'en') => {
  i18n.changeLanguage(lang);
  document.documentElement.lang = lang;
  document.documentElement.dir = lang === 'he' ? 'rtl' : 'ltr';
};

export default i18n; 