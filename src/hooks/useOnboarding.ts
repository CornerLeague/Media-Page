import { useReducer, useEffect, useCallback } from 'react';
import { useUser, useAuth } from '@clerk/clerk-react';
import { OnboardingState, OnboardingAction, ONBOARDING_STEPS } from '@/lib/types/onboarding-types';
import { OnboardingStorage } from '@/lib/onboarding/localStorage';
import { OnboardingValidator } from '@/lib/onboarding/validation';
import { apiClient, createApiQueryClient, ClerkAuthContext } from '@/lib/api-client';

// Onboarding reducer
function onboardingReducer(state: OnboardingState, action: OnboardingAction): OnboardingState {
  switch (action.type) {
    case 'SET_CURRENT_STEP':
      return {
        ...state,
        currentStep: Math.max(0, Math.min(action.payload, state.steps.length - 1)),
        errors: {}, // Clear errors when changing steps
      };

    case 'UPDATE_SPORTS':
      return {
        ...state,
        userPreferences: {
          ...state.userPreferences,
          sports: action.payload,
        },
        errors: {}, // Clear errors after update
      };

    case 'UPDATE_TEAMS':
      return {
        ...state,
        userPreferences: {
          ...state.userPreferences,
          teams: action.payload,
        },
        errors: {},
      };

    case 'UPDATE_PREFERENCES':
      return {
        ...state,
        userPreferences: {
          ...state.userPreferences,
          preferences: action.payload,
        },
        errors: {},
      };

    case 'SET_STEP_COMPLETED':
      return {
        ...state,
        steps: state.steps.map(step =>
          step.id === action.payload.stepId
            ? { ...step, isCompleted: action.payload.completed }
            : step
        ),
      };

    case 'SET_ERROR':
      return {
        ...state,
        errors: {
          ...state.errors,
          [action.payload.field]: action.payload.error,
        },
      };

    case 'CLEAR_ERRORS':
      return {
        ...state,
        errors: {},
      };

    case 'COMPLETE_ONBOARDING':
      return {
        ...state,
        isComplete: true,
        userPreferences: {
          ...state.userPreferences,
          completedAt: new Date().toISOString(),
        },
      };

    case 'RESET_ONBOARDING':
      return OnboardingStorage.createDefaultOnboardingState();

    default:
      return state;
  }
}

export function useOnboarding() {
  const { user, isLoaded: userLoaded } = useUser();
  const { getToken, isSignedIn } = useAuth();

  // Initialize state from localStorage or create default
  const [state, dispatch] = useReducer(onboardingReducer, null, () => {
    const savedState = OnboardingStorage.loadOnboardingState();
    return savedState || OnboardingStorage.createDefaultOnboardingState();
  });

  // Set up API client with Clerk authentication
  useEffect(() => {
    if (isSignedIn && userLoaded) {
      const clerkAuth: ClerkAuthContext = {
        getToken,
        isSignedIn,
        userId: user?.id,
      };
      apiClient.setClerkAuth(clerkAuth);
    }
  }, [isSignedIn, userLoaded, user?.id, getToken]);

  // Initialize user preferences with Clerk user data
  useEffect(() => {
    if (userLoaded && user && !state.userPreferences.id) {
      dispatch({
        type: 'UPDATE_SPORTS',
        payload: state.userPreferences.sports || []
      });

      // Set user ID from Clerk in preferences
      const updatedPreferences = {
        ...state.userPreferences,
        id: user.id,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      // Update state with user info
      Object.assign(state.userPreferences, updatedPreferences);
    }
  }, [userLoaded, user, state.userPreferences]);

  // Save state to localStorage whenever it changes
  useEffect(() => {
    OnboardingStorage.saveOnboardingState(state);
  }, [state]);

  // Navigation functions
  const goToStep = useCallback((stepIndex: number) => {
    dispatch({ type: 'SET_CURRENT_STEP', payload: stepIndex });
  }, []);

  const nextStep = useCallback(() => {
    const currentStepData = state.steps[state.currentStep];
    const validation = OnboardingValidator.validateStepCompletion(
      currentStepData.id,
      state.userPreferences
    );

    if (!validation.canProceed) {
      // Set validation errors
      validation.errors.forEach(error => {
        dispatch({
          type: 'SET_ERROR',
          payload: { field: currentStepData.id, error }
        });
      });
      return false;
    }

    // Mark current step as completed
    dispatch({
      type: 'SET_STEP_COMPLETED',
      payload: { stepId: currentStepData.id, completed: true }
    });

    // Move to next step
    if (state.currentStep < state.steps.length - 1) {
      dispatch({ type: 'SET_CURRENT_STEP', payload: state.currentStep + 1 });
    } else {
      dispatch({ type: 'COMPLETE_ONBOARDING' });
    }

    return true;
  }, [state.currentStep, state.steps, state.userPreferences]);

  const prevStep = useCallback(() => {
    if (state.currentStep > 0) {
      dispatch({ type: 'SET_CURRENT_STEP', payload: state.currentStep - 1 });
    }
  }, [state.currentStep]);

  const skipStep = useCallback(() => {
    const currentStepData = state.steps[state.currentStep];
    if (!currentStepData.isRequired) {
      if (state.currentStep < state.steps.length - 1) {
        dispatch({ type: 'SET_CURRENT_STEP', payload: state.currentStep + 1 });
      }
    }
  }, [state.currentStep, state.steps]);

  // Data update functions
  const updateSports = useCallback((sports: typeof state.userPreferences.sports) => {
    dispatch({ type: 'UPDATE_SPORTS', payload: sports || [] });
  }, []);

  const updateTeams = useCallback((teams: typeof state.userPreferences.teams) => {
    dispatch({ type: 'UPDATE_TEAMS', payload: teams || [] });
  }, []);

  const updatePreferences = useCallback((preferences: typeof state.userPreferences.preferences) => {
    if (preferences) {
      dispatch({ type: 'UPDATE_PREFERENCES', payload: preferences });
    }
  }, []);

  // Completion functions
  const completeOnboarding = useCallback(async () => {
    const validation = OnboardingValidator.validateCompletePreferences(state.userPreferences);

    if (!validation.isValid) {
      validation.errors.forEach(error => {
        dispatch({
          type: 'SET_ERROR',
          payload: { field: 'complete', error }
        });
      });
      return false;
    }

    // Save final preferences
    if (state.userPreferences.id &&
        state.userPreferences.sports &&
        state.userPreferences.teams &&
        state.userPreferences.preferences &&
        user) {

      try {
        const completePreferences = {
          ...state.userPreferences,
          completedAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        } as Required<typeof state.userPreferences>;

        // Save to backend via API
        const userData = {
          clerkUserId: user.id,
          displayName: user.firstName && user.lastName
            ? `${user.firstName} ${user.lastName}`
            : user.firstName || undefined,
          email: user.primaryEmailAddress?.emailAddress,
          sports: state.userPreferences.sports?.map(sport => ({
            sportId: sport.sportId,
            name: sport.name,
            rank: sport.rank,
            hasTeams: sport.hasTeams,
          })) || [],
          teams: state.userPreferences.teams?.map(team => ({
            teamId: team.teamId,
            name: team.name,
            sportId: team.sportId,
            league: team.league,
            affinityScore: team.affinityScore,
          })) || [],
          preferences: {
            newsTypes: state.userPreferences.preferences?.newsTypes?.map(nt => ({
              type: nt.type,
              enabled: nt.enabled,
              priority: nt.priority,
            })) || [],
            notifications: state.userPreferences.preferences?.notifications || {
              push: false,
              email: false,
              gameReminders: false,
              newsAlerts: false,
              scoreUpdates: false,
            },
            contentFrequency: state.userPreferences.preferences?.contentFrequency || 'standard',
          },
        };

        // Create user profile in backend
        await apiClient.createUser(userData);

        // Save to local storage as backup
        OnboardingStorage.saveUserPreferences(completePreferences);
        OnboardingStorage.setOnboardingCompleted(true);

        dispatch({ type: 'COMPLETE_ONBOARDING' });
        return true;
      } catch (error) {
        console.error('Failed to complete onboarding:', error);
        dispatch({
          type: 'SET_ERROR',
          payload: {
            field: 'complete',
            error: 'Failed to save preferences. Please try again.'
          }
        });
        return false;
      }
    }

    return false;
  }, [state.userPreferences, user]);

  const resetOnboarding = useCallback(() => {
    OnboardingStorage.clearAll();
    dispatch({ type: 'RESET_ONBOARDING' });
  }, []);

  // Error handling
  const setError = useCallback((field: string, error: string) => {
    dispatch({ type: 'SET_ERROR', payload: { field, error } });
  }, []);

  const clearErrors = useCallback(() => {
    dispatch({ type: 'CLEAR_ERRORS' });
  }, []);

  // Computed properties
  const currentStepData = state.steps[state.currentStep];
  const isFirstStep = state.currentStep === 0;
  const isLastStep = state.currentStep === state.steps.length - 1;
  const canSkipCurrentStep = currentStepData && !currentStepData.isRequired;
  const progress = ((state.currentStep + 1) / state.steps.length) * 100;

  return {
    // State
    state,
    currentStep: state.currentStep,
    steps: state.steps,
    userPreferences: state.userPreferences,
    errors: state.errors,
    isComplete: state.isComplete,
    currentStepData,
    isFirstStep,
    isLastStep,
    canSkipCurrentStep,
    progress,

    // Navigation
    goToStep,
    nextStep,
    prevStep,
    skipStep,

    // Data updates
    updateSports,
    updateTeams,
    updatePreferences,

    // Completion
    completeOnboarding,
    resetOnboarding,

    // Error handling
    setError,
    clearErrors,
  };
}