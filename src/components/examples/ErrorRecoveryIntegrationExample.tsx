/**
 * Error Recovery Integration Example
 *
 * This file demonstrates how to integrate all the error recovery components
 * into the main application. It shows the recommended setup for:
 *
 * 1. ErrorBoundaryProvider (global error handling)
 * 2. OnboardingWithErrorRecovery (onboarding-specific error recovery)
 * 3. OfflineIndicator (connection status display)
 * 4. useOnboardingApiWithRetry (API calls with retry logic)
 * 5. Enhanced API client with retry functionality
 */

import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Toaster } from '@/components/ui/toaster';

// Error recovery components
import ErrorBoundaryProvider from '@/components/error-boundaries/ErrorBoundaryProvider';
import OnboardingWithErrorRecovery from '@/components/onboarding/OnboardingWithErrorRecovery';
import OfflineIndicator from '@/components/ui/OfflineIndicator';

// Existing onboarding components
import OnboardingLayout from '@/pages/onboarding/OnboardingLayout';

// Hooks
import useOnlineStatus from '@/hooks/useOnlineStatus';
import useOnboardingApiWithRetry from '@/hooks/useOnboardingApiWithRetry';

// API client with retry functionality
import { apiClient } from '@/lib/api-client';

/**
 * 1. App-level setup with ErrorBoundaryProvider
 *
 * Wrap your entire app with ErrorBoundaryProvider to catch all React errors
 * and provide global error recovery functionality.
 */
function AppWithErrorRecovery() {
  // Configure React Query client with retry policies
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: (failureCount, error: any) => {
          // Don't retry authentication errors
          if (error?.statusCode === 401 || error?.statusCode === 403) {
            return false;
          }
          // Retry up to 3 times for other errors
          return failureCount < 3;
        },
        retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
        staleTime: 5 * 60 * 1000, // 5 minutes
      },
      mutations: {
        retry: (failureCount, error: any) => {
          // Only retry server errors for mutations
          if (error?.statusCode >= 500) {
            return failureCount < 2;
          }
          return false;
        },
      },
    },
  });

  return (
    <ErrorBoundaryProvider
      enableErrorReporting={true}
      enableAutoRecovery={true}
      autoRecoveryDelay={3000}
      onError={(error, errorInfo) => {
        // Custom error handling (e.g., send to monitoring service)
        console.log('Global error caught:', error, errorInfo);
      }}
      onRecovery={() => {
        // Custom recovery handling
        console.log('Global error recovery completed');
      }}
    >
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <div className="min-h-screen bg-background">
            {/* Global offline indicator in header */}
            <header className="border-b p-4 flex justify-between items-center">
              <h1>Corner League Media</h1>
              <OfflineIndicator variant="minimal" />
            </header>

            <main>
              <Routes>
                <Route path="/onboarding/*" element={<OnboardingFlow />} />
                <Route path="/" element={<HomePage />} />
              </Routes>
            </main>
          </div>
          <Toaster />
        </BrowserRouter>
      </QueryClientProvider>
    </ErrorBoundaryProvider>
  );
}

/**
 * 2. Onboarding flow with enhanced error recovery
 *
 * Each onboarding step is wrapped with OnboardingWithErrorRecovery
 * to provide step-specific error handling and recovery.
 */
function OnboardingFlow() {
  const { isOnline, connectionQuality } = useOnlineStatus();

  return (
    <div className="container max-w-4xl mx-auto p-4">
      {/* Connection status alert */}
      {!isOnline && (
        <div className="mb-4">
          <OfflineIndicator
            variant="alert"
            showRetryButton={true}
            onRetry={() => window.location.reload()}
            customOfflineMessage="You're offline, but you can continue with onboarding. Your progress will be saved locally and synced when you reconnect."
          />
        </div>
      )}

      <Routes>
        <Route path="/step/1" element={<OnboardingStep1 />} />
        <Route path="/step/2" element={<OnboardingStep2 />} />
        <Route path="/step/3" element={<OnboardingStep3 />} />
        <Route path="/step/4" element={<OnboardingStep4 />} />
        <Route path="/completion" element={<OnboardingCompletion />} />
      </Routes>
    </div>
  );
}

/**
 * 3. Example onboarding step with error recovery
 *
 * Shows how to integrate OnboardingWithErrorRecovery with existing
 * onboarding step components.
 */
function OnboardingStep2() {
  return (
    <OnboardingLayout
      step={2}
      totalSteps={4}
      title="Select Your Sports"
      subtitle="Choose the sports you want to follow"
    >
      <OnboardingWithErrorRecovery
        step={2}
        stepName="Sports Selection"
        allowOfflineMode={true}
        requiresConnection={false}
        autoSaveEnabled={true}
        onStepComplete={(stepData) => {
          console.log('Step 2 completed:', stepData);
          // Navigate to next step
        }}
        onStepError={(error, step) => {
          console.error(`Error in step ${step}:`, error);
        }}
      >
        <SportsSelectionStep />
      </OnboardingWithErrorRecovery>
    </OnboardingLayout>
  );
}

/**
 * 4. Sports selection component using API with retry
 *
 * Demonstrates how to use useOnboardingApiWithRetry for robust API calls
 * with automatic retry logic and offline handling.
 */
