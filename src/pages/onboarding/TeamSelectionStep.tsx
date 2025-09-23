import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { toast } from "@/components/ui/use-toast";
import { AlertCircle } from "lucide-react";
import { OnboardingLayout } from "./OnboardingLayout";
import { createApiQueryClient, type OnboardingTeam, apiClient } from "@/lib/api-client";
import { useFirebaseAuth } from "@/contexts/FirebaseAuthContext";
import { updateLocalOnboardingStep, getLocalOnboardingStatus } from "@/lib/onboarding-storage";
import { VirtualizedTeamList } from "@/components/VirtualizedTeamList";
import { useOnboardingPrefetch } from "@/hooks/useOnboardingPrefetch";
import { cn } from "@/lib/utils";

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

  // Fetch teams data with fallback
  const {
    data: teamsData,
    isLoading,
    error,
  } = useQuery({
    ...queryConfigs.getOnboardingTeams(sportIds),
    retry: 2,
    retryDelay: 1000,
    enabled: sportIds.length > 0,
  });

  // Track API availability
  useEffect(() => {
    if (error) {
      setIsApiAvailable(false);
      console.warn('Teams API unavailable, using fallback data:', error);
      toast({
        title: "Working Offline",
        description: "Using offline mode. Your progress will be saved.",
        variant: "default",
      });
    }
  }, [error]);

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

  // Initialize teams state when data loads
  useEffect(() => {
    if (activeTeamsData.length > 0) {
      // Try to restore previous selections from localStorage
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
    }
  }, [activeTeamsData, localStatus]);

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

    // Try to save to API if available
    if (isApiAvailable && isAuthenticated) {
      try {
        await apiClient.updateOnboardingStep({
          step: 3,
          data: { teams: teamsData }
        });
        console.log('Team selection saved to API');
      } catch (error) {
        console.warn('Failed to save teams to API, continuing with localStorage:', error);
        toast({
          title: "Saved Offline",
          description: "Your team selection has been saved locally.",
          variant: "default",
        });
      }
    }

    navigate("/onboarding/step/4");
  };

  // Show loading state
  if (isLoading && !activeTeamsData.length) {
    return (
      <OnboardingLayout
        step={3}
        totalSteps={5}
        title="Select Your Teams"
        subtitle="Loading teams..."
        showProgress={true}
        completedSteps={2}
      >
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
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
        {/* Offline indicator */}
        {!isApiAvailable && (
          <div className="bg-orange-50 dark:bg-orange-950/30 border border-orange-200 dark:border-orange-800 rounded-lg p-4">
            <div className="flex items-center gap-3">
              <AlertCircle className="h-5 w-5 text-orange-600 dark:text-orange-400" />
              <div className="text-sm">
                <p className="font-medium text-orange-800 dark:text-orange-200">
                  Working Offline
                </p>
                <p className="text-orange-700 dark:text-orange-300">
                  Your selections are being saved locally and will sync when connection is restored.
                </p>
              </div>
            </div>
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
                  />
                ) : (
                  <div className="grid gap-3">
                    {sportTeams.map(team => (
                      <div
                        key={team.id}
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
                )}
              </div>
            );
          })}
        </div>

        {/* Status */}
        <div className="text-center">
          <span className="font-display font-semibold text-primary">
            {selectedCount} teams selected
          </span>
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