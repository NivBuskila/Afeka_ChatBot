import { supabase, Database } from '../config/supabase';

type Document = Database['public']['Tables']['documents']['Row'];
type DocumentInsert = Database['public']['Tables']['documents']['Insert'];
type DocumentUpdate = Database['public']['Tables']['documents']['Update'];

export const documentService = {
  async getAllDocuments() {
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
    const { error } = await supabase
      .from('documents')
      .delete()
      .eq('id', id);

    if (error) throw error;
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