import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { toast } from "@/components/ui/use-toast";
import { AlertCircle } from "lucide-react";
import { OnboardingLayout } from "./OnboardingLayout";
import { TeamSelector } from "@/components/TeamSelector";
import { createApiQueryClient, type Team, type OnboardingTeam, apiClient } from "@/lib/api-client";
import { useFirebaseAuth } from "@/contexts/FirebaseAuthContext";
import { updateLocalOnboardingStep, getLocalOnboardingStatus } from "@/lib/onboarding-storage";

export function TeamSelectionStep() {
  const navigate = useNavigate();
  const { isAuthenticated, getIdToken, user } = useFirebaseAuth();

  const [selectedTeams, setSelectedTeams] = useState<Team[]>([]);
  const [isApiAvailable, setIsApiAvailable] = useState(true);

  // Get previously selected sports from localStorage
  const localStatus = getLocalOnboardingStatus();
  const selectedSports = localStatus?.selectedSports || [];
  const sportIds = selectedSports.map(s => s.sportId);

  // Set up API client
  const queryConfigs = createApiQueryClient(
    isAuthenticated ? { getIdToken, isAuthenticated: true, userId: user?.uid } : undefined
  );

  // Load previous team selections from localStorage
  useEffect(() => {
    const previousSelections = localStatus?.selectedTeams || [];

    // Convert stored team data back to Team objects if available
    // For now, we'll start fresh with the new selector
    // In production, you might want to restore from a proper teams API call
    setSelectedTeams([]);
  }, [localStatus]);

  const handleTeamSelect = (teams: Team[]) => {
    setSelectedTeams(teams);
  };

  const handleContinue = async () => {
    // Convert to API format for storage
    const teamsData = selectedTeams.map(team => ({
      teamId: team.id,
      sportId: team.sport_id,
      affinityScore: 0.8, // Default affinity score
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
        setIsApiAvailable(false);
        toast({
          title: "Saved Offline",
          description: "Your team selection has been saved locally.",
          variant: "default",
        });
      }
    }

    navigate("/onboarding/step/4");
  };

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
      isNextDisabled={selectedTeams.length === 0}
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
        <div className="text-center space-y-4">
          <p className="text-lg font-body text-muted-foreground">
            Search and select teams from your chosen sports to personalize your content feed.
          </p>
          <div className="text-sm text-muted-foreground">
            Selected sports: {selectedSports.map(s => s.sportId.toUpperCase()).join(', ')}
          </div>
        </div>

        {/* Team Selector Component */}
        <div className="max-w-2xl mx-auto">
          <TeamSelector
            selectedTeams={selectedTeams}
            onTeamSelect={handleTeamSelect}
            sportIds={sportIds}
            multiSelect={true}
            placeholder="Select your favorite teams..."
            searchPlaceholder="Search for teams..."
            maxSelections={10}
          />
        </div>

        {/* Status and tips */}
        {selectedTeams.length > 0 && (
          <div className="text-center space-y-4">
            <div className="font-display font-semibold text-primary">
              {selectedTeams.length} team{selectedTeams.length === 1 ? '' : 's'} selected
            </div>

            <div className="bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-800 rounded-lg p-4 max-w-2xl mx-auto">
              <p className="text-sm text-blue-800 dark:text-blue-200 font-body">
                <strong>Great choice!</strong> Your selected teams will be used to personalize your content feed and dashboard.
                You can always change your team preferences later in settings.
              </p>
            </div>
          </div>
        )}

        {/* Help text */}
        {selectedTeams.length === 0 && (
          <div className="text-center">
            <p className="text-sm text-muted-foreground">
              Start typing to search for teams, or browse teams from your selected sports.
            </p>
          </div>
        )}
      </div>
    </OnboardingLayout>
  );
}

export default TeamSelectionStep;