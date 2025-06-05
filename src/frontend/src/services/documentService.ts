import { supabase, Database } from '../config/supabase';
import { cacheService } from './cacheService';
import axios from 'axios';

// Get the backend URL from environment
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

type Document = Database['public']['Tables']['documents']['Row'];
type DocumentInsert = Database['public']['Tables']['documents']['Insert'];
type DocumentUpdate = Database['public']['Tables']['documents']['Update'];

export const documentService = {
  async getAllDocuments() {
    // Check if we should bust cache
    const isCacheStale = cacheService.isCacheStale('documents', 30000); // 30 seconds
    
    // Use cache busting query parameter if cache is stale
    const cacheBuster = isCacheStale ? `?cache=${Date.now()}` : '';
    
    try {
      const response = await axios.get(`${BACKEND_URL}/api/proxy/documents${cacheBuster}`);
      if (!response.data) {
        throw new Error('No data returned from documents request');
      }
      return response.data;
    } catch (error) {
      console.error('Error fetching documents:', error);
      throw error;
    }
  },

  async getDocumentById(id: number) {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/proxy/documents/${id}`);
      if (!response.data) {
        throw new Error('No document found');
      }
      return response.data;
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
      
      const response = await axios.post(`${BACKEND_URL}/api/proxy/documents`, documentData);
      if (!response.data) {
        throw new Error('Failed to create document');
      }
      
      return response.data;
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
      const response = await axios.delete(`${BACKEND_URL}/api/proxy/documents/${id}`);
      if (!response.data || !response.data.success) {
        throw new Error('Failed to delete document');
      }
      return response.data;
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
  }
}; 