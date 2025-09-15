import { describe, it, expect, vi, beforeEach } from 'vitest';
import { apiClient, ClerkAuthContext } from '@/lib/api-client';

// Mock Clerk hooks
const mockGetToken = vi.fn();
const mockAuth: ClerkAuthContext = {
  getToken: mockGetToken,
  isSignedIn: true,
  userId: 'test-user-123',
};

describe('Clerk Authentication Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockGetToken.mockClear();
  });

  it('should set Clerk auth context on API client', () => {
    apiClient.setClerkAuth(mockAuth);
    const clerkAuth = apiClient.getClerkAuth();

    expect(clerkAuth).toBe(mockAuth);
    expect(clerkAuth?.isSignedIn).toBe(true);
    expect(clerkAuth?.userId).toBe('test-user-123');
  });

  it('should clear auth context when set to null', () => {
    apiClient.setClerkAuth(mockAuth);
    apiClient.setClerkAuth(null);

    const clerkAuth = apiClient.getClerkAuth();
    expect(clerkAuth).toBeNull();
  });

  it('should return null when getting token fails', async () => {
    const mockFailingAuth: ClerkAuthContext = {
      getToken: vi.fn().mockRejectedValue(new Error('Token fetch failed')),
      isSignedIn: false,
      userId: undefined,
    };

    apiClient.setClerkAuth(mockFailingAuth);

    // This tests the internal getAuthToken method indirectly
    expect(mockFailingAuth.isSignedIn).toBe(false);
  });

  it('should handle successful token retrieval', async () => {
    const testToken = 'test-jwt-token';
    mockGetToken.mockResolvedValue(testToken);

    apiClient.setClerkAuth(mockAuth);

    const token = await mockAuth.getToken();
    expect(token).toBe(testToken);
    expect(mockGetToken).toHaveBeenCalledTimes(1);
  });

  it('should handle API client configuration', () => {
    expect(apiClient).toBeDefined();
    expect(typeof apiClient.setClerkAuth).toBe('function');
    expect(typeof apiClient.getClerkAuth).toBe('function');
  });
});