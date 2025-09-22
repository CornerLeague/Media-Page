import { QueryClient, QueryClientProvider, useQuery } from "@tanstack/react-query";
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from "react-router-dom";
import { ThemeProvider } from "@/components/ThemeProvider";
import { Toaster } from "@/components/ui/toaster";
import { TopNavBar } from "@/components/TopNavBar";
import { AISummarySection } from "@/components/AISummarySection";
import { SportsFeedSection } from "@/components/SportsFeedSection";
import { BestSeatsSection } from "@/components/BestSeatsSection";
import { FanExperiencesSection } from "@/components/FanExperiencesSection";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { FirebaseAuthProvider, useFirebaseAuth } from "@/contexts/FirebaseAuthContext";
import { FirebaseSignIn } from "@/components/auth/FirebaseSignIn";
import { OnboardingRouter } from "@/pages/onboarding";
import { apiClient, createApiQueryClient, type OnboardingStatus } from "@/lib/api-client";
import { useEffect, useState } from "react";

// Create React Query client with optimized settings
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes
      retry: (failureCount, error) => {
        // Don't retry on 4xx errors (except 429)
        if (error && typeof error === 'object' && 'statusCode' in error) {
          const statusCode = (error as any).statusCode;
          if (statusCode >= 400 && statusCode < 500 && statusCode !== 429) {
            return false;
          }
        }
        return failureCount < 3;
      },
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    },
  },
});

// Main dashboard component that loads the team data
function DashboardPage() {
  const { isAuthenticated, getIdToken, user } = useFirebaseAuth();
  const navigate = useNavigate();

  // Set up API client with Firebase authentication
  useEffect(() => {
    if (isAuthenticated && getIdToken) {
      apiClient.setFirebaseAuth({
        getIdToken,
        isAuthenticated: true,
        userId: user?.uid,
      });
    }
  }, [isAuthenticated, getIdToken, user?.uid]);

  // Get query configurations with Firebase auth
  const queryConfigs = createApiQueryClient(
    isAuthenticated ? { getIdToken, isAuthenticated: true, userId: user?.uid } : undefined
  );

  // Check onboarding status first
  const {
    data: onboardingStatus,
    isLoading: onboardingLoading,
    error: onboardingError,
  } = useQuery(queryConfigs.getOnboardingStatus());

  // Redirect to onboarding if not complete (with fallback logic)
  useEffect(() => {
    if (onboardingError) {
      // API failed, check localStorage for fallback
      import('@/lib/onboarding-storage').then(({ getLocalOnboardingStatus, isFirstVisit }) => {
        const localStatus = getLocalOnboardingStatus();

        if (isFirstVisit() || (localStatus && !localStatus.isComplete)) {
          const targetStep = localStatus?.currentStep || 1;
          navigate(`/onboarding/step/${targetStep}`);
        }
        // If no local data and not first visit, stay on dashboard
      });
    } else if (onboardingStatus && !onboardingStatus.isComplete) {
      navigate(`/onboarding/step/${onboardingStatus.currentStep}`);
    }
  }, [onboardingStatus, onboardingError, navigate]);

  // Fetch home data to get the user's most liked team
  const {
    data: homeData,
    isLoading: homeLoading,
    error: homeError,
  } = useQuery({
    ...queryConfigs.getHomeData(),
    enabled: onboardingStatus?.isComplete === true,
  });

  // Fetch team dashboard data for the user's most liked team
  const {
    data: teamDashboard,
    isLoading: dashboardLoading,
    error: dashboardError,
  } = useQuery({
    ...queryConfigs.getTeamDashboard(homeData?.most_liked_team_id || ''),
    enabled: !!homeData?.most_liked_team_id && onboardingStatus?.isComplete === true,
  });

  const isLoading = onboardingLoading || homeLoading || dashboardLoading;
  const error = onboardingError || homeError || dashboardError;

  // Show loading while checking onboarding status
  if (onboardingLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground font-body">Loading your profile...</p>
        </div>
      </div>
    );
  }

  // Don't render dashboard if onboarding is not complete
  if (!onboardingStatus?.isComplete) {
    return null; // Redirect happens in useEffect
  }

  return (
    <div className="min-h-screen bg-background">
      <TopNavBar />

      <main className="relative">
        {/* AI Summary Section - Hero area */}
        <AISummarySection
          teamDashboard={teamDashboard}
          isLoading={isLoading}
          error={error as Error | null}
        />

        {/* Sports Feed Section */}
        <SportsFeedSection
          teamDashboard={teamDashboard}
          isLoading={isLoading}
          error={error as Error | null}
        />

        {/* Best Seats Section */}
        <BestSeatsSection
          teamDashboard={teamDashboard}
          isLoading={isLoading}
          error={error as Error | null}
        />

        {/* Fan Experiences Section */}
        <FanExperiencesSection
          teamDashboard={teamDashboard}
          isLoading={isLoading}
          error={error as Error | null}
        />
      </main>
    </div>
  );
}

