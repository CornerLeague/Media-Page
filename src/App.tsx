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
import { apiClient, createApiQueryClient } from "@/lib/api-client";
import { useEffect } from "react";

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

  // Fetch home data to get the user's most liked team
  const {
    data: homeData,
    isLoading: homeLoading,
    error: homeError,
  } = useQuery(queryConfigs.getHomeData());

  // Fetch team dashboard data for the user's most liked team
  const {
    data: teamDashboard,
    isLoading: dashboardLoading,
    error: dashboardError,
  } = useQuery({
    ...queryConfigs.getTeamDashboard(homeData?.most_liked_team_id || ''),
    enabled: !!homeData?.most_liked_team_id,
  });

  const isLoading = homeLoading || dashboardLoading;
  const error = homeError || dashboardError;

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

// Sign in page component
function SignInPage() {
  const navigate = useNavigate();

  const handleSignInSuccess = () => {
    navigate('/');
  };

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