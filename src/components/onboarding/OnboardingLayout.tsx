import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { ArrowLeft, ArrowRight, X } from 'lucide-react';
import { OnboardingStep } from '@/lib/types/onboarding-types';

interface OnboardingLayoutProps {
  children: React.ReactNode;
  currentStep: number;
  steps: OnboardingStep[];
  onNext: () => void;
  onBack: () => void;
  onSkip?: () => void;
  onExit: () => void;
  nextDisabled?: boolean;
  nextLabel?: string;
  backLabel?: string;
  showSkip?: boolean;
  skipLabel?: string;
}

export const OnboardingLayout: React.FC<OnboardingLayoutProps> = ({
  children,
  currentStep,
  steps,
  onNext,
  onBack,
  onSkip,
  onExit,
  nextDisabled = false,
  nextLabel = 'Next',
  backLabel = 'Back',
  showSkip = false,
  skipLabel = 'Skip',
}) => {
  const progress = ((currentStep + 1) / steps.length) * 100;
  const currentStepData = steps[currentStep];
  const isFirstStep = currentStep === 0;
  const isLastStep = currentStep === steps.length - 1;

  return (
    <motion.div
      className="min-h-screen bg-background flex items-center justify-center p-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.3 }}
    >
      <motion.div
        className="w-full max-w-2xl mx-auto"
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.1 }}
      >
        {/* Header with progress and exit */}
        <motion.div
          className="mb-8"
          initial={{ y: -10, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.4, delay: 0.2 }}
        >
          <div className="flex items-center justify-between mb-4">
            <motion.div
              className="flex items-center space-x-2 text-sm text-muted-foreground"
              initial={{ x: -10, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ duration: 0.3, delay: 0.3 }}
            >
              <span>Step {currentStep + 1} of {steps.length}</span>
            </motion.div>
            <motion.div
              whileHover={{ scale: 1.1, rotate: 90 }}
              whileTap={{ scale: 0.9 }}
              transition={{ type: "spring", stiffness: 400, damping: 17 }}
            >
              <Button
                variant="ghost"
                size="icon"
                onClick={onExit}
                className="h-8 w-8 text-muted-foreground hover:text-foreground"
                aria-label="Exit onboarding"
              >
                <X className="h-4 w-4" />
              </Button>
            </motion.div>
          </div>

          {/* Progress bar */}
          <motion.div
            className="w-full"
            initial={{ scaleX: 0 }}
            animate={{ scaleX: 1 }}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <Progress value={progress} className="h-2" />
          </motion.div>

          {/* Step indicator dots */}
          <div className="flex justify-center mt-4 space-x-2">
            {steps.map((step, index) => (
              <motion.div
                key={step.id}
                className={`h-2 w-2 rounded-full transition-colors ${
                  index === currentStep
                    ? 'bg-primary'
                    : index < currentStep
                    ? 'bg-primary/60'
                    : 'bg-muted'
                }`}
                aria-label={`Step ${index + 1}: ${step.title}`}
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{
                  duration: 0.3,
                  delay: 0.5 + index * 0.05,
                  type: "spring",
                  stiffness: 300
                }}
                whileHover={{ scale: 1.2 }}
              />
            ))}
          </div>
        </motion.div>

        {/* Main content card */}
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.6 }}
        >
          <Card className="border-0 shadow-lg overflow-hidden">
            <CardContent className="p-8">
              {/* Step title and description */}
              <AnimatePresence mode="wait">
                {currentStepData && (
                  <motion.div
                    key={currentStep}
                    className="mb-8 text-center"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    transition={{ duration: 0.3 }}
                  >
                    <motion.h1
                      className="text-3xl font-bold tracking-tight mb-2"
                      initial={{ opacity: 0, y: 5 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.4, delay: 0.1 }}
                    >
                      {currentStepData.title}
                    </motion.h1>
                    <motion.p
                      className="text-muted-foreground text-lg"
                      initial={{ opacity: 0, y: 5 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.4, delay: 0.2 }}
                    >
                      {currentStepData.description}
                    </motion.p>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Step content */}
              <AnimatePresence mode="wait">
                <motion.div
                  key={currentStep}
                  className="min-h-[400px] flex flex-col justify-center"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.4 }}
                >
                  {children}
                </motion.div>
              </AnimatePresence>
            </CardContent>
          </Card>
        </motion.div>

        {/* Navigation footer */}
        <motion.div
          className="mt-8 flex items-center justify-between"
          initial={{ y: 10, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.4, delay: 0.8 }}
        >
          <div className="flex space-x-2">
            {!isFirstStep && (
              <motion.div
                initial={{ x: -10, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ duration: 0.3, delay: 0.9 }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Button
                  variant="outline"
                  onClick={onBack}
                  className="flex items-center space-x-2"
                >
                  <ArrowLeft className="h-4 w-4" />
                  <span>{backLabel}</span>
                </Button>
              </motion.div>
            )}
          </div>

          <div className="flex space-x-2">
            {showSkip && !isLastStep && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.3, delay: 1.0 }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Button
                  variant="ghost"
                  onClick={onSkip}
                  className="text-muted-foreground hover:text-foreground"
                >
                  {skipLabel}
                </Button>
              </motion.div>
            )}

            <motion.div
              initial={{ x: 10, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ duration: 0.3, delay: 1.1 }}
              whileHover={{ scale: nextDisabled ? 1 : 1.02 }}
              whileTap={{ scale: nextDisabled ? 1 : 0.98 }}
            >
              <Button
                onClick={onNext}
                disabled={nextDisabled}
                className="flex items-center space-x-2 min-w-[100px]"
              >
                <span>{nextLabel}</span>
                {!isLastStep && (
                  <motion.div
                    animate={nextDisabled ? {} : { x: [0, 3, 0] }}
                    transition={{ duration: 2, repeat: Infinity, repeatDelay: 1 }}
                  >
                    <ArrowRight className="h-4 w-4" />
                  </motion.div>
                )}
              </Button>
            </motion.div>
          </div>
        </motion.div>

        {/* Optional step completion status */}
        <motion.div
          className="mt-4 text-center text-sm text-muted-foreground"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.4, delay: 1.2 }}
        >
          {steps.filter(step => step.isCompleted).length} of {steps.length} steps completed
        </motion.div>
      </motion.div>
    </motion.div>
  );
};

export default OnboardingLayout;