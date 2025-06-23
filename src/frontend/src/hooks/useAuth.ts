import { useState } from 'react';
import { authService, AuthResult } from '../services/authService';

export const useAuth = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const login = async (email: string, password: string): Promise<AuthResult> => {
    setIsLoading(true);
    setError(null);
    
    try {
      const result = await authService.login(email, password);
      
      if (result.error) {
        setError(result.error);
      }
      
      return result;
    } catch (err: any) {
      const errorMessage = err.message || 'An unexpected error occurred';
      setError(errorMessage);
      return { user: null, isAdmin: false, error: errorMessage };
    } finally {
      setIsLoading(false);
    }
  };

  const resetPassword = async (email: string): Promise<{ error: string | null }> => {
    setIsLoading(true);
    setError(null);
    
    try {
      const result = await authService.resetPassword(email);
      
      if (result.error) {
        setError(result.error);
      }
      
      return result;
    } catch (err: any) {
      const errorMessage = err.message || 'An unexpected error occurred';
      setError(errorMessage);
      return { error: errorMessage };
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async (): Promise<{ error: string | null }> => {
    setIsLoading(true);
    setError(null);
    
    try {
      const result = await authService.logout();
      
      if (result.error) {
        setError(result.error);
      }
      
      return result;
    } catch (err: any) {
      const errorMessage = err.message || 'An unexpected error occurred';
      setError(errorMessage);
      return { error: errorMessage };
    } finally {
      setIsLoading(false);
    }
  };

  return {
    login,
    resetPassword,
    logout,
    isLoading,
    error,
    clearError: () => setError(null)
  };
}; 