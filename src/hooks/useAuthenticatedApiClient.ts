import { useEffect } from 'react';
import { useFirebaseAuth } from '@/contexts/FirebaseAuthContext';
import { apiClient, FirebaseAuthContext } from '@/lib/api-client';

/**
 * Hook to setup the API client with Firebase authentication context
 * This should be used at the app level to ensure the API client
 * has access to Firebase authentication tokens
 */
export function useAuthenticatedApiClient() {
  const { getIdToken, isAuthenticated, user } = useFirebaseAuth();

  useEffect(() => {
    if (isAuthenticated && user) {
      const firebaseAuth: FirebaseAuthContext = {
        getIdToken,
        isAuthenticated,
        userId: user.uid,
      };

      apiClient.setFirebaseAuth(firebaseAuth);
    } else {
      // Clear auth if user is signed out
      apiClient.setFirebaseAuth(null);
    }
  }, [isAuthenticated, user?.uid, getIdToken]);

  return {
    apiClient,
    isAuthenticated,
    user,
  };
}