import { useState, useEffect, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient, type Team, type TeamSearchParams, type EnhancedTeam, type EnhancedTeamSearchResponse } from '@/lib/api-client';

interface UseTeamSelectionOptions {
  sportIds?: string[];
  leagueIds?: string[];
  initialSelectedTeams?: Team[];
  debounceMs?: number;
  pageSize?: number;
  useEnhancedSearch?: boolean;
}

export function useTeamSelection({
  sportIds = [],
  leagueIds = [],
  initialSelectedTeams = [],
  debounceMs = 300,
  pageSize = 50,
  useEnhancedSearch = true,
}: UseTeamSelectionOptions = {}) {
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedQuery, setDebouncedQuery] = useState('');
  const [selectedTeams, setSelectedTeams] = useState<Team[]>(initialSelectedTeams);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  // Debounce search query
  useEffect(() => {
    const timeout = setTimeout(() => {
      setDebouncedQuery(searchQuery);
    }, debounceMs);

    return () => clearTimeout(timeout);
  }, [searchQuery, debounceMs]);

  // Build search parameters
  const searchParams: TeamSearchParams = {
    query: debouncedQuery || undefined,
    sport_id: sportIds.length > 0 ? sportIds.join(',') : undefined,
    league_id: leagueIds.length > 0 ? leagueIds.join(',') : undefined,
    page_size: pageSize,
    is_active: true,
  };

  // Team search query (enhanced or regular)
  const {
    data: searchResults,
    isLoading: isSearching,
    error: searchError,
    refetch: refetchTeams,
  } = useQuery({
    queryKey: useEnhancedSearch
      ? ['teams', 'search-enhanced', searchParams]
      : ['teams', 'search', searchParams],
    queryFn: () => useEnhancedSearch
      ? apiClient.searchTeamsEnhanced(searchParams)
      : apiClient.searchTeams(searchParams),
    enabled: (debouncedQuery.length >= 2) || ((sportIds.length > 0 || leagueIds.length > 0) && debouncedQuery.length === 0),
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
  });

  // Handle team selection
  const toggleTeamSelection = useCallback((team: Team) => {
    setSelectedTeams(prev => {
      const isSelected = prev.some(t => t.id === team.id);
      if (isSelected) {
        return prev.filter(t => t.id !== team.id);
      } else {
        return [...prev, team];
      }
    });
  }, []);

  const selectTeam = useCallback((team: Team) => {
    setSelectedTeams(prev => {
      const isAlreadySelected = prev.some(t => t.id === team.id);
      if (!isAlreadySelected) {
        return [...prev, team];
      }
      return prev;
    });
  }, []);

  const deselectTeam = useCallback((teamId: string) => {
    setSelectedTeams(prev => prev.filter(t => t.id !== teamId));
  }, []);

  const clearSelection = useCallback(() => {
    setSelectedTeams([]);
  }, []);

  const isTeamSelected = useCallback((teamId: string) => {
    return selectedTeams.some(t => t.id === teamId);
  }, [selectedTeams]);

  // Get filtered teams (search results or all teams for selected sports)
  const teams = searchResults?.items || [];
  const enhancedTeams = useEnhancedSearch ? (teams as EnhancedTeam[]) : [];
  const searchMetadata = useEnhancedSearch ? (searchResults as EnhancedTeamSearchResponse)?.search_metadata : undefined;

  // Create stable reference to setSelectedTeams
  const memoizedSetSelectedTeams = setSelectedTeams;

  return {
    // Search state
    searchQuery,
    setSearchQuery,
    debouncedQuery,
    isSearching,
    searchError,
    refetchTeams,

    // Teams data
    teams,
    enhancedTeams, // Enhanced teams with search highlighting
    totalTeams: searchResults?.total || 0,
    hasMoreTeams: searchResults?.has_next || false,
    searchMetadata, // Enhanced search metadata

    // Selection state
    selectedTeams,
    setSelectedTeams: memoizedSetSelectedTeams,
    toggleTeamSelection,
    selectTeam,
    deselectTeam,
    clearSelection,
    isTeamSelected,
    selectedCount: selectedTeams.length,

    // Dropdown state
    isDropdownOpen,
    setIsDropdownOpen,

    // Enhanced search features
    useEnhancedSearch,
  };
}

export type UseTeamSelectionReturn = ReturnType<typeof useTeamSelection>;