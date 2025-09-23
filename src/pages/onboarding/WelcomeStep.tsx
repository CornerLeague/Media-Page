import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { ArrowRight, Trophy, Users, TrendingUp, Star } from "lucide-react";
import { OnboardingLayout } from "./OnboardingLayout";
import { createOnboardingStep } from "@/components/error-boundaries/withOnboardingErrorBoundary";
import { useSessionRecovery } from "@/hooks/useSessionRecovery";
import { reportOnboardingError } from "@/lib/error-reporting";
import { SyncStatusIndicator } from "@/components/fallback/OnboardingFallbackUI";
import { useOnboardingAssetPrefetch } from "@/hooks/useOnboardingPrefetch";

function WelcomeStepComponent() {
  const navigate = useNavigate();
  const {
    syncStatus,
    hasUnsyncedData,
    lastSyncTime,
    syncWithAPI,
    saveStepProgress,
  } = useSessionRecovery();

  // Prefetch assets for better performance
  useOnboardingAssetPrefetch();

  const handleGetStarted = async () => {
    try {
      // Save step 1 completion
      saveStepProgress(1, { completed: true });

      navigate("/onboarding/step/2");
    } catch (error) {
      reportOnboardingError(
        1,
        'Failed to complete welcome step',
        error instanceof Error ? error : new Error(String(error)),
        { action: 'get_started' }
      );

      // Continue anyway - this is not a blocking error
      navigate("/onboarding/step/2");
    }
  };

  const features = [
    {
      icon: Trophy,
      title: "Personalized Content",
      description: "Get news and updates tailored to your favorite teams and sports",
    },
    {
      icon: Users,
      title: "Community Insights",
      description: "Connect with fans and get exclusive insider perspectives",
    },
    {
      icon: TrendingUp,
      title: "Real-time Updates",
      description: "Stay on top of scores, trades, and breaking news",
    },
    {
      icon: Star,
      title: "Premium Features",
      description: "Access advanced analytics and exclusive content",
    },
  ];

  return (
    <OnboardingLayout
      step={1}
      totalSteps={5}
      title="Welcome"
      subtitle="Get started with Corner League"
      showProgress={true}
      completedSteps={0}
    >
      {/* Sync Status Indicator */}
      <div className="flex justify-end mb-4">
        <SyncStatusIndicator
          status={syncStatus}
          lastSyncTime={lastSyncTime}
          hasUnsyncedData={hasUnsyncedData}
          onSync={syncWithAPI}
        />
      </div>
      <div className="space-y-8">
        {/* Hero section with stadium icon */}
        <div className="text-center space-y-6">
          <div className="text-6xl">🏟️</div>
          <div className="space-y-4 max-w-2xl mx-auto">
            <h2 className="font-display font-semibold text-2xl text-foreground">
              Your personalized sports media platform
            </h2>
            <p className="text-lg text-muted-foreground font-body leading-relaxed">
              Let's tailor your sports experience. Choose your favorite sports and teams to get started with content that matters to you.
            </p>
          </div>
        </div>

        {/* Feature highlights */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {features.map((feature, index) => (
            <Card key={index} className="border hover:shadow-md transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0">
                    <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                      <feature.icon className="h-5 w-5 text-primary" />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <h3 className="font-display font-semibold text-lg text-foreground">
                      {feature.title}
                    </h3>
                    <p className="text-muted-foreground font-body">
                      {feature.description}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Progress footer */}
        <div className="bg-muted/50 rounded-lg p-6 space-y-4">
          <div className="text-center space-y-2">
            <p className="font-body font-medium text-foreground">
              This setup will only take 2-3 minutes
            </p>
            <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
              <span>Choose sports</span>
              <ArrowRight className="h-4 w-4" />
              <span>Select teams</span>
              <ArrowRight className="h-4 w-4" />
              <span>Set preferences</span>
            </div>
          </div>

          {/* Get Started button */}
          <div className="flex justify-center pt-4">
            <Button
              size="lg"
              onClick={handleGetStarted}
              className="flex items-center gap-2 px-8 py-3 text-lg"
            >
              Get Started
              <ArrowRight className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </div>
    </OnboardingLayout>
  );
}

// Wrap with error boundary
export const WelcomeStep = createOnboardingStep(
  WelcomeStepComponent,
  1,
  'Welcome',
  {
    canGoBack: false, // First step, can't go back
  }
);

export default WelcomeStep;