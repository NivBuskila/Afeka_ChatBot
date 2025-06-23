import { supabase } from '../../config/supabase';
import type { Document } from '../../config/supabase';

export interface DocumentHandlerCallbacks {
  onSuccess: (message: string) => void;
  onError: (message: string) => void;
  onDocumentsUpdate: (updater: (prev: Document[]) => Document[]) => void;
  onLoadingChange: (loading: boolean) => void;
  onModalClose: (modalType: 'upload' | 'edit' | 'delete') => void;
  onSelectedDocumentChange: (document: Document | null) => void;
}

export interface DocumentHandlerConfig {
  t?: (key: string, fallback?: string) => string;
}

export class DocumentHandlerService {
  constructor(
    private callbacks: DocumentHandlerCallbacks,
    private config: DocumentHandlerConfig = {}
  ) {}

  /**
   * Handles file upload with authentication and user verification
   */
  async uploadDocument(file: File): Promise<void> {
    try {
      // Verify user is authenticated before upload
      const { data: authData } = await supabase.auth.getSession();
      if (!authData.session) {
        console.error('User not authenticated');
        this.callbacks.onError('יש להתחבר מחדש למערכת');
        return;
      }

      // Check if user exists in users table
      const { data: userData, error: userError } = await supabase
        .from('users')
        .select('id')
        .eq('id', authData.session.user.id)
        .single();

      // If user doesn't exist, try creating them (may fail due to RLS)
      if (userError || !userData) {
        console.error('User not found in database:', userError);
        await this.createUserIfNeeded(authData.session.user);
      }

      // Create safe filename without Hebrew characters
      const fileExt = file.name.split('.').pop() || '';
      const safeFileName = `${Date.now()}.${fileExt}`;
      const path = `documents/${safeFileName}`;

      // Upload the file
      const { error: uploadError } = await supabase.storage
        .from('documents')
        .upload(path, file);

      if (uploadError) {
        console.error('Error uploading file:', uploadError);
        this.callbacks.onError(`שגיאה בהעלאת הקובץ: ${uploadError.message}`);
        return;
      }

      // Get public URL
      const { data: urlData } = supabase.storage
        .from('documents')
        .getPublicUrl(path);

      // Create document record
      const { data: docData, error: docError } = await supabase
        .from('documents')
        .insert({
          name: file.name,
          type: file.type,
          size: file.size,
          url: urlData.publicUrl,
        })
        .select()
        .single();

      if (docError) {
        console.error('Error creating document record:', docError);
        this.callbacks.onError(`שגיאה ביצירת רשומת מסמך: ${docError.message}`);
        return;
      }

      // Add analytics record (may fail due to RLS)
      await this.addDocumentAnalytics(docData.id, authData.session.user.id, 'upload');

      // Update local state
      this.callbacks.onDocumentsUpdate((prev) => [docData, ...prev]);
      this.callbacks.onModalClose('upload');
      this.callbacks.onSuccess(this.config.t?.('documents.uploadSuccess') || 'File uploaded successfully');
    } catch (error) {
      console.error('Error uploading file:', error);
      this.callbacks.onError('אירעה שגיאה בתהליך ההעלאה');
    }
  }

  /**
   * Updates an existing document with a new file
   */
  async updateDocument(document: Document, file: File): Promise<void> {
    try {
      this.callbacks.onLoadingChange(true);

      // Delete the old file from storage
      await this.deleteFileFromStorage(document.url);

      // Upload new file
      const fileExt = file.name.split('.').pop() || '';
      const safeFileName = `${Date.now()}.${fileExt}`;
      const path = `documents/${safeFileName}`;

      const { error: uploadError } = await supabase.storage
        .from('documents')
        .upload(path, file);

      if (uploadError) {
        console.error('Error uploading new file:', uploadError);
        this.callbacks.onError(`שגיאה בהעלאת הקובץ החדש: ${uploadError.message}`);
        return;
      }

      // Get public URL for new file
      const { data: urlData } = supabase.storage
        .from('documents')
        .getPublicUrl(path);

      // Update document record
      const { data: updatedDoc, error: updateError } = await supabase
        .from('documents')
        .update({
          name: file.name,
          type: file.type,
          size: file.size,
          url: urlData.publicUrl,
          updated_at: new Date().toISOString(),
        })
        .eq('id', document.id)
        .select()
        .single();

      if (updateError) {
        console.error('Error updating document record:', updateError);
        this.callbacks.onError(`שגיאה בעדכון רשומת המסמך: ${updateError.message}`);
        return;
      }

      // Update local state
      this.callbacks.onDocumentsUpdate((prev) =>
        prev.map((doc) => (doc.id === document.id ? updatedDoc : doc))
      );

      this.callbacks.onModalClose('edit');
      this.callbacks.onSelectedDocumentChange(null);
      this.callbacks.onSuccess(this.config.t?.('documents.updateSuccess') || 'Document updated successfully');
    } catch (error) {
      console.error('Error updating document:', error);
      this.callbacks.onError('אירעה שגיאה בעדכון המסמך');
    } finally {
      this.callbacks.onLoadingChange(false);
    }
  }

  /**
   * Deletes a document from both storage and database
   */
  async deleteDocument(document: Document): Promise<void> {
    try {
      this.callbacks.onLoadingChange(true);

      // Delete from storage
      await this.deleteFileFromStorage(document.url);

      // Delete from database
      const { error: dbError } = await supabase
        .from('documents')
        .delete()
        .eq('id', document.id);

      if (dbError) {
        console.error('Error deleting from database:', dbError);
        this.callbacks.onError(`שגיאה במחיקת המסמך: ${dbError.message}`);
        return;
      }

      // Update local state
      this.callbacks.onDocumentsUpdate((prev) => 
        prev.filter((doc) => doc.id !== document.id)
      );
      
      this.callbacks.onModalClose('delete');
      this.callbacks.onSelectedDocumentChange(null);
      this.callbacks.onSuccess(this.config.t?.('documents.deleteSuccess') || 'Document deleted successfully');
    } catch (error) {
      console.error('Error deleting document:', error);
      this.callbacks.onError('אירעה שגיאה במחיקת המסמך');
    } finally {
      this.callbacks.onLoadingChange(false);
    }
  }

  /**
   * Private helper methods
   */
  private async createUserIfNeeded(user: any): Promise<void> {
    try {
      const { error: insertError } = await supabase.from('users').insert({
        id: user.id,
        email: user.email || '',
        name: user.email?.split('@')[0] || 'User',
        status: 'active',
      });

      if (insertError) {
        console.error('Failed to insert user record:', insertError);
      } else {
        // Check if user should be admin and add to admins table
        if (user.user_metadata?.is_admin || user.user_metadata?.role === 'admin') {
          await this.createAdminRecord(user.id);
        }
      }
    } catch (createError) {
      console.error('Error creating user record:', createError);
    }
  }

  private async createAdminRecord(userId: string): Promise<void> {
    try {
      const { error: adminError } = await supabase
        .from('admins')
        .insert({ user_id: userId });

      if (adminError) {
        console.error('Failed to insert admin record:', adminError);
      }
    } catch (adminError) {
      console.error('Error creating admin record:', adminError);
    }
  }

  private async addDocumentAnalytics(
    documentId: number, 
    userId: string, 
    action: string
  ): Promise<void> {
    try {
      const { error: analyticsError } = await supabase
        .from('document_analytics')
        .insert({
          document_id: documentId,
          user_id: userId,
          action,
        });

      if (analyticsError) {
        console.error('Error adding analytics record:', analyticsError);
      }
    } catch (analyticsError) {
      console.error('Failed to add analytics record:', analyticsError);
    }
  }

  private async deleteFileFromStorage(url: string): Promise<void> {
    const storagePathMatch = url.match(/\/documents\/([^\/]+)$/);
    const storagePath = storagePathMatch ? storagePathMatch[1] : null;

    if (storagePath) {
      const { error: deleteError } = await supabase.storage
        .from('documents')
        .remove([`documents/${storagePath}`]);

      if (deleteError) {
        console.error('Error deleting old file:', deleteError);
      }
    }
  }
} 