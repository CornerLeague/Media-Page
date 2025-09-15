/**
 * Migration Utilities
 *
 * This module handles the migration of user data from local storage to the backend database.
 * It provides utilities for data transformation, conflict resolution, and rollback capabilities.
 */

import { UserPreferences } from '../types/onboarding-types';
import { CreateUserRequest, ApiClient, ApiClientError } from '../api-client';
import { LocalStorageMigration, MigrationResult } from '../types/supabase-types';
import { OnboardingStorage } from './localStorage';

export interface MigrationConfig {
  batchSize: number;
  retryAttempts: number;
  retryDelay: number;
  validateData: boolean;
  createBackup: boolean;
}

export const DEFAULT_MIGRATION_CONFIG: MigrationConfig = {
  batchSize: 10,
  retryAttempts: 3,
  retryDelay: 1000,
  validateData: true,
  createBackup: true,
};

export class MigrationManager {
  private apiClient: ApiClient;
  private config: MigrationConfig;

  constructor(apiClient: ApiClient, config: MigrationConfig = DEFAULT_MIGRATION_CONFIG) {
    this.apiClient = apiClient;
    this.config = config;
  }

  /**
   * Migrate user preferences from local storage to backend
   */
  async migrateUserPreferences(clerkUserId: string): Promise<MigrationResult> {
    try {
      console.log('Starting user preferences migration...');

      // Load local storage data
      const localPreferences = OnboardingStorage.loadUserPreferences();
      if (!localPreferences) {
        return {
          success: false,
          migrated_records: 0,
          conflicts: ['No local preferences found'],
        };
      }

      // Create backup if enabled
      let backupData: UserPreferences | undefined;
      if (this.config.createBackup) {
        backupData = { ...localPreferences };
      }

      // Validate local data if enabled
      if (this.config.validateData) {
        const validationResult = this.validateLocalData(localPreferences);
        if (!validationResult.isValid) {
          return {
            success: false,
            migrated_records: 0,
            conflicts: validationResult.errors,
            rollback_data: backupData,
          };
        }
      }

      // Transform local data to API format
      const createUserData = this.transformToApiFormat(localPreferences, clerkUserId);

      // Attempt to create user profile
      const result = await this.createUserWithRetry(createUserData);

      if (result.success) {
        // Mark migration as complete
        this.markMigrationComplete(localPreferences);

        return {
          success: true,
          migrated_records: 1,
          conflicts: [],
        };
      } else {
        return {
          success: false,
          migrated_records: 0,
          conflicts: result.errors || ['Unknown migration error'],
          rollback_data: backupData,
        };
      }
    } catch (error) {
      console.error('Migration failed:', error);
      return {
        success: false,
        migrated_records: 0,
        conflicts: [error instanceof Error ? error.message : 'Unknown error'],
      };
    }
  }

  /**
   * Check for existing user data and handle conflicts
   */
  async checkForConflicts(clerkUserId: string): Promise<{
    hasConflicts: boolean;
    conflicts: string[];
    remoteData?: any;
  }> {
    try {
      // Try to fetch existing user data
      const existingUser = await this.apiClient.getCurrentUser();

      if (existingUser) {
        const localPreferences = OnboardingStorage.loadUserPreferences();
        if (!localPreferences) {
          return { hasConflicts: false, conflicts: [] };
        }

        // Compare local and remote data
        const conflicts = this.detectDataConflicts(localPreferences, existingUser.preferences);

        return {
          hasConflicts: conflicts.length > 0,
          conflicts,
          remoteData: existingUser.preferences,
        };
      }

      return { hasConflicts: false, conflicts: [] };
    } catch (error) {
      if (error instanceof ApiClientError && error.statusCode === 404) {
        // User doesn't exist, no conflicts
        return { hasConflicts: false, conflicts: [] };
      }

      console.error('Error checking for conflicts:', error);
      return {
        hasConflicts: true,
        conflicts: ['Unable to check for existing data'],
      };
    }
  }

  /**
   * Resolve conflicts by merging local and remote data
   */
  async resolveConflicts(
    strategy: 'local-wins' | 'remote-wins' | 'merge' | 'manual',
    localData: UserPreferences,
    remoteData: UserPreferences,
    manualResolution?: Partial<UserPreferences>
  ): Promise<UserPreferences> {
    switch (strategy) {
      case 'local-wins':
        return localData;

      case 'remote-wins':
        return remoteData;

      case 'merge':
        return this.mergeUserPreferences(localData, remoteData);

      case 'manual':
        if (!manualResolution) {
          throw new Error('Manual resolution data is required');
        }
        return { ...localData, ...manualResolution };

      default:
        throw new Error(`Unknown conflict resolution strategy: ${strategy}`);
    }
  }

