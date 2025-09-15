import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useUser } from "@clerk/clerk-react";
import { TopNavBar } from "@/components/TopNavBar";
import { AISummarySection } from "@/components/AISummarySection";
import { SportsFeedSection } from "@/components/SportsFeedSection";
import { BestSeatsSection } from "@/components/BestSeatsSection";
import { FanExperiencesSection } from "@/components/FanExperiencesSection";
import { FirstTimeExperience } from "@/components/onboarding/FirstTimeExperience";
import { OnboardingStorage } from "@/lib/onboarding/localStorage";
import { useAuthenticatedApiClient } from "@/hooks/useAuthenticatedApiClient";

const Index = () => {
  const navigate = useNavigate();
  const { user, isLoaded } = useUser();
  const { apiClient, isAuthenticated } = useAuthenticatedApiClient();
  const [showFirstTimeExperience, setShowFirstTimeExperience] = useState(false);
  const [userPreferences, setUserPreferences] = useState(null);

  // Check if user has completed onboarding
  useEffect(() => {
    if (!isLoaded || !isAuthenticated) return;

    console.log('Index component loaded for user:', user?.id);

    const isOnboardingCompleted = OnboardingStorage.isOnboardingCompleted();
    console.log('Onboarding completed:', isOnboardingCompleted);

    if (!isOnboardingCompleted) {
      // Redirect to onboarding if not completed
      console.log('Redirecting to onboarding');
      navigate('/onboarding', { replace: true });
      return;
    }

    // Load user preferences
    const preferences = OnboardingStorage.loadUserPreferences();
    setUserPreferences(preferences);

    // Check if this is the first time visiting after onboarding
    const hasSeenTutorial = localStorage.getItem(`corner-league-tutorial-seen-${user?.id}`);
    if (!hasSeenTutorial && preferences) {
      setShowFirstTimeExperience(true);
    }
  }, [navigate, isLoaded, isAuthenticated, user?.id]);

  const handleTutorialComplete = () => {
    localStorage.setItem(`corner-league-tutorial-seen-${user?.id}`, 'true');
    setShowFirstTimeExperience(false);
  };

  const handleTutorialClose = () => {
    localStorage.setItem(`corner-league-tutorial-seen-${user?.id}`, 'true');
    setShowFirstTimeExperience(false);
  };

  return (
    <div className="min-h-screen bg-background font-body">
      {/* Navigation */}
      <TopNavBar />

      {/* Main Content Area */}
      <div className="flex flex-col min-h-[calc(100vh-4rem)]">
        {/* AI Summary - Takes available space */}
        <div data-section="ai-summary">
          <AISummarySection />
        </div>

        {/* Sports Feed - Bottom sections */}
        <div className="pb-4 sm:pb-8">
          <div data-section="sports-feed">
            <SportsFeedSection />
          </div>
          <div data-section="best-seats">
            <BestSeatsSection />
          </div>
          <div data-section="fan-experiences">
            <FanExperiencesSection />
          </div>
        </div>
      </div>

      {/* First Time Experience Tutorial */}
      <FirstTimeExperience
        isOpen={showFirstTimeExperience}
        onClose={handleTutorialClose}
        onComplete={handleTutorialComplete}
        userPreferences={userPreferences}
      />
    </div>
  );
};

export default Index;
