/**
 * Onboarding Data Recovery Utilities
 *
 * Comprehensive data recovery system for onboarding flow including
 * automatic validation, data migration, conflict resolution, and backup management.
 */

import { OnboardingStatus, OnboardingSport, OnboardingTeam } from './api-client';
import { sessionRecoveryManager, StepProgress } from './session-recovery';

export interface RecoveryValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
  fixedIssues: string[];
}

export interface DataRecoveryResult {
  success: boolean;
  recoveredData: any;
  validationResult: RecoveryValidationResult;
  source: 'localStorage' | 'sessionStorage' | 'memory' | 'api' | 'default';
  timestamp: number;
}

export interface ConflictResolution {
  strategy: 'local' | 'remote' | 'merge' | 'prompt';
  reason: string;
  mergedData?: any;
}

export interface DataBackup {
  id: string;
  timestamp: number;
  step: number;
  data: any;
  version: string;
  checksum: string;
}

/**
 * Onboarding Data Recovery Manager
 */
export class OnboardingDataRecovery {
  private backupKey = 'corner-league-onboarding-backups';
  private maxBackups = 10;
  private version = '1.0.0';

  /**
   * Recover data for a specific onboarding step
   */
  async recoverStepData(step: number): Promise<DataRecoveryResult> {
    const sources = await this.gatherDataSources(step);
    const bestSource = this.selectBestDataSource(sources);

    if (!bestSource) {
      return this.createEmptyRecoveryResult(step);
    }

    const validationResult = this.validateStepData(step, bestSource.data);
    const recoveredData = this.sanitizeAndFixData(step, bestSource.data, validationResult);

    return {
      success: true,
      recoveredData,
      validationResult,
      source: bestSource.source,
      timestamp: Date.now(),
    };
  }

  /**
   * Gather data from all available sources
   */
  private async gatherDataSources(step: number): Promise<Array<{
    source: 'localStorage' | 'sessionStorage' | 'memory' | 'api';
    data: any;
    timestamp: number;
    confidence: number;
  }>> {
    const sources = [];

    // Local storage (session recovery)
    try {
      const localData = sessionRecoveryManager.recoverStepData(step);
      if (localData) {
        sources.push({
          source: 'localStorage' as const,
          data: localData,
          timestamp: Date.now(),
          confidence: 0.8,
        });
      }
    } catch (error) {
      console.warn('Failed to get localStorage data:', error);
    }

    // Session storage
    try {
      const sessionData = this.getSessionStorageData(step);
      if (sessionData) {
        sources.push({
          source: 'sessionStorage' as const,
          data: sessionData,
          timestamp: sessionData.timestamp || Date.now(),
          confidence: 0.6,
        });
      }
    } catch (error) {
      console.warn('Failed to get sessionStorage data:', error);
    }

    // Memory cache (if available)
    try {
      const memoryData = this.getMemoryData(step);
      if (memoryData) {
        sources.push({
          source: 'memory' as const,
          data: memoryData,
          timestamp: Date.now(),
          confidence: 0.9,
        });
      }
    } catch (error) {
      console.warn('Failed to get memory data:', error);
    }

    // Backups
    try {
      const backupData = this.getBackupData(step);
      if (backupData) {
        sources.push({
          source: 'localStorage' as const, // Backups are stored in localStorage
          data: backupData.data,
          timestamp: backupData.timestamp,
          confidence: 0.7,
        });
      }
    } catch (error) {
      console.warn('Failed to get backup data:', error);
    }

    return sources;
  }

  /**
   * Select the best data source based on recency and confidence
   */
  private selectBestDataSource(sources: Array<{
    source: string;
    data: any;
    timestamp: number;
    confidence: number;
  }>): any {
    if (sources.length === 0) return null;

    // Sort by weighted score (recency + confidence)
    const now = Date.now();
    const scoredSources = sources.map(source => {
      const ageMs = now - source.timestamp;
      const ageHours = ageMs / (1000 * 60 * 60);
      const recencyScore = Math.max(0, 1 - (ageHours / 24)); // Decays over 24 hours
      const weightedScore = (source.confidence * 0.7) + (recencyScore * 0.3);

      return { ...source, score: weightedScore };
    });

    scoredSources.sort((a, b) => b.score - a.score);
    return scoredSources[0];
  }

