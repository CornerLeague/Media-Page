/**
 * useResetOnboarding Hook
 *
 * Provides functionality to reset user onboarding and redirect to onboarding flow.
 * This hook handles the API call to reset onboarding data and manages navigation.
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { useFirebaseAuth } from '@/contexts/FirebaseAuthContext';
import { apiClient } from '@/lib/api-client';
import { toast } from '@/components/ui/use-toast';

export interface UseResetOnboardingResult {
  resetOnboarding: () => Promise<void>;
  isResetting: boolean;
  error: Error | null;
  reset: () => void;
}

export function useResetOnboarding(): UseResetOnboardingResult {
  const { isAuthenticated } = useFirebaseAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const {
    mutateAsync: resetOnboarding,
    isPending: isResetting,
    error,
    reset,
  } = useMutation({
    mutationFn: async () => {
      if (!isAuthenticated) {
        throw new Error('Not authenticated');
      }
      return await apiClient.resetOnboarding();
    },
    onSuccess: () => {
      // Clear all user-related query cache
      queryClient.invalidateQueries({ queryKey: ['user'] });
      queryClient.invalidateQueries({ queryKey: ['auth'] });
      queryClient.invalidateQueries({ queryKey: ['home'] });

      // Clear onboarding cache specifically
      queryClient.removeQueries({ queryKey: ['user', 'profile'] });
      queryClient.removeQueries({ queryKey: ['auth', 'onboarding-status'] });

      toast({
        title: 'Onboarding Reset',
        description: 'Your preferences have been reset. Redirecting to onboarding...',
      });

      // Redirect to onboarding after a short delay
      setTimeout(() => {
        navigate('/onboarding', { replace: true });
      }, 1500);
    },
    onError: (error) => {
      console.error('Failed to reset onboarding:', error);
      toast({
        title: 'Reset Failed',
        description: 'Failed to reset onboarding. Please try again or contact support.',
        variant: 'destructive',
      });
    },
  });

  return {
    resetOnboarding,
    isResetting,
    error: error as Error | null,
    reset,
  };
}