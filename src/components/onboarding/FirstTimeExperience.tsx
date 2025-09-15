import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  X,
  ArrowRight,
  ArrowLeft,
  Sparkles,
  Trophy,
  Newspaper,
  Bell,
  Settings,
  Heart,
  TrendingUp,
} from 'lucide-react';

interface TutorialStep {
  id: string;
  title: string;
  description: string;
  icon: React.ComponentType<any>;
  target?: string; // CSS selector for highlighting
  position: 'top' | 'bottom' | 'left' | 'right' | 'center';
  action?: {
    label: string;
    onClick: () => void;
  };
}

interface FirstTimeExperienceProps {
  isOpen: boolean;
  onClose: () => void;
  onComplete: () => void;
  userPreferences?: {
    sports?: Array<{ name: string }>;
    teams?: Array<{ name: string }>;
  };
}

const tutorialSteps: TutorialStep[] = [
  {
    id: 'welcome',
    title: 'Welcome to Your Personalized Dashboard! 🎉',
    description: 'Your dashboard is now customized based on your favorite teams and preferences. Let\'s take a quick tour of what you can do here.',
    icon: Sparkles,
    position: 'center',
  },
  {
    id: 'sports-feed',
    title: 'Your Sports Feed',
    description: 'This section shows the latest news and updates for your favorite teams. Stories are prioritized based on your preferences.',
    icon: Newspaper,
    target: '[data-section="sports-feed"]',
    position: 'top',
  },
  {
    id: 'ai-summary',
    title: 'AI-Powered Summaries',
    description: 'Get quick, intelligent summaries of the day\'s most important sports news, tailored to your interests.',
    icon: TrendingUp,
    target: '[data-section="ai-summary"]',
    position: 'bottom',
  },
  {
    id: 'best-seats',
    title: 'Find the Best Seats',
    description: 'Discover great ticket deals and seating options for your favorite teams\' upcoming games.',
    icon: Trophy,
    target: '[data-section="best-seats"]',
    position: 'top',
  },
  {
    id: 'fan-experiences',
    title: 'Fan Experiences',
    description: 'Connect with other fans and discover exclusive experiences related to your teams.',
    icon: Heart,
    target: '[data-section="fan-experiences"]',
    position: 'top',
  },
  {
    id: 'notifications',
    title: 'Stay Updated',
    description: 'You\'ll receive notifications for breaking news, game reminders, and important updates based on your notification preferences.',
    icon: Bell,
    position: 'center',
  },
  {
    id: 'customization',
    title: 'Customize Anytime',
    description: 'You can always update your team preferences, notification settings, and content types from the settings menu.',
    icon: Settings,
    position: 'center',
  },
];

export const FirstTimeExperience: React.FC<FirstTimeExperienceProps> = ({
  isOpen,
  onClose,
  onComplete,
  userPreferences,
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [highlightedElement, setHighlightedElement] = useState<Element | null>(null);

  const currentStepData = tutorialSteps[currentStep];
  const isFirstStep = currentStep === 0;
  const isLastStep = currentStep === tutorialSteps.length - 1;

  // Handle element highlighting
  useEffect(() => {
    if (!isOpen || !currentStepData?.target) {
      setHighlightedElement(null);
      return;
    }

    const element = document.querySelector(currentStepData.target);
    if (element) {
      setHighlightedElement(element);
      element.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    return () => {
      setHighlightedElement(null);
    };
  }, [currentStep, isOpen, currentStepData]);

  // Add highlight styles to target element
  useEffect(() => {
    if (highlightedElement) {
      const originalStyle = highlightedElement.getAttribute('style') || '';
      highlightedElement.setAttribute('style',
        `${originalStyle}; position: relative; z-index: 1000; box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.5), 0 0 20px rgba(59, 130, 246, 0.3); border-radius: 8px; transition: all 0.3s ease;`
      );

      return () => {
        highlightedElement.setAttribute('style', originalStyle);
      };
    }
  }, [highlightedElement]);

  const handleNext = () => {
    if (isLastStep) {
      onComplete();
    } else {
      setCurrentStep(prev => prev + 1);
    }
  };

  const handlePrev = () => {
    if (!isFirstStep) {
      setCurrentStep(prev => prev - 1);
    }
  };

  const handleSkip = () => {
    onClose();
  };

  const getTooltipPosition = () => {
    if (!highlightedElement || currentStepData.position === 'center') {
      return {
        position: 'fixed' as const,
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        zIndex: 10001,
      };
    }

    const rect = highlightedElement.getBoundingClientRect();
    const tooltipWidth = 320;
    const tooltipHeight = 200;

    switch (currentStepData.position) {
      case 'top':
        return {
          position: 'fixed' as const,
          top: rect.top - tooltipHeight - 20,
          left: Math.max(20, Math.min(window.innerWidth - tooltipWidth - 20, rect.left + rect.width / 2 - tooltipWidth / 2)),
          zIndex: 10001,
        };
      case 'bottom':
        return {
          position: 'fixed' as const,
          top: rect.bottom + 20,
          left: Math.max(20, Math.min(window.innerWidth - tooltipWidth - 20, rect.left + rect.width / 2 - tooltipWidth / 2)),
          zIndex: 10001,
        };
      case 'left':
        return {
          position: 'fixed' as const,
          top: Math.max(20, Math.min(window.innerHeight - tooltipHeight - 20, rect.top + rect.height / 2 - tooltipHeight / 2)),
          left: rect.left - tooltipWidth - 20,
          zIndex: 10001,
        };
      case 'right':
        return {
          position: 'fixed' as const,
          top: Math.max(20, Math.min(window.innerHeight - tooltipHeight - 20, rect.top + rect.height / 2 - tooltipHeight / 2)),
          left: rect.right + 20,
          zIndex: 10001,
        };
      default:
        return {
          position: 'fixed' as const,
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          zIndex: 10001,
        };
    }
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/60 backdrop-blur-sm"
        style={{ zIndex: 10000 }}
        onClick={handleSkip}
      />

      {/* Tutorial Card */}
      <AnimatePresence mode="wait">
        <motion.div
          key={currentStep}
          initial={{ opacity: 0, scale: 0.9, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.9, y: -20 }}
          transition={{ duration: 0.3 }}
          style={getTooltipPosition()}
          className="w-80 max-w-[calc(100vw-40px)]"
        >
          <Card className="border-2 border-primary/20 shadow-2xl">
            <CardContent className="p-6">
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="h-10 w-10 bg-primary/10 rounded-full flex items-center justify-center">
                    <currentStepData.icon className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <Badge variant="secondary" className="text-xs">
                      {currentStep + 1} of {tutorialSteps.length}
                    </Badge>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={handleSkip}
                  className="h-8 w-8 text-muted-foreground hover:text-foreground"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>

              {/* Content */}
              <div className="space-y-4">
                <h3 className="font-semibold text-lg leading-tight">
                  {currentStepData.title}
                </h3>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {currentStepData.description}
                </p>

                {/* Show user selections on welcome step */}
                {currentStep === 0 && userPreferences && (
                  <div className="space-y-3 p-3 bg-primary/5 rounded-lg border border-primary/10">
                    {userPreferences.sports && userPreferences.sports.length > 0 && (
                      <div>
                        <p className="text-xs font-medium text-primary mb-1">Your Sports:</p>
                        <div className="flex flex-wrap gap-1">
                          {userPreferences.sports.slice(0, 3).map((sport, index) => (
                            <Badge key={index} variant="outline" className="text-xs">
                              {sport.name}
                            </Badge>
                          ))}
                          {userPreferences.sports.length > 3 && (
                            <Badge variant="outline" className="text-xs">
                              +{userPreferences.sports.length - 3} more
                            </Badge>
                          )}
                        </div>
                      </div>
                    )}

                    {userPreferences.teams && userPreferences.teams.length > 0 && (
                      <div>
                        <p className="text-xs font-medium text-primary mb-1">Your Teams:</p>
                        <div className="flex flex-wrap gap-1">
                          {userPreferences.teams.slice(0, 3).map((team, index) => (
                            <Badge key={index} variant="outline" className="text-xs">
                              {team.name}
                            </Badge>
                          ))}
                          {userPreferences.teams.length > 3 && (
                            <Badge variant="outline" className="text-xs">
                              +{userPreferences.teams.length - 3} more
                            </Badge>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Navigation */}
              <div className="flex items-center justify-between mt-6">
                <div className="flex items-center space-x-2">
                  {!isFirstStep && (
                    <Button variant="outline" size="sm" onClick={handlePrev}>
                      <ArrowLeft className="h-4 w-4 mr-1" />
                      Back
                    </Button>
                  )}
                </div>

                <div className="flex items-center space-x-2">
                  <Button variant="ghost" size="sm" onClick={handleSkip}>
                    Skip Tour
                  </Button>
                  <Button size="sm" onClick={handleNext}>
                    {isLastStep ? 'Get Started' : 'Next'}
                    {!isLastStep && <ArrowRight className="h-4 w-4 ml-1" />}
                  </Button>
                </div>
              </div>

              {/* Progress dots */}
              <div className="flex justify-center mt-4 space-x-1">
                {tutorialSteps.map((_, index) => (
                  <div
                    key={index}
                    className={`h-1.5 w-1.5 rounded-full transition-colors ${
                      index === currentStep
                        ? 'bg-primary'
                        : index < currentStep
                        ? 'bg-primary/60'
                        : 'bg-muted'
                    }`}
                  />
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </AnimatePresence>
    </>
  );
};

export default FirstTimeExperience;