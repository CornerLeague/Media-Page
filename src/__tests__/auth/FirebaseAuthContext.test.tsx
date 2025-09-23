import React, { useEffect } from 'react';
import { act, render, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import type { User } from 'firebase/auth';

import {
  FirebaseAuthProvider,
  useFirebaseAuth,
  type FirebaseAuthContextType,
} from '@/contexts/FirebaseAuthContext';

class MockUser {
  uid = 'mock-uid';
  email = 'mock.user@example.com';
  displayName: string | null = 'Mock User';
  photoURL: string | null = 'https://example.com/avatar.png';
  emailVerified = true;
  metadata = {
    creationTime: new Date().toISOString(),
    lastSignInTime: new Date().toISOString(),
  };

  constructor(
    private readonly getIdTokenImpl: (forceRefresh?: boolean) => Promise<string>,
    private readonly reloadImpl: () => Promise<void>,
  ) {}

  async getIdToken(forceRefresh?: boolean): Promise<string> {
    return this.getIdTokenImpl(forceRefresh);
  }

  async reload(): Promise<void> {
    await this.reloadImpl();
  }
}

let currentUser: MockUser;
let getIdTokenSpy: ReturnType<typeof vi.fn>;
let reloadSpy: ReturnType<typeof vi.fn>;

const updateProfileMock = vi.fn(
  async (updates: { displayName?: string; photoURL?: string }) => {
    if (updates.displayName !== undefined) {
      currentUser.displayName = updates.displayName;
    }
    if (updates.photoURL !== undefined) {
      currentUser.photoURL = updates.photoURL;
    }
  },
);

const onAuthStateChangedMock = vi.fn(
  (callback: (user: User | null) => void) => {
    callback(currentUser as unknown as User);
    return () => {};
  },
);

const getCurrentUserMock = vi.fn(() => currentUser as unknown as User);

vi.mock('@/lib/firebase', () => ({
  authService: {
    onAuthStateChanged: (
      callback: Parameters<typeof onAuthStateChangedMock>[0],
    ) => onAuthStateChangedMock(callback),
    updateUserProfile: (
      updates: Parameters<typeof updateProfileMock>[0],
    ) => updateProfileMock(updates),
    getCurrentUser: () => getCurrentUserMock(),
    signInWithGoogle: vi.fn(),
    signInWithEmail: vi.fn(),
    createAccountWithEmail: vi.fn(),
    signOut: vi.fn(),
    getIdToken: vi.fn(),
    sendPasswordResetEmail: vi.fn(),
    sendEmailVerification: vi.fn(),
    updateUserPassword: vi.fn(),
    reauthenticateWithPassword: vi.fn(),
    isEmailVerified: vi.fn(() => true),
    getUserMetadata: vi.fn(() => null),
  },
}));

describe('FirebaseAuthProvider updateUserProfile', () => {
  beforeEach(() => {
    getIdTokenSpy = vi.fn().mockResolvedValue('mock-token');
    reloadSpy = vi.fn().mockResolvedValue(undefined);
    currentUser = new MockUser(getIdTokenSpy, reloadSpy);

    updateProfileMock.mockClear();
    onAuthStateChangedMock.mockClear();
    getCurrentUserMock.mockClear();

    onAuthStateChangedMock.mockImplementation((callback: (user: User | null) => void) => {
      callback(currentUser as unknown as User);
      return () => {};
    });

    getCurrentUserMock.mockImplementation(
      () => currentUser as unknown as User,
    );
  });

  it('preserves Firebase user prototype methods after profile updates', async () => {
    let latestContext: FirebaseAuthContextType | null = null;

    const TestConsumer: React.FC = () => {
      const auth = useFirebaseAuth();

      useEffect(() => {
        latestContext = auth;
      }, [auth]);

      return null;
    };

    render(
      <FirebaseAuthProvider>
        <TestConsumer />
      </FirebaseAuthProvider>,
    );

    await waitFor(() => {
      expect(latestContext?.user).toBeTruthy();
    });

    const initialUser = latestContext!.user!;
    expect(initialUser).toBeInstanceOf(MockUser);
    await expect(initialUser.getIdToken()).resolves.toBe('mock-token');

    await act(async () => {
      await latestContext!.updateUserProfile({ displayName: 'Updated Name' });
    });

    expect(updateProfileMock).toHaveBeenCalledWith({ displayName: 'Updated Name' });
    expect(reloadSpy).toHaveBeenCalledTimes(1);

    await waitFor(() => {
      expect(latestContext?.user?.displayName).toBe('Updated Name');
    });

    const updatedUser = latestContext!.user!;
    expect(updatedUser).not.toBe(initialUser);
    expect(updatedUser).toBeInstanceOf(MockUser);
    expect(
      Object.prototype.hasOwnProperty.call(updatedUser, 'getIdToken'),
    ).toBe(false);
    await expect(updatedUser.getIdToken()).resolves.toBe('mock-token');
  });
});
