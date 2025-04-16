import { supabase, Database } from '../config/supabase';
import { cacheService } from './cacheService';

type Document = Database['public']['Tables']['documents']['Row'];
type DocumentInsert = Database['public']['Tables']['documents']['Insert'];
type DocumentUpdate = Database['public']['Tables']['documents']['Update'];

export const documentService = {
  async getAllDocuments() {
    // Check if we should bust cache
    const isCacheStale = cacheService.isCacheStale('documents', 30000); // 30 seconds
    
    // Use cache busting query parameter if cache is stale
    const cacheBuster = isCacheStale ? `?cache=${Date.now()}` : '';
    
    const { data, error } = await supabase
      .from('documents')
      .select('*')
      .order('created_at', { ascending: false });

    if (error) throw error;
    return data;
  },

  async getDocumentById(id: number) {
    const { data, error } = await supabase
      .from('documents')
      .select('*')
      .eq('id', id)
      .single();

    if (error) throw error;
    return data;
  },

  async createDocument(document: DocumentInsert) {
    const { data, error } = await supabase
      .rpc('create_document', {
        name: document.name,
        type: document.type,
        size: document.size,
        url: document.url,
        user_id: (await supabase.auth.getUser()).data.user?.id
      });

    if (error) throw error;
    
    const { data: newDoc, error: fetchError } = await supabase
      .from('documents')
      .select('*')
      .eq('id', data)
      .single();
      
    if (fetchError) throw fetchError;
    return newDoc;
  },

  async updateDocument(id: number, updates: DocumentUpdate) {
    const { data, error } = await supabase
      .from('documents')
      .update(updates)
      .eq('id', id)
      .select()
      .single();

    if (error) throw error;
    return data;
  },

  async deleteDocument(id: number) {
    // Get document info before deletion to make sure we have the URL
    const { data: document, error: fetchError } = await supabase
      .from('documents')
      .select('*')
      .eq('id', id)
      .single();
      
    if (fetchError) {
      console.error('Error fetching document before deletion:', fetchError);
      throw fetchError;
    }
    
    // Extract storage path from URL
    let storageFullPath = null;
    let storageBucketPath = null;
    
    try {
      console.log('Document URL:', document.url);
      
      // הוצאת שם הקובץ בכמה דרכים אפשריות
      // שיטה 1: חיפוש בתבנית URL מלאה
      const urlRegex = /\/storage\/v1\/object\/(?:public\/)?([^?]+)/;
      const match = document.url.match(urlRegex);
      
      if (match && match[1]) {
        // מסלול מלא שכולל את שם הדלי והקובץ
        storageFullPath = match[1];
        
        // חילוץ רק את החלק הפנימי (אחרי שם הדלי)
        const pathParts = storageFullPath.split('/');
        if (pathParts.length > 1) {
          // הדלי הוא החלק הראשון, שאר הנתיב הוא מה שאנחנו צריכים
          const bucketName = pathParts[0];
          storageBucketPath = storageFullPath.substring(bucketName.length + 1);
        } else {
          // רק שם קובץ ללא תיקיות
          storageBucketPath = storageFullPath;
        }
      } else {
        // שיטה 2: חילוץ רק שם הקובץ
        const parts = document.url.split('/');
        const filename = parts[parts.length - 1].split('?')[0];
        storageBucketPath = filename;
        storageFullPath = `documents/${filename}`;
      }
      
      console.log('Storage paths:', { 
        fullPath: storageFullPath,
        bucketPath: storageBucketPath
      });
    } catch (e) {
      console.warn('Could not extract storage path from URL:', document.url, e);
    }
    
    // Delete the document record from the database
    const { error } = await supabase
      .from('documents')
      .delete()
      .eq('id', id);

    if (error) {
      console.error('Error deleting document record:', error);
      throw error;
    }
    
    // מחיקת הקובץ מהאחסון - ננסה כמה שיטות
    let storageDeleteSuccess = false;
    
    // שיטה 1: מחיקה לפי הנתיב המלא (אם יש)
    if (storageBucketPath) {
      try {
        console.log('Attempting to delete by direct path:', storageBucketPath);
        const { error: storageError } = await supabase.storage
          .from('documents')
          .remove([storageBucketPath]);
          
        if (storageError) {
          console.warn('Method 1 - Could not delete file:', storageError);
        } else {
          console.log('Method 1 - Successfully deleted file:', storageBucketPath);
          storageDeleteSuccess = true;
        }
      } catch (storageError) {
        console.warn('Method 1 - Error in storage deletion:', storageError);
      }
    }
    
    // שיטה 2: ניסיון עם path אחר אם שיטה 1 נכשלה
    if (!storageDeleteSuccess && document.url) {
      try {
        // חילוץ רק שם הקובץ
        const parts = document.url.split('/');
        const filename = parts[parts.length - 1].split('?')[0];
        
        console.log('Method 2 - Attempting to delete by filename:', filename);
        const { error: storageError } = await supabase.storage
          .from('documents')
          .remove([filename]);
          
        if (storageError) {
          console.warn('Method 2 - Could not delete file:', storageError);
        } else {
          console.log('Method 2 - Successfully deleted file:', filename);
          storageDeleteSuccess = true;
        }
      } catch (storageError) {
        console.warn('Method 2 - Error in storage deletion:', storageError);
      }
    }
    
    // שיטה 3: ניסיון עם נתיב מלא כולל 'documents'
    if (!storageDeleteSuccess && storageBucketPath) {
      try {
        const fullDocPath = `documents/${storageBucketPath}`;
        console.log('Method 3 - Attempting to delete with full path:', fullDocPath);
        
        const { error: storageError } = await supabase.storage
          .from('documents')
          .remove([fullDocPath]);
          
        if (storageError) {
          console.warn('Method 3 - Could not delete file:', storageError);
        } else {
          console.log('Method 3 - Successfully deleted file:', fullDocPath);
          storageDeleteSuccess = true;
        }
      } catch (storageError) {
        console.warn('Method 3 - Error in storage deletion:', storageError);
      }
    }
    
    // אם כל השיטות נכשלו, ננסה אחת אחרונה בעזרת ה-URL המלא
    if (!storageDeleteSuccess) {
      try {
        // הסתמך על הטריגר בצד השרת למחיקת הקובץ
        console.log('All deletion methods failed, relying on server-side trigger');
      } catch (err) {
        console.error('Error handling storage deletion:', err);
      }
    }
    
    // Invalidate the documents cache to ensure fresh data on next load
    await cacheService.invalidateDocumentsCache();
    
    return true;
  },

  async uploadFile(file: File, path: string) {
    const { data, error } = await supabase.storage
      .from('documents')
      .upload(path, file);

    if (error) throw error;
    return data;
  },

  async getFileUrl(path: string) {
    const { data } = supabase.storage
      .from('documents')
      .getPublicUrl(path);

    return data.publicUrl;
  }
}; 