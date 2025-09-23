import { Routes, Route, Navigate, useParams } from "react-router-dom";
import { WelcomeStep } from "./WelcomeStep";
import { SportsSelectionStep } from "./SportsSelectionStep";
import { TeamSelectionStep } from "./TeamSelectionStep";
import { PreferencesStep } from "./PreferencesStep";
import { CompletionStep } from "./CompletionStep";

function OnboardingStepRouter() {
  const { step } = useParams<{ step: string }>();
  const stepNumber = parseInt(step || "1", 10);

  // Validate step number
  if (isNaN(stepNumber) || stepNumber < 1 || stepNumber > 5) {
    return <Navigate to="/onboarding/step/1" replace />;
  }

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