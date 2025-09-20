/**
 * Firebase Configuration and Initialization
 *
 * This module initializes Firebase authentication and provides
 * configuration for the Corner League Media application.
 */

import { initializeApp } from 'firebase/app';
import {
  getAuth,
  connectAuthEmulator,
  Auth,
  GoogleAuthProvider,
  signInWithPopup,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  sendPasswordResetEmail,
  sendEmailVerification,
  updateProfile,
  updatePassword,
  reauthenticateWithCredential,
  EmailAuthProvider,
  User
} from 'firebase/auth';
import { getFirebaseErrorMessage } from './firebase-errors';
import { devAuthService, shouldUseDevelopmentAuth } from './firebase-dev';
import {
  getFirestore,
  connectFirestoreEmulator,
  Firestore
} from 'firebase/firestore';

// Firebase configuration from environment variables
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

// Debug Firebase configuration in development
if (import.meta.env.DEV) {
  console.log('Firebase Configuration:', {
    apiKey: firebaseConfig.apiKey ? '[PRESENT]' : '[MISSING]',
    authDomain: firebaseConfig.authDomain || '[MISSING]',
    projectId: firebaseConfig.projectId || '[MISSING]',
    storageBucket: firebaseConfig.storageBucket || '[MISSING]',
    messagingSenderId: firebaseConfig.messagingSenderId || '[MISSING]',
    appId: firebaseConfig.appId || '[MISSING]'
  });
}

// Validate required environment variables
const requiredEnvVars = [
  'VITE_FIREBASE_API_KEY',
  'VITE_FIREBASE_AUTH_DOMAIN',
  'VITE_FIREBASE_PROJECT_ID'
];

const missingEnvVars = requiredEnvVars.filter(
  envVar => !import.meta.env[envVar]
);

if (missingEnvVars.length > 0) {
  console.warn(
    `Missing Firebase environment variables: ${missingEnvVars.join(', ')}. ` +
    'Authentication may not work properly.'
  );
}

// Initialize Firebase
// For development with demo/invalid credentials, we'll rely on emulator mode
let app;
try {
  app = initializeApp(firebaseConfig);
} catch (error) {
  console.warn('Firebase initialization failed with provided config:', error);
  // For development, initialize with minimal config if emulator is enabled
  if (import.meta.env.DEV && import.meta.env.VITE_FIREBASE_USE_EMULATOR === 'true') {
    console.log('Initializing Firebase with demo project for emulator use');
    app = initializeApp({
      apiKey: 'demo-key',
      authDomain: 'demo-project.firebaseapp.com',
      projectId: 'demo-project',
    });
  } else {
    throw error;
  }
}

// Initialize Firebase Authentication
export const auth: Auth = getAuth(app);

// Initialize Firestore
export const db: Firestore = getFirestore(app);

// Configure emulators for local development
if (import.meta.env.DEV && import.meta.env.VITE_FIREBASE_USE_EMULATOR === 'true') {
  try {
    // Check if already connected to avoid multiple connections
    if (!auth.config.emulator) {
      connectAuthEmulator(auth, 'http://localhost:9099', { disableWarnings: true });
      console.log('Connected to Firebase Auth emulator');
    }

    // Connect to Firestore emulator - need to check if not already connected
    try {
      connectFirestoreEmulator(db, 'localhost', 8080);
      console.log('Connected to Firebase Firestore emulator');
    } catch (firestoreError) {
      // Ignore if already connected
      if (!firestoreError.message?.includes('already')) {
        console.warn('Firestore emulator connection failed:', firestoreError);
      }
    }
  } catch (error) {
    console.warn('Failed to connect to Firebase emulators:', error);
  }
}

// Google Auth Provider
export const googleProvider = new GoogleAuthProvider();
googleProvider.addScope('email');
googleProvider.addScope('profile');

// Authentication helper functions
export const authService = {
  // Sign in with Google
  signInWithGoogle: async (): Promise<User> => {
    // Use development auth service if in dev mode
    if (shouldUseDevelopmentAuth()) {
      return devAuthService.signInWithGoogle() as Promise<User>;
    }

    try {
      const result = await signInWithPopup(auth, googleProvider);
      return result.user;
    } catch (error) {
      throw new Error(getFirebaseErrorMessage(error));
    }
  },

  // Sign in with email and password
  signInWithEmail: async (email: string, password: string): Promise<User> => {
    // Use development auth service if in dev mode
    if (shouldUseDevelopmentAuth()) {
      return devAuthService.signInWithEmail(email, password) as Promise<User>;
    }

    try {
      const result = await signInWithEmailAndPassword(auth, email, password);
      return result.user;
    } catch (error) {
      throw new Error(getFirebaseErrorMessage(error));
    }
  },

  // Create account with email and password
  createAccountWithEmail: async (email: string, password: string): Promise<User> => {
    // Use development auth service if in dev mode
    if (shouldUseDevelopmentAuth()) {
      return devAuthService.createAccountWithEmail(email, password) as Promise<User>;
    }

    try {
      const result = await createUserWithEmailAndPassword(auth, email, password);
      return result.user;
    } catch (error) {
      throw new Error(getFirebaseErrorMessage(error));
    }
  },

  // Sign out
  signOut: async (): Promise<void> => {
    // Use development auth service if in dev mode
    if (shouldUseDevelopmentAuth()) {
      return devAuthService.signOut();
    }

    try {
      await signOut(auth);
    } catch (error) {
      throw new Error(getFirebaseErrorMessage(error));
    }
  },

  // Get current user
  getCurrentUser: (): User | null => {
    // Use development auth service if in dev mode
    if (shouldUseDevelopmentAuth()) {
      return devAuthService.getCurrentUser() as User | null;
    }

    return auth.currentUser;
  },

  // Get ID token for API calls
  getIdToken: async (forceRefresh = false): Promise<string | null> => {
    // Use development auth service if in dev mode
    if (shouldUseDevelopmentAuth()) {
      return devAuthService.getIdToken(forceRefresh);
    }

    const user = auth.currentUser;
    if (!user) return null;

    try {
      return await user.getIdToken(forceRefresh);
    } catch (error) {
      console.error('Failed to get Firebase ID token:', error);
      return null;
    }
  },

  // Listen to auth state changes
  onAuthStateChanged: (callback: (user: User | null) => void) => {
    // Use development auth service if in dev mode
    if (shouldUseDevelopmentAuth()) {
      return devAuthService.onAuthStateChanged(callback as any);
    }

    return onAuthStateChanged(auth, callback);
  },

  // Password reset
  sendPasswordResetEmail: async (email: string): Promise<void> => {
    try {
      await sendPasswordResetEmail(auth, email);
    } catch (error) {
      throw new Error(getFirebaseErrorMessage(error));
    }
  },

  // Email verification
  sendEmailVerification: async (): Promise<void> => {
    try {
      const user = auth.currentUser;
      if (!user) throw new Error('No user is currently signed in');
      await sendEmailVerification(user);
    } catch (error) {
      throw new Error(getFirebaseErrorMessage(error));
    }
  },

  // Update user profile
  updateUserProfile: async (updates: { displayName?: string; photoURL?: string }): Promise<void> => {
    try {
      const user = auth.currentUser;
      if (!user) throw new Error('No user is currently signed in');
      await updateProfile(user, updates);
    } catch (error) {
      throw new Error(getFirebaseErrorMessage(error));
    }
  },

  // Update password
  updateUserPassword: async (newPassword: string): Promise<void> => {
    try {
      const user = auth.currentUser;
      if (!user) throw new Error('No user is currently signed in');
      await updatePassword(user, newPassword);
    } catch (error) {
      throw new Error(getFirebaseErrorMessage(error));
    }
  },

  // Reauthenticate user
  reauthenticateWithPassword: async (password: string): Promise<void> => {
    try {
      const user = auth.currentUser;
      if (!user || !user.email) throw new Error('No user is currently signed in');

      const credential = EmailAuthProvider.credential(user.email, password);
      await reauthenticateWithCredential(user, credential);
    } catch (error) {
      throw new Error(getFirebaseErrorMessage(error));
    }
  },

  // Check if email is verified
  isEmailVerified: (): boolean => {
    return auth.currentUser?.emailVerified ?? false;
  },

  // Get user metadata
  getUserMetadata: () => {
    const user = auth.currentUser;
    if (!user) return null;

    return {
      creationTime: user.metadata.creationTime,
      lastSignInTime: user.metadata.lastSignInTime,
      isEmailVerified: user.emailVerified,
    };
  },
};

export default app;