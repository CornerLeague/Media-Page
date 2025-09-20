/**
 * Firebase Authentication Context
 *
 * Provides Firebase authentication state and methods throughout the app
 * using React Context for dependency injection pattern.
 */

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { User } from 'firebase/auth';
import { authService } from '@/lib/firebase';

// Firebase Auth Context Type
export interface FirebaseAuthContextType {
  // Auth state
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;

  // Auth methods
  signInWithGoogle: () => Promise<User>;
  signInWithEmail: (email: string, password: string) => Promise<User>;
  createAccountWithEmail: (email: string, password: string) => Promise<User>;
  signOut: () => Promise<void>;
  getIdToken: (forceRefresh?: boolean) => Promise<string | null>;

  // Helper methods
  getUserId: () => string | null;
  getUserEmail: () => string | null;
  getUserDisplayName: () => string | null;
  getUserPhotoURL: () => string | null;
}

// Create the context
const FirebaseAuthContext = createContext<FirebaseAuthContextType | null>(null);

// Provider Props
interface FirebaseAuthProviderProps {
  children: ReactNode;
}

// Firebase Auth Provider Component
export function FirebaseAuthProvider({ children }: FirebaseAuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Listen to authentication state changes
    const unsubscribe = authService.onAuthStateChanged((firebaseUser) => {
      setUser(firebaseUser);
      setIsLoading(false);
    });

    // Cleanup subscription on unmount
    return () => unsubscribe();
  }, []);

  // Context value
  const contextValue: FirebaseAuthContextType = {
    // Auth state
    user,
    isLoading,
    isAuthenticated: !!user,

    // Auth methods - wrapped to handle errors and state updates
    signInWithGoogle: async (): Promise<User> => {
      const firebaseUser = await authService.signInWithGoogle();
      setUser(firebaseUser);
      return firebaseUser;
    },

    signInWithEmail: async (email: string, password: string): Promise<User> => {
      const firebaseUser = await authService.signInWithEmail(email, password);
      setUser(firebaseUser);
      return firebaseUser;
    },

    createAccountWithEmail: async (email: string, password: string): Promise<User> => {
      const firebaseUser = await authService.createAccountWithEmail(email, password);
      setUser(firebaseUser);
      return firebaseUser;
    },

    signOut: async (): Promise<void> => {
      await authService.signOut();
      setUser(null);
    },

    getIdToken: async (forceRefresh = false): Promise<string | null> => {
      return await authService.getIdToken(forceRefresh);
    },

    // Helper methods
    getUserId: (): string | null => user?.uid || null,
    getUserEmail: (): string | null => user?.email || null,
    getUserDisplayName: (): string | null => user?.displayName || null,
    getUserPhotoURL: (): string | null => user?.photoURL || null,
  };

  return (
    <FirebaseAuthContext.Provider value={contextValue}>
      {children}
    </FirebaseAuthContext.Provider>
  );
}

// Custom hook to use Firebase Auth context
export function useFirebaseAuth(): FirebaseAuthContextType {
  const context = useContext(FirebaseAuthContext);

  if (!context) {
    throw new Error('useFirebaseAuth must be used within a FirebaseAuthProvider');
  }

  return context;
}

// Convenience hooks for common auth operations
export function useAuthUser() {
  const { user, isLoading, isAuthenticated } = useFirebaseAuth();
  return { user, isLoading, isAuthenticated };
}

export function useAuthMethods() {
  const {
    signInWithGoogle,
    signInWithEmail,
    createAccountWithEmail,
    signOut,
  } = useFirebaseAuth();

  return {
    signInWithGoogle,
    signInWithEmail,
    createAccountWithEmail,
    signOut,
  };
}

export function useAuthToken() {
  const { getIdToken, isAuthenticated } = useFirebaseAuth();
  return { getIdToken, isAuthenticated };
}

export default FirebaseAuthContext;