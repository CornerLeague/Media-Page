/**
 * usePersonalizedFeed Hook
 *
 * Provides personalized content based on user preferences from onboarding.
 * Filters and prioritizes content based on selected sports, teams, and content frequency.
 */

import { useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient, createApiQueryClient, type SportsFeedItem, type TeamDashboard } from '@/lib/api-client';
import { type UserPreferences } from '@/hooks/useAuth';

export interface PersonalizedFeedData {
  // Aggregated team dashboards for all user's teams
  teamDashboards: TeamDashboard[];

  // Filtered sports feed based on preferences
  sportsFeed: SportsFeedItem[];

  // Combined news from all followed teams
  aggregatedNews: Array<{
    id: string;
    title: string;
    category: 'injuries' | 'roster' | 'trade' | 'general';
    published_at: string;
    summary?: string;
    url?: string;
    teamId?: string;
    teamName?: string;
    sportId?: string;
    priority: number;
  }>;

  // Featured team (highest affinity score)
  featuredTeam?: TeamDashboard;

  // Loading and error states
  isLoading: boolean;
  error: Error | null;
}

interface UsePersonalizedFeedOptions {
  enabled?: boolean;
  refetchInterval?: number;
}

/**
 * Hook to fetch and aggregate personalized content based on user preferences
 */
export function usePersonalizedFeed(
  userPreferences: UserPreferences,
  firebaseAuth?: { getIdToken: (forceRefresh?: boolean) => Promise<string | null>; isAuthenticated: boolean; userId?: string },
  options: UsePersonalizedFeedOptions = {}
): PersonalizedFeedData {
  const { enabled = true, refetchInterval } = options;

  // Get query configurations with Firebase auth
  const queryConfigs = createApiQueryClient(firebaseAuth);

  // Extract team IDs for data fetching
  const teamIds = useMemo(() => userPreferences.teams.map(team => team.teamId), [userPreferences.teams]);
  const sportIds = useMemo(() => userPreferences.sports.map(sport => sport.sportId), [userPreferences.sports]);

  // Fetch team dashboards for all user's teams
  const teamDashboardQueries = teamIds.map(teamId =>
    useQuery({
      ...queryConfigs.getTeamDashboard(teamId),
      enabled: enabled && firebaseAuth?.isAuthenticated && !!teamId,
      refetchInterval,
    })
  );

  // Fetch personalized sports feed
  const {
    data: sportsFeedData,
    isLoading: sportsFeedLoading,
    error: sportsFeedError,
  } = useQuery({
    ...queryConfigs.getSportsFeed({
      sportId: sportIds.length > 0 ? sportIds[0] : undefined, // For now, use first sport
      pageSize: getContentLimit(userPreferences.preferences.contentFrequency),
    }),
    enabled: enabled && firebaseAuth?.isAuthenticated,
    refetchInterval,
  });

  // Determine loading state
  const isLoading = teamDashboardQueries.some(query => query.isLoading) || sportsFeedLoading;

  // Determine error state
  const error = teamDashboardQueries.find(query => query.error)?.error as Error || sportsFeedError as Error || null;

  // Process and aggregate data
  const personalizedData = useMemo((): PersonalizedFeedData => {
    // Get successful team dashboard data
    const teamDashboards = teamDashboardQueries
      .filter(query => query.data && !query.error)
      .map(query => query.data!)
      .filter(Boolean);

    // Filter sports feed based on user preferences
    const filteredSportsFeed = filterSportsFeedByPreferences(
      sportsFeedData?.items || [],
      userPreferences
    );

    // Aggregate news from all team dashboards
    const aggregatedNews = aggregateTeamNews(teamDashboards, userPreferences);

    // Find featured team (highest affinity score)
    const featuredTeam = findFeaturedTeam(teamDashboards, userPreferences);

    return {
      teamDashboards,
      sportsFeed: filteredSportsFeed,
      aggregatedNews,
      featuredTeam,
      isLoading,
      error,
    };
  }, [teamDashboardQueries, sportsFeedData, userPreferences, isLoading, error]);

  return personalizedData;
}

/**
 * Determine content limit based on user's frequency preference
 */
function getContentLimit(frequency: 'minimal' | 'standard' | 'comprehensive'): number {
  switch (frequency) {
    case 'minimal':
      return 10;
    case 'standard':
      return 25;
    case 'comprehensive':
      return 50;
    default:
      return 25;
  }
}

/**
 * Filter sports feed items based on user preferences
 */
function filterSportsFeedByPreferences(
  feedItems: SportsFeedItem[],
  userPreferences: UserPreferences
): SportsFeedItem[] {
  const enabledNewsTypes = userPreferences.preferences.newsTypes
    .filter(nt => nt.enabled)
    .map(nt => nt.type);

  const userSportIds = userPreferences.sports.map(s => s.sportId);
  const userTeamIds = userPreferences.teams.map(t => t.teamId);

  return feedItems
    .filter(item => {
      // Filter by news type preferences
      if (!enabledNewsTypes.includes(item.category)) {
        return false;
      }

      // Prioritize content from user's sports
      const hasUserSport = item.sports.some(sportId => userSportIds.includes(sportId));
      if (hasUserSport) return true;

      // Prioritize content from user's teams
      const hasUserTeam = item.teams.some(teamId => userTeamIds.includes(teamId));
      if (hasUserTeam) return true;

      // Include general content with lower priority
      return item.category === 'general';
    })
    .sort((a, b) => {
      // Sort by priority and recency
      const aPriority = calculateContentPriority(a, userPreferences);
      const bPriority = calculateContentPriority(b, userPreferences);

      if (aPriority !== bPriority) {
        return bPriority - aPriority; // Higher priority first
      }

      // If same priority, sort by published date (newer first)
      return new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime();
    });
}

/**
 * Calculate content priority based on user preferences
 */
function calculateContentPriority(item: SportsFeedItem, userPreferences: UserPreferences): number {
  let priority = item.priority || 0;

  // Boost priority for user's teams
  const userTeamIds = userPreferences.teams.map(t => t.teamId);
  if (item.teams.some(teamId => userTeamIds.includes(teamId))) {
    priority += 10;
  }

  // Boost priority for user's sports
  const userSportIds = userPreferences.sports.map(s => s.sportId);
  if (item.sports.some(sportId => userSportIds.includes(sportId))) {
    priority += 5;
  }

  // Apply news type priority from user preferences
  const newsTypePref = userPreferences.preferences.newsTypes.find(nt => nt.type === item.category);
  if (newsTypePref) {
    priority += (6 - newsTypePref.priority); // Invert priority (1 = highest = +5, 5 = lowest = +1)
  }

  return priority;
}

/**
 * Aggregate news from all team dashboards
 */
function aggregateTeamNews(
  teamDashboards: TeamDashboard[],
  userPreferences: UserPreferences
): PersonalizedFeedData['aggregatedNews'] {
  const allNews: PersonalizedFeedData['aggregatedNews'] = [];

  teamDashboards.forEach(dashboard => {
    const team = userPreferences.teams.find(t => t.teamId === dashboard.team.id);

    dashboard.news.forEach(article => {
      allNews.push({
        ...article,
        teamId: dashboard.team.id,
        teamName: dashboard.team.name,
        sportId: team?.sportId,
        priority: calculateNewsPriority(article, userPreferences, team?.affinityScore || 0),
      });
    });
  });

  // Sort by priority and date
  return allNews
    .sort((a, b) => {
      if (a.priority !== b.priority) {
        return b.priority - a.priority; // Higher priority first
      }
      return new Date(b.published_at).getTime() - new Date(a.published_at).getTime();
    })
    .slice(0, getContentLimit(userPreferences.preferences.contentFrequency));
}

/**
 * Calculate news priority based on team affinity and user preferences
 */
function calculateNewsPriority(
  article: { category: string },
  userPreferences: UserPreferences,
  teamAffinityScore: number
): number {
  let priority = teamAffinityScore * 10; // Base priority from team affinity

  // Apply news type preference
  const newsTypePref = userPreferences.preferences.newsTypes.find(nt => nt.type === article.category);
  if (newsTypePref && newsTypePref.enabled) {
    priority += (6 - newsTypePref.priority) * 2; // News type priority boost
  } else if (!newsTypePref?.enabled) {
    priority -= 5; // Penalty for disabled news types
  }

  return Math.max(0, priority);
}

/**
 * Find the featured team (highest affinity score)
 */
function findFeaturedTeam(
  teamDashboards: TeamDashboard[],
  userPreferences: UserPreferences
): TeamDashboard | undefined {
  if (teamDashboards.length === 0) return undefined;

  // Find team with highest affinity score
  let featuredTeam = teamDashboards[0];
  let highestAffinity = 0;

  teamDashboards.forEach(dashboard => {
    const team = userPreferences.teams.find(t => t.teamId === dashboard.team.id);
    if (team && team.affinityScore > highestAffinity) {
      highestAffinity = team.affinityScore;
      featuredTeam = dashboard;
    }
  });

  return featuredTeam;
}

export default usePersonalizedFeed;