/**
 * Development Firebase Authentication Service
 *
 * Provides a mock authentication service for development when
 * real Firebase credentials are not available. This allows
 * developers to work on the application without requiring
 * Firebase project setup.
 */

import { User } from 'firebase/auth';

// Mock User type that matches Firebase User interface
interface MockUser extends Partial<User> {
  uid: string;
  email: string | null;
  displayName: string | null;
  photoURL: string | null;
  emailVerified: boolean;
  metadata: {
    creationTime?: string;
    lastSignInTime?: string;
  };
  getIdToken: (forceRefresh?: boolean) => Promise<string>;
}

// Development user store
let currentUser: MockUser | null = null;
let authStateCallbacks: Array<(user: MockUser | null) => void> = [];

// Mock authentication service for development
export const devAuthService = {
  // Sign in with Google (mock)
  signInWithGoogle: async (): Promise<MockUser> => {
    const mockUser: MockUser = {
      uid: 'dev-user-google-' + Date.now(),
      email: 'dev.user@example.com',
      displayName: 'Development User (Google)',
      photoURL: 'https://via.placeholder.com/150',
      emailVerified: true,
      metadata: {
        creationTime: new Date().toISOString(),
        lastSignInTime: new Date().toISOString(),
      },
      getIdToken: async () => 'mock-firebase-token-' + Date.now(),
    };

    currentUser = mockUser;
    authStateCallbacks.forEach(callback => callback(mockUser));

    console.log('🔥 Development Mode: Mock Google sign-in successful');
    return mockUser;
  },

  // Sign in with email and password (mock)
  signInWithEmail: async (email: string, password: string): Promise<MockUser> => {
    // Simulate some validation
    if (!email || !password) {
      throw new Error('Email and password are required');
    }

    if (password.length < 6) {
      throw new Error('Password must be at least 6 characters');
    }

    const mockUser: MockUser = {
      uid: 'dev-user-email-' + Date.now(),
      email: email,
      displayName: email.split('@')[0],
      photoURL: null,
      emailVerified: email.includes('verified'),
      metadata: {
        creationTime: new Date().toISOString(),
        lastSignInTime: new Date().toISOString(),
      },
      getIdToken: async () => 'mock-firebase-token-' + Date.now(),
    };

    currentUser = mockUser;
    authStateCallbacks.forEach(callback => callback(mockUser));

    console.log('🔥 Development Mode: Mock email sign-in successful');
    return mockUser;
  },

  // Create account with email and password (mock)
  createAccountWithEmail: async (email: string, password: string): Promise<MockUser> => {
    // Simulate some validation
    if (!email || !password) {
      throw new Error('Email and password are required');
    }

    if (password.length < 6) {
      throw new Error('Password must be at least 6 characters');
    }

    if (!email.includes('@')) {
      throw new Error('Invalid email format');
    }

    const mockUser: MockUser = {
      uid: 'dev-user-new-' + Date.now(),
      email: email,
      displayName: email.split('@')[0],
      photoURL: null,
      emailVerified: false, // New accounts start unverified
      metadata: {
        creationTime: new Date().toISOString(),
        lastSignInTime: new Date().toISOString(),
      },
      getIdToken: async () => 'mock-firebase-token-' + Date.now(),
    };

    currentUser = mockUser;
    authStateCallbacks.forEach(callback => callback(mockUser));

    console.log('🔥 Development Mode: Mock account creation successful');
    return mockUser;
  },

  // Sign out
  signOut: async (): Promise<void> => {
    currentUser = null;
    authStateCallbacks.forEach(callback => callback(null));
    console.log('🔥 Development Mode: Mock sign-out successful');
  },

  // Get current user
  getCurrentUser: (): MockUser | null => {
    return currentUser;
  },

  // Get ID token
  getIdToken: async (forceRefresh = false): Promise<string | null> => {
    if (!currentUser) return null;
    return await currentUser.getIdToken(forceRefresh);
  },

  // Listen to auth state changes
  onAuthStateChanged: (callback: (user: MockUser | null) => void) => {
    authStateCallbacks.push(callback);
    // Immediately call with current user
    callback(currentUser);

    // Return unsubscribe function
    return () => {
      const index = authStateCallbacks.indexOf(callback);
      if (index > -1) {
        authStateCallbacks.splice(index, 1);
      }
    };
  },

  // Send password reset email (mock)
  sendPasswordResetEmail: async (email: string): Promise<void> => {
    console.log('🔥 Development Mode: Mock password reset email sent to', email);
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));
  },

  // Send email verification (mock)
  sendEmailVerification: async (): Promise<void> => {
    if (!currentUser) throw new Error('No user is currently signed in');
    console.log('🔥 Development Mode: Mock email verification sent');
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));
  },

  // Update user profile (mock)
  updateUserProfile: async (updates: { displayName?: string; photoURL?: string }): Promise<void> => {
    if (!currentUser) throw new Error('No user is currently signed in');

    if (updates.displayName !== undefined) {
      currentUser.displayName = updates.displayName;
    }
    if (updates.photoURL !== undefined) {
      currentUser.photoURL = updates.photoURL;
    }

    // Notify auth state listeners
    authStateCallbacks.forEach(callback => callback(currentUser));

    console.log('🔥 Development Mode: Mock profile update successful', updates);
  },

  // Update password (mock)
  updateUserPassword: async (newPassword: string): Promise<void> => {
    if (!currentUser) throw new Error('No user is currently signed in');
    if (newPassword.length < 6) throw new Error('Password must be at least 6 characters');

    console.log('🔥 Development Mode: Mock password update successful');
  },

  // Reauthenticate with password (mock)
  reauthenticateWithPassword: async (password: string): Promise<void> => {
    if (!currentUser) throw new Error('No user is currently signed in');
    if (!password) throw new Error('Password is required');

    console.log('🔥 Development Mode: Mock reauthentication successful');
  },

  // Check if email is verified
  isEmailVerified: (): boolean => {
    return currentUser?.emailVerified ?? false;
  },

  // Get user metadata
  getUserMetadata: () => {
    if (!currentUser) return null;

    return {
      creationTime: currentUser.metadata.creationTime,
      lastSignInTime: currentUser.metadata.lastSignInTime,
      isEmailVerified: currentUser.emailVerified,
    };
  },
};

// Check if we should use development mode
export const shouldUseDevelopmentAuth = (): boolean => {
  return import.meta.env.DEV &&
         import.meta.env.VITE_FIREBASE_USE_EMULATOR === 'true' &&
         import.meta.env.VITE_FIREBASE_API_KEY === 'demo-key';
};

// Development mode notice
if (shouldUseDevelopmentAuth()) {
  console.log(
    '🔥 Firebase Development Mode Active\n' +
    'Using mock authentication service for development.\n' +
    'To use real Firebase:\n' +
    '1. Set up a Firebase project\n' +
    '2. Update VITE_FIREBASE_* environment variables in .env\n' +
    '3. Set VITE_FIREBASE_USE_EMULATOR=false'
  );
}