// Authentication loading component
function AuthLoading() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center space-y-4">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
        <p className="text-muted-foreground font-body">Loading Corner League Media...</p>
      </div>
    </div>
  );
}

// Sign in page component with intelligent routing
function SignInPage() {
  const navigate = useNavigate();
  const { isAuthenticated, getIdToken, user } = useFirebaseAuth();
  const [isCheckingOnboarding, setIsCheckingOnboarding] = useState(false);

  // Set up API client with Firebase authentication when user signs in
  useEffect(() => {
    if (isAuthenticated && getIdToken) {
      apiClient.setFirebaseAuth({
        getIdToken,
        isAuthenticated: true,
        userId: user?.uid,
      });
    }
  }, [isAuthenticated, getIdToken, user?.uid]);

  // Get query configurations with Firebase auth
  const queryConfigs = createApiQueryClient(
    isAuthenticated ? { getIdToken, isAuthenticated: true, userId: user?.uid } : undefined
  );

  const handleSignInSuccess = async () => {
    setIsCheckingOnboarding(true);

    try {
      // Wait a moment for Firebase auth to fully initialize
      await new Promise(resolve => setTimeout(resolve, 100));

      // Check onboarding status after successful sign-in with timeout
      const onboardingStatusPromise = apiClient.getOnboardingStatus();
      const timeoutPromise = new Promise((_, reject) =>
        setTimeout(() => reject(new Error('API timeout')), 5000)
      );

      const onboardingStatus = await Promise.race([
        onboardingStatusPromise,
        timeoutPromise
      ]) as OnboardingStatus;

      if (onboardingStatus.isComplete) {
        // User has completed onboarding, go to main dashboard
        navigate('/');
      } else {
        // New user or incomplete onboarding, go to appropriate step
        navigate(`/onboarding/step/${onboardingStatus.currentStep}`);
      }
    } catch (error) {
      console.error('Failed to check onboarding status:', error);

      // Implement robust fallback logic when API fails
      const {
        determineOnboardingRoute,
        getLocalOnboardingStatus,
        isFirstVisit,
        markUserVisited
      } = await import('@/lib/onboarding-storage');

      // Check if this is a new user by looking at Firebase user metadata
      const isNewUser = user?.metadata?.creationTime === user?.metadata?.lastSignInTime;

      // Use fallback logic to determine where to navigate
      const fallbackRoute = determineOnboardingRoute(
        null, // API status is null because it failed
        true, // API error occurred
        isNewUser || isFirstVisit()
      );

      console.log('Using fallback navigation route:', fallbackRoute);
      navigate(fallbackRoute);
    } finally {
      setIsCheckingOnboarding(false);
    }
  };

  // Show loading state while checking onboarding status
  if (isCheckingOnboarding) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground font-body">Setting up your experience...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center space-y-6 max-w-md mx-auto px-4">
        <div className="space-y-2">
          <h1 className="font-display font-bold text-3xl text-foreground">
            Corner League Media
          </h1>
          <p className="text-muted-foreground font-body">
            Your personalized sports experience awaits
          </p>
        </div>

        <div className="space-y-4">
          <p className="text-sm text-muted-foreground">
            Sign in to access your personalized team dashboard, news feed, and exclusive content.
          </p>

          <FirebaseSignIn onSuccess={handleSignInSuccess} />
        </div>
      </div>
    </div>
  );
}

// App router component
function AppRouter() {
  return (
    <Router>
      <Routes>
        {/* Main dashboard route */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          }
        />

        {/* Onboarding routes */}
        <Route
          path="/onboarding/*"
          element={
            <ProtectedRoute>
              <OnboardingRouter />
            </ProtectedRoute>
          }
        />

        {/* Authentication route */}
        <Route path="/auth/sign-in" element={<SignInPage />} />

        {/* Catch all route - redirect to home */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

// Main App component
function App() {
  return (
    <FirebaseAuthProvider>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <AppRouter />
          <Toaster />
        </ThemeProvider>
      </QueryClientProvider>
    </FirebaseAuthProvider>
  );
}

export default App;