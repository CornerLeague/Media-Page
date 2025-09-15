import { UserPreferences, OnboardingState, DEFAULT_USER_SETTINGS, ONBOARDING_STEPS } from '../types/onboarding-types';

const STORAGE_KEYS = {
  USER_PREFERENCES: 'corner-league-user-preferences',
  ONBOARDING_STATE: 'corner-league-onboarding-state',
  ONBOARDING_COMPLETED: 'corner-league-onboarding-completed',
} as const;

export class OnboardingStorage {
  /**
   * Save user preferences to local storage
   */
  static saveUserPreferences(preferences: UserPreferences): void {
    try {
      const data = {
        ...preferences,
        updatedAt: new Date().toISOString(),
      };
      localStorage.setItem(STORAGE_KEYS.USER_PREFERENCES, JSON.stringify(data));
    } catch (error) {
      console.error('Failed to save user preferences:', error);
    }
  }

  /**
   * Load user preferences from local storage
   */
  static loadUserPreferences(): UserPreferences | null {
    try {
      const data = localStorage.getItem(STORAGE_KEYS.USER_PREFERENCES);
      if (!data) return null;

      const preferences = JSON.parse(data) as UserPreferences;
      return this.validateUserPreferences(preferences) ? preferences : null;
    } catch (error) {
      console.error('Failed to load user preferences:', error);
      return null;
    }
  }

  /**
   * Save onboarding state to local storage
   */
  static saveOnboardingState(state: OnboardingState): void {
    try {
      localStorage.setItem(STORAGE_KEYS.ONBOARDING_STATE, JSON.stringify(state));
    } catch (error) {
      console.error('Failed to save onboarding state:', error);
    }
  }

  /**
   * Load onboarding state from local storage
   */
  static loadOnboardingState(): OnboardingState | null {
    try {
      const data = localStorage.getItem(STORAGE_KEYS.ONBOARDING_STATE);
      if (!data) return null;

      const state = JSON.parse(data) as OnboardingState;
      return this.validateOnboardingState(state) ? state : null;
    } catch (error) {
      console.error('Failed to load onboarding state:', error);
      return null;
    }
  }

  /**
   * Mark onboarding as completed
   */
  static setOnboardingCompleted(completed: boolean = true): void {
    try {
      localStorage.setItem(STORAGE_KEYS.ONBOARDING_COMPLETED, JSON.stringify({
        completed,
        completedAt: completed ? new Date().toISOString() : null,
      }));
    } catch (error) {
      console.error('Failed to set onboarding completion status:', error);
    }
  }

  /**
   * Check if onboarding has been completed
   */
  static isOnboardingCompleted(): boolean {
    try {
      const data = localStorage.getItem(STORAGE_KEYS.ONBOARDING_COMPLETED);
      if (!data) return false;

      const status = JSON.parse(data);
      return status.completed === true;
    } catch (error) {
      console.error('Failed to check onboarding completion status:', error);
      return false;
    }
  }

  /**
   * Clear all onboarding data
   */
  static clearAll(): void {
    try {
      Object.values(STORAGE_KEYS).forEach(key => {
        localStorage.removeItem(key);
      });
    } catch (error) {
      console.error('Failed to clear onboarding data:', error);
    }
  }

  /**
   * Create default onboarding state
   */
  static createDefaultOnboardingState(): OnboardingState {
    return {
      currentStep: 0,
      steps: [...ONBOARDING_STEPS],
      userPreferences: {
        id: crypto.randomUUID(),
        sports: [],
        teams: [],
        preferences: DEFAULT_USER_SETTINGS,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      },
      isComplete: false,
      errors: {},
    };
  }

  /**
   * Validate user preferences structure
   */
  private static validateUserPreferences(preferences: any): preferences is UserPreferences {
    return (
      preferences &&
      typeof preferences === 'object' &&
      typeof preferences.id === 'string' &&
      Array.isArray(preferences.sports) &&
      Array.isArray(preferences.teams) &&
      preferences.preferences &&
      typeof preferences.preferences === 'object'
    );
  }

  /**
   * Validate onboarding state structure
   */
  private static validateOnboardingState(state: any): state is OnboardingState {
    return (
      state &&
      typeof state === 'object' &&
      typeof state.currentStep === 'number' &&
      Array.isArray(state.steps) &&
      state.userPreferences &&
      typeof state.userPreferences === 'object' &&
      typeof state.isComplete === 'boolean' &&
      typeof state.errors === 'object'
    );
  }

  /**
   * Get storage usage information
   */
  static getStorageInfo(): { used: number; available: number; percentage: number } {
    try {
      let used = 0;
      Object.values(STORAGE_KEYS).forEach(key => {
        const data = localStorage.getItem(key);
        if (data) {
          used += new Blob([data]).size;
        }
      });

      // Estimate available storage (most browsers allow ~5MB for localStorage)
      const available = 5 * 1024 * 1024; // 5MB in bytes
      const percentage = (used / available) * 100;

      return { used, available, percentage };
    } catch (error) {
      console.error('Failed to get storage info:', error);
      return { used: 0, available: 0, percentage: 0 };
    }
  }
}