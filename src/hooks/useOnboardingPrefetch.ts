import { useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { createApiQueryClient } from "@/lib/api-client";
import { useFirebaseAuth } from "@/contexts/FirebaseAuthContext";
import { getLocalOnboardingStatus } from "@/lib/onboarding-storage";

interface UsePrefetchOptions {
  enabled?: boolean;
  prefetchDelay?: number;
}

/**
 * Hook for prefetching next step data in the onboarding flow
 * Reduces perceived loading time by fetching data before user navigates
 */
export function useOnboardingPrefetch({
  enabled = true,
  prefetchDelay = 1000
}: UsePrefetchOptions = {}) {
  const queryClient = useQueryClient();
  const { isAuthenticated, getIdToken, user } = useFirebaseAuth();

  const apiQueries = createApiQueryClient(
    isAuthenticated ? { getIdToken, isAuthenticated: true, userId: user?.uid } : undefined
  );

  // Prefetch teams data when sports are selected
  const prefetchTeamsForSports = (sportIds: string[]) => {
    if (!enabled || sportIds.length === 0) return;

    setTimeout(() => {
      queryClient.prefetchQuery({
        ...apiQueries.getOnboardingTeams(sportIds),
        staleTime: 5 * 60 * 1000, // 5 minutes
      });
    }, prefetchDelay);
  };

  // Prefetch preferences data
  const prefetchPreferences = () => {
    if (!enabled || !isAuthenticated) return;

    setTimeout(() => {
      queryClient.prefetchQuery({
        ...apiQueries.getUserPreferences(),
        staleTime: 5 * 60 * 1000,
      });
    }, prefetchDelay);
  };

  // Prefetch dashboard data for completion step
  const prefetchDashboardData = () => {
    if (!enabled || !isAuthenticated) return;

    setTimeout(() => {
      // Prefetch user feed data
      queryClient.prefetchQuery({
        ...apiQueries.getPersonalizedFeed(),
        staleTime: 2 * 60 * 1000, // 2 minutes for fresh content
      });

      // Prefetch user analytics
      queryClient.prefetchQuery({
        ...apiQueries.getUserAnalytics(),
        staleTime: 10 * 60 * 1000, // 10 minutes
      });
    }, prefetchDelay);
  };

  // Auto-prefetch based on current onboarding state
  useEffect(() => {
    if (!enabled) return;

    const localStatus = getLocalOnboardingStatus();

    // If user has selected sports, prefetch teams
    if (localStatus?.selectedSports && localStatus.selectedSports.length > 0) {
      const sportIds = localStatus.selectedSports.map(s => s.sportId);
      prefetchTeamsForSports(sportIds);
    }

    // If user has selected teams, prefetch preferences
    if (localStatus?.selectedTeams && localStatus.selectedTeams.length > 0) {
      prefetchPreferences();
    }

    // If user has set preferences, prefetch dashboard data
    if (localStatus?.preferences) {
      prefetchDashboardData();
    }
  }, [enabled, isAuthenticated]);

  return {
    prefetchTeamsForSports,
    prefetchPreferences,
    prefetchDashboardData,
  };
}

/**
 * Hook for preloading critical onboarding assets
 * Preloads images, fonts, and other resources to improve performance
 */
export function useOnboardingAssetPrefetch() {
  useEffect(() => {
    // Preload critical images
    const criticalImages = [
      '/images/logos/nfl.png',
      '/images/logos/nba.png',
      '/images/logos/mlb.png',
      '/images/logos/nhl.png',
    ];

    criticalImages.forEach(src => {
      const link = document.createElement('link');
      link.rel = 'prefetch';
      link.href = src;
      link.as = 'image';
      document.head.appendChild(link);
    });

    // Preload next step routes
    const routes = [
      '/onboarding/step/2',
      '/onboarding/step/3',
      '/onboarding/step/4',
      '/onboarding/step/5',
    ];

    routes.forEach(route => {
      const link = document.createElement('link');
      link.rel = 'prefetch';
      link.href = route;
      document.head.appendChild(link);
    });

    // Cleanup
    return () => {
      const prefetchLinks = document.querySelectorAll('link[rel="prefetch"]');
      prefetchLinks.forEach(link => {
        if (criticalImages.includes(link.getAttribute('href') || '') ||
            routes.includes(link.getAttribute('href') || '')) {
          document.head.removeChild(link);
        }
      });
    };
  }, []);
}

export default useOnboardingPrefetch;