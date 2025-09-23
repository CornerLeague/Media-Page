/**
 * Onboarding Validation Hooks
 *
 * Custom React hooks for client-side validation of onboarding steps
 * with real-time validation, error handling, and recovery guidance.
 */

import { useState, useCallback, useEffect, useMemo } from 'react';
import { useToast } from '@/components/ui/use-toast';
import {
  validateSportsSelection,
  validateTeamSelection,
  validateContentPreferences,
  validateUserProfile,
  type ValidationResult,
  type SportsSelectionData,
  type TeamSelectionData,
  type ContentPreferencesData,
  type UserProfileData,
  type SportsFormState,
  type TeamsFormState,
} from '@/lib/validation/onboarding-schemas';
import { reportValidationError, reportOnboardingError } from '@/lib/error-reporting';

// Base validation hook interface
interface UseValidationHookResult<T> {
  data: T | null;
  errors: Record<string, string[]>;
  fieldErrors: Record<string, string>;
  isValid: boolean;
  isDirty: boolean;
  isValidating: boolean;
  hasErrors: boolean;
  validate: (data: unknown) => Promise<boolean>;
  validateField: (field: string, value: unknown) => boolean;
  clearErrors: () => void;
  clearFieldError: (field: string) => void;
  setFieldError: (field: string, error: string) => void;
  touch: () => void;
  reset: () => void;
}

// Generic validation hook
function useValidationHook<T>(
  validator: (data: unknown) => ValidationResult<T>,
  stepNumber: number,
  stepName: string
): UseValidationHookResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [errors, setErrors] = useState<Record<string, string[]>>({});
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [isDirty, setIsDirty] = useState(false);
  const [isValidating, setIsValidating] = useState(false);
  const { toast } = useToast();

  const isValid = useMemo(() => {
    return Object.keys(errors).length === 0 && data !== null;
  }, [errors, data]);

  const hasErrors = useMemo(() => {
    return Object.keys(errors).length > 0;
  }, [errors]);

  const validate = useCallback(async (inputData: unknown): Promise<boolean> => {
    setIsValidating(true);

    try {
      const result = validator(inputData);

      if (result.success) {
        setData(result.data);
        setErrors({});
        setFieldErrors({});
        return true;
      } else {
        setErrors(result.errors);
        setFieldErrors(result.fieldErrors);
        setData(null);

        // Report validation error for analytics
        reportValidationError(
          `Step ${stepNumber} validation failed`,
          result.errors,
          { step: stepNumber, stepName }
        );

        return false;
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown validation error';

      // Report unexpected validation error
      reportOnboardingError(
        stepNumber,
        `Unexpected validation error in ${stepName}`,
        error instanceof Error ? error : new Error(errorMessage),
        { inputData: typeof inputData === 'object' ? JSON.stringify(inputData) : String(inputData) }
      );

      setErrors({ general: [errorMessage] });
      setFieldErrors({ general: errorMessage });
      setData(null);

      toast({
        title: 'Validation Error',
        description: 'An unexpected error occurred while validating your input.',
        variant: 'destructive',
      });

      return false;
    } finally {
      setIsValidating(false);
    }
  }, [validator, stepNumber, stepName, toast]);

  const validateField = useCallback((field: string, value: unknown): boolean => {
    try {
      // For field-level validation, we create a minimal object
      const testData = { [field]: value };
      const result = validator(testData);

      if (result.success) {
        // Clear field error
        setFieldErrors(prev => {
          const next = { ...prev };
          delete next[field];
          return next;
        });
        setErrors(prev => {
          const next = { ...prev };
          delete next[field];
          return next;
        });
        return true;
      } else {
        // Set field error
        const fieldError = result.fieldErrors[field];
        if (fieldError) {
          setFieldErrors(prev => ({ ...prev, [field]: fieldError }));
          setErrors(prev => ({ ...prev, [field]: result.errors[field] || [fieldError] }));
        }
        return false;
      }
    } catch {
      return false; // Ignore field validation errors for partial data
    }
  }, [validator]);

  const clearErrors = useCallback(() => {
    setErrors({});
    setFieldErrors({});
  }, []);

  const clearFieldError = useCallback((field: string) => {
    setFieldErrors(prev => {
      const next = { ...prev };
      delete next[field];
      return next;
    });
    setErrors(prev => {
      const next = { ...prev };
      delete next[field];
      return next;
    });
  }, []);

  const setFieldError = useCallback((field: string, error: string) => {
    setFieldErrors(prev => ({ ...prev, [field]: error }));
    setErrors(prev => ({ ...prev, [field]: [error] }));
  }, []);

  const touch = useCallback(() => {
    setIsDirty(true);
  }, []);

  const reset = useCallback(() => {
    setData(null);
    setErrors({});
    setFieldErrors({});
    setIsDirty(false);
    setIsValidating(false);
  }, []);

  return {
    data,
    errors,
    fieldErrors,
    isValid,
    isDirty,
    isValidating,
    hasErrors,
    validate,
    validateField,
    clearErrors,
    clearFieldError,
    setFieldError,
    touch,
    reset,
  };
}