function SportsSelectionStep() {
  const [selectedSports, setSelectedSports] = React.useState<string[]>([]);
  const {
    apiState,
    isOnline,
    canRetry,
    getSports,
    updateOnboardingStep,
    clearError,
    retryLastRequest,
  } = useOnboardingApiWithRetry();

  const [sports, setSports] = React.useState<any[]>([]);
  const [isLoading, setIsLoading] = React.useState(true);

  // Load sports on component mount
  React.useEffect(() => {
    loadSports();
  }, []);

  const loadSports = async () => {
    try {
      setIsLoading(true);
      const sportsData = await getSports();
      setSports(sportsData);
    } catch (error) {
      console.error('Failed to load sports:', error);
      // Error is handled by the hook and displayed via toast
    } finally {
      setIsLoading(false);
    }
  };

  const handleSportSelection = (sportId: string) => {
    setSelectedSports(prev =>
      prev.includes(sportId)
        ? prev.filter(id => id !== sportId)
        : [...prev, sportId]
    );
  };

  const handleContinue = async () => {
    if (selectedSports.length === 0) {
      alert('Please select at least one sport.');
      return;
    }

    try {
      await updateOnboardingStep({
        step: 2,
        data: { sports: selectedSports },
      });
      // Navigation will be handled by parent component
    } catch (error) {
      // Error is handled by the hook
      console.error('Failed to save sports selection:', error);
    }
  };

  if (isLoading) {
    return <div className="text-center py-8">Loading sports...</div>;
  }

  return (
    <div className="space-y-6">
      {/* API Error Display */}
      {apiState.error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex justify-between items-start">
            <div>
              <h4 className="font-medium text-red-800">Error Loading Sports</h4>
              <p className="text-red-700 text-sm mt-1">{apiState.error.message}</p>
              {!isOnline && (
                <p className="text-red-600 text-xs mt-2">
                  You're currently offline. Please check your connection and try again.
                </p>
              )}
            </div>
            <div className="flex gap-2">
              {canRetry && (
                <button
                  onClick={retryLastRequest}
                  disabled={apiState.isRetrying}
                  className="bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700 disabled:opacity-50"
                >
                  {apiState.isRetrying ? 'Retrying...' : 'Retry'}
                </button>
              )}
              <button
                onClick={clearError}
                className="bg-gray-600 text-white px-3 py-1 rounded text-sm hover:bg-gray-700"
              >
                Dismiss
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Connection Quality Warning */}
      <OfflineIndicator
        variant="alert"
        hideWhenOnline={false}
        showConnectionQuality={true}
      />

      {/* Sports Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {sports.map((sport) => (
          <div
            key={sport.id}
            onClick={() => handleSportSelection(sport.id)}
            className={`
              p-4 border-2 rounded-lg cursor-pointer transition-all
              ${selectedSports.includes(sport.id)
                ? 'border-primary bg-primary/10'
                : 'border-gray-200 hover:border-gray-300'
              }
            `}
          >
            <div className="text-center">
              <div className="text-2xl mb-2">{sport.icon}</div>
              <div className="font-medium">{sport.name}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Actions */}
      <div className="flex justify-between">
        <button
          onClick={() => history.back()}
          className="px-4 py-2 border border-gray-300 rounded hover:bg-gray-50"
        >
          Back
        </button>
        <button
          onClick={handleContinue}
          disabled={selectedSports.length === 0 || apiState.isLoading}
          className="px-4 py-2 bg-primary text-primary-foreground rounded hover:bg-primary/90 disabled:opacity-50"
        >
          {apiState.isLoading ? 'Saving...' : 'Continue'}
        </button>
      </div>

      {/* Retry Count Display (for demo) */}
      {apiState.retryCount > 0 && (
        <div className="text-center text-sm text-muted-foreground">
          Retry attempts: {apiState.retryCount}
        </div>
      )}
    </div>
  );
}

/**
 * 5. Homepage with offline indicator
 *
 * Shows how to integrate offline indicators in regular pages
 */
function HomePage() {
  const { isOnline } = useOnlineStatus();

  return (
    <div className="container mx-auto p-4">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <OfflineIndicator variant="badge" showConnectionQuality />
      </div>

      {!isOnline && (
        <OfflineIndicator
          variant="card"
          showRetryButton
          onRetry={() => window.location.reload()}
          className="mb-6"
        />
      )}

      <div className="grid gap-6">
        {/* Your dashboard content */}
        <div className="bg-card p-6 rounded-lg border">
          <h2 className="text-xl font-semibold mb-4">Your Teams</h2>
          {/* Content */}
        </div>
      </div>
    </div>
  );
}

/**
 * 6. API Client Configuration
 *
 * Configure the API client with retry settings for the entire app
 */
export function configureApiClient() {
  // Enable retries globally
  apiClient.enableRetry(true);

  // You can also create specific instances for different use cases
  const onboardingApiClient = new (await import('@/lib/api-client')).ApiClient(
    process.env.REACT_APP_API_URL,
    {
      maxRetries: 3,
      baseDelay: 1000,
      maxDelay: 10000,
      backoffFactor: 2,
      jitter: true,
    },
    true // enable retries
  );

  return { apiClient, onboardingApiClient };
}

export default AppWithErrorRecovery;

/**
 * Usage Instructions:
 *
 * 1. Replace your main App component with AppWithErrorRecovery
 * 2. Wrap onboarding steps with OnboardingWithErrorRecovery
 * 3. Use OfflineIndicator components throughout your app
 * 4. Replace API hooks with useOnboardingApiWithRetry where appropriate
 * 5. Configure the API client with retry settings
 *
 * The error recovery system will:
 * - Catch and display React errors gracefully
 * - Provide retry functionality for failed operations
 * - Show offline indicators and handle offline scenarios
 * - Automatically retry API calls with exponential backoff
 * - Save progress locally when offline
 * - Sync data when connection is restored
 */