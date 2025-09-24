import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { toast } from "@/components/ui/use-toast";
import { CheckCircle, ArrowRight, AlertCircle, Loader2 } from "lucide-react";
import { OnboardingLayout } from "./OnboardingLayout";
import { apiClient } from "@/lib/api-client";
import { useFirebaseAuth } from "@/contexts/FirebaseAuthContext";
import { completeLocalOnboarding, getLocalOnboardingStatus } from "@/lib/onboarding-storage";

export function CompletionStep() {
  const navigate = useNavigate();
  const { isAuthenticated } = useFirebaseAuth();

  const [isCompleting, setIsCompleting] = useState(false);
  const [isApiAvailable, setIsApiAvailable] = useState(true);

  const handleFinish = async () => {
    setIsCompleting(true);

    try {
      // Get all onboarding data from localStorage
      const localStatus = getLocalOnboardingStatus();

      if (!localStatus) {
        throw new Error('No onboarding data found');
      }

      // Always mark as complete in localStorage first
      completeLocalOnboarding();

      // Try to complete onboarding via API if available
      if (isAuthenticated && localStatus.selectedSports.length > 0) {
        try {
          await apiClient.completeOnboarding({
            sports: localStatus.selectedSports.map(s => ({
              sportId: s.sportId,
              name: s.sportId, // Will be enriched by API
              rank: s.rank,
              hasTeams: true, // Default assumption
            })),
            teams: localStatus.selectedTeams.map(t => ({
              teamId: t.teamId,
              name: t.teamId, // Will be enriched by API
              sportId: t.sportId,
              league: 'Unknown', // Will be enriched by API
              affinityScore: t.affinityScore,
            })),
            preferences: localStatus.preferences,
          });

          console.log('Onboarding completed successfully via API');
          toast({
            title: "Welcome to Corner League!",
            description: "Your account has been set up successfully.",
            variant: "default",
          });
        } catch (error) {
          console.warn('Failed to complete onboarding via API, using local completion:', error);
          setIsApiAvailable(false);
          toast({
            title: "Setup Complete (Offline)",
            description: "Your settings have been saved locally and will sync when you're back online.",
            variant: "default",
          });
        }
      } else {
        console.log('Completing onboarding locally');
        toast({
          title: "Setup Complete",
          description: "Your personalized sports experience is ready!",
          variant: "default",
        });
      }

      // Navigate to dashboard
      navigate("/");
    } catch (error) {
      console.error('Failed to complete onboarding:', error);
      toast({
        title: "Error",
        description: "Something went wrong. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsCompleting(false);
    }
  };

  return (
    <OnboardingLayout
      step={5}
      totalSteps={5}
      title="You're All Set!"
      subtitle="Welcome to Corner League Media"
      showProgress={true}
      completedSteps={5}
    >
      <div className="space-y-8">
        {/* Offline indicator */}
        {!isApiAvailable && (
          <div className="bg-orange-50 dark:bg-orange-950/30 border border-orange-200 dark:border-orange-800 rounded-lg p-4">
            <div className="flex items-center gap-3">
              <AlertCircle className="h-5 w-5 text-orange-600 dark:text-orange-400" />
              <div className="text-sm">
                <p className="font-medium text-orange-800 dark:text-orange-200">
                  Completed Offline
                </p>
                <p className="text-orange-700 dark:text-orange-300">
                  Your settings have been saved locally and will sync when you're back online.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Success message */}
        <div className="text-center space-y-6">
          <div className="flex justify-center">
            <CheckCircle className="h-16 w-16 text-green-500" />
          </div>

          <div className="space-y-4 max-w-2xl mx-auto">
            <h2 className="font-display font-semibold text-2xl text-foreground">
              Your sports experience is now personalized!
            </h2>
            <p className="text-lg text-muted-foreground font-body leading-relaxed">
              We've set up your feed based on your favorite sports, teams, and preferences.
              You can always update these settings later in your profile.
            </p>
          </div>
        </div>

        {/* Summary card */}
        <Card className="bg-primary/5 border-primary/20" data-testid="summary-section">
          <CardContent className="p-6">
            <div className="text-center space-y-4">
              <h3 className="font-display font-semibold text-lg text-foreground">
                What's next?
              </h3>
              <div className="space-y-2 text-muted-foreground font-body">
                <p>• Get personalized news and updates from your favorite teams</p>
                <p>• Discover exclusive content and insider perspectives</p>
                <p>• Stay updated with real-time scores and breaking news</p>
                <p>• Connect with other fans in your community</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Finish button */}
        <div className="flex justify-center pt-4">
          <Button
            size="lg"
            onClick={handleFinish}
            disabled={isCompleting}
            className="flex items-center gap-2 px-8 py-3 text-lg"
          >
            {isCompleting ? (
              <>
                <Loader2 className="h-5 w-5 animate-spin" />
                Setting up your experience...
              </>
            ) : (
              <>
                Enter Corner League
                <ArrowRight className="h-5 w-5" />
              </>
            )}
          </Button>
        </div>
      </div>
    </OnboardingLayout>
  );
}

export default CompletionStep;