  /**
   * Rollback migration by restoring local storage data
   */
  async rollbackMigration(backupData: UserPreferences): Promise<void> {
    try {
      OnboardingStorage.saveUserPreferences(backupData);
      OnboardingStorage.setOnboardingCompleted(true);

      // Remove migration markers
      localStorage.removeItem('corner-league-migration-complete');

      console.log('Migration rollback completed');
    } catch (error) {
      console.error('Rollback failed:', error);
      throw new Error('Failed to rollback migration');
    }
  }

  /**
   * Sync preferences between local and remote
   */
  async syncPreferences(): Promise<{
    success: boolean;
    localUpdated: boolean;
    remoteUpdated: boolean;
    errors: string[];
  }> {
    try {
      const localPreferences = OnboardingStorage.loadUserPreferences();
      const remoteUser = await this.apiClient.getCurrentUser();

      if (!localPreferences || !remoteUser) {
        return {
          success: false,
          localUpdated: false,
          remoteUpdated: false,
          errors: ['Missing local or remote data'],
        };
      }

      // Compare timestamps to determine which is newer
      const localTimestamp = new Date(localPreferences.updatedAt).getTime();
      const remoteTimestamp = new Date(remoteUser.updatedAt).getTime();

      let localUpdated = false;
      let remoteUpdated = false;
      const errors: string[] = [];

      if (localTimestamp > remoteTimestamp) {
        // Local is newer, update remote
        try {
          const updateData = this.transformToUpdateFormat(localPreferences);
          await this.apiClient.updateUserPreferences(updateData);
          remoteUpdated = true;
        } catch (error) {
          errors.push(`Failed to update remote: ${error}`);
        }
      } else if (remoteTimestamp > localTimestamp) {
        // Remote is newer, update local
        try {
          OnboardingStorage.saveUserPreferences(remoteUser.preferences);
          localUpdated = true;
        } catch (error) {
          errors.push(`Failed to update local: ${error}`);
        }
      }

      return {
        success: errors.length === 0,
        localUpdated,
        remoteUpdated,
        errors,
      };
    } catch (error) {
      return {
        success: false,
        localUpdated: false,
        remoteUpdated: false,
        errors: [error instanceof Error ? error.message : 'Sync failed'],
      };
    }
  }

  // Private helper methods

