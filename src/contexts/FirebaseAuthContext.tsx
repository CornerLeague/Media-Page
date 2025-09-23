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

  // Password and email management
  sendPasswordResetEmail: (email: string) => Promise<void>;
  sendEmailVerification: () => Promise<void>;
  updateUserProfile: (updates: { displayName?: string; photoURL?: string }) => Promise<void>;
  updateUserPassword: (newPassword: string) => Promise<void>;
  reauthenticateWithPassword: (password: string) => Promise<void>;

  // Helper methods
  getUserId: () => string | null;
  getUserEmail: () => string | null;
  getUserDisplayName: () => string | null;
  getUserPhotoURL: () => string | null;
  isEmailVerified: () => boolean;
  getUserMetadata: () => {
    creationTime: string | undefined;
    lastSignInTime: string | undefined;
    isEmailVerified: boolean;
  } | null;
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

  const cloneFirebaseUser = <T extends User>(firebaseUser: T): T => {
    return Object.assign(
      Object.create(Object.getPrototypeOf(firebaseUser)),
      firebaseUser
    );
  };

  const updateUserState = (nextUser: User | null) => {
    if (!nextUser) {
      setUser(null);
      return;
    }

    setUser((previousUser) => {
      if (previousUser === nextUser) {
        return cloneFirebaseUser(nextUser);
      }
      return nextUser;
    });
  };

  useEffect(() => {
    // Listen to authentication state changes
    const unsubscribe = authService.onAuthStateChanged((firebaseUser) => {
      updateUserState(firebaseUser);
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
      updateUserState(firebaseUser);
      return firebaseUser;
    },

    signInWithEmail: async (email: string, password: string): Promise<User> => {
      const firebaseUser = await authService.signInWithEmail(email, password);
      updateUserState(firebaseUser);
      return firebaseUser;
    },

    createAccountWithEmail: async (email: string, password: string): Promise<User> => {
      const firebaseUser = await authService.createAccountWithEmail(email, password);
      updateUserState(firebaseUser);
      return firebaseUser;
    },

    signOut: async (): Promise<void> => {
      await authService.signOut();
      updateUserState(null);
    },

    getIdToken: async (forceRefresh = false): Promise<string | null> => {
      return await authService.getIdToken(forceRefresh);
    },

    // Password and email management
    sendPasswordResetEmail: async (email: string): Promise<void> => {
      await authService.sendPasswordResetEmail(email);
    },

    sendEmailVerification: async (): Promise<void> => {
      await authService.sendEmailVerification();
    },

    updateUserProfile: async (updates: { displayName?: string; photoURL?: string }): Promise<void> => {
      await authService.updateUserProfile(updates);
      const updatedUser = authService.getCurrentUser();
      if (updatedUser) {
        if (typeof updatedUser.reload === 'function') {
          try {
            await updatedUser.reload();
          } catch (error) {
            console.warn('Failed to reload Firebase user after profile update', error);
          }
        }
        updateUserState(updatedUser);
      }
    },

    updateUserPassword: async (newPassword: string): Promise<void> => {
      await authService.updateUserPassword(newPassword);
    },

    reauthenticateWithPassword: async (password: string): Promise<void> => {
      await authService.reauthenticateWithPassword(password);
    },

    // Helper methods
    getUserId: (): string | null => user?.uid || null,
    getUserEmail: (): string | null => user?.email || null,
    getUserDisplayName: (): string | null => user?.displayName || null,
    getUserPhotoURL: (): string | null => user?.photoURL || null,
    isEmailVerified: (): boolean => authService.isEmailVerified(),
    getUserMetadata: () => authService.getUserMetadata(),
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

// Hook for password reset functionality
export function usePasswordReset() {
  const { sendPasswordResetEmail } = useFirebaseAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const resetPassword = async (email: string) => {
    setIsLoading(true);
    setError(null);
    setSuccess(false);

    try {
      await sendPasswordResetEmail(email);
      setSuccess(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send password reset email');
    } finally {
      setIsLoading(false);
    }
  };

  const clearState = () => {
    setError(null);
    setSuccess(false);
  };

  return { resetPassword, isLoading, error, success, clearState };
}

// Hook for email verification
export function useEmailVerification() {
  const { sendEmailVerification, isEmailVerified, user } = useFirebaseAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const sendVerification = async () => {
    if (!user) {
      setError('No user is signed in');
      return;
    }

    setIsLoading(true);
    setError(null);
    setSuccess(false);

    try {
      await sendEmailVerification();
      setSuccess(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send verification email');
    } finally {
      setIsLoading(false);
    }
  };

  const clearState = () => {
    setError(null);
    setSuccess(false);
  };

  return {
    sendVerification,
    isLoading,
    error,
    success,
    isEmailVerified: isEmailVerified(),
    clearState,
  };
}

// Hook for profile management
export function useProfileManagement() {
  const { updateUserProfile, user } = useFirebaseAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const updateProfile = async (updates: { displayName?: string; photoURL?: string }) => {
    setIsLoading(true);
    setError(null);
    setSuccess(false);

    try {
      await updateUserProfile(updates);
      setSuccess(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update profile');
    } finally {
      setIsLoading(false);
    }
  };

  const clearState = () => {
    setError(null);
    setSuccess(false);
  };

  return { updateProfile, isLoading, error, success, user, clearState };
}

// Hook for password management
export function usePasswordManagement() {
  const { updateUserPassword, reauthenticateWithPassword } = useFirebaseAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const changePassword = async (currentPassword: string, newPassword: string) => {
    setIsLoading(true);
    setError(null);
    setSuccess(false);

    try {
      // First reauthenticate the user
      await reauthenticateWithPassword(currentPassword);
      // Then update the password
      await updateUserPassword(newPassword);
      setSuccess(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update password');
    } finally {
      setIsLoading(false);
    }
  };

  const clearState = () => {
    setError(null);
    setSuccess(false);
  };

  return { changePassword, isLoading, error, success, clearState };
}

// Hook for user metadata and status
export function useUserStatus() {
  const { user, getUserMetadata, isEmailVerified, isAuthenticated } = useFirebaseAuth();

  const metadata = getUserMetadata();

  return {
    user,
    isAuthenticated,
    isEmailVerified: isEmailVerified(),
    metadata,
    hasDisplayName: !!user?.displayName,
    hasPhotoURL: !!user?.photoURL,
    providerData: user?.providerData || [],
  };
}

export default FirebaseAuthContext;