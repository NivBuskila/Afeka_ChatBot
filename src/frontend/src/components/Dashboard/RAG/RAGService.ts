import { supabase } from '../../../config/supabase';

const API_BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

export interface RAGProfile {
  id: string;
  name: string;
  description: string;
  isActive: boolean;
  isCustom?: boolean;
  config: {
    similarityThreshold: number;
    maxChunks: number;
    maxChunksForContext?: number;
    temperature: number;
    modelName: string;
    chunkSize?: number;
    chunkOverlap?: number;
    maxContextTokens?: number;
    targetTokensPerChunk?: number;
    hybridSemanticWeight?: number;
    hybridKeywordWeight?: number;
  };
  characteristics: {
    focus: string;
    expectedSpeed: string;
    expectedQuality: string;
    bestFor: string;
    tradeoffs: string;
  };
}

export interface RAGTestResult {
  query: string;
  answer: string;
  responseTime: number;
  processingTime?: number;
  totalChunks?: number;
  sourcesFound: number;
  chunks: number;
  searchMethod?: string;
  configUsed?: any;
  chunkText?: string;
  similarity?: number;
  documentTitle?: string;
}

export class RAGService {
  private async makeAuthenticatedRequest(url: string, options: RequestInit = {}) {
    const { data: { session } } = await supabase.auth.getSession();
    
    const headers = {
      'Content-Type': 'application/json',
      ...(session?.access_token && {
        'Authorization': `Bearer ${session.access_token}`,
      }),
      ...options.headers,
    };

    return fetch(url, {
      ...options,
      headers,
    });
  }

  async getAllProfiles(language: string = 'he'): Promise<RAGProfile[]> {
    const { data } = await supabase.auth.getSession();
    if (!data.session) throw new Error('Not authenticated');

    const response = await fetch(`${API_BASE_URL}/api/rag/profiles?language=${language}`, {
      headers: {
        'Authorization': `Bearer ${data.session.access_token}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch profiles: ${response.statusText}`);
    }

    const result = await response.json();
    return result.profiles;
  }

  async activateProfile(profileId: string): Promise<any> {
    const { data } = await supabase.auth.getSession();
    if (!data.session) throw new Error('Not authenticated');

    const response = await fetch(`${API_BASE_URL}/api/rag/profiles/${profileId}/activate`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${data.session.access_token}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      throw new Error(`Failed to activate profile: ${response.statusText}`);
    }
    
    // Return the JSON response from the server
    return await response.json();
  }

  async getCurrentProfile(): Promise<string> {
    const { data } = await supabase.auth.getSession();
    if (!data.session) throw new Error('Not authenticated');

    const response = await fetch(`${API_BASE_URL}/api/rag/current-profile`, {
      headers: {
        'Authorization': `Bearer ${data.session.access_token}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      throw new Error(`Failed to get current profile: ${response.statusText}`);
    }

    const result = await response.json();
    return result.profileId;
  }

  async testQuery(query: string): Promise<RAGTestResult> {
    const { data } = await supabase.auth.getSession();
    if (!data.session) throw new Error('Not authenticated');

    const response = await fetch(`${API_BASE_URL}/api/rag/test`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${data.session.access_token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ query })
    });

    if (!response.ok) {
      throw new Error(`Failed to test query: ${response.statusText}`);
    }

    return await response.json();
  }

  async createProfile(profileData: Partial<RAGProfile>): Promise<RAGProfile> {
    const { data } = await supabase.auth.getSession();
    if (!data.session) throw new Error('Not authenticated');

    const response = await fetch(`${API_BASE_URL}/api/rag/profiles`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${data.session.access_token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(profileData)
    });

    if (!response.ok) {
      throw new Error(`Failed to create profile: ${response.statusText}`);
    }

    const result = await response.json();
    return result.profile; // Return the profile object from the response
  }

  async deleteProfile(profileId: string, force: boolean = false): Promise<any> {
    const { data } = await supabase.auth.getSession();
    if (!data.session) throw new Error('Not authenticated');

    const url = `${API_BASE_URL}/api/rag/profiles/${profileId}${force ? '?force=true' : ''}`;
    const response = await fetch(url, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${data.session.access_token}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to delete profile: ${errorText}`);
    }

    return await response.json();
  }

  async restoreProfile(profileId: string): Promise<any> {
    const { data } = await supabase.auth.getSession();
    if (!data.session) throw new Error('Not authenticated');

    const response = await fetch(`${API_BASE_URL}/api/rag/profiles/${profileId}/restore`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${data.session.access_token}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to restore profile: ${errorText}`);
    }

    return await response.json();
  }

  async getHiddenProfiles(): Promise<string[]> {
    const { data } = await supabase.auth.getSession();
    if (!data.session) throw new Error('Not authenticated');

    const response = await fetch(`${API_BASE_URL}/api/rag/hidden-profiles`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${data.session.access_token}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      // If endpoint doesn't exist, return empty array
      if (response.status === 404) {
        return [];
      }
      throw new Error(`Failed to get hidden profiles: ${response.statusText}`);
    }

    const result = await response.json();
    return result.hiddenProfiles || [];
  }
}

export const ragService = new RAGService(); 