  private validateLocalData(preferences: UserPreferences): {
    isValid: boolean;
    errors: string[];
  } {
    const errors: string[] = [];

    if (!preferences.id) {
      errors.push('Missing user ID');
    }

    if (!preferences.sports || preferences.sports.length === 0) {
      errors.push('No sports selected');
    }

    if (!preferences.preferences) {
      errors.push('Missing user preferences');
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  }

  private transformToApiFormat(
    localPreferences: UserPreferences,
    clerkUserId: string
  ): CreateUserRequest {
    return {
      clerkUserId,
      sports: localPreferences.sports || [],
      teams: localPreferences.teams || [],
      preferences: {
        newsTypes: localPreferences.preferences?.newsTypes || [],
        notifications: localPreferences.preferences?.notifications || {
          push: false,
          email: false,
          gameReminders: false,
          newsAlerts: false,
          scoreUpdates: false,
        },
        contentFrequency: localPreferences.preferences?.contentFrequency || 'standard',
      },
    };
  }

  private transformToUpdateFormat(preferences: UserPreferences) {
    return {
      sports: preferences.sports,
      teams: preferences.teams,
      preferences: preferences.preferences,
    };
  }

  private async createUserWithRetry(userData: CreateUserRequest): Promise<{
    success: boolean;
    errors?: string[];
  }> {
    let lastError: Error | null = null;

    for (let attempt = 1; attempt <= this.config.retryAttempts; attempt++) {
      try {
        await this.apiClient.createUser(userData);
        return { success: true };
      } catch (error) {
        lastError = error instanceof Error ? error : new Error(String(error));

        if (attempt < this.config.retryAttempts) {
          // Wait before retrying
          await new Promise(resolve => setTimeout(resolve, this.config.retryDelay * attempt));
        }
      }
    }

    return {
      success: false,
      errors: [lastError?.message || 'Failed to create user after retries'],
    };
  }

  private detectDataConflicts(
    localData: UserPreferences,
    remoteData: UserPreferences
  ): string[] {
    const conflicts: string[] = [];

    // Check sports conflicts
    const localSports = localData.sports?.map(s => s.sportId).sort() || [];
    const remoteSports = remoteData.sports?.map(s => s.sportId).sort() || [];

    if (JSON.stringify(localSports) !== JSON.stringify(remoteSports)) {
      conflicts.push('Sports selection differs between local and remote');
    }

    // Check teams conflicts
    const localTeams = localData.teams?.map(t => t.teamId).sort() || [];
    const remoteTeams = remoteData.teams?.map(t => t.teamId).sort() || [];

    if (JSON.stringify(localTeams) !== JSON.stringify(remoteTeams)) {
      conflicts.push('Team selection differs between local and remote');
    }

    // Check preferences conflicts
    if (localData.preferences?.contentFrequency !== remoteData.preferences?.contentFrequency) {
      conflicts.push('Content frequency settings differ');
    }

    // Check news types
    const localNewsTypes = localData.preferences?.newsTypes?.map(nt => `${nt.type}:${nt.enabled}`).sort() || [];
    const remoteNewsTypes = remoteData.preferences?.newsTypes?.map(nt => `${nt.type}:${nt.enabled}`).sort() || [];

    if (JSON.stringify(localNewsTypes) !== JSON.stringify(remoteNewsTypes)) {
      conflicts.push('News type preferences differ');
    }

    return conflicts;
  }

  private mergeUserPreferences(
    localData: UserPreferences,
    remoteData: UserPreferences
  ): UserPreferences {
    // Merge strategy: prefer more recent data, but combine collections
    const localTime = new Date(localData.updatedAt).getTime();
    const remoteTime = new Date(remoteData.updatedAt).getTime();

    const newerData = localTime > remoteTime ? localData : remoteData;
    const olderData = localTime > remoteTime ? remoteData : localData;

    return {
      ...newerData,
      // Merge sports and teams by combining unique items
      sports: this.mergeUniqueSports(localData.sports || [], remoteData.sports || []),
      teams: this.mergeUniqueTeams(localData.teams || [], remoteData.teams || []),
      preferences: {
        // Use newer preferences as base, but merge enabled news types
        ...newerData.preferences,
        newsTypes: this.mergeNewsTypes(
          localData.preferences?.newsTypes || [],
          remoteData.preferences?.newsTypes || []
        ),
      },
    };
  }

  private mergeUniqueSports(local: UserPreferences['sports'], remote: UserPreferences['sports']) {
    const sportMap = new Map();

    // Add remote sports first
    remote?.forEach(sport => sportMap.set(sport.sportId, sport));

    // Add local sports, overriding with local data
    local?.forEach(sport => sportMap.set(sport.sportId, sport));

    return Array.from(sportMap.values());
  }

  private mergeUniqueTeams(local: UserPreferences['teams'], remote: UserPreferences['teams']) {
    const teamMap = new Map();

    // Add remote teams first
    remote?.forEach(team => teamMap.set(team.teamId, team));

    // Add local teams, overriding with local data
    local?.forEach(team => teamMap.set(team.teamId, team));

    return Array.from(teamMap.values());
  }

  private mergeNewsTypes(
    local: UserPreferences['preferences']['newsTypes'],
    remote: UserPreferences['preferences']['newsTypes']
  ) {
    const typeMap = new Map();

    // Start with remote news types
    remote.forEach(nt => typeMap.set(nt.type, nt));

    // Merge with local, preferring enabled status if either is enabled
    local.forEach(localNt => {
      const existing = typeMap.get(localNt.type);
      if (existing) {
        typeMap.set(localNt.type, {
          ...existing,
          enabled: existing.enabled || localNt.enabled, // Keep enabled if either is enabled
          priority: Math.min(existing.priority, localNt.priority), // Use higher priority (lower number)
        });
      } else {
        typeMap.set(localNt.type, localNt);
      }
    });

    return Array.from(typeMap.values());
  }

  private markMigrationComplete(preferences: UserPreferences): void {
    localStorage.setItem('corner-league-migration-complete', JSON.stringify({
      completed: true,
      completedAt: new Date().toISOString(),
      migratedPreferences: preferences.id,
    }));
  }
}

// Utility functions
export const createMigrationManager = (apiClient: ApiClient) => {
  return new MigrationManager(apiClient);
};

export const isMigrationComplete = (): boolean => {
  const migrationData = localStorage.getItem('corner-league-migration-complete');
  if (!migrationData) return false;

  try {
    const data = JSON.parse(migrationData);
    return data.completed === true;
  } catch {
    return false;
  }
};

export const getMigrationInfo = (): {
  isComplete: boolean;
  completedAt?: string;
  migratedPreferences?: string;
} => {
  const migrationData = localStorage.getItem('corner-league-migration-complete');
  if (!migrationData) {
    return { isComplete: false };
  }

  try {
    const data = JSON.parse(migrationData);
    return {
      isComplete: data.completed === true,
      completedAt: data.completedAt,
      migratedPreferences: data.migratedPreferences,
    };
  } catch {
    return { isComplete: false };
  }
};