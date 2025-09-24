import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { toast } from "@/components/ui/use-toast";
import { AlertCircle, RefreshCw, Wifi, WifiOff, AlertTriangle } from "lucide-react";
import { OnboardingLayout } from "./OnboardingLayout";
import { createApiQueryClient, type OnboardingTeam, apiClient, ApiClientError } from "@/lib/api-client";
import { useFirebaseAuth } from "@/contexts/FirebaseAuthContext";
import { updateLocalOnboardingStep, getLocalOnboardingStatus } from "@/lib/onboarding-storage";
import { VirtualizedTeamList } from "@/components/VirtualizedTeamList";
import { useOnboardingPrefetch } from "@/hooks/useOnboardingPrefetch";
import { cn } from "@/lib/utils";
import { reportApiError, reportOnboardingError, ErrorLevel, ErrorCategory } from "@/lib/error-reporting";
import { defaultRetryManager } from "@/lib/api-retry";
import { TeamSelectionSkeleton, SportSectionSkeleton } from "@/components/skeletons/TeamSelectionSkeleton";

interface TeamWithSelection extends OnboardingTeam {
  isSelected: boolean;
  affinityScore: number;
}

export function TeamSelectionStep() {
  const navigate = useNavigate();
  const { isAuthenticated, getIdToken, user } = useFirebaseAuth();

  const [teams, setTeams] = useState<TeamWithSelection[]>([]);
  const [selectedCount, setSelectedCount] = useState(0);
  const [isApiAvailable, setIsApiAvailable] = useState(true);
  const [apiError, setApiError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  const [isRetrying, setIsRetrying] = useState(false);
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  // Progressive loading state
  const [loadedTeamCount, setLoadedTeamCount] = useState(0);
  const [totalTeamCount, setTotalTeamCount] = useState<number | undefined>(undefined);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const CHUNK_SIZE = 20; // Number of teams to load per chunk

  // Initialize prefetching for next steps
  const { prefetchPreferences } = useOnboardingPrefetch();

  // Get previously selected sports from localStorage
  const localStatus = getLocalOnboardingStatus();
  const selectedSports = localStatus?.selectedSports || [];
  const sportIds = selectedSports.map(s => s.sportId);

  // Set up API client
  const queryConfigs = createApiQueryClient(
    isAuthenticated ? { getIdToken, isAuthenticated: true, userId: user?.uid } : undefined
  );

  // Enhanced retry configuration for team selection API
  const retryConfig = {
    maxRetries: 3,
    baseDelay: 1000,
    backoffFactor: 2,
    retryCondition: (error: unknown) => {
      // Retry on network errors, timeouts, and 5xx errors
      if (error instanceof ApiClientError) {
        const shouldRetry = error.statusCode >= 500 ||
                          error.statusCode === 0 ||
                          error.code === 'NETWORK_ERROR' ||
                          error.code === 'TIMEOUT';
        return shouldRetry;
      }
      return true; // Retry unknown errors
    },
    onRetry: (attempt: number, error: unknown) => {
      setRetryCount(attempt);
      setIsRetrying(true);
      reportApiError(`Team selection API retry attempt ${attempt}`, error, {
        step: 3,
        sportIds,
        attempt,
      });
      toast({
        title: "Retrying...",
        description: `Attempting to load teams (${attempt}/${3})`,
        variant: "default",
        duration: 2000,
      });
    },
    onMaxRetries: (error: unknown) => {
      reportOnboardingError(3, 'Team selection API failed after max retries', error, {
        sportIds,
        maxRetries: 3,
      });
      setApiError(getErrorMessage(error));
      setIsRetrying(false);
    },
  };

  // Fetch teams data with enhanced retry and error handling
  const {
    data: teamsData,
    isLoading,
    error,
    refetch,
    isRefetching,
  } = useQuery({
    ...queryConfigs.getOnboardingTeams(sportIds),
    enabled: sportIds.length > 0,
    retry: (failureCount, error) => {
      const shouldRetry = retryConfig.retryCondition(error);
      if (shouldRetry && failureCount < retryConfig.maxRetries) {
        if (retryConfig.onRetry) {
          retryConfig.onRetry(failureCount + 1, error);
        }
        return true;
      }
      if (failureCount >= retryConfig.maxRetries && retryConfig.onMaxRetries) {
        retryConfig.onMaxRetries(error);
      }
      return false;
    },
    retryDelay: (attemptIndex) => {
      return Math.min(retryConfig.baseDelay * Math.pow(retryConfig.backoffFactor, attemptIndex), 30000);
    },
  });

  // Network status monitoring
  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      if (error && retryCount > 0) {
        toast({
          title: "Connection Restored",
          description: "Attempting to reload team data...",
          variant: "default",
        });
        refetch();
      }
    };

    const handleOffline = () => {
      setIsOnline(false);
      toast({
        title: "Connection Lost",
        description: "Working in offline mode with cached data.",
        variant: "destructive",
      });
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [error, retryCount, refetch]);

  // Track API availability and error states
  useEffect(() => {
    if (error) {
      setIsApiAvailable(false);
      setIsRetrying(false);

      const errorMessage = getErrorMessage(error);
      setApiError(errorMessage);

      reportApiError('Team selection API error', error instanceof Error ? error : new Error(String(error)), {
        step: 3,
        sportIds,
        retryCount,
        isOnline,
      });

      console.warn('Teams API unavailable, using fallback data:', error);
      toast({
        title: "API Error",
        description: "Using fallback team data. Your progress will still be saved.",
        variant: "destructive",
        duration: 5000,
      });
    } else if (teamsData) {
      // API call successful
      setIsApiAvailable(true);
      setApiError(null);
      setRetryCount(0);
      setIsRetrying(false);
    }
  }, [error, teamsData, retryCount, isOnline, sportIds, getErrorMessage]);

  // Helper function to get user-friendly error message
  const getErrorMessage = useCallback((error: unknown): string => {
    if (error instanceof ApiClientError) {
      switch (error.code) {
        case 'NETWORK_ERROR':
          return 'Unable to connect to our servers. Please check your internet connection.';
        case 'TIMEOUT':
          return 'The request took too long to complete. Please try again.';
        case 'HTTP_ERROR':
          if (error.statusCode >= 500) {
            return 'Our servers are experiencing issues. We\'re working to fix this.';
          }
          if (error.statusCode === 429) {
            return 'Too many requests. Please wait a moment and try again.';
          }
          if (error.statusCode >= 400) {
            return 'There was a problem with your request. Please try again.';
          }
          break;
      }
    }

    if (!isOnline) {
      return 'You appear to be offline. Please check your internet connection.';
    }

    return 'Something went wrong while loading teams. Please try again.';
  }, [isOnline]);

  // Fallback team data based on popular teams from selected sports
  const getFallbackTeams = (): OnboardingTeam[] => {
    const fallbackTeams: OnboardingTeam[] = [];

    selectedSports.forEach(sport => {
      switch (sport.sportId) {
        case 'nfl':
          fallbackTeams.push(
            { id: 'chiefs', name: 'Kansas City Chiefs', market: 'Kansas City', sportId: 'nfl', league: 'NFL', logo: '🏈' },
            { id: 'cowboys', name: 'Dallas Cowboys', market: 'Dallas', sportId: 'nfl', league: 'NFL', logo: '🏈' },
            { id: 'patriots', name: 'New England Patriots', market: 'New England', sportId: 'nfl', league: 'NFL', logo: '🏈' },
          );
          break;
        case 'nba':
          fallbackTeams.push(
            { id: 'lakers', name: 'Los Angeles Lakers', market: 'Los Angeles', sportId: 'nba', league: 'NBA', logo: '🏀' },
            { id: 'warriors', name: 'Golden State Warriors', market: 'Golden State', sportId: 'nba', league: 'NBA', logo: '🏀' },
            { id: 'celtics', name: 'Boston Celtics', market: 'Boston', sportId: 'nba', league: 'NBA', logo: '🏀' },
          );
          break;
        case 'mlb':
          fallbackTeams.push(
            { id: 'yankees', name: 'New York Yankees', market: 'New York', sportId: 'mlb', league: 'MLB', logo: '⚾' },
            { id: 'dodgers', name: 'Los Angeles Dodgers', market: 'Los Angeles', sportId: 'mlb', league: 'MLB', logo: '⚾' },
            { id: 'red-sox', name: 'Boston Red Sox', market: 'Boston', sportId: 'mlb', league: 'MLB', logo: '⚾' },
          );
          break;
        case 'nhl':
          fallbackTeams.push(
            { id: 'rangers', name: 'New York Rangers', market: 'New York', sportId: 'nhl', league: 'NHL', logo: '🏒' },
            { id: 'bruins', name: 'Boston Bruins', market: 'Boston', sportId: 'nhl', league: 'NHL', logo: '🏒' },
            { id: 'blackhawks', name: 'Chicago Blackhawks', market: 'Chicago', sportId: 'nhl', league: 'NHL', logo: '🏒' },
          );
          break;
      }
    });

    return fallbackTeams;
  };

  // Use API data if available, otherwise use fallback
  const activeTeamsData = teamsData || getFallbackTeams();

  // Progressive team loading function
  const loadTeamsProgressively = useCallback((teamsData: OnboardingTeam[], chunkStart = 0) => {
    const previousSelections = localStatus?.selectedTeams || [];
    const chunkEnd = Math.min(chunkStart + CHUNK_SIZE, teamsData.length);
    const chunk = teamsData.slice(chunkStart, chunkEnd);

    const teamsWithSelection = chunk.map(team => {
      const previousSelection = previousSelections.find(t => t.teamId === team.id);
      return {
        ...team,
        isSelected: !!previousSelection,
        affinityScore: previousSelection?.affinityScore || 5, // Default affinity
      };
    });

    if (chunkStart === 0) {
      // First chunk - replace all teams
      setTeams(teamsWithSelection);
      setLoadedTeamCount(teamsWithSelection.length);
      setTotalTeamCount(teamsData.length);
    } else {
      // Subsequent chunks - append to existing teams
      setTeams(prev => [...prev, ...teamsWithSelection]);
      setLoadedTeamCount(prev => prev + teamsWithSelection.length);
    }

    return chunkEnd < teamsData.length; // Return true if more chunks to load
  }, [localStatus, CHUNK_SIZE]);

  // Handle loading more teams
  const handleLoadMore = useCallback(() => {
    if (!activeTeamsData.length || isLoadingMore || loadedTeamCount >= activeTeamsData.length) {
      return;
    }

    setIsLoadingMore(true);

    // Simulate progressive loading with a small delay for better UX
    setTimeout(() => {
      const hasMore = loadTeamsProgressively(activeTeamsData, loadedTeamCount);
      setIsLoadingMore(false);

      if (!hasMore) {
        // All teams loaded
        setLoadedTeamCount(activeTeamsData.length);
      }
    }, 300); // Small delay to show loading state
  }, [activeTeamsData, loadedTeamCount, isLoadingMore, loadTeamsProgressively]);

  // Initialize teams state when data loads
  useEffect(() => {
    if (activeTeamsData.length > 0) {
      // For large team lists (>50), use progressive loading
      if (activeTeamsData.length > 50) {
        loadTeamsProgressively(activeTeamsData, 0);
      } else {
        // For smaller lists, load all at once
        const previousSelections = localStatus?.selectedTeams || [];

        const teamsWithSelection = activeTeamsData.map(team => {
          const previousSelection = previousSelections.find(t => t.teamId === team.id);
          return {
            ...team,
            isSelected: !!previousSelection,
            affinityScore: previousSelection?.affinityScore || 5, // Default affinity
          };
        });

        setTeams(teamsWithSelection);
        setLoadedTeamCount(teamsWithSelection.length);
        setTotalTeamCount(teamsWithSelection.length);
      }
    }
  }, [activeTeamsData, localStatus, loadTeamsProgressively]);

  // Update selected count
  useEffect(() => {
    setSelectedCount(teams.filter(team => team.isSelected).length);
  }, [teams]);

  const handleToggleTeam = useCallback((teamId: string) => {
    setTeams(prev => {
      const updatedTeams = prev.map(team =>
        team.id === teamId
          ? { ...team, isSelected: !team.isSelected }
          : team
      );

      // Prefetch preferences when user selects first team
      const newSelectedCount = updatedTeams.filter(t => t.isSelected).length;
      if (newSelectedCount === 1 && prev.filter(t => t.isSelected).length === 0) {
        prefetchPreferences();
      }

      return updatedTeams;
    });
  }, [prefetchPreferences]);

  const handleAffinityChange = useCallback((teamId: string, affinity: number) => {
    setTeams(prev =>
      prev.map(team =>
        team.id === teamId
          ? { ...team, affinityScore: affinity }
          : team
      )
    );
  }, []);

  const handleContinue = async () => {
    const selectedTeams = teams.filter(team => team.isSelected);

    // Convert to API format
    const teamsData = selectedTeams.map(team => ({
      teamId: team.id,
      sportId: team.sportId,
      affinityScore: team.affinityScore,
    }));

    // Always save to localStorage first
    updateLocalOnboardingStep(3, { selectedTeams: teamsData });

    // Try to save to API if available with enhanced retry
    if (isApiAvailable && isAuthenticated) {
      try {
        await defaultRetryManager.executeWithRetry(
          () => apiClient.updateOnboardingStep({
            step: 3,
            data: { teams: teamsData }
          }),
          {
            maxRetries: 2,
            baseDelay: 500,
            onRetry: (attempt) => {
              toast({
                title: "Saving...",
                description: `Saving your team selection (attempt ${attempt}/2)`,
                variant: "default",
                duration: 1500,
              });
            },
            onMaxRetries: (error) => {
              reportOnboardingError(3, 'Failed to save team selection to API', error, {
                selectedTeams: teamsData,
              });
            },
          }
        );
        console.log('Team selection saved to API');
        toast({
          title: "Teams Saved",
          description: "Your team selection has been saved successfully.",
          variant: "default",
          duration: 2000,
        });
      } catch (error) {
        console.warn('Failed to save teams to API, continuing with localStorage:', error);
        reportApiError('Failed to save team selection', error instanceof Error ? error : new Error(String(error)), {
          step: 3,
          selectedTeams: teamsData,
        });
        toast({
          title: "Saved Offline",
          description: "Your team selection has been saved locally and will sync when online.",
          variant: "default",
          duration: 3000,
        });
      }
    }

    navigate("/onboarding/step/4");
  };

  // Manual retry function
  const handleRetry = async () => {
    setApiError(null);
    setRetryCount(0);
    setIsRetrying(true);

    try {
      await refetch();
      toast({
        title: "Refreshed",
        description: "Team data has been reloaded successfully.",
        variant: "default",
      });
    } catch (error) {
      toast({
        title: "Retry Failed",
        description: "Unable to reload team data. Using offline mode.",
        variant: "destructive",
      });
    } finally {
      setIsRetrying(false);
    }
  };

  // Show enhanced loading state with skeleton UI
  if ((isLoading || isRetrying || isRefetching) && !activeTeamsData.length) {
    const loadingTitle = isRetrying
      ? `Retrying Connection${retryCount > 0 ? ` (${retryCount}/3)` : ''}...`
      : isRefetching
        ? "Refreshing Teams..."
        : "Loading Teams...";

    const loadingSubtitle = isRetrying
      ? "Having trouble connecting. Please wait while we retry..."
      : isRefetching
        ? "Getting the latest team information..."
        : "Fetching teams from your selected sports...";

    return (
      <OnboardingLayout
        step={3}
        totalSteps={5}
        title="Select Your Teams"
        subtitle={loadingTitle}
        showProgress={true}
        completedSteps={2}
      >
        <div className="space-y-6">
          {/* Status message */}
          <div className="text-center space-y-2">
            <div className="flex items-center justify-center gap-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></div>
              <p className="text-sm text-muted-foreground">
                {loadingSubtitle}
              </p>
            </div>
            {isRetrying && (
              <div className="bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-800 rounded-lg p-3 mt-4">
                <p className="text-xs text-blue-800 dark:text-blue-200">
                  <strong>Connection Issue:</strong> We're working to restore the connection.
                  If this continues, we'll show you popular teams to choose from.
                </p>
              </div>
            )}
          </div>

          {/* Enhanced skeleton loading */}
          <TeamSelectionSkeleton
            sports={selectedSports.map(sport => ({
              sportId: sport.sportId,
              name: sport.sportId.toUpperCase()
            }))}
            itemsPerSport={4}
            showVirtualized={false}
          />
        </div>
      </OnboardingLayout>
    );
  }

  // Show message if no sports selected
  if (sportIds.length === 0) {
    return (
      <OnboardingLayout
        step={3}
        totalSteps={5}
        title="Select Your Teams"
        subtitle="No sports selected"
        showProgress={true}
        completedSteps={2}
      >
        <div className="text-center space-y-6">
          <p className="text-lg font-body text-muted-foreground">
            Please go back and select your sports first.
          </p>
          <Button onClick={() => navigate("/onboarding/step/2")}>
            Go Back to Sports Selection
          </Button>
        </div>
      </OnboardingLayout>
    );
  }

  return (
    <OnboardingLayout
      step={3}
      totalSteps={5}
      title="Select Your Teams"
      subtitle="Choose your favorite teams from your selected sports"
      showProgress={true}
      completedSteps={2}
      onNext={handleContinue}
      isNextDisabled={selectedCount === 0}
    >
      <div className="space-y-6">
        {/* Connection and Error Status */}
        {(!isOnline || !isApiAvailable || apiError || isRetrying) && (
          <div className="space-y-3">
            {/* Network Status */}
            {!isOnline && (
              <div className="bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800 rounded-lg p-4">
                <div className="flex items-center gap-3">
                  <WifiOff className="h-5 w-5 text-red-600 dark:text-red-400" />
                  <div className="flex-1 text-sm">
                    <p className="font-medium text-red-800 dark:text-red-200">
                      No Internet Connection
                    </p>
                    <p className="text-red-700 dark:text-red-300">
                      You're currently offline. Team data may be limited, but your selections will still be saved.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* API Error Status */}
            {apiError && isOnline && (
              <div className="bg-yellow-50 dark:bg-yellow-950/30 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
                <div className="flex items-center gap-3">
                  <AlertTriangle className="h-5 w-5 text-yellow-600 dark:text-yellow-400" />
                  <div className="flex-1 text-sm">
                    <p className="font-medium text-yellow-800 dark:text-yellow-200">
                      Connection Issues
                    </p>
                    <p className="text-yellow-700 dark:text-yellow-300 mb-2">
                      {apiError}
                    </p>
                    <Button
                      onClick={handleRetry}
                      disabled={isRetrying || isRefetching}
                      size="sm"
                      variant="outline"
                      className="h-8 text-xs"
                    >
                      {isRetrying || isRefetching ? (
                        <>
                          <RefreshCw className="w-3 h-3 mr-1 animate-spin" />
                          Retrying...
                        </>
                      ) : (
                        <>
                          <RefreshCw className="w-3 h-3 mr-1" />
                          Try Again
                        </>
                      )}
                    </Button>
                  </div>
                </div>
              </div>
            )}

            {/* Retry Status */}
            {isRetrying && (
              <div className="bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                <div className="flex items-center gap-3">
                  <RefreshCw className="h-5 w-5 text-blue-600 dark:text-blue-400 animate-spin" />
                  <div className="text-sm">
                    <p className="font-medium text-blue-800 dark:text-blue-200">
                      Retrying Connection{retryCount > 0 && ` (${retryCount}/3)`}
                    </p>
                    <p className="text-blue-700 dark:text-blue-300">
                      Attempting to reload team data...
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Fallback Mode */}
            {!isApiAvailable && isOnline && !apiError && (
              <div className="bg-orange-50 dark:bg-orange-950/30 border border-orange-200 dark:border-orange-800 rounded-lg p-4">
                <div className="flex items-center gap-3">
                  <Wifi className="h-5 w-5 text-orange-600 dark:text-orange-400" />
                  <div className="flex-1 text-sm">
                    <p className="font-medium text-orange-800 dark:text-orange-200">
                      Using Cached Data
                    </p>
                    <p className="text-orange-700 dark:text-orange-300">
                      Showing popular teams from your selected sports. Your selections will be saved and synced when connection is restored.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Instructions */}
        <div className="text-center">
          <p className="text-lg font-body text-muted-foreground">
            Select teams from your chosen sports to personalize your content feed.
          </p>
        </div>

        {/* Teams list grouped by sport */}
        <div className="space-y-6">
          {selectedSports.map(sport => {
            const sportTeams = teams.filter(team => team.sportId === sport.sportId);

            if (sportTeams.length === 0) return null;

            return (
              <div key={sport.sportId} className="space-y-3">
                <h3 className="font-display font-bold text-lg capitalize">
                  {sport.sportId.toUpperCase()} Teams ({sportTeams.length})
                </h3>

                {/* Use virtualized list for large team lists */}
                {sportTeams.length > 10 ? (
                  <VirtualizedTeamList
                    teams={sportTeams}
                    onToggleTeam={handleToggleTeam}
                    onAffinityChange={handleAffinityChange}
                    containerHeight={400}
                    itemHeight={120}
                    className="border rounded-lg"
                    isLoading={isLoadingMore}
                    loadedCount={loadedTeamCount}
                    totalCount={totalTeamCount}
                    onLoadMore={handleLoadMore}
                    loadingChunkSize={CHUNK_SIZE}
                  />
                ) : (
                  <div className="space-y-3">
                    <div className="grid gap-3">
                      {sportTeams.map(team => (
                        <div
                          key={team.id}
                          data-testid="team-card"
                          data-selected={team.isSelected}
                          className={cn(
                            "p-4 border rounded-lg hover:shadow-md transition-all duration-200",
                            team.isSelected && "ring-2 ring-primary bg-primary/5"
                          )}
                        >
                          <div className="flex items-center gap-4">
                            <div className="text-2xl">{team.logo || '🏆'}</div>
                            <div className="flex-1">
                              <h4 className="font-display font-semibold">{team.name}</h4>
                              <div className="flex items-center gap-2">
                                <Badge variant="secondary">{team.league}</Badge>
                                {team.market && (
                                  <Badge variant="outline">{team.market}</Badge>
                                )}
                              </div>
                            </div>
                            <div className="flex items-center gap-3">
                              {team.isSelected && (
                                <div className="flex items-center gap-1">
                                  {[1, 2, 3, 4, 5].map(rating => (
                                    <button
                                      key={rating}
                                      onClick={() => handleAffinityChange(team.id, rating)}
                                      className={cn(
                                        "w-4 h-4 transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 rounded-sm",
                                        rating <= team.affinityScore
                                          ? "text-yellow-400"
                                          : "text-gray-300"
                                      )}
                                      aria-label={`Rate ${team.name} ${rating} stars`}
                                    >
                                      <svg className="w-full h-full fill-current" viewBox="0 0 24 24">
                                        <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                                      </svg>
                                    </button>
                                  ))}
                                </div>
                              )}
                              <input
                                type="checkbox"
                                checked={team.isSelected}
                                onChange={() => handleToggleTeam(team.id)}
                                className="w-4 h-4 text-primary border-gray-300 rounded focus:ring-primary"
                                aria-label={`Select ${team.name}`}
                              />
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* Progressive loading indicator for non-virtualized lists */}
                    {totalTeamCount !== undefined &&
                     loadedTeamCount < totalTeamCount &&
                     sport.sportId === selectedSports[selectedSports.length - 1]?.sportId && (
                      <div className="text-center py-4">
                        {isLoadingMore ? (
                          <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
                            <RefreshCw className="w-4 h-4 animate-spin" />
                            <span>Loading more teams...</span>
                          </div>
                        ) : (
                          <Button
                            variant="outline"
                            onClick={handleLoadMore}
                            disabled={loadedTeamCount >= totalTeamCount}
                            className="text-sm"
                          >
                            Load More Teams ({loadedTeamCount} / {totalTeamCount})
                          </Button>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Status and Recovery Options */}
        <div className="text-center space-y-3">
          <span className="font-display font-semibold text-primary">
            {selectedCount} teams selected
          </span>

          {/* Show recovery options if there are persistent issues */}
          {apiError && !isOnline && selectedCount === 0 && (
            <div className="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg p-4 text-sm">
              <p className="font-medium text-gray-800 dark:text-gray-200 mb-2">
                Having trouble loading teams?
              </p>
              <div className="space-y-2 text-gray-600 dark:text-gray-400">
                <p>• Check your internet connection and try refreshing</p>
                <p>• You can continue with popular teams shown above</p>
                <p>• Your selections will sync once you're back online</p>
              </div>
            </div>
          )}

          {/* Alternative action if no teams could be loaded and user wants to skip */}
          {teams.length === 0 && apiError && (
            <div className="mt-4">
              <Button
                variant="outline"
                onClick={() => {
                  updateLocalOnboardingStep(3, { selectedTeams: [] });
                  navigate("/onboarding/step/4");
                }}
                className="text-sm"
              >
                Skip Team Selection for Now
              </Button>
              <p className="text-xs text-muted-foreground mt-2">
                You can add teams later from your profile settings
              </p>
            </div>
          )}
        </div>

        {/* Tip */}
        {selectedCount > 0 && (
          <div className="bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
            <p className="text-sm text-blue-800 dark:text-blue-200 font-body">
              <strong>Tip:</strong> Use the star rating to indicate how much you follow each team.
              Higher ratings will prioritize that team's content in your feed.
            </p>
          </div>
        )}
      </div>
    </OnboardingLayout>
  );
}

export default TeamSelectionStep;