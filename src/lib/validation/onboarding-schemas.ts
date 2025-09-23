/**
 * Onboarding Validation Schemas
 *
 * Comprehensive Zod schemas for validating all onboarding form inputs
 * with detailed error messages and transformation logic.
 */

import { z } from 'zod';

// Base validation messages
const VALIDATION_MESSAGES = {
  required: 'This field is required',
  minLength: (min: number) => `Must be at least ${min} characters`,
  maxLength: (max: number) => `Must be no more than ${max} characters`,
  email: 'Please enter a valid email address',
  invalidChoice: 'Please select a valid option',
  minItems: (min: number) => `Please select at least ${min} item${min === 1 ? '' : 's'}`,
  maxItems: (max: number) => `Please select no more than ${max} item${max === 1 ? '' : 's'}`,
  invalidRank: 'Rank must be a positive number',
  duplicateRank: 'Each item must have a unique rank',
  invalidRange: (min: number, max: number) => `Value must be between ${min} and ${max}`,
} as const;

// Common field schemas
const sportIdSchema = z.string().min(1, VALIDATION_MESSAGES.required).regex(
  /^[a-z0-9_-]+$/,
  'Sport ID must contain only lowercase letters, numbers, underscore, and dash'
);

const teamIdSchema = z.string().min(1, VALIDATION_MESSAGES.required).regex(
  /^[a-zA-Z0-9_-]+$/,
  'Team ID must contain only letters, numbers, underscore, and dash'
);

const rankSchema = z.number()
  .int('Rank must be a whole number')
  .positive('Rank must be a positive number')
  .max(10, 'Rank cannot exceed 10');

const emailSchema = z.string()
  .min(1, VALIDATION_MESSAGES.required)
  .email(VALIDATION_MESSAGES.email)
  .max(320, 'Email address is too long'); // RFC 5321 limit

// Sports Selection Schema (Step 2)
export const sportsSelectionSchema = z.object({
  selectedSports: z.array(
    z.object({
      sportId: sportIdSchema,
      rank: rankSchema,
    })
  )
  .min(1, VALIDATION_MESSAGES.minItems(1))
  .max(5, VALIDATION_MESSAGES.maxItems(5))
  .refine(
    (sports) => {
      const ranks = sports.map(s => s.rank);
      const uniqueRanks = new Set(ranks);
      return ranks.length === uniqueRanks.size;
    },
    { message: VALIDATION_MESSAGES.duplicateRank }
  )
  .refine(
    (sports) => {
      const sortedRanks = sports.map(s => s.rank).sort((a, b) => a - b);
      for (let i = 0; i < sortedRanks.length; i++) {
        if (sortedRanks[i] !== i + 1) {
          return false;
        }
      }
      return true;
    },
    { message: 'Ranks must be consecutive starting from 1' }
  ),
}).strict();

// Team Selection Schema (Step 3)
export const teamSelectionSchema = z.object({
  selectedTeams: z.array(
    z.object({
      teamId: teamIdSchema,
      sportId: sportIdSchema,
      rank: rankSchema,
    })
  )
  .min(1, VALIDATION_MESSAGES.minItems(1))
  .max(10, VALIDATION_MESSAGES.maxItems(10))
  .refine(
    (teams) => {
      const ranks = teams.map(t => t.rank);
      const uniqueRanks = new Set(ranks);
      return ranks.length === uniqueRanks.size;
    },
    { message: VALIDATION_MESSAGES.duplicateRank }
  )
  .refine(
    (teams) => {
      const sortedRanks = teams.map(t => t.rank).sort((a, b) => a - b);
      for (let i = 0; i < sortedRanks.length; i++) {
        if (sortedRanks[i] !== i + 1) {
          return false;
        }
      }
      return true;
    },
    { message: 'Ranks must be consecutive starting from 1' }
  ),
}).strict();

// Content Preferences Schema (Step 4)
export const contentPreferencesSchema = z.object({
  contentFrequency: z.enum(['low', 'medium', 'high'], {
    required_error: 'Please select a content frequency',
    invalid_type_error: 'Please select a valid frequency option',
  }),

  emailNotifications: z.boolean().optional().default(false),

  emailAddress: z.union([
    z.string().length(0, 'Email address cannot be empty'),
    emailSchema,
  ]).optional(),

  pushNotifications: z.boolean().optional().default(false),

  newsTypes: z.array(
    z.enum(['breaking', 'analysis', 'scores', 'trades', 'injuries', 'predictions'], {
      invalid_type_error: 'Please select valid news types',
    })
  )
  .min(1, 'Please select at least one news type')
  .max(6, 'Too many news types selected'),

  timeZone: z.string()
    .min(1, 'Please select a time zone')
    .max(50, 'Time zone identifier is too long'),

}).strict()
.refine(
  (data) => {
    // If email notifications are enabled, email address is required
    if (data.emailNotifications && (!data.emailAddress || data.emailAddress.length === 0)) {
      return false;
    }
    return true;
  },
  {
    message: 'Email address is required when email notifications are enabled',
    path: ['emailAddress'],
  }
);

// User Profile Schema (Optional - Step 5)
export const userProfileSchema = z.object({
  displayName: z.string()
    .min(1, VALIDATION_MESSAGES.required)
    .min(2, VALIDATION_MESSAGES.minLength(2))
    .max(50, VALIDATION_MESSAGES.maxLength(50))
    .regex(
      /^[a-zA-Z0-9\s._-]+$/,
      'Display name can only contain letters, numbers, spaces, dots, underscores, and dashes'
    ),

  bio: z.string()
    .max(500, VALIDATION_MESSAGES.maxLength(500))
    .optional(),

  location: z.string()
    .max(100, VALIDATION_MESSAGES.maxLength(100))
    .optional(),

  favoritePlayer: z.string()
    .max(100, VALIDATION_MESSAGES.maxLength(100))
    .optional(),

  yearsAsAFan: z.number()
    .int('Years must be a whole number')
    .min(0, 'Years cannot be negative')
    .max(100, 'Years seems too high')
    .optional(),

}).strict();

// Complete Onboarding Data Schema
export const completeOnboardingSchema = z.object({
  step1: z.object({
    completed: z.boolean(),
    timestamp: z.number().optional(),
  }).strict(),

  step2: sportsSelectionSchema,

  step3: teamSelectionSchema,

  step4: contentPreferencesSchema,

  step5: userProfileSchema.optional(),

}).strict();

// API Request Schemas
export const updateStepRequestSchema = z.object({
  step: z.number().int().min(1).max(5),
  data: z.record(z.any()), // Flexible for different step data
}).strict();

export const bulkUpdateRequestSchema = z.object({
  userId: z.string().min(1, 'User ID is required'),
  steps: z.array(
    z.object({
      step: z.number().int().min(1).max(5),
      data: z.record(z.any()),
      timestamp: z.number().optional(),
    })
  ).min(1, 'At least one step is required'),
}).strict();

// Error Response Schema
export const apiErrorSchema = z.object({
  error: z.string(),
  message: z.string(),
  details: z.record(z.any()).optional(),
  timestamp: z.string().optional(),
  requestId: z.string().optional(),
}).strict();

// Form State Schemas for Client-Side Validation
export const sportsFormStateSchema = z.object({
  sports: z.array(
    z.object({
      id: sportIdSchema,
      name: z.string().min(1),
      icon: z.string().optional(),
      isSelected: z.boolean(),
      rank: z.number().int().min(0),
      isPopular: z.boolean().optional(),
      hasTeams: z.boolean().optional(),
    })
  ),
  selectedCount: z.number().int().min(0).max(5),
  isDirty: z.boolean().optional().default(false),
}).strict();

export const teamsFormStateSchema = z.object({
  teams: z.array(
    z.object({
      id: teamIdSchema,
      name: z.string().min(1),
      sport: sportIdSchema,
      conference: z.string().optional(),
      division: z.string().optional(),
      logo: z.string().optional(),
      isSelected: z.boolean(),
      rank: z.number().int().min(0),
    })
  ),
  selectedCount: z.number().int().min(0).max(10),
  filterBySport: z.string().optional(),
  searchQuery: z.string().optional(),
  isDirty: z.boolean().optional().default(false),
}).strict();

// Validation Result Types
export type ValidationResult<T> = {
  success: true;
  data: T;
} | {
  success: false;
  errors: Record<string, string[]>;
  fieldErrors: Record<string, string>;
};

// Validation Helper Functions
export function validateSportsSelection(data: unknown): ValidationResult<z.infer<typeof sportsSelectionSchema>> {
  try {
    const result = sportsSelectionSchema.parse(data);
    return { success: true, data: result };
  } catch (error) {
    if (error instanceof z.ZodError) {
      const fieldErrors: Record<string, string> = {};
      const errors: Record<string, string[]> = {};

      error.errors.forEach(err => {
        const path = err.path.join('.');
        const message = err.message;

        if (!errors[path]) {
          errors[path] = [];
        }
        errors[path].push(message);
        fieldErrors[path] = message; // Use first error for field-level display
      });

      return { success: false, errors, fieldErrors };
    }
    throw error;
  }
}

export function validateTeamSelection(data: unknown): ValidationResult<z.infer<typeof teamSelectionSchema>> {
  try {
    const result = teamSelectionSchema.parse(data);
    return { success: true, data: result };
  } catch (error) {
    if (error instanceof z.ZodError) {
      const fieldErrors: Record<string, string> = {};
      const errors: Record<string, string[]> = {};

      error.errors.forEach(err => {
        const path = err.path.join('.');
        const message = err.message;

        if (!errors[path]) {
          errors[path] = [];
        }
        errors[path].push(message);
        fieldErrors[path] = message;
      });

      return { success: false, errors, fieldErrors };
    }
    throw error;
  }
}

export function validateContentPreferences(data: unknown): ValidationResult<z.infer<typeof contentPreferencesSchema>> {
  try {
    const result = contentPreferencesSchema.parse(data);
    return { success: true, data: result };
  } catch (error) {
    if (error instanceof z.ZodError) {
      const fieldErrors: Record<string, string> = {};
      const errors: Record<string, string[]> = {};

      error.errors.forEach(err => {
        const path = err.path.join('.');
        const message = err.message;

        if (!errors[path]) {
          errors[path] = [];
        }
        errors[path].push(message);
        fieldErrors[path] = message;
      });

      return { success: false, errors, fieldErrors };
    }
    throw error;
  }
}

export function validateUserProfile(data: unknown): ValidationResult<z.infer<typeof userProfileSchema>> {
  try {
    const result = userProfileSchema.parse(data);
    return { success: true, data: result };
  } catch (error) {
    if (error instanceof z.ZodError) {
      const fieldErrors: Record<string, string> = {};
      const errors: Record<string, string[]> = {};

      error.errors.forEach(err => {
        const path = err.path.join('.');
        const message = err.message;

        if (!errors[path]) {
          errors[path] = [];
        }
        errors[path].push(message);
        fieldErrors[path] = message;
      });

      return { success: false, errors, fieldErrors };
    }
    throw error;
  }
}

// Export schema types
export type SportsSelectionData = z.infer<typeof sportsSelectionSchema>;
export type TeamSelectionData = z.infer<typeof teamSelectionSchema>;
export type ContentPreferencesData = z.infer<typeof contentPreferencesSchema>;
export type UserProfileData = z.infer<typeof userProfileSchema>;
export type CompleteOnboardingData = z.infer<typeof completeOnboardingSchema>;
export type SportsFormState = z.infer<typeof sportsFormStateSchema>;
export type TeamsFormState = z.infer<typeof teamsFormStateSchema>;

export default {
  sportsSelectionSchema,
  teamSelectionSchema,
  contentPreferencesSchema,
  userProfileSchema,
  completeOnboardingSchema,
  validateSportsSelection,
  validateTeamSelection,
  validateContentPreferences,
  validateUserProfile,
  VALIDATION_MESSAGES,
};