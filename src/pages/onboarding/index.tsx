import { lazy, Suspense } from "react";
import { Routes, Route, Navigate, useParams } from "react-router-dom";

// Lazy load onboarding components for better code splitting
const WelcomeStep = lazy(() => import("./WelcomeStep").then(m => ({ default: m.WelcomeStep })));
const SportsSelectionStep = lazy(() => import("./SportsSelectionStep").then(m => ({ default: m.SportsSelectionStep })));
const TeamSelectionStep = lazy(() => import("./TeamSelectionStep").then(m => ({ default: m.TeamSelectionStep })));
const PreferencesStep = lazy(() => import("./PreferencesStep").then(m => ({ default: m.PreferencesStep })));
const CompletionStep = lazy(() => import("./CompletionStep").then(m => ({ default: m.CompletionStep })));

// Loading component for code-split chunks
const StepLoadingFallback = () => (
  <div className="min-h-screen flex items-center justify-center bg-background">
    <div className="text-center space-y-4">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
      <p className="text-muted-foreground font-body">Loading...</p>
    </div>
  </div>
);

function OnboardingStepRouter() {
  const { step } = useParams<{ step: string }>();
  const stepNumber = parseInt(step || "1", 10);

  // Validate step number
  if (isNaN(stepNumber) || stepNumber < 1 || stepNumber > 5) {
    return <Navigate to="/onboarding/step/1" replace />;
  }

  const StepComponent = () => {
    switch (stepNumber) {
      case 1:
        return <WelcomeStep />;
      case 2:
        return <SportsSelectionStep />;
      case 3:
        return <TeamSelectionStep />;
      case 4:
        return <PreferencesStep />;
      case 5:
        return <CompletionStep />;
      default:
        return <Navigate to="/onboarding/step/1" replace />;
    }
  };

  return (
    <Suspense fallback={<StepLoadingFallback />}>
      <StepComponent />
    </Suspense>
  );
}

export function OnboardingRouter() {
  return (
    <Routes>
      <Route path="step/:step" element={<OnboardingStepRouter />} />
      <Route path="*" element={<Navigate to="step/1" replace />} />
    </Routes>
  );
}

export default OnboardingRouter;