// Sports Selection Validation Hook
export function useSportsSelectionValidation() {
  const validation = useValidationHook(validateSportsSelection, 2, 'Sports Selection');

  // Additional sports-specific validation methods
  const validateSportsArray = useCallback((sports: SportsFormState['sports']) => {
    const selectedSports = sports.filter(s => s.isSelected);

    if (selectedSports.length === 0) {
      validation.setFieldError('selectedSports', 'Please select at least one sport');
      return false;
    }

    if (selectedSports.length > 5) {
      validation.setFieldError('selectedSports', 'Please select no more than 5 sports');
      return false;
    }

    // Check for duplicate ranks
    const ranks = selectedSports.map(s => s.rank).filter(r => r > 0);
    const uniqueRanks = new Set(ranks);
    if (ranks.length !== uniqueRanks.size) {
      validation.setFieldError('selectedSports', 'Each sport must have a unique rank');
      return false;
    }

    validation.clearFieldError('selectedSports');
    return true;
  }, [validation]);

  const validateSportsData = useCallback(async (sports: SportsFormState['sports']) => {
    const selectedSports = sports
      .filter(s => s.isSelected)
      .map(s => ({
        sportId: s.id,
        rank: s.rank,
      }));

    return validation.validate({ selectedSports });
  }, [validation]);

  return {
    ...validation,
    validateSportsArray,
    validateSportsData,
  };
}

// Team Selection Validation Hook
export function useTeamSelectionValidation() {
  const validation = useValidationHook(validateTeamSelection, 3, 'Team Selection');

  // Additional team-specific validation methods
  const validateTeamsArray = useCallback((teams: TeamsFormState['teams']) => {
    const selectedTeams = teams.filter(t => t.isSelected);

    if (selectedTeams.length === 0) {
      validation.setFieldError('selectedTeams', 'Please select at least one team');
      return false;
    }

    if (selectedTeams.length > 10) {
      validation.setFieldError('selectedTeams', 'Please select no more than 10 teams');
      return false;
    }

    // Check for duplicate ranks
    const ranks = selectedTeams.map(t => t.rank).filter(r => r > 0);
    const uniqueRanks = new Set(ranks);
    if (ranks.length !== uniqueRanks.size) {
      validation.setFieldError('selectedTeams', 'Each team must have a unique rank');
      return false;
    }

    validation.clearFieldError('selectedTeams');
    return true;
  }, [validation]);

  const validateTeamsData = useCallback(async (teams: TeamsFormState['teams']) => {
    const selectedTeams = teams
      .filter(t => t.isSelected)
      .map(t => ({
        teamId: t.id,
        sportId: t.sport,
        rank: t.rank,
      }));

    return validation.validate({ selectedTeams });
  }, [validation]);

  return {
    ...validation,
    validateTeamsArray,
    validateTeamsData,
  };
}

