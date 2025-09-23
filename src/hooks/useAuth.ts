/**
 * useAuth Hook
 *
 * Provides enhanced authentication state with user preferences from onboarding.
 * This hook combines Firebase authentication with user preference data for
 * dashboard personalization as required by section 1.2.
 */

import { useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useFirebaseAuth } from '@/contexts/FirebaseAuthContext';
import { useAuthOnboarding } from '@/hooks/useAuthOnboarding';
import { apiClient, createApiQueryClient, type UserProfile } from '@/lib/api-client';
import { getLocalOnboardingStatus } from '@/lib/onboarding-storage';

// Extended user preferences interface for dashboard
export interface UserPreferences {
  // Selected sports from onboarding
  sports: Array<{
    sportId: string;
    name: string;
    rank: number;
    hasTeams: boolean;
  }>;

  // Selected teams from onboarding
  teams: Array<{
    teamId: string;
    name: string;
    sportId: string;
    league: string;
    affinityScore: number;
  }>;

  // Content preferences from onboarding
  preferences: {
    newsTypes: Array<{
      type: string;
      enabled: boolean;
      priority: number;
    }>;
    notifications: {
      push: boolean;
      email: boolean;
      gameReminders: boolean;
      newsAlerts: boolean;
      scoreUpdates: boolean;
    };
    contentFrequency: 'minimal' | 'standard' | 'comprehensive';
  };
}

// Default preferences for fallback
const DEFAULT_PREFERENCES: UserPreferences = {
  sports: [],
  teams: [],
  preferences: {
    newsTypes: [
      { type: 'injuries', enabled: true, priority: 1 },
      { type: 'trades', enabled: true, priority: 2 },
      { type: 'roster', enabled: true, priority: 3 },
      { type: 'scores', enabled: true, priority: 4 },
      { type: 'analysis', enabled: false, priority: 5 },
    ],
    notifications: {
      push: true,
      email: false,
      gameReminders: true,
      newsAlerts: false,
      scoreUpdates: true,
    },
    contentFrequency: 'standard',
  },
};

export interface UseAuthResult {
  // User authentication state
  user: any;
  isLoading: boolean;
  isAuthenticated: boolean;
  isOnboarded: boolean;

  // User preferences for dashboard personalization
  userPreferences: UserPreferences;

  // Firebase auth methods
  signOut: () => Promise<void>;
  getIdToken: (forceRefresh?: boolean) => Promise<string | null>;

  // Status flags
  hasSelectedSports: boolean;
  hasSelectedTeams: boolean;
  shouldShowTeams: boolean;

  // Actions
  refreshUserData: () => void;
}

/**
 * useAuth Hook
 *
 * Combines Firebase authentication with user preferences from backend API
 * and local onboarding storage for comprehensive auth state.
 */
export function useAuth(): UseAuthResult {
  const { user, isLoading: firebaseLoading, isAuthenticated, signOut, getIdToken } = useFirebaseAuth();
  const { isOnboarded, flowState } = useAuthOnboarding();

  // Get query configurations with Firebase auth
  const queryConfigs = createApiQueryClient(
    isAuthenticated ? { getIdToken, isAuthenticated: true, userId: user?.uid } : undefined
  );

  // Fetch user profile from backend API
  const {
    data: userProfile,
    isLoading: profileLoading,
    error: profileError,
    refetch: refetchProfile,
  } = useQuery({
    ...queryConfigs.getCurrentUser(),
    enabled: isAuthenticated && isOnboarded && flowState === 'authenticated',
    retry: 1,
  });

  // Get local onboarding data as fallback
  const localOnboardingData = useMemo(() => {
    if (!isAuthenticated) return null;
    return getLocalOnboardingStatus();
  }, [isAuthenticated]);

  // Determine user preferences from API or local storage
  const userPreferences = useMemo((): UserPreferences => {
    // Try to use backend API data first
    if (userProfile) {
      return {
        sports: [], // Will be populated when backend provides sports data
        teams: [], // Will be populated when backend provides teams data
        preferences: userProfile.preferences,
      };
    }

    // Fallback to local onboarding data
    if (localOnboardingData && (localOnboardingData.selectedSports.length > 0 || localOnboardingData.selectedTeams.length > 0)) {
      return {
        sports: localOnboardingData.selectedSports.map(s => ({
          sportId: s.sportId,
          name: s.sportId, // Will be enriched later
          rank: s.rank,
          hasTeams: true,
        })),
        teams: localOnboardingData.selectedTeams.map(t => ({
          teamId: t.teamId,
          name: t.teamId, // Will be enriched later
          sportId: t.sportId,
          league: 'Unknown',
          affinityScore: t.affinityScore,
        })),
        preferences: localOnboardingData.preferences,
      };
    }

    // Final fallback to defaults
    return DEFAULT_PREFERENCES;
  }, [userProfile, localOnboardingData]);

  // Computed flags
  const hasSelectedSports = userPreferences.sports.length > 0;
  const hasSelectedTeams = userPreferences.teams.length > 0;
  const shouldShowTeams = hasSelectedTeams && isOnboarded;

  // Status flags
  const isLoading = firebaseLoading || profileLoading;

  // Action methods
  const refreshUserData = () => {
    if (isAuthenticated && isOnboarded) {
      refetchProfile();
    }
  };

  return {
    // User authentication state
    user,
    isLoading,
    isAuthenticated,
    isOnboarded,

    // User preferences for dashboard personalization
    userPreferences,

    // Firebase auth methods
    signOut,
    getIdToken,

    // Status flags
    hasSelectedSports,
    hasSelectedTeams,
    shouldShowTeams,

    // Actions
    refreshUserData,
  };
}

export default useAuth;