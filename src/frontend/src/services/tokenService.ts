import { supabase } from '../config/supabase';

export interface TokenUsageData {
  total_keys: number;
  current_key_index: number;
  fallback_key_available: boolean;
  fallback_key_hash?: string;
  limits: {
    max_requests_per_minute: number;
    max_tokens_per_day: number;
    max_tokens_per_minute: number;
  };
  keys: {
    [key_hash: string]: {
      status: string;
      is_fallback: boolean;
      error_count: number;
      limit_type?: string;
      requests_today: number;
      requests_this_minute: number;
      tokens_used_today: number;
      tokens_used_this_minute: number;
      cooldown_until?: string;
      last_used: string;
      last_error?: string;
      total_successful_requests: number;
      average_response_time: number;
      last_response_time: number;
      requests_per_minute_usage: string;
      tokens_per_day_usage: string;
      tokens_per_minute_usage: string;
    };
  };
}

export interface TokenUsageReport {
  summary: {
    total_keys: number;
    total_requests_today: number;
    total_tokens_today: number;
    tokens_remaining_today: number;
    keys_near_limit: number;
  };
  limits: {
    max_requests_per_minute: number;
    max_tokens_per_day: number;
    max_tokens_per_minute: number;
  };
  keys: TokenUsageData['keys'];
  warnings: Array<{
    key_hash: string;
    tokens_today_pct: number;
    requests_minute_pct: number;
  }>;
}

const API_BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

export const tokenService = {
  async getTokenUsageData(): Promise<TokenUsageData> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/key-monitoring/metrics`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching token usage data:', error);
      throw error;
    }
  },

  // Alias for getTokenUsageData for backward compatibility
  async getMetrics(): Promise<TokenUsageData> {
    return this.getTokenUsageData();
  },

  async getUsageReport(): Promise<TokenUsageReport> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/key-monitoring/usage-report`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching usage report:', error);
      throw error;
    }
  },

  async getKeyConfig() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/key-monitoring/config`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching key config:', error);
      throw error;
    }
  }
}; 