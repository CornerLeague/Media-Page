/**
 * Mock Firebase Auth Utilities
 *
 * Creates mock implementations of Firebase authentication
 * for testing authentication-related error scenarios.
 */

import { vi } from 'vitest';

export interface MockUser {
  uid: string;
  email: string | null;
  displayName: string | null;
  emailVerified: boolean;
}

export interface MockAuthContext {
  user: MockUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: Error | null;
  getIdToken: () => Promise<string>;
  signOut: () => Promise<void>;
}

export function createMockFirebaseAuth(
  initialState: Partial<MockAuthContext> = {}
): MockAuthContext {
  const defaultUser: MockUser = {
    uid: 'test-user-123',
    email: 'test@example.com',
    displayName: 'Test User',
    emailVerified: true,
  };

  const defaultState: MockAuthContext = {
    user: defaultUser,
    isAuthenticated: true,
    isLoading: false,
    error: null,
    getIdToken: vi.fn().mockResolvedValue('mock-token'),
    signOut: vi.fn().mockResolvedValue(undefined),
  };

  return {
    ...defaultState,
    ...initialState,
  };
}

export function createUnauthenticatedFirebaseAuth(): MockAuthContext {
  return {
    user: null,
    isAuthenticated: false,
    isLoading: false,
    error: null,
    getIdToken: vi.fn().mockRejectedValue(new Error('User not authenticated')),
    signOut: vi.fn().mockResolvedValue(undefined),
  };
}

export function createLoadingFirebaseAuth(): MockAuthContext {
  return {
    user: null,
    isAuthenticated: false,
    isLoading: true,
    error: null,
    getIdToken: vi.fn().mockRejectedValue(new Error('Still loading')),
    signOut: vi.fn().mockResolvedValue(undefined),
  };
}

export function createErrorFirebaseAuth(error: Error): MockAuthContext {
  return {
    user: null,
    isAuthenticated: false,
    isLoading: false,
    error,
    getIdToken: vi.fn().mockRejectedValue(error),
    signOut: vi.fn().mockResolvedValue(undefined),
  };
}

export function createExpiredTokenFirebaseAuth(): MockAuthContext {
  const user: MockUser = {
    uid: 'test-user-123',
    email: 'test@example.com',
    displayName: 'Test User',
    emailVerified: true,
  };

  return {
    user,
    isAuthenticated: true,
    isLoading: false,
    error: null,
    getIdToken: vi.fn().mockRejectedValue(new Error('Token expired')),
    signOut: vi.fn().mockResolvedValue(undefined),
  };
}

export function createUnverifiedEmailFirebaseAuth(): MockAuthContext {
  const user: MockUser = {
    uid: 'test-user-123',
    email: 'test@example.com',
    displayName: 'Test User',
    emailVerified: false,
  };

  return {
    user,
    isAuthenticated: true,
    isLoading: false,
    error: null,
    getIdToken: vi.fn().mockResolvedValue('mock-token'),
    signOut: vi.fn().mockResolvedValue(undefined),
  };
}

export function createNetworkErrorFirebaseAuth(): MockAuthContext {
  const networkError = new Error('Network error');
  (networkError as any).code = 'auth/network-request-failed';

  return {
    user: null,
    isAuthenticated: false,
    isLoading: false,
    error: networkError,
    getIdToken: vi.fn().mockRejectedValue(networkError),
    signOut: vi.fn().mockResolvedValue(undefined),
  };
}

export function createRateLimitFirebaseAuth(): MockAuthContext {
  const rateLimitError = new Error('Too many requests');
  (rateLimitError as any).code = 'auth/too-many-requests';

  return {
    user: null,
    isAuthenticated: false,
    isLoading: false,
    error: rateLimitError,
    getIdToken: vi.fn().mockRejectedValue(rateLimitError),
    signOut: vi.fn().mockResolvedValue(undefined),
  };
}

export default {
  createMockFirebaseAuth,
  createUnauthenticatedFirebaseAuth,
  createLoadingFirebaseAuth,
  createErrorFirebaseAuth,
  createExpiredTokenFirebaseAuth,
  createUnverifiedEmailFirebaseAuth,
  createNetworkErrorFirebaseAuth,
  createRateLimitFirebaseAuth,
};