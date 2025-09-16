import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useUser } from "@clerk/clerk-react";
import { TopNavBar } from "@/components/TopNavBar";
import { AISummarySection } from "@/components/AISummarySection";
import { SportsFeedSection } from "@/components/SportsFeedSection";
import { BestSeatsSection } from "@/components/BestSeatsSection";
import { FanExperiencesSection } from "@/components/FanExperiencesSection";
import { DepthChartSection } from "@/components/DepthChartSection";
import { FirstTimeExperience } from "@/components/onboarding/FirstTimeExperience";
import { OnboardingStorage } from "@/lib/onboarding/localStorage";
import { useAuthenticatedApiClient } from "@/hooks/useAuthenticatedApiClient";
import { useDashboard } from "@/hooks/useDashboard";
import { useToast } from "@/hooks/use-toast";

const Index = () => {
  const navigate = useNavigate();
  const { user, isLoaded } = useUser();
  const { apiClient, isAuthenticated } = useAuthenticatedApiClient();
  const [showFirstTimeExperience, setShowFirstTimeExperience] = useState(false);
  const [userPreferences, setUserPreferences] = useState(null);
  const { toast } = useToast();

  // Get dashboard data using custom hook
  const {
    homeData,
    teamDashboard,
    isLoading: dashboardLoading,
    error: dashboardError,
    refetchAll,
    homeError,
    teamError
  } = useDashboard();

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

  // Handle API errors with toast notifications
  useEffect(() => {
    if (dashboardError) {
      toast({
        title: "Dashboard Error",
        description: "Unable to load dashboard data. Please try refreshing the page.",
        variant: "destructive",
      });
    }
  }, [dashboardError, toast]);

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
        {/* AI Summary Section - Hero area with team name, summary, and scores */}
        <div data-section="ai-summary">
          <AISummarySection
            teamDashboard={teamDashboard}
            isLoading={dashboardLoading}
            error={dashboardError}
          />
        </div>

        {/* Dashboard Sections */}
        <div className="pb-4 sm:pb-8">
          {/* Sports Feed Section - News articles */}
          <div data-section="sports-feed">
            <SportsFeedSection
              teamDashboard={teamDashboard}
              isLoading={dashboardLoading}
              error={teamError}
            />
          </div>

          {/* Depth Chart Section - Team roster */}
          <div data-section="depth-chart">
            <DepthChartSection
              depthChart={teamDashboard?.depthChart || []}
              teamName={teamDashboard?.team.name}
              isLoading={dashboardLoading}
              error={teamError}
            />
          </div>

          {/* Best Seats Section - Ticket deals */}
          <div data-section="best-seats">
            <BestSeatsSection
              teamDashboard={teamDashboard}
              isLoading={dashboardLoading}
              error={teamError}
            />
          </div>

          {/* Fan Experiences Section */}
          <div data-section="fan-experiences">
            <FanExperiencesSection
              teamDashboard={teamDashboard}
              isLoading={dashboardLoading}
              error={teamError}
            />
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
