import { useQuery } from '@tanstack/react-query';
import { useAuth } from '@clerk/clerk-react';
import { createApiQueryClient } from '@/lib/api-client';
import { HomeData, TeamDashboard } from '@/lib/api-client';

export const useDashboard = () => {
  const { getToken, isSignedIn, userId } = useAuth();

  // Create API query client with Clerk auth
  const apiQueries = createApiQueryClient({
    getToken,
    isSignedIn: isSignedIn ?? false,
    userId
  });

  // Get home data (most-liked team)
  const {
    data: homeData,
    isLoading: homeLoading,
    error: homeError,
    refetch: refetchHome
  } = useQuery<HomeData, Error>({
    ...apiQueries.getHomeData(),
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });

  // Get team dashboard data for the most-liked team
  const {
    data: teamDashboard,
    isLoading: teamLoading,
    error: teamError,
    refetch: refetchTeam
  } = useQuery<TeamDashboard, Error>({
    ...apiQueries.getTeamDashboard(homeData?.most_liked_team_id || ''),
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });

  const isLoading = homeLoading || teamLoading;
  const error = homeError || teamError;

  const refetchAll = async () => {
    await Promise.all([refetchHome(), refetchTeam()]);
  };

  return {
    homeData,
    teamDashboard,
    isLoading,
    error,
    refetchAll,
    // Individual loading states for granular control
    homeLoading,
    teamLoading,
    // Individual errors for specific error handling
    homeError,
    teamError,
    // Individual refetch functions
    refetchHome,
    refetchTeam,
  };
};

// Hook for getting team dashboard data for a specific team
export const useTeamDashboard = (teamId: string) => {
  const { getToken, isSignedIn, userId } = useAuth();

  const apiQueries = createApiQueryClient({
    getToken,
    isSignedIn: isSignedIn ?? false,
    userId
  });

  return useQuery<TeamDashboard, Error>({
    ...apiQueries.getTeamDashboard(teamId),
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
};

// Hook for getting home data only
export const useHomeData = () => {
  const { getToken, isSignedIn, userId } = useAuth();

  const apiQueries = createApiQueryClient({
    getToken,
    isSignedIn: isSignedIn ?? false,
    userId
  });

  return useQuery<HomeData, Error>({
    ...apiQueries.getHomeData(),
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
};