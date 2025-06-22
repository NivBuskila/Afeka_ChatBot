/**
 * System Prompt Service
 * =====================
 * 
 * Service for managing system prompts through the Admin Dashboard.
 * Handles CRUD operations for system prompts stored in Supabase.
 */

import { supabase } from "../config/supabase";

// Types
export interface SystemPrompt {
  id: string;
  prompt_text: string;
  version: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  updated_by: string | null;
  notes: string | null;
  updated_by_email: string | null;
}

export interface SystemPromptCreateData {
  prompt_text: string;
  notes?: string | null;
}

export interface SystemPromptUpdateData {
  prompt_text: string;
  notes?: string | null;
}

class SystemPromptService {
  private readonly baseUrl = '/api/system-prompts';

  /**
   * Get headers for API requests
   */
  private async getHeaders(): Promise<HeadersInit> {
    const session = await supabase.auth.getSession();
    const token = session.data.session?.access_token;

    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
    };
  }

  /**
   * Handle API response and errors
   */
  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      let errorMessage = `HTTP error! status: ${response.status}`;
      
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorData.message || errorMessage;
      } catch {
        // If we can't parse the error response, use the default message
      }
      
      throw new Error(errorMessage);
    }

    return response.json();
  }

  /**
   * Get the currently active system prompt
   */
  async getCurrentPrompt(): Promise<SystemPrompt> {
    try {
      const response = await fetch(`${this.baseUrl}/current`, {
        method: 'GET',
        headers: await this.getHeaders(),
      });

      return this.handleResponse<SystemPrompt>(response);
    } catch (error) {
      console.error('Error getting current system prompt:', error);
      throw error;
    }
  }

  /**
   * Get system prompt history
   */
  async getPromptHistory(limit: number = 10): Promise<SystemPrompt[]> {
    try {
      const response = await fetch(`${this.baseUrl}/history?limit=${limit}`, {
        method: 'GET',
        headers: await this.getHeaders(),
      });

      return this.handleResponse<SystemPrompt[]>(response);
    } catch (error) {
      console.error('Error getting system prompt history:', error);
      throw error;
    }
  }

  /**
   * Create a new system prompt
   */
  async createPrompt(data: SystemPromptCreateData): Promise<SystemPrompt> {
    try {
      const response = await fetch(this.baseUrl, {
        method: 'POST',
        headers: await this.getHeaders(),
        body: JSON.stringify(data),
      });

      return this.handleResponse<SystemPrompt>(response);
    } catch (error) {
      console.error('Error creating system prompt:', error);
      throw error;
    }
  }

  /**
   * Update an existing system prompt
   */
  async updatePrompt(promptId: string, data: SystemPromptUpdateData): Promise<SystemPrompt> {
    try {
      const response = await fetch(`${this.baseUrl}/${promptId}`, {
        method: 'PUT',
        headers: await this.getHeaders(),
        body: JSON.stringify(data),
      });

      return this.handleResponse<SystemPrompt>(response);
    } catch (error) {
      console.error('Error updating system prompt:', error);
      throw error;
    }
  }

  /**
   * Activate a specific system prompt version
   */
  async activatePrompt(promptId: string): Promise<SystemPrompt> {
    try {
      const response = await fetch(`${this.baseUrl}/${promptId}/activate`, {
        method: 'POST',
        headers: await this.getHeaders(),
      });

      return this.handleResponse<SystemPrompt>(response);
    } catch (error) {
      console.error('Error activating system prompt:', error);
      throw error;
    }
  }

  /**
   * Reset to the default system prompt
   */
  async resetToDefault(): Promise<SystemPrompt> {
    try {
      const response = await fetch(`${this.baseUrl}/reset-to-default`, {
        method: 'POST',
        headers: await this.getHeaders(),
      });

      return this.handleResponse<SystemPrompt>(response);
    } catch (error) {
      console.error('Error resetting to default system prompt:', error);
      throw error;
    }
  }

  /**
   * Check if user has permission to manage system prompts
   */
  async checkPermissions(): Promise<boolean> {
    try {
      const session = await supabase.auth.getSession();
      if (!session.data.session) return false;

      // Try to get current prompt - if it succeeds, user has permissions
      await this.getCurrentPrompt();
      return true;
    } catch (error) {
      console.error('Permission check failed:', error);
      return false;
    }
  }
}

// Export singleton instance
export const systemPromptService = new SystemPromptService(); 