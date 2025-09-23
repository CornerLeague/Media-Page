/**
 * Onboarding Storage Utilities
 *
 * Provides localStorage-based fallback functionality for onboarding flow
 * when the backend API is unavailable or failing.
 */

import { OnboardingStatus, OnboardingSport, OnboardingTeam } from './api-client';

const STORAGE_KEYS = {
  ONBOARDING_STATUS: 'corner-league-onboarding-status',
  ONBOARDING_PROGRESS: 'corner-league-onboarding-progress',
  USER_FIRST_VISIT: 'corner-league-user-first-visit',
} as const;

// Default onboarding status for new users
const DEFAULT_ONBOARDING_STATUS: OnboardingStatus = {
  currentStep: 1,
  totalSteps: 5,
  isComplete: false,
  selectedSports: [],
  selectedTeams: [],
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

/**
 * Get onboarding status from localStorage
 */
export const getLocalOnboardingStatus = (): OnboardingStatus | null => {
  try {
    const stored = localStorage.getItem(STORAGE_KEYS.ONBOARDING_STATUS);
    if (!stored) return null;

    const parsed = JSON.parse(stored);

    // Validate the structure to ensure it matches our expected format
    if (typeof parsed === 'object' &&
        typeof parsed.currentStep === 'number' &&
        typeof parsed.isComplete === 'boolean') {
      return parsed as OnboardingStatus;
    }

    return null;
  } catch (error) {
    console.warn('Failed to parse stored onboarding status:', error);
    return null;
  }
};

/**
 * Set onboarding status in localStorage
 */
export const setLocalOnboardingStatus = (status: OnboardingStatus): void => {
  try {
    localStorage.setItem(STORAGE_KEYS.ONBOARDING_STATUS, JSON.stringify(status));
  } catch (error) {
    console.warn('Failed to store onboarding status:', error);
  }
};

/**
 * Update specific onboarding step data in localStorage
 */
export const updateLocalOnboardingStep = (
  step: number,
  data: Partial<Pick<OnboardingStatus, 'selectedSports' | 'selectedTeams' | 'preferences'>>
): void => {
  try {
    const current = getLocalOnboardingStatus() || DEFAULT_ONBOARDING_STATUS;
    const updated: OnboardingStatus = {
      ...current,
      currentStep: Math.max(step, current.currentStep), // Only advance, never go backwards
      ...data,
    };

    setLocalOnboardingStatus(updated);
  } catch (error) {
    console.warn('Failed to update onboarding step:', error);
  }
};

/**
 * Mark onboarding as complete in localStorage
 */
export const completeLocalOnboarding = (): void => {
  try {
    const current = getLocalOnboardingStatus() || DEFAULT_ONBOARDING_STATUS;
    const completed: OnboardingStatus = {
      ...current,
      currentStep: 5,
      isComplete: true,
    };

    setLocalOnboardingStatus(completed);
  } catch (error) {
    console.warn('Failed to complete onboarding:', error);
  }
};

/**
 * Check if this is the user's first visit
 */
export const isFirstVisit = (): boolean => {
  try {
    return !localStorage.getItem(STORAGE_KEYS.USER_FIRST_VISIT);
  } catch (error) {
    console.warn('Failed to check first visit status:', error);
    return true; // Default to first visit if we can't check
  }
};

/**
 * Mark that the user has visited before
 */
export const markUserVisited = (): void => {
  try {
    localStorage.setItem(STORAGE_KEYS.USER_FIRST_VISIT, 'true');
  } catch (error) {
    console.warn('Failed to mark user as visited:', error);
  }
};

/**
 * Clear all onboarding data from localStorage
 */
export const clearLocalOnboardingData = (): void => {
  try {
    Object.values(STORAGE_KEYS).forEach(key => {
      localStorage.removeItem(key);
    });
  } catch (error) {
    console.warn('Failed to clear onboarding data:', error);
  }
};

/**
 * Get default onboarding status for new users
 */
export const getDefaultOnboardingStatus = (): OnboardingStatus => {
  return { ...DEFAULT_ONBOARDING_STATUS };
};

/**
 * Determine navigation target based on stored onboarding state and API availability
 */
export const determineOnboardingRoute = (
  apiStatus: OnboardingStatus | null,
  apiError: boolean,
  isNewUser?: boolean
): string => {
  // If API is working, use API data
  if (!apiError && apiStatus) {
    if (apiStatus.isComplete) {
      return '/';
    }
    return `/onboarding/step/${apiStatus.currentStep}`;
  }

  // API is failing, use fallback logic
  const localStatus = getLocalOnboardingStatus();

  // For new users (first visit), start onboarding
  if (isNewUser || isFirstVisit()) {
    markUserVisited();
    return '/onboarding/step/1';
  }

  // For returning users, check local storage
  if (localStatus) {
    if (localStatus.isComplete) {
      return '/';
    }
    return `/onboarding/step/${localStatus.currentStep}`;
  }

  // Default fallback - assume returning user and go to dashboard
  return '/';
};

/**
 * Sync local data with API when connection is restored
 */
export const syncWithApi = async (
  apiClient: any,
  localStatus: OnboardingStatus
): Promise<boolean> => {
  try {
    // Attempt to update the API with local data
    if (localStatus.selectedSports.length > 0) {
      await apiClient.updateOnboardingStep({
        step: 2,
        data: { sports: localStatus.selectedSports }
      });
    }

    if (localStatus.selectedTeams.length > 0) {
      await apiClient.updateOnboardingStep({
        step: 3,
        data: { teams: localStatus.selectedTeams }
      });
    }

    if (localStatus.currentStep >= 4) {
      await apiClient.updateOnboardingStep({
        step: 4,
        data: { preferences: localStatus.preferences }
      });
    }

    if (localStatus.isComplete) {
      // Complete onboarding on the server
      await apiClient.completeOnboarding({
        sports: localStatus.selectedSports.map(s => ({
          sportId: s.sportId,
          name: s.sportId, // Will be enriched by API
          rank: s.rank,
          hasTeams: true, // Default assumption
        })),
        teams: localStatus.selectedTeams.map(t => ({
          teamId: t.teamId,
          name: t.teamId, // Will be enriched by API
          sportId: t.sportId,
          league: 'Unknown', // Will be enriched by API
          affinityScore: t.affinityScore,
        })),
        preferences: localStatus.preferences,
      });
    }

    return true;
  } catch (error) {
    console.warn('Failed to sync local data with API:', error);
    return false;
  }
};