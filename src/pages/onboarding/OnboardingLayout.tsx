import { ReactNode, useState, useRef, useCallback, useEffect } from "react";
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

  // Navigation state management to prevent race conditions
  const [isNavigating, setIsNavigating] = useState(false);
  const navigationTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Debounced navigation handler to prevent rapid consecutive calls
  const debounceNavigation = useCallback((navigationFn: () => void) => {
    if (isNavigating) return;

    setIsNavigating(true);

    // Clear any existing timeout
    if (navigationTimeoutRef.current) {
      clearTimeout(navigationTimeoutRef.current);
    }

    // Execute navigation immediately
    navigationFn();

    // Reset navigation state after a short delay to prevent rapid re-navigation
    navigationTimeoutRef.current = setTimeout(() => {
      setIsNavigating(false);
    }, 300);
  }, [isNavigating]);

  const handleBack = useCallback(() => {
    debounceNavigation(() => {
      if (onBack) {
        onBack();
      } else if (step > 1) {
        navigate(`/onboarding/step/${step - 1}`);
      }
    });
  }, [debounceNavigation, onBack, step, navigate]);

  const handleNext = useCallback(() => {
    debounceNavigation(() => {
      if (onNext) {
        onNext();
      } else if (step < totalSteps) {
        navigate(`/onboarding/step/${step + 1}`);
      }
    });
  }, [debounceNavigation, onNext, step, totalSteps, navigate]);

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (navigationTimeoutRef.current) {
        clearTimeout(navigationTimeoutRef.current);
      }
    };
  }, []);

  return (
    <div className="min-h-screen bg-background">
      {/* Header with Progress */}
      <div className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
        <div className="container max-w-4xl mx-auto px-4 py-6">
          <div className="space-y-4">
            {/* Step indicator */}
            <div className="flex items-center justify-between">
              <div className="text-sm text-muted-foreground font-body">
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
              <Progress value={progressPercentage} className="h-2" />
              <div className="text-xs text-muted-foreground font-body">
                {Math.round(progressPercentage)}% complete
              </div>
            </div>

            {/* Title and subtitle */}
            <div className="space-y-2">
              <h1 className="font-display font-bold text-3xl text-foreground">
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
      </div>

      {/* Main content */}
      <main className="container max-w-4xl mx-auto px-4 py-8">
        <div className="space-y-8">
          {children}
        </div>
      </main>

      {/* Footer with navigation */}
      <div className="sticky bottom-0 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-t">
        <div className="container max-w-4xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            {step > 1 ? (
              <Button
                variant="outline"
                onClick={handleBack}
                disabled={isNavigating}
                className="flex items-center gap-2"
              >
                <ArrowLeft className="h-4 w-4" />
                {backLabel}
              </Button>
            ) : (
              <div /> /* Placeholder for alignment */
            )}

            {step < totalSteps && (
              <Button
                onClick={handleNext}
                disabled={isNextDisabled || isNavigating}
                className="flex items-center gap-2 ml-auto"
              >
                {nextLabel}
                <ArrowRight className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default OnboardingLayout;