// Content Preferences Validation Hook
export function useContentPreferencesValidation() {
  const validation = useValidationHook(validateContentPreferences, 4, 'Content Preferences');

  // Additional preferences-specific validation methods
  const validateEmailRequirement = useCallback((emailNotifications: boolean, emailAddress: string) => {
    if (emailNotifications && (!emailAddress || emailAddress.trim().length === 0)) {
      validation.setFieldError('emailAddress', 'Email address is required when email notifications are enabled');
      return false;
    }

    validation.clearFieldError('emailAddress');
    return true;
  }, [validation]);

  const validateNewsTypesSelection = useCallback((newsTypes: string[]) => {
    if (newsTypes.length === 0) {
      validation.setFieldError('newsTypes', 'Please select at least one news type');
      return false;
    }

    if (newsTypes.length > 6) {
      validation.setFieldError('newsTypes', 'Please select no more than 6 news types');
      return false;
    }

    validation.clearFieldError('newsTypes');
    return true;
  }, [validation]);

  return {
    ...validation,
    validateEmailRequirement,
    validateNewsTypesSelection,
  };
}

// User Profile Validation Hook
export function useUserProfileValidation() {
  const validation = useValidationHook(validateUserProfile, 5, 'User Profile');

  // Additional profile-specific validation methods
  const validateDisplayName = useCallback((displayName: string) => {
    if (!displayName || displayName.trim().length === 0) {
      validation.setFieldError('displayName', 'Display name is required');
      return false;
    }

    if (displayName.length < 2) {
      validation.setFieldError('displayName', 'Display name must be at least 2 characters');
      return false;
    }

    if (displayName.length > 50) {
      validation.setFieldError('displayName', 'Display name must be no more than 50 characters');
      return false;
    }

    const validChars = /^[a-zA-Z0-9\s._-]+$/;
    if (!validChars.test(displayName)) {
      validation.setFieldError('displayName', 'Display name can only contain letters, numbers, spaces, dots, underscores, and dashes');
      return false;
    }

    validation.clearFieldError('displayName');
    return true;
  }, [validation]);

  const validateBio = useCallback((bio: string) => {
    if (bio.length > 500) {
      validation.setFieldError('bio', 'Bio must be no more than 500 characters');
      return false;
    }

    validation.clearFieldError('bio');
    return true;
  }, [validation]);

  return {
    ...validation,
    validateDisplayName,
    validateBio,
  };
}

// Combined validation hook for multiple steps
export function useMultiStepValidation() {
  const sportsValidation = useSportsSelectionValidation();
  const teamsValidation = useTeamSelectionValidation();
  const preferencesValidation = useContentPreferencesValidation();
  const profileValidation = useUserProfileValidation();

  const validateStep = useCallback(async (step: number, data: unknown): Promise<boolean> => {
    switch (step) {
      case 2:
        return sportsValidation.validate(data);
      case 3:
        return teamsValidation.validate(data);
      case 4:
        return preferencesValidation.validate(data);
      case 5:
        return profileValidation.validate(data);
      default:
        return false;
    }
  }, [sportsValidation, teamsValidation, preferencesValidation, profileValidation]);

  const getStepValidation = useCallback((step: number) => {
    switch (step) {
      case 2:
        return sportsValidation;
      case 3:
        return teamsValidation;
      case 4:
        return preferencesValidation;
      case 5:
        return profileValidation;
      default:
        return null;
    }
  }, [sportsValidation, teamsValidation, preferencesValidation, profileValidation]);

  const resetAllValidations = useCallback(() => {
    sportsValidation.reset();
    teamsValidation.reset();
    preferencesValidation.reset();
    profileValidation.reset();
  }, [sportsValidation, teamsValidation, preferencesValidation, profileValidation]);

  const hasAnyErrors = useMemo(() => {
    return sportsValidation.hasErrors ||
           teamsValidation.hasErrors ||
           preferencesValidation.hasErrors ||
           profileValidation.hasErrors;
  }, [sportsValidation.hasErrors, teamsValidation.hasErrors, preferencesValidation.hasErrors, profileValidation.hasErrors]);

  return {
    validateStep,
    getStepValidation,
    resetAllValidations,
    hasAnyErrors,
    sports: sportsValidation,
    teams: teamsValidation,
    preferences: preferencesValidation,
    profile: profileValidation,
  };
}

export default {
  useSportsSelectionValidation,
  useTeamSelectionValidation,
  useContentPreferencesValidation,
  useUserProfileValidation,
  useMultiStepValidation,
};