  /**
   * Validate step data integrity
   */
  private validateStepData(step: number, data: any): RecoveryValidationResult {
    const result: RecoveryValidationResult = {
      isValid: true,
      errors: [],
      warnings: [],
      fixedIssues: [],
    };

    if (!data) {
      result.isValid = false;
      result.errors.push('No data provided for validation');
      return result;
    }

    switch (step) {
      case 2:
        this.validateSportsData(data, result);
        break;
      case 3:
        this.validateTeamsData(data, result);
        break;
      case 4:
        this.validatePreferencesData(data, result);
        break;
      default:
        result.warnings.push(`No specific validation available for step ${step}`);
    }

    return result;
  }

  /**
   * Validate sports selection data
   */
  private validateSportsData(data: any, result: RecoveryValidationResult): void {
    if (!data.selectedSports) {
      result.errors.push('Missing selectedSports array');
      return;
    }

    if (!Array.isArray(data.selectedSports)) {
      result.errors.push('selectedSports must be an array');
      return;
    }

    if (data.selectedSports.length === 0) {
      result.warnings.push('No sports selected');
      return;
    }

    if (data.selectedSports.length > 5) {
      result.warnings.push('More than 5 sports selected (maximum is 5)');
    }

    // Validate each sport
    data.selectedSports.forEach((sport: any, index: number) => {
      if (!sport.sportId) {
        result.errors.push(`Sport at index ${index} missing sportId`);
      }

      if (typeof sport.rank !== 'number' || sport.rank < 1) {
        result.warnings.push(`Sport at index ${index} has invalid rank`);
        result.fixedIssues.push(`Fixed rank for sport ${sport.sportId || index}`);
      }
    });

    // Check for duplicate sports
    const sportIds = data.selectedSports.map((s: any) => s.sportId).filter(Boolean);
    const uniqueIds = new Set(sportIds);
    if (uniqueIds.size !== sportIds.length) {
      result.warnings.push('Duplicate sports detected');
    }

    // Check for duplicate ranks
    const ranks = data.selectedSports.map((s: any) => s.rank).filter((r: any) => typeof r === 'number');
    const uniqueRanks = new Set(ranks);
    if (uniqueRanks.size !== ranks.length) {
      result.warnings.push('Duplicate ranks detected');
      result.fixedIssues.push('Will re-rank sports to fix duplicates');
    }
  }

  /**
   * Validate teams selection data
   */
  private validateTeamsData(data: any, result: RecoveryValidationResult): void {
    if (!data.selectedTeams) {
      result.errors.push('Missing selectedTeams array');
      return;
    }

    if (!Array.isArray(data.selectedTeams)) {
      result.errors.push('selectedTeams must be an array');
      return;
    }

    if (data.selectedTeams.length === 0) {
      result.warnings.push('No teams selected');
      return;
    }

    // Validate each team
    data.selectedTeams.forEach((team: any, index: number) => {
      if (!team.teamId) {
        result.errors.push(`Team at index ${index} missing teamId`);
      }

      if (!team.sportId) {
        result.warnings.push(`Team at index ${index} missing sportId`);
      }

      if (typeof team.affinityScore !== 'number' || team.affinityScore < 0 || team.affinityScore > 1) {
        result.warnings.push(`Team at index ${index} has invalid affinityScore`);
        result.fixedIssues.push(`Fixed affinity score for team ${team.teamId || index}`);
      }
    });

    // Check for duplicate teams
    const teamIds = data.selectedTeams.map((t: any) => t.teamId).filter(Boolean);
    const uniqueIds = new Set(teamIds);
    if (uniqueIds.size !== teamIds.length) {
      result.warnings.push('Duplicate teams detected');
    }
  }

  /**
   * Validate preferences data
   */
  private validatePreferencesData(data: any, result: RecoveryValidationResult): void {
    if (!data.preferences) {
      result.errors.push('Missing preferences object');
      return;
    }

    const prefs = data.preferences;

    // Validate news types
    if (prefs.newsTypes && Array.isArray(prefs.newsTypes)) {
      prefs.newsTypes.forEach((newsType: any, index: number) => {
        if (!newsType.type || typeof newsType.enabled !== 'boolean') {
          result.warnings.push(`Invalid news type at index ${index}`);
        }
      });
    } else {
      result.warnings.push('Invalid or missing newsTypes');
    }

    // Validate notifications
    if (prefs.notifications && typeof prefs.notifications === 'object') {
      const requiredFields = ['push', 'email', 'gameReminders', 'newsAlerts', 'scoreUpdates'];
      requiredFields.forEach(field => {
        if (typeof prefs.notifications[field] !== 'boolean') {
          result.warnings.push(`Missing or invalid notification setting: ${field}`);
        }
      });
    } else {
      result.warnings.push('Invalid or missing notifications settings');
    }

    // Validate content frequency
    const validFrequencies = ['minimal', 'standard', 'detailed'];
    if (!validFrequencies.includes(prefs.contentFrequency)) {
      result.warnings.push('Invalid content frequency setting');
      result.fixedIssues.push('Reset content frequency to default');
    }
  }

  /**
   * Sanitize and fix data issues
   */
  private sanitizeAndFixData(step: number, data: any, validation: RecoveryValidationResult): any {
    if (!data) return this.getDefaultStepData(step);

    let fixed = { ...data };

    switch (step) {
      case 2:
        fixed = this.fixSportsData(fixed);
        break;
      case 3:
        fixed = this.fixTeamsData(fixed);
        break;
      case 4:
        fixed = this.fixPreferencesData(fixed);
        break;
    }

    return fixed;
  }

  /**
   * Fix sports data issues
   */
  private fixSportsData(data: any): any {
    if (!data.selectedSports || !Array.isArray(data.selectedSports)) {
      return { selectedSports: [] };
    }

    let sports = [...data.selectedSports];

    // Remove invalid sports
    sports = sports.filter(sport => sport && sport.sportId);

    // Limit to 5 sports
    if (sports.length > 5) {
      sports = sports.slice(0, 5);
    }

    // Fix ranks
    sports.forEach((sport, index) => {
      if (typeof sport.rank !== 'number' || sport.rank < 1) {
        sport.rank = index + 1;
      }
    });

    // Remove duplicates (keep first occurrence)
    const seen = new Set();
    sports = sports.filter(sport => {
      if (seen.has(sport.sportId)) {
        return false;
      }
      seen.add(sport.sportId);
      return true;
    });

    // Re-rank to ensure sequential ranking
    sports.sort((a, b) => a.rank - b.rank);
    sports.forEach((sport, index) => {
      sport.rank = index + 1;
    });

    return { selectedSports: sports };
  }

  /**
   * Fix teams data issues
   */
  private fixTeamsData(data: any): any {
    if (!data.selectedTeams || !Array.isArray(data.selectedTeams)) {
      return { selectedTeams: [] };
    }

    let teams = [...data.selectedTeams];

    // Remove invalid teams
    teams = teams.filter(team => team && team.teamId);

    // Fix affinity scores
    teams.forEach(team => {
      if (typeof team.affinityScore !== 'number' || team.affinityScore < 0 || team.affinityScore > 1) {
        team.affinityScore = 0.5; // Default neutral score
      }
    });

    // Remove duplicates
    const seen = new Set();
    teams = teams.filter(team => {
      if (seen.has(team.teamId)) {
        return false;
      }
      seen.add(team.teamId);
      return true;
    });

    return { selectedTeams: teams };
  }

  /**
   * Fix preferences data issues
   */
  private fixPreferencesData(data: any): any {
    const defaultPrefs = {
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
    };

    if (!data.preferences || typeof data.preferences !== 'object') {
      return { preferences: defaultPrefs };
    }

    const fixed = { ...data.preferences };

    // Fix news types
    if (!Array.isArray(fixed.newsTypes)) {
      fixed.newsTypes = defaultPrefs.newsTypes;
    }

    // Fix notifications
    if (!fixed.notifications || typeof fixed.notifications !== 'object') {
      fixed.notifications = defaultPrefs.notifications;
    } else {
      Object.keys(defaultPrefs.notifications).forEach(key => {
        if (typeof fixed.notifications[key] !== 'boolean') {
          fixed.notifications[key] = defaultPrefs.notifications[key as keyof typeof defaultPrefs.notifications];
        }
      });
    }

    // Fix content frequency
    const validFrequencies = ['minimal', 'standard', 'detailed'];
    if (!validFrequencies.includes(fixed.contentFrequency)) {
      fixed.contentFrequency = 'standard';
    }

    return { preferences: fixed };
  }

  /**
   * Get default data for a step
   */
  private getDefaultStepData(step: number): any {
    switch (step) {
      case 2:
        return { selectedSports: [] };
      case 3:
        return { selectedTeams: [] };
      case 4:
        return {
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
          }
        };
      default:
        return {};
    }
  }

  /**
   * Create empty recovery result
   */
  private createEmptyRecoveryResult(step: number): DataRecoveryResult {
    return {
      success: false,
      recoveredData: this.getDefaultStepData(step),
      validationResult: {
        isValid: false,
        errors: ['No data sources available'],
        warnings: [],
        fixedIssues: [],
      },
      source: 'default',
      timestamp: Date.now(),
    };
  }

  /**
   * Get data from session storage
   */
  private getSessionStorageData(step: number): any {
    try {
      const key = `corner-league-step-${step}`;
      const stored = sessionStorage.getItem(key);
      return stored ? JSON.parse(stored) : null;
    } catch {
      return null;
    }
  }

  /**
   * Get data from memory cache
   */
  private getMemoryData(step: number): any {
    // Implementation would depend on your memory cache strategy
    // For now, return null
    return null;
  }

  /**
   * Create backup of step data
   */
  createBackup(step: number, data: any): void {
    try {
      const backup: DataBackup = {
        id: `backup-${step}-${Date.now()}`,
        timestamp: Date.now(),
        step,
        data,
        version: this.version,
        checksum: this.calculateChecksum(data),
      };

      const existing = this.getBackups();
      existing.push(backup);

      // Keep only recent backups
      existing.sort((a, b) => b.timestamp - a.timestamp);
      const trimmed = existing.slice(0, this.maxBackups);

      localStorage.setItem(this.backupKey, JSON.stringify(trimmed));
    } catch (error) {
      console.warn('Failed to create backup:', error);
    }
  }

  /**
   * Get backup data for step
   */
  private getBackupData(step: number): DataBackup | null {
    const backups = this.getBackups();
    const stepBackups = backups.filter(b => b.step === step);

    if (stepBackups.length === 0) return null;

    // Return most recent backup
    stepBackups.sort((a, b) => b.timestamp - a.timestamp);
    return stepBackups[0];
  }

  /**
   * Get all backups
   */
  private getBackups(): DataBackup[] {
    try {
      const stored = localStorage.getItem(this.backupKey);
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  }

  /**
   * Calculate simple checksum for data integrity
   */
  private calculateChecksum(data: any): string {
    const str = JSON.stringify(data);
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return hash.toString(16);
  }

  /**
   * Resolve conflicts between local and remote data
   */
  resolveConflict(localData: any, remoteData: any, step: number): ConflictResolution {
    // Simple strategy: prefer more recent data
    const localTimestamp = localData?.timestamp || 0;
    const remoteTimestamp = remoteData?.timestamp || 0;

    if (remoteTimestamp > localTimestamp) {
      return {
        strategy: 'remote',
        reason: 'Remote data is more recent',
      };
    } else if (localTimestamp > remoteTimestamp) {
      return {
        strategy: 'local',
        reason: 'Local data is more recent',
      };
    } else {
      // Merge strategy for same timestamps
      return {
        strategy: 'merge',
        reason: 'Timestamps are equal, merging data',
        mergedData: this.mergeData(localData, remoteData, step),
      };
    }
  }

  /**
   * Merge local and remote data
   */
  private mergeData(localData: any, remoteData: any, step: number): any {
    // Simple merge strategy - can be enhanced based on step type
    return { ...remoteData, ...localData };
  }

  /**
   * Clear all recovery data
   */
  clearAllRecoveryData(): void {
    try {
      localStorage.removeItem(this.backupKey);
      sessionRecoveryManager.clearSessionData();
    } catch (error) {
      console.warn('Failed to clear recovery data:', error);
    }
  }
}

// Export singleton instance
export const onboardingDataRecovery = new OnboardingDataRecovery();

export default onboardingDataRecovery;