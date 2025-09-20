/**
 * Firebase Error Utilities
 *
 * Provides user-friendly error messages for Firebase Authentication errors.
 */

import { AuthError } from 'firebase/auth';

// Firebase Auth error codes and their user-friendly messages
const FIREBASE_ERROR_MESSAGES: Record<string, string> = {
  // Authentication errors
  'auth/user-not-found': 'No account found with this email address.',
  'auth/wrong-password': 'Incorrect password. Please try again.',
  'auth/invalid-email': 'Please enter a valid email address.',
  'auth/user-disabled': 'This account has been disabled. Please contact support.',
  'auth/too-many-requests': 'Too many failed attempts. Please try again later.',
  'auth/operation-not-allowed': 'This sign-in method is not enabled.',

  // Account creation errors
  'auth/email-already-in-use': 'An account with this email already exists.',
  'auth/weak-password': 'Password should be at least 6 characters long.',
  'auth/account-exists-with-different-credential': 'An account already exists with the same email but different sign-in credentials.',

  // Password reset errors
  'auth/invalid-action-code': 'The action code is invalid. This can happen if the code is malformed or has already been used.',
  'auth/expired-action-code': 'The action code has expired.',

  // Email verification errors
  'auth/invalid-verification-code': 'The verification code is invalid.',
  'auth/invalid-verification-id': 'The verification ID is invalid.',

  // Profile update errors
  'auth/requires-recent-login': 'This operation requires recent authentication. Please sign in again.',

  // Network and general errors
  'auth/network-request-failed': 'Network error. Please check your connection and try again.',
  'auth/internal-error': 'An internal error occurred. Please try again.',
  'auth/quota-exceeded': 'Project quota exceeded. Please try again later.',

  // Popup and redirect errors
  'auth/popup-blocked': 'Popup was blocked by the browser. Please allow popups and try again.',
  'auth/popup-closed-by-user': 'Sign-in was cancelled.',
  'auth/cancelled-popup-request': 'Sign-in was cancelled.',
  'auth/redirect-cancelled-by-user': 'Sign-in was cancelled.',

  // Token errors
  'auth/invalid-user-token': 'Your session has expired. Please sign in again.',
  'auth/user-token-expired': 'Your session has expired. Please sign in again.',
  'auth/null-user': 'No user is currently signed in.',

  // Custom errors
  'auth/missing-email': 'Email address is required.',
  'auth/missing-password': 'Password is required.',
  'auth/password-mismatch': 'Passwords do not match.',
  'auth/invalid-display-name': 'Display name cannot be empty.',
};

/**
 * Converts Firebase auth errors to user-friendly messages
 */
export function getFirebaseErrorMessage(error: unknown): string {
  if (!error) return 'An unknown error occurred.';

  // Handle Firebase AuthError
  if (isAuthError(error)) {
    const message = FIREBASE_ERROR_MESSAGES[error.code];
    if (message) return message;

    // Fallback to original message if we don't have a custom one
    return error.message || 'An authentication error occurred.';
  }

  // Handle regular Error objects
  if (error instanceof Error) {
    return error.message;
  }

  // Handle string errors
  if (typeof error === 'string') {
    return error;
  }

  return 'An unknown error occurred.';
}

/**
 * Type guard to check if an error is a Firebase AuthError
 */
function isAuthError(error: unknown): error is AuthError {
  return (
    typeof error === 'object' &&
    error !== null &&
    'code' in error &&
    typeof (error as any).code === 'string' &&
    (error as any).code.startsWith('auth/')
  );
}

/**
 * Creates a standardized error object for auth operations
 */
export function createAuthError(code: string, message?: string): AuthError {
  const error = new Error(message || FIREBASE_ERROR_MESSAGES[code] || 'Authentication error') as AuthError;
  error.code = code;
  return error;
}

/**
 * Validates email format
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Validates password strength
 */
export function validatePassword(password: string): {
  isValid: boolean;
  errors: string[];
} {
  const errors: string[] = [];

  if (password.length < 6) {
    errors.push('Password must be at least 6 characters long');
  }

  if (password.length > 128) {
    errors.push('Password must be less than 128 characters');
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
}

/**
 * Validates display name
 */
export function validateDisplayName(displayName: string): {
  isValid: boolean;
  error?: string;
} {
  if (!displayName || displayName.trim().length === 0) {
    return {
      isValid: false,
      error: 'Display name cannot be empty',
    };
  }

  if (displayName.length > 50) {
    return {
      isValid: false,
      error: 'Display name must be less than 50 characters',
    };
  }

  return { isValid: true };
}

/**
 * Format Firebase Auth provider names for display
 */
export function getProviderDisplayName(providerId: string): string {
  const providers: Record<string, string> = {
    'google.com': 'Google',
    'facebook.com': 'Facebook',
    'twitter.com': 'Twitter',
    'github.com': 'GitHub',
    'apple.com': 'Apple',
    'microsoft.com': 'Microsoft',
    'yahoo.com': 'Yahoo',
    'password': 'Email/Password',
  };

  return providers[providerId] || providerId;
}