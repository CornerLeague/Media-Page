import { useEffect } from 'react';
import { useAuth, useUser } from '@clerk/clerk-react';
import { apiClient, ClerkAuthContext } from '@/lib/api-client';

/**
 * Hook to setup the API client with Clerk authentication context
 * This should be used at the app level to ensure the API client
 * has access to Clerk authentication tokens
 */
export function useAuthenticatedApiClient() {
  const { getToken, isSignedIn } = useAuth();
  const { user } = useUser();

  useEffect(() => {
    if (isSignedIn && user) {
      const clerkAuth: ClerkAuthContext = {
        getToken,
        isSignedIn,
        userId: user.id,
      };

      apiClient.setClerkAuth(clerkAuth);
    } else {
      // Clear auth if user is signed out
      apiClient.setClerkAuth(null);
    }
  }, [isSignedIn, user?.id, getToken]);

  return {
    apiClient,
    isAuthenticated: isSignedIn,
    user,
  };
}