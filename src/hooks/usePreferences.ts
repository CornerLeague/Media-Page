/**
 * usePreferences Hook
 *
 * Provides CRUD operations for user preferences including sports, teams, and settings.
 * This hook enables the edit flow for user profile preferences as required by section 2.1.
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useFirebaseAuth } from '@/contexts/FirebaseAuthContext';
import { apiClient, createApiQueryClient, type UserPreferences } from '@/lib/api-client';
import { toast } from '@/components/ui/use-toast';
import { useState } from 'react';

export interface SportPreference {
  sportId: string;
  name: string;
  rank: number;
  hasTeams: boolean;
}

export interface TeamPreference {
  teamId: string;
  name: string;
  sportId: string;
  league: string;
  affinityScore: number;
}

export interface ContentPreferences {
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
}

export interface PreferencesData {
  sports: SportPreference[];
  teams: TeamPreference[];
  preferences: ContentPreferences;
}

export interface UsePreferencesResult {
  // Data
  preferencesData: PreferencesData | undefined;
  isLoading: boolean;
  error: Error | null;

  // Sports operations
  updateSportsPreferences: (sports: SportPreference[]) => Promise<void>;
  isUpdatingSports: boolean;
  sportsError: Error | null;

  // Teams operations
  updateTeamsPreferences: (teams: TeamPreference[]) => Promise<void>;
  isUpdatingTeams: boolean;
  teamsError: Error | null;

  // Content preferences operations
  updateContentPreferences: (preferences: ContentPreferences) => Promise<void>;
  isUpdatingContent: boolean;
  contentError: Error | null;

  // Global operations
  refreshPreferences: () => void;
  hasUnsavedChanges: boolean;
  clearErrors: () => void;
}

export function usePreferences(): UsePreferencesResult {
  const { isAuthenticated, getIdToken, user } = useFirebaseAuth();
  const queryClient = useQueryClient();
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  // Set up API client with authentication
  const queryConfigs = createApiQueryClient(
    isAuthenticated ? { getIdToken, isAuthenticated: true, userId: user?.uid } : undefined
  );

  // Fetch current preferences
  const {
    data: preferencesData,
    isLoading,
    error,
    refetch: refreshPreferences,
  } = useQuery({
    ...queryConfigs.getUserProfile(),
    enabled: isAuthenticated,
    select: (data): PreferencesData => ({
      sports: data?.sports || [],
      teams: data?.teams || [],
      preferences: data?.preferences || {
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
        contentFrequency: 'standard' as const,
      },
    }),
  });

  // Sports preferences mutation
  const {
    mutateAsync: updateSportsPreferences,
    isPending: isUpdatingSports,
    error: sportsError,
    reset: resetSportsError,
  } = useMutation({
    mutationFn: async (sports: SportPreference[]) => {
      if (!isAuthenticated) throw new Error('Not authenticated');
      // Convert to API format
      const apiSports = sports.map(sport => ({
        sportId: sport.sportId,
        name: sport.name,
        rank: sport.rank,
        hasTeams: sport.hasTeams,
      }));
      return await apiClient.updateUserPreferences({ sports: apiSports });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user', 'profile'] });
      setHasUnsavedChanges(false);
      toast({
        title: 'Sports Updated',
        description: 'Your sports preferences have been saved successfully.',
      });
    },
    onError: (error) => {
      toast({
        title: 'Update Failed',
        description: 'Failed to update sports preferences. Please try again.',
        variant: 'destructive',
      });
    },
  });

  // Teams preferences mutation
  const {
    mutateAsync: updateTeamsPreferences,
    isPending: isUpdatingTeams,
    error: teamsError,
    reset: resetTeamsError,
  } = useMutation({
    mutationFn: async (teams: TeamPreference[]) => {
      if (!isAuthenticated) throw new Error('Not authenticated');
      // Convert to API format
      const apiTeams = teams.map(team => ({
        teamId: team.teamId,
        name: team.name,
        sportId: team.sportId,
        league: team.league,
        affinityScore: team.affinityScore,
      }));
      return await apiClient.updateUserPreferences({ teams: apiTeams });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user', 'profile'] });
      setHasUnsavedChanges(false);
      toast({
        title: 'Teams Updated',
        description: 'Your team preferences have been saved successfully.',
      });
    },
    onError: (error) => {
      toast({
        title: 'Update Failed',
        description: 'Failed to update team preferences. Please try again.',
        variant: 'destructive',
      });
    },
  });

  // Content preferences mutation
  const {
    mutateAsync: updateContentPreferences,
    isPending: isUpdatingContent,
    error: contentError,
    reset: resetContentError,
  } = useMutation({
    mutationFn: async (preferences: ContentPreferences) => {
      if (!isAuthenticated) throw new Error('Not authenticated');
      return await apiClient.updateUserPreferences({ preferences });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user', 'profile'] });
      setHasUnsavedChanges(false);
      toast({
        title: 'Preferences Updated',
        description: 'Your content preferences have been saved successfully.',
      });
    },
    onError: (error) => {
      toast({
        title: 'Update Failed',
        description: 'Failed to update content preferences. Please try again.',
        variant: 'destructive',
      });
    },
  });

  const clearErrors = () => {
    resetSportsError();
    resetTeamsError();
    resetContentError();
  };

  return {
    // Data
    preferencesData,
    isLoading,
    error: error as Error | null,

    // Sports operations
    updateSportsPreferences,
    isUpdatingSports,
    sportsError: sportsError as Error | null,

    // Teams operations
    updateTeamsPreferences,
    isUpdatingTeams,
    teamsError: teamsError as Error | null,

    // Content preferences operations
    updateContentPreferences,
    isUpdatingContent,
    contentError: contentError as Error | null,

    // Global operations
    refreshPreferences,
    hasUnsavedChanges,
    clearErrors,
  };
}