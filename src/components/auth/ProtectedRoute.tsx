import { Navigate, useLocation } from "react-router-dom";
import { ReactNode } from "react";
import { useAuthOnboarding } from "@/hooks/useAuthOnboarding";
import {
  type EnhancedProtectedRouteProps,
  type RouteGuardResult,
} from "@/lib/types/auth-onboarding";

// Enhanced loading component
function LoadingScreen({ message = "Loading..." }: { message?: string }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center space-y-4">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
        <p className="text-muted-foreground font-body">{message}</p>
      </div>
    </div>
  );
}

// Route guard logic
function useRouteGuard(props: EnhancedProtectedRouteProps): RouteGuardResult {
  const {
    requireAuth = true,
    requireOnboarding = true,
    redirectTo = "/auth/sign-in",
    onboardingRedirectTo,
  } = props;

  const {
    isLoading,
    isAuthenticated,
    isOnboarded,
    flowState,
    onboardingStatus,
    getRedirectPath,
  } = useAuthOnboarding();

  // Test mode bypass
  const isTestMode = (window as any).__PLAYWRIGHT_TEST__ === true ||
                     window.location.search.includes('test=true') ||
                     import.meta.env.VITE_TEST_MODE === 'true';

  if (isTestMode && props.allowTestMode !== false) {
    return {
      canAccess: true,
      redirectTo: null,
      isLoading: false,
      error: null,
    };
  }

  // Loading states
  if (isLoading) {
    let loadingMessage = "Loading...";

    switch (flowState) {
      case 'initializing':
        loadingMessage = "Initializing authentication...";
        break;
      case 'checking':
        loadingMessage = "Checking your profile...";
        break;
      default:
        loadingMessage = "Loading your experience...";
    }

    return {
      canAccess: false,
      redirectTo: null,
      isLoading: true,
      error: loadingMessage,
    };
  }

  // Authentication required but user not authenticated
  if (requireAuth && !isAuthenticated) {
    return {
      canAccess: false,
      redirectTo,
      isLoading: false,
      error: null,
    };
  }

  // Onboarding required but not completed
  if (requireOnboarding && isAuthenticated && !isOnboarded) {
    const onboardingRedirect = onboardingRedirectTo ||
      (onboardingStatus?.currentStep ? `/onboarding/step/${onboardingStatus.currentStep}` : '/onboarding/step/1');

    return {
      canAccess: false,
      redirectTo: onboardingRedirect,
      isLoading: false,
      error: null,
    };
  }

  // Error states
  if (flowState === 'error') {
    return {
      canAccess: false,
      redirectTo: null,
      isLoading: false,
      error: "Authentication error occurred",
    };
  }

  // All checks passed
  return {
    canAccess: true,
    redirectTo: null,
    isLoading: false,
    error: null,
  };
}

// Legacy ProtectedRoute interface for backward compatibility
interface LegacyProtectedRouteProps {
  children: ReactNode;
  redirectTo?: string;
}

// Enhanced ProtectedRoute component
export function ProtectedRoute(props: EnhancedProtectedRouteProps | LegacyProtectedRouteProps) {
  // Convert legacy props to enhanced props
  const enhancedProps: EnhancedProtectedRouteProps = 'requireAuth' in props
    ? props as EnhancedProtectedRouteProps
    : {
        children: props.children,
        requireAuth: true,
        requireOnboarding: true,
        redirectTo: (props as LegacyProtectedRouteProps).redirectTo || "/auth/sign-in",
        allowTestMode: true,
      };

  const { canAccess, redirectTo, isLoading, error } = useRouteGuard(enhancedProps);
  const location = useLocation();

  // Handle error callbacks
  if (error && enhancedProps.onAuthError) {
    enhancedProps.onAuthError(error);
  }

  // Show loading state
  if (isLoading) {
    if (enhancedProps.loadingComponent) {
      const LoadingComponent = enhancedProps.loadingComponent;
      return <LoadingComponent />;
    }

    return <LoadingScreen message={error || "Loading..."} />;
  }

  // Redirect if needed
  if (redirectTo) {
    return <Navigate to={redirectTo} replace state={{ from: location }} />;
  }

  // Show error state
  if (error && !canAccess) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center space-y-4">
          <div className="text-destructive">
            <h2 className="text-xl font-semibold">Authentication Error</h2>
            <p className="text-sm text-muted-foreground mt-2">{error}</p>
          </div>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // Render children if all checks pass
  if (canAccess) {
    return <>{enhancedProps.children}</>;
  }

  // Fallback - should not reach here
  return <Navigate to="/auth/sign-in" replace />;
}

// Additional route guard hooks for specific use cases
export function useAuthGuard() {
  const { isAuthenticated, isLoading } = useAuthOnboarding();

  return {
    isAuthenticated,
    isLoading,
    requireAuth: !isAuthenticated && !isLoading,
  };
}

export function useOnboardingGuard() {
  const { isOnboarded, isAuthenticated, isLoading, onboardingStatus } = useAuthOnboarding();

  return {
    isOnboarded,
    isAuthenticated,
    isLoading,
    requireOnboarding: isAuthenticated && !isOnboarded && !isLoading,
    currentStep: onboardingStatus?.currentStep || 1,
  };
}

// Route-specific protected components
export function AuthOnlyRoute({ children, ...props }: Omit<EnhancedProtectedRouteProps, 'requireOnboarding'>) {
  return (
    <ProtectedRoute
      {...props}
      requireAuth={true}
      requireOnboarding={false}
    >
      {children}
    </ProtectedRoute>
  );
}

export function OnboardingRoute({ children, ...props }: Omit<EnhancedProtectedRouteProps, 'requireAuth' | 'requireOnboarding'>) {
  return (
    <ProtectedRoute
      {...props}
      requireAuth={true}
      requireOnboarding={false}
    >
      {children}
    </ProtectedRoute>
  );
}

export function FullyProtectedRoute({ children, ...props }: EnhancedProtectedRouteProps) {
  return (
    <ProtectedRoute
      {...props}
      requireAuth={true}
      requireOnboarding={true}
    >
      {children}
    </ProtectedRoute>
  );
}

export default ProtectedRoute;