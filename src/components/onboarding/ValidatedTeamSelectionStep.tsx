/**
 * Validated Team Selection Step
 *
 * Enhanced team selection component with comprehensive validation,
 * error handling, and recovery mechanisms.
 */

import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import { toast } from "@/components/ui/use-toast";
import { AlertCircle, Star, Loader2 } from "lucide-react";

import { OnboardingLayout } from "@/pages/onboarding/OnboardingLayout";
import { createApiQueryClient, type OnboardingTeam, apiClient } from "@/lib/api-client";
import { useFirebaseAuth } from "@/contexts/FirebaseAuthContext";
import { updateLocalOnboardingStep, getLocalOnboardingStatus } from "@/lib/onboarding-storage";
import { cn } from "@/lib/utils";

// Validation imports
import { useTeamSelectionValidation } from "@/hooks/useOnboardingValidation";
import { ErrorAlert, FieldError, RecoveryGuidance } from "@/components/error-boundaries/ErrorRecoveryComponents";
import { TeamSelectionSkeleton } from "@/components/fallback/OnboardingFallbackUI";
import { reportOnboardingError, reportValidationError } from "@/lib/error-reporting";
import { retryableFetch } from "@/lib/api-retry";

// Types
interface TeamWithSelection extends OnboardingTeam {
  isSelected: boolean;
  affinityScore: number;
  rank: number;
}

interface ValidationState {
  isValidating: boolean;
  showValidationErrors: boolean;
  hasBeenSubmitted: boolean;
}

interface TeamCardProps {
  team: TeamWithSelection;
  onToggle: (teamId: string) => void;
  onAffinityChange: (teamId: string, affinity: number) => void;
  hasError?: boolean;
  errorMessage?: string;
}

/**
 * Team Card Component with Validation
 */
function TeamCard({ team, onToggle, onAffinityChange, hasError, errorMessage }: TeamCardProps) {
  const handleAffinityClick = useCallback((rating: number) => {
    onAffinityChange(team.id, rating);
  }, [team.id, onAffinityChange]);

  const handleToggle = useCallback(() => {
    onToggle(team.id);
  }, [team.id, onToggle]);

  return (
    <Card
      data-testid={`team-card-${team.id}`}
      data-selected={team.isSelected}
      aria-invalid={hasError}
      aria-describedby={hasError ? `${team.id}-error` : undefined}
      className={cn(
        "hover:shadow-md transition-all duration-200",
        team.isSelected && "ring-2 ring-primary bg-primary/5",
        hasError && "border-red-300 bg-red-50/50 dark:border-red-800 dark:bg-red-950/30"
      )}
    >
      <CardContent className="p-4">
        <div className="flex items-center gap-4">
          <div className="text-2xl flex-shrink-0" aria-hidden="true">
            {team.logo || '🏆'}
          </div>

          <div className="flex-1">
            <h4 className="font-display font-semibold">{team.name}</h4>
            <div className="flex items-center gap-2">
              <Badge variant="secondary">{team.league}</Badge>
              {team.market && (
                <Badge variant="outline">{team.market}</Badge>
              )}
            </div>
            {team.isSelected && team.rank > 0 && (
              <p className="text-sm text-primary font-medium mt-1">
                #{team.rank} choice
              </p>
            )}
          </div>

          <div className="flex items-center gap-3">
            {/* Affinity rating */}
            {team.isSelected && (
              <div className="flex items-center gap-1" role="radiogroup" aria-label={`Affinity rating for ${team.name}`}>
                {[1, 2, 3, 4, 5].map(rating => (
                  <button
                    key={rating}
                    onClick={() => handleAffinityClick(rating)}
                    role="radio"
                    aria-checked={rating <= team.affinityScore}
                    aria-label={`Rate ${team.name} ${rating} out of 5 stars`}
                    className={cn(
                      "w-4 h-4 transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-1 rounded",
                      rating <= team.affinityScore
                        ? "text-yellow-400"
                        : "text-gray-300"
                    )}
                  >
                    <Star className="w-full h-full fill-current" />
                  </button>
                ))}
              </div>
            )}

            {/* Selection checkbox */}
            <Checkbox
              checked={team.isSelected}
              onCheckedChange={handleToggle}
              aria-label={`${team.isSelected ? 'Deselect' : 'Select'} ${team.name}`}
            />
          </div>
        </div>

        {/* Error message for this specific team */}
        {hasError && errorMessage && (
          <div id={`${team.id}-error`} className="mt-2">
            <FieldError
              error={errorMessage}
              field={team.id}
              severity="error"
            />
          </div>
        )}
      </CardContent>
    </Card>
  );
}

/**
 * Enhanced Team Selection Step with Validation
 */
export function ValidatedTeamSelectionStep() {
  const navigate = useNavigate();
  const { isAuthenticated, getIdToken, user } = useFirebaseAuth();

  // Component state
  const [teams, setTeams] = useState<TeamWithSelection[]>([]);
  const [selectedCount, setSelectedCount] = useState(0);
  const [isApiAvailable, setIsApiAvailable] = useState(true);
  const [validationState, setValidationState] = useState<ValidationState>({
    isValidating: false,
    showValidationErrors: false,
    hasBeenSubmitted: false,
  });

  // Validation hook
  const validation = useTeamSelectionValidation();

  // Get previously selected sports from localStorage
  const localStatus = getLocalOnboardingStatus();
  const selectedSports = localStatus?.selectedSports || [];
  const sportIds = selectedSports.map(s => s.sportId);

  // Set up API client
  const queryConfigs = createApiQueryClient(
    isAuthenticated ? { getIdToken, isAuthenticated: true, userId: user?.uid } : undefined
  );

  // Fetch teams data with enhanced error handling
  const {
    data: teamsData,
    isLoading,
    error,
    refetch: refetchTeams,
  } = useQuery({
    ...queryConfigs.getOnboardingTeams(sportIds),
    retry: (failureCount, error) => {
      // Custom retry logic for teams fetching
      if (failureCount >= 3) return false;

      // Don't retry on 4xx errors
      const status = (error as any)?.status;
      if (status >= 400 && status < 500) return false;

      return true;
    },
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    enabled: sportIds.length > 0,
    onError: (error) => {
      reportOnboardingError(
        3,
        'Failed to fetch teams data',
        error instanceof Error ? error : new Error(String(error)),
        { sportIds, userId: user?.uid }
      );
    },
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
    } else if (teamsData) {
      setIsApiAvailable(true);
    }
  }, [error, teamsData]);

  // Fallback team data based on popular teams from selected sports
  const getFallbackTeams = useCallback((): OnboardingTeam[] => {
    const fallbackTeams: OnboardingTeam[] = [];

    selectedSports.forEach(sport => {
      switch (sport.sportId) {
        case 'nfl':
          fallbackTeams.push(
            { id: 'chiefs', name: 'Kansas City Chiefs', market: 'Kansas City', sportId: 'nfl', league: 'NFL', logo: '🏈' },
            { id: 'cowboys', name: 'Dallas Cowboys', market: 'Dallas', sportId: 'nfl', league: 'NFL', logo: '🏈' },
            { id: 'patriots', name: 'New England Patriots', market: 'New England', sportId: 'nfl', league: 'NFL', logo: '🏈' },
            { id: 'packers', name: 'Green Bay Packers', market: 'Green Bay', sportId: 'nfl', league: 'NFL', logo: '🏈' },
            { id: '49ers', name: 'San Francisco 49ers', market: 'San Francisco', sportId: 'nfl', league: 'NFL', logo: '🏈' },
          );
          break;
        case 'nba':
          fallbackTeams.push(
            { id: 'lakers', name: 'Los Angeles Lakers', market: 'Los Angeles', sportId: 'nba', league: 'NBA', logo: '🏀' },
            { id: 'warriors', name: 'Golden State Warriors', market: 'Golden State', sportId: 'nba', league: 'NBA', logo: '🏀' },
            { id: 'celtics', name: 'Boston Celtics', market: 'Boston', sportId: 'nba', league: 'NBA', logo: '🏀' },
            { id: 'heat', name: 'Miami Heat', market: 'Miami', sportId: 'nba', league: 'NBA', logo: '🏀' },
            { id: 'bulls', name: 'Chicago Bulls', market: 'Chicago', sportId: 'nba', league: 'NBA', logo: '🏀' },
          );
          break;
        case 'mlb':
          fallbackTeams.push(
            { id: 'yankees', name: 'New York Yankees', market: 'New York', sportId: 'mlb', league: 'MLB', logo: '⚾' },
            { id: 'dodgers', name: 'Los Angeles Dodgers', market: 'Los Angeles', sportId: 'mlb', league: 'MLB', logo: '⚾' },
            { id: 'red-sox', name: 'Boston Red Sox', market: 'Boston', sportId: 'mlb', league: 'MLB', logo: '⚾' },
            { id: 'giants', name: 'San Francisco Giants', market: 'San Francisco', sportId: 'mlb', league: 'MLB', logo: '⚾' },
            { id: 'cubs', name: 'Chicago Cubs', market: 'Chicago', sportId: 'mlb', league: 'MLB', logo: '⚾' },
          );
          break;
        case 'nhl':
          fallbackTeams.push(
            { id: 'rangers', name: 'New York Rangers', market: 'New York', sportId: 'nhl', league: 'NHL', logo: '🏒' },
            { id: 'bruins', name: 'Boston Bruins', market: 'Boston', sportId: 'nhl', league: 'NHL', logo: '🏒' },
            { id: 'blackhawks', name: 'Chicago Blackhawks', market: 'Chicago', sportId: 'nhl', league: 'NHL', logo: '🏒' },
            { id: 'kings', name: 'Los Angeles Kings', market: 'Los Angeles', sportId: 'nhl', league: 'NHL', logo: '🏒' },
            { id: 'penguins', name: 'Pittsburgh Penguins', market: 'Pittsburgh', sportId: 'nhl', league: 'NHL', logo: '🏒' },
          );
          break;
      }
    });

    return fallbackTeams;
  }, [selectedSports]);

  // Use API data if available, otherwise use fallback
  const activeTeamsData = teamsData || getFallbackTeams();

  // Initialize teams state when data loads
  useEffect(() => {
    if (activeTeamsData.length > 0) {
      // Try to restore previous selections from localStorage
      const previousSelections = localStatus?.selectedTeams || [];

      const teamsWithSelection = activeTeamsData.map((team, index) => {
        const previousSelection = previousSelections.find(t => t.teamId === team.id);
        return {
          ...team,
          isSelected: !!previousSelection,
          affinityScore: previousSelection?.affinityScore || 5, // Default affinity
          rank: previousSelection?.rank || 0,
        };
      });

      setTeams(teamsWithSelection);
    }
  }, [activeTeamsData, localStatus]);

  // Update selected count and ranks when teams change
  useEffect(() => {
    const selectedTeams = teams.filter(team => team.isSelected);
    setSelectedCount(selectedTeams.length);

    // Update ranks for selected teams
    const updatedTeams = teams.map(team => {
      if (team.isSelected) {
        const rank = selectedTeams.findIndex(t => t.id === team.id) + 1;
        return { ...team, rank };
      }
      return { ...team, rank: 0 };
    });

    if (JSON.stringify(updatedTeams) !== JSON.stringify(teams)) {
      setTeams(updatedTeams);
    }

    // Validate in real-time if user has attempted submission
    if (validationState.hasBeenSubmitted || validationState.showValidationErrors) {
      validation.validateTeamsArray(updatedTeams);
    }
  }, [teams, validationState.hasBeenSubmitted, validationState.showValidationErrors, validation]);

  // Toggle team selection with validation
  const handleToggleTeam = useCallback((teamId: string) => {
    setTeams(prev => {
      const updatedTeams = prev.map(team => {
        if (team.id === teamId) {
          const isSelecting = !team.isSelected;

          // Validate selection limit
          if (isSelecting && prev.filter(t => t.isSelected).length >= 10) {
            validation.setFieldError('selectedTeams', 'You can select a maximum of 10 teams. Please deselect one first.');
            toast({
              title: "Maximum 10 Teams",
              description: "You can select a maximum of 10 teams. Please deselect one first.",
              variant: "destructive",
            });
            return team;
          }

          return { ...team, isSelected: isSelecting };
        }
        return team;
      });

      // Clear validation errors when making valid selections
      if (updatedTeams.filter(t => t.isSelected).length > 0) {
        validation.clearFieldError('selectedTeams');
      }

      return updatedTeams;
    });

    // Mark as dirty for validation
    validation.touch();
  }, [validation]);

  // Handle affinity score changes
  const handleAffinityChange = useCallback((teamId: string, affinity: number) => {
    setTeams(prev =>
      prev.map(team =>
        team.id === teamId
          ? { ...team, affinityScore: affinity }
          : team
      )
    );

    // Mark as dirty for validation
    validation.touch();
  }, [validation]);

  // Enhanced submission with validation
  const handleContinue = useCallback(async () => {
    setValidationState(prev => ({
      ...prev,
      isValidating: true,
      hasBeenSubmitted: true,
      showValidationErrors: true,
    }));

    try {
      // Validate current selections
      const isValid = await validation.validateTeamsData(teams);

      if (!isValid) {
        setValidationState(prev => ({ ...prev, isValidating: false }));
        toast({
          title: "Validation Error",
          description: "Please fix the errors below and try again.",
          variant: "destructive",
        });
        return;
      }

      const selectedTeams = teams.filter(team => team.isSelected);

      // Convert to API format
      const teamsData = selectedTeams.map(team => ({
        teamId: team.id,
        sportId: team.sportId,
        rank: team.rank,
        affinityScore: team.affinityScore,
      }));

      // Always save to localStorage first
      updateLocalOnboardingStep(3, { selectedTeams: teamsData });

      // Try to save to API if available
      if (isApiAvailable && isAuthenticated) {
        try {
          await retryableFetch.post('/api/onboarding/step', {
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

      // Navigation success
      setValidationState(prev => ({ ...prev, isValidating: false }));
      navigate("/onboarding/step/4");

    } catch (error) {
      setValidationState(prev => ({ ...prev, isValidating: false }));

      reportOnboardingError(
        3,
        'Failed to submit team selection',
        error instanceof Error ? error : new Error(String(error)),
        { selectedCount, userId: user?.uid }
      );

      toast({
        title: "Submission Failed",
        description: "Failed to save your team selection. Please try again.",
        variant: "destructive",
      });
    }
  }, [
    validation,
    teams,
    isApiAvailable,
    isAuthenticated,
    selectedCount,
    user?.uid,
    navigate
  ]);

  // Loading state
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
        <TeamSelectionSkeleton />
      </OnboardingLayout>
    );
  }

  // Show message if no sports selected
  if (sportIds.length === 0) {
    const recoverySteps = [
      'Go back to sports selection',
      'Select at least one sport',
      'Return to team selection',
    ];

    return (
      <OnboardingLayout
        step={3}
        totalSteps={5}
        title="Select Your Teams"
        subtitle="No sports selected"
        showProgress={true}
        completedSteps={2}
      >
        <div className="space-y-6">
          <ErrorAlert
            title="No Sports Selected"
            message="Please go back and select your sports first before choosing teams."
            severity="warning"
            recoveryActions={[
              {
                label: 'Go Back to Sports Selection',
                action: () => navigate("/onboarding/step/2"),
                variant: 'default',
              },
            ]}
          />
          <RecoveryGuidance steps={recoverySteps} />
        </div>
      </OnboardingLayout>
    );
  }

  // Error state when API fails and no fallback data
  if (error && !activeTeamsData.length) {
    const recoverySteps = [
      'Check your internet connection',
      'Try refreshing the page',
      'If the problem persists, contact support',
    ];

    return (
      <OnboardingLayout
        step={3}
        totalSteps={5}
        title="Select Your Teams"
        subtitle="Error loading teams"
        showProgress={true}
        completedSteps={2}
      >
        <div className="space-y-6">
          <ErrorAlert
            title="Failed to Load Teams"
            message="We couldn't load the teams data. Please try again."
            severity="error"
            recoveryActions={[
              {
                label: 'Retry',
                action: () => refetchTeams(),
                variant: 'default',
                icon: Loader2,
              },
            ]}
          />
          <RecoveryGuidance steps={recoverySteps} />
        </div>
      </OnboardingLayout>
    );
  }

  // Main render
  return (
    <OnboardingLayout
      step={3}
      totalSteps={5}
      title="Select Your Teams"
      subtitle="Choose your favorite teams from your selected sports"
      showProgress={true}
      completedSteps={2}
      onNext={handleContinue}
      isNextDisabled={selectedCount === 0 || validationState.isValidating}
    >
      <div className="space-y-6">
        {/* Offline indicator */}
        {!isApiAvailable && (
          <ErrorAlert
            title="Working Offline"
            message="Your selections are being saved locally and will sync when connection is restored."
            severity="warning"
          />
        )}

        {/* Validation errors */}
        {validationState.showValidationErrors && validation.hasErrors && (
          <ErrorAlert
            title="Please Fix These Issues"
            message="There are some issues with your selections that need to be fixed."
            severity="error"
          />
        )}

        {/* Field-level errors */}
        {validation.fieldErrors.selectedTeams && (
          <FieldError
            error={validation.fieldErrors.selectedTeams}
            field="selectedTeams"
            severity="error"
            onClear={() => validation.clearFieldError('selectedTeams')}
            helpText="You can select between 1 and 10 teams. Use the star rating to show your affinity for each team."
          />
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
                  {sport.sportId.toUpperCase()} Teams
                </h3>
                <div className="grid gap-3">
                  {sportTeams.map(team => (
                    <TeamCard
                      key={team.id}
                      team={team}
                      onToggle={handleToggleTeam}
                      onAffinityChange={handleAffinityChange}
                      hasError={validation.fieldErrors.selectedTeams && selectedCount === 0}
                      errorMessage={validation.fieldErrors.selectedTeams}
                    />
                  ))}
                </div>
              </div>
            );
          })}
        </div>

        {/* Status */}
        <div className="text-center">
          <span className="font-display font-semibold text-primary">
            {selectedCount} teams selected
          </span>
          {selectedCount > 0 && !validation.hasErrors && (
            <span className="ml-2 text-green-500">✓</span>
          )}
          {validation.hasErrors && (
            <span className="ml-2 text-red-500">⚠</span>
          )}
        </div>

        {/* Help tip */}
        {selectedCount > 0 && (
          <div className="bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
            <p className="text-sm text-blue-800 dark:text-blue-200 font-body">
              <strong>Tip:</strong> Use the star rating to indicate how much you follow each team.
              Higher ratings will prioritize that team's content in your feed.
            </p>
          </div>
        )}

        {/* Continue button state */}
        {validationState.isValidating && (
          <div className="flex justify-center">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Validating your selections...</span>
            </div>
          </div>
        )}
      </div>
    </OnboardingLayout>
  );
}

export default ValidatedTeamSelectionStep;