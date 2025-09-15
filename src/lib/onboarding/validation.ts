import { z } from 'zod';
import { SportPreference, TeamPreference, UserSettings } from '../types/onboarding-types';

// Zod schemas for validation
export const sportPreferenceSchema = z.object({
  sportId: z.string().min(1, 'Sport ID is required'),
  name: z.string().min(1, 'Sport name is required'),
  rank: z.number().min(1, 'Rank must be at least 1'),
  hasTeams: z.boolean(),
});

export const teamPreferenceSchema = z.object({
  teamId: z.string().min(1, 'Team ID is required'),
  name: z.string().min(1, 'Team name is required'),
  sportId: z.string().min(1, 'Sport ID is required'),
  league: z.string().min(1, 'League is required'),
  affinityScore: z.number().min(0).max(100, 'Affinity score must be between 0 and 100'),
});

export const newsTypePreferenceSchema = z.object({
  type: z.enum(['injuries', 'trades', 'roster', 'general', 'scores', 'analysis']),
  enabled: z.boolean(),
  priority: z.number().min(1).max(10),
});

export const notificationSettingsSchema = z.object({
  push: z.boolean(),
  email: z.boolean(),
  gameReminders: z.boolean(),
  newsAlerts: z.boolean(),
  scoreUpdates: z.boolean(),
});

export const userSettingsSchema = z.object({
  newsTypes: z.array(newsTypePreferenceSchema),
  notifications: notificationSettingsSchema,
  contentFrequency: z.enum(['minimal', 'standard', 'comprehensive']),
});

export const userPreferencesSchema = z.object({
  id: z.string().uuid('Invalid user ID format'),
  sports: z.array(sportPreferenceSchema).min(1, 'At least one sport must be selected'),
  teams: z.array(teamPreferenceSchema).min(1, 'At least one team must be selected'),
  preferences: userSettingsSchema,
  completedAt: z.string().optional(),
  createdAt: z.string(),
  updatedAt: z.string(),
});

// Validation functions
export class OnboardingValidator {
  /**
   * Validate sports selection
   */
  static validateSportsSelection(sports: SportPreference[]): {
    isValid: boolean;
    errors: string[];
  } {
    const errors: string[] = [];

    if (sports.length === 0) {
      errors.push('At least one sport must be selected');
    }

    // Check for duplicate sports
    const sportIds = sports.map(s => s.sportId);
    const duplicates = sportIds.filter((id, index) => sportIds.indexOf(id) !== index);
    if (duplicates.length > 0) {
      errors.push(`Duplicate sports found: ${duplicates.join(', ')}`);
    }

    // Validate individual sports
    sports.forEach((sport, index) => {
      const result = sportPreferenceSchema.safeParse(sport);
      if (!result.success) {
        errors.push(`Sport ${index + 1}: ${result.error.issues.map(i => i.message).join(', ')}`);
      }
    });

    // Validate rank sequence
    const ranks = sports.map(s => s.rank).sort((a, b) => a - b);
    for (let i = 0; i < ranks.length; i++) {
      if (ranks[i] !== i + 1) {
        errors.push('Sport rankings must be sequential starting from 1');
        break;
      }
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  }

  /**
   * Validate team selection
   */
  static validateTeamSelection(teams: TeamPreference[], selectedSports: SportPreference[]): {
    isValid: boolean;
    errors: string[];
  } {
    const errors: string[] = [];

    // Check that teams are selected for sports that have teams
    const sportsWithTeams = selectedSports.filter(s => s.hasTeams);
    const sportsWithTeamsIds = sportsWithTeams.map(s => s.sportId);

    if (sportsWithTeams.length > 0 && teams.length === 0) {
      errors.push('At least one team must be selected for sports that have teams');
    }

    // Check that all teams belong to selected sports
    teams.forEach(team => {
      if (!sportsWithTeamsIds.includes(team.sportId)) {
        errors.push(`Team ${team.name} belongs to a sport that wasn't selected`);
      }
    });

    // Check for duplicate teams
    const teamIds = teams.map(t => t.teamId);
    const duplicates = teamIds.filter((id, index) => teamIds.indexOf(id) !== index);
    if (duplicates.length > 0) {
      errors.push(`Duplicate teams found: ${duplicates.join(', ')}`);
    }

    // Validate individual teams
    teams.forEach((team, index) => {
      const result = teamPreferenceSchema.safeParse(team);
      if (!result.success) {
        errors.push(`Team ${index + 1}: ${result.error.issues.map(i => i.message).join(', ')}`);
      }
    });

    return {
      isValid: errors.length === 0,
      errors,
    };
  }

  /**
   * Validate user settings
   */
  static validateUserSettings(settings: UserSettings): {
    isValid: boolean;
    errors: string[];
  } {
    const errors: string[] = [];

    const result = userSettingsSchema.safeParse(settings);
    if (!result.success) {
      errors.push(...result.error.issues.map(i => i.message));
    }

    // Check that at least one news type is enabled
    const enabledNewsTypes = settings.newsTypes.filter(nt => nt.enabled);
    if (enabledNewsTypes.length === 0) {
      errors.push('At least one news type must be enabled');
    }

    // Check for duplicate news types
    const newsTypes = settings.newsTypes.map(nt => nt.type);
    const duplicates = newsTypes.filter((type, index) => newsTypes.indexOf(type) !== index);
    if (duplicates.length > 0) {
      errors.push(`Duplicate news types found: ${duplicates.join(', ')}`);
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  }

  /**
   * Validate complete user preferences
   */
  static validateCompletePreferences(preferences: Partial<UserPreferences>): {
    isValid: boolean;
    errors: string[];
    warnings: string[];
  } {
    const errors: string[] = [];
    const warnings: string[] = [];

    // Check required fields
    if (!preferences.id) {
      errors.push('User ID is required');
    }

    if (!preferences.sports || preferences.sports.length === 0) {
      errors.push('Sports selection is required');
    }

    if (!preferences.teams || preferences.teams.length === 0) {
      warnings.push('No teams selected - you may see limited personalized content');
    }

    if (!preferences.preferences) {
      errors.push('User preferences are required');
    }

    // Validate individual sections if present
    if (preferences.sports) {
      const sportsValidation = this.validateSportsSelection(preferences.sports);
      errors.push(...sportsValidation.errors);
    }

    if (preferences.teams && preferences.sports) {
      const teamsValidation = this.validateTeamSelection(preferences.teams, preferences.sports);
      errors.push(...teamsValidation.errors);
    }

    if (preferences.preferences) {
      const settingsValidation = this.validateUserSettings(preferences.preferences);
      errors.push(...settingsValidation.errors);
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings,
    };
  }

  /**
   * Validate step completion requirements
   */
  static validateStepCompletion(stepId: string, data: any): {
    canProceed: boolean;
    errors: string[];
  } {
    const errors: string[] = [];

    switch (stepId) {
      case 'welcome':
        // Welcome step always allows proceeding
        break;

      case 'sports':
        if (!data.sports || data.sports.length === 0) {
          errors.push('Please select at least one sport to continue');
        }
        break;

      case 'teams':
        const sportsWithTeams = data.sports?.filter((s: SportPreference) => s.hasTeams) || [];
        if (sportsWithTeams.length > 0 && (!data.teams || data.teams.length === 0)) {
          errors.push('Please select at least one team for the sports you chose');
        }
        break;

      case 'preferences':
        // Preferences step is optional, so no validation required
        break;

      case 'complete':
        const validation = this.validateCompletePreferences(data);
        errors.push(...validation.errors);
        break;

      default:
        errors.push('Unknown step');
    }

    return {
      canProceed: errors.length === 0,
      errors,
    };
  }
}