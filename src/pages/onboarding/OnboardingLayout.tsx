import { ReactNode } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { ArrowLeft, ArrowRight } from "lucide-react";

interface OnboardingLayoutProps {
  children: ReactNode;
  step: number;
  totalSteps: number;
  title: string;
  subtitle?: string;
  onNext?: () => void;
  onBack?: () => void;
  nextLabel?: string;
  backLabel?: string;
  isNextDisabled?: boolean;
  showProgress?: boolean;
  completedSteps?: number;
}

export function OnboardingLayout({
  children,
  step,
  totalSteps,
  title,
  subtitle,
  onNext,
  onBack,
  nextLabel = "Continue",
  backLabel = "Back",
  isNextDisabled = false,
  showProgress = true,
  completedSteps = 0,
}: OnboardingLayoutProps) {
  const navigate = useNavigate();
  const progressPercentage = (step / totalSteps) * 100;

  const handleBack = () => {
    if (onBack) {
      onBack();
    } else if (step > 1) {
      navigate(`/onboarding/step/${step - 1}`);
    }
  };

  const handleNext = () => {
    if (onNext) {
      onNext();
    } else if (step < totalSteps) {
      navigate(`/onboarding/step/${step + 1}`);
    }
  };

  return (
    <div className="min-h-screen bg-background" data-testid="onboarding-layout">
      {/* Skip to main content link for accessibility */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 bg-primary text-primary-foreground px-4 py-2 rounded-md z-50 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
      >
        Skip to main content
      </a>

      {/* Header with Progress */}
      <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
        <div className="container max-w-4xl mx-auto px-4 py-6">
          <div className="space-y-4">
            {/* Step indicator */}
            <div className="flex items-center justify-between">
              <div className="text-sm text-muted-foreground font-body" data-testid="step-indicator">
                Step {step} of {totalSteps}
              </div>
              {showProgress && (
                <div className="text-sm text-muted-foreground font-body">
                  {completedSteps} of {totalSteps} steps completed
                </div>
              )}
            </div>

            {/* Progress bar */}
            <div className="space-y-2">
              <Progress
                value={progressPercentage}
                className="h-2"
                role="progressbar"
                aria-valuenow={progressPercentage}
                aria-valuemin={0}
                aria-valuemax={100}
                aria-label={`Onboarding progress: ${Math.round(progressPercentage)}% complete`}
              />
              <div className="text-xs text-muted-foreground font-body">
                {Math.round(progressPercentage)}% complete
              </div>
            </div>

            {/* Title and subtitle */}
            <div className="space-y-2">
              <h1 id="page-title" className="font-display font-bold text-3xl text-foreground">
                {title}
              </h1>
              {subtitle && (
                <p className="text-lg text-muted-foreground font-body">
                  {subtitle}
                </p>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main
        id="main-content"
        className="container max-w-4xl mx-auto px-4 py-8"
        data-testid="main-content"
        role="main"
        aria-live="polite"
        aria-labelledby="page-title"
      >
        <div className="space-y-8">
          {children}
        </div>
      </main>

      {/* Footer with navigation */}
      <footer className="sticky bottom-0 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-t">
        <div className="container max-w-4xl mx-auto px-4 py-6">
          <nav className="flex items-center justify-between" role="navigation" aria-label="Onboarding navigation">
            {step > 1 ? (
              <Button
                variant="outline"
                onClick={handleBack}
                className="flex items-center gap-2"
                data-testid="back-button"
                aria-label={`Go back to step ${step - 1}`}
              >
                <ArrowLeft className="h-4 w-4" aria-hidden="true" />
                {backLabel}
              </Button>
            ) : (
              <div /> /* Placeholder for alignment */
            )}

            {step < totalSteps && (
              <Button
                onClick={handleNext}
                disabled={isNextDisabled}
                className="flex items-center gap-2 ml-auto"
                data-testid="continue-button"
                aria-label={isNextDisabled ? `Complete step ${step} to continue` : `Continue to step ${step + 1}`}
              >
                {nextLabel}
                <ArrowRight className="h-4 w-4" aria-hidden="true" />
              </Button>
            )}
          </nav>
        </div>
      </footer>
    </div>
  );
}

export default OnboardingLayout;