import { supabase, Database } from '../config/supabase';
import { cacheService } from './cacheService';

// Get the backend URL from environment
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

// Helper function to replace axios with native fetch
const apiRequest = async (url: string, options: RequestInit = {}) => {
  // Get current session
  const { data: { session } } = await supabase.auth.getSession();
  
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...(session?.access_token && {
        'Authorization': `Bearer ${session.access_token}`
      }),
      ...options.headers,
    },
    ...options,
  });
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  const result = await response.json();
  return result;
};

type DocumentInsert = Database['public']['Tables']['documents']['Insert'];
type DocumentUpdate = Database['public']['Tables']['documents']['Update'];

export const documentService = {
  async getAllDocuments() {
    // Check if we should bust cache
    const isCacheStale = cacheService.isCacheStale('documents', 30000); // 30 seconds
    
    // Use cache busting query parameter if cache is stale
    const cacheBuster = isCacheStale ? `?cache=${Date.now()}` : '';
    
    try {
      const response = await apiRequest(`${BACKEND_URL}/api/proxy/documents${cacheBuster}`);
      
      if (!response) {
        throw new Error('No data returned from documents request');
      }
      return response;
    } catch (error) {
      console.error('🚨 [DocumentService] Error fetching documents:', error);
      throw error;
    }
  },

  async getDocumentById(id: number) {
    try {
      const response = await apiRequest(`${BACKEND_URL}/api/proxy/documents/${id}`);
      if (!response) {
        throw new Error('No document found');
      }
      return response;
    } catch (error) {
      console.error('Error fetching document:', error);
      throw error;
    }
  },

  async createDocument(document: DocumentInsert) {
    try {
      // Get current user
      const { data: { user } } = await supabase.auth.getUser();
      
      // Create document with user_id
      const documentData = {
        ...document,
        user_id: user?.id
      };
      
      const response = await apiRequest(`${BACKEND_URL}/api/proxy/documents`, {
        method: 'POST',
        body: JSON.stringify(documentData)
      });
      if (!response) {
        throw new Error('Failed to create document');
      }
      
      return response;
    } catch (error) {
      console.error('Error creating document:', error);
      throw error;
    }
  },

  async updateDocument(id: number, updates: DocumentUpdate) {
    // Not implemented in the backend proxy yet
    // Fallback to direct Supabase access for now
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
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session?.access_token) {
        throw new Error('User not authenticated or session expired');
      }

      const response = await fetch(`${BACKEND_URL}/api/vector/document/${id}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`
        }
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData?.message || 'Failed to delete document');
      }
      
      const data = await response.json().catch(() => ({ success: true, message: "Document deleted successfully" }));
      return data;
    } catch (error) {
      console.error('Error deleting document:', error);
      throw error;
    }
  },

  // Storage operations will still need to go through Supabase client directly
  // as they require storage access which our backend proxy doesn't handle yet
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
  },

  async getProcessingStatus(documentId: string): Promise<any> {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session?.access_token) {
        throw new Error('User not authenticated or session expired');
      }
      
      const response = await fetch(`${BACKEND_URL}/api/vector/document/${documentId}/status`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`
        }
      });

      if (!response.ok) {
        let errorData;
        try {
          errorData = await response.json();
        } catch (e) {
          // If parsing JSON fails, use text content
          errorData = { error: await response.text() || 'שגיאה בקבלת נתוני העיבוד - תגובה לא תקינה' };
        }
        throw new Error(errorData.error || errorData.detail || 'שגיאה בקבלת נתוני העיבוד');
      }

      const data = await response.json();
      
      // Normalize status field for frontend components
      if (data && !data.status) {
        if (data.processing_status) {
          data.status = data.processing_status;
        } else {
          console.warn(`Document ${documentId} status field is missing.`, data);
          // If we have chunk_count but no status, assume it's completed as a fallback
          if (data.chunk_count > 0) {
            data.status = 'completed';
          }
        }
      }
      
      return data;
    } catch (error) {
      console.error('Error getting document processing status:', error);
      throw error;
    }
  }
}; 