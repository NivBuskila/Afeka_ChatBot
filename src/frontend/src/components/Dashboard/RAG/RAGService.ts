import { supabase } from '../../../config/supabase';

const API_BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

export interface RAGProfile {
  id: string;
  name: string;
  description: string;
  isActive: boolean;
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
  sourcesFound: number;
  chunks: number;
  searchMethod?: string;
  configUsed?: any;
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

  async activateProfile(profileId: string): Promise<void> {
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
}

export const ragService = new RAGService(); 