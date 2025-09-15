import React from 'react';
import { useNavigate } from 'react-router-dom';
import { OnboardingLayout } from '@/components/onboarding/OnboardingLayout';
import { useOnboarding } from '@/hooks/useOnboarding';
import WelcomeScreen from './WelcomeScreen';
import SportsSelection from './SportsSelection';
import TeamSelection from './TeamSelection';
import PreferencesSetup from './PreferencesSetup';
import OnboardingComplete from './OnboardingComplete';

const OnboardingIndex: React.FC = () => {
  console.log('OnboardingIndex component loaded');

  const navigate = useNavigate();
  const {
    currentStep,
    steps,
    currentStepData,
    isFirstStep,
    isLastStep,
    canSkipCurrentStep,
    nextStep,
    prevStep,
    skipStep,
    completeOnboarding,
    resetOnboarding,
    errors,
  } = useOnboarding();

  console.log('Onboarding hook data:', { currentStep, steps, currentStepData });

  const handleNext = () => {
    if (isLastStep) {
      const success = completeOnboarding();
      if (success) {
        navigate('/', { replace: true });
      }
    } else {
      nextStep();
    }
  };

  const handleBack = () => {
    prevStep();
  };

  const handleSkip = () => {
    skipStep();
  };

  const handleExit = () => {
    // Show confirmation dialog in a real app
    const confirmed = window.confirm(
      'Are you sure you want to exit onboarding? Your progress will be saved.'
    );
    if (confirmed) {
      navigate('/', { replace: true });
    }
  };

  const renderStepContent = () => {
    console.log('Rendering step content:', currentStepData?.id);

    if (!currentStepData) {
      console.log('No current step data');
      return (
        <div className="text-center p-8">
          <h2 className="text-xl font-semibold mb-4">Loading...</h2>
          <p className="text-muted-foreground">
            Initializing onboarding...
          </p>
        </div>
      );
    }

    switch (currentStepData.id) {
      case 'welcome':
        return <WelcomeScreen />;
      case 'sports':
        return <SportsSelection />;
      case 'teams':
        return <TeamSelection />;
      case 'preferences':
        return <PreferencesSetup />;
      case 'complete':
        return <OnboardingComplete />;
      default:
        return (
          <div className="text-center">
            <h2 className="text-xl font-semibold mb-4">Unknown Step</h2>
            <p className="text-muted-foreground">
              This step is not yet implemented: {currentStepData.id}
            </p>
          </div>
        );
    }
  };

  const getNextLabel = () => {
    if (isLastStep) return 'Complete Setup';
    if (currentStepData?.id === 'welcome') return 'Get Started';
    return 'Continue';
  };

  const hasStepErrors = errors[currentStepData?.id || ''];

  return (
    <OnboardingLayout
      currentStep={currentStep}
      steps={steps}
      onNext={handleNext}
      onBack={handleBack}
      onSkip={handleSkip}
      onExit={handleExit}
      nextDisabled={!!hasStepErrors}
      nextLabel={getNextLabel()}
      showSkip={canSkipCurrentStep}
    >
      {renderStepContent()}

      {/* Display step-specific errors */}
      {hasStepErrors && (
        <div className="mt-4 p-4 bg-destructive/10 border border-destructive/20 rounded-md">
          <p className="text-sm text-destructive font-medium">
            {hasStepErrors}
          </p>
        </div>
      )}
    </OnboardingLayout>
  );
};

export default OnboardingIndex;