/**
 * OnboardingErrorBoundary Tests
 *
 * Comprehensive tests for error boundary functionality in onboarding flow.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import { OnboardingStepErrorBoundary } from '@/components/error-boundaries/OnboardingStepErrorBoundary';
import { withOnboardingErrorBoundary } from '@/components/error-boundaries/withOnboardingErrorBoundary';

// Mock components
const ThrowingComponent = ({ shouldThrow = true }: { shouldThrow?: boolean }) => {
  if (shouldThrow) {
    throw new Error('Test error');
  }
  return <div data-testid="working-component">Component is working</div>;
};

const NetworkErrorComponent = () => {
  throw new Error('Failed to fetch');
};

const AsyncErrorComponent = () => {
  React.useEffect(() => {
    throw new Error('Async error');
  }, []);
  return <div>Loading...</div>;
};

// Test wrapper
const TestWrapper = ({ children }: { children: React.ReactNode }) => (
  <BrowserRouter>{children}</BrowserRouter>
);

describe('OnboardingStepErrorBoundary', () => {
  const mockOnRetry = vi.fn();
  const mockOnGoBack = vi.fn();
  const mockOnGoHome = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    // Mock console to suppress error logs during tests
    vi.spyOn(console, 'error').mockImplementation(() => {});
    vi.spyOn(console, 'warn').mockImplementation(() => {});
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders children when no error occurs', () => {
    render(
      <TestWrapper>
        <OnboardingStepErrorBoundary
          step={1}
          stepName="Welcome"
          onRetry={mockOnRetry}
          onGoBack={mockOnGoBack}
          onGoHome={mockOnGoHome}
        >
          <ThrowingComponent shouldThrow={false} />
        </OnboardingStepErrorBoundary>
      </TestWrapper>
    );

    expect(screen.getByTestId('working-component')).toBeInTheDocument();
  });

  it('displays error UI when component throws', () => {
    render(
      <TestWrapper>
        <OnboardingStepErrorBoundary
          step={2}
          stepName="Sports Selection"
          onRetry={mockOnRetry}
          onGoBack={mockOnGoBack}
          onGoHome={mockOnGoHome}
        >
          <ThrowingComponent />
        </OnboardingStepErrorBoundary>
      </TestWrapper>
    );

    expect(screen.getByText(/Oops! Something went wrong/)).toBeInTheDocument();
    expect(screen.getByText(/We encountered an error on step 2/)).toBeInTheDocument();
    expect(screen.getByText(/Sports Selection/)).toBeInTheDocument();
  });

  it('shows error details when error is provided', () => {
    render(
      <TestWrapper>
        <OnboardingStepErrorBoundary
          step={1}
          stepName="Welcome"
          onRetry={mockOnRetry}
        >
          <ThrowingComponent />
        </OnboardingStepErrorBoundary>
      </TestWrapper>
    );

    expect(screen.getByText(/Error details:/)).toBeInTheDocument();
    expect(screen.getByText(/Test error/)).toBeInTheDocument();
  });

  it('calls onRetry when retry button is clicked', async () => {
    render(
      <TestWrapper>
        <OnboardingStepErrorBoundary
          step={1}
          stepName="Welcome"
          onRetry={mockOnRetry}
        >
          <ThrowingComponent />
        </OnboardingStepErrorBoundary>
      </TestWrapper>
    );

    const retryButton = screen.getByRole('button', { name: /Try Again/ });
    fireEvent.click(retryButton);

    expect(mockOnRetry).toHaveBeenCalledTimes(1);
  });

  it('calls onGoBack when back button is clicked', async () => {
    render(
      <TestWrapper>
        <OnboardingStepErrorBoundary
          step={2}
          stepName="Sports Selection"
          onRetry={mockOnRetry}
          onGoBack={mockOnGoBack}
        >
          <ThrowingComponent />
        </OnboardingStepErrorBoundary>
      </TestWrapper>
    );

    const backButton = screen.getByRole('button', { name: /Go Back/ });
    fireEvent.click(backButton);

    expect(mockOnGoBack).toHaveBeenCalledTimes(1);
  });

  it('calls onGoHome when home button is clicked', async () => {
    render(
      <TestWrapper>
        <OnboardingStepErrorBoundary
          step={1}
          stepName="Welcome"
          onRetry={mockOnRetry}
          onGoHome={mockOnGoHome}
        >
          <ThrowingComponent />
        </OnboardingStepErrorBoundary>
      </TestWrapper>
    );

    const homeButton = screen.getByRole('button', { name: /Go Home/ });
    fireEvent.click(homeButton);

    expect(mockOnGoHome).toHaveBeenCalledTimes(1);
  });

  it('tracks retry attempts and shows count', async () => {
    const { rerender } = render(
      <TestWrapper>
        <OnboardingStepErrorBoundary
          step={1}
          stepName="Welcome"
          onRetry={mockOnRetry}
        >
          <ThrowingComponent />
        </OnboardingStepErrorBoundary>
      </TestWrapper>
    );

    // First retry
    fireEvent.click(screen.getByRole('button', { name: /Try Again/ }));

    // Re-render to simulate error boundary reset and new error
    rerender(
      <TestWrapper>
        <OnboardingStepErrorBoundary
          step={1}
          stepName="Welcome"
          onRetry={mockOnRetry}
        >
          <ThrowingComponent />
        </OnboardingStepErrorBoundary>
      </TestWrapper>
    );

    // Should show retry count in button
    expect(screen.getByText(/Try Again \(1\/3\)/)).toBeInTheDocument();
  });

  it('disables retry button after max retries', async () => {
    // Mock the error boundary to simulate max retries reached
    const { rerender } = render(
      <TestWrapper>
        <OnboardingStepErrorBoundary
          step={1}
          stepName="Welcome"
          onRetry={mockOnRetry}
        >
          <ThrowingComponent />
        </OnboardingStepErrorBoundary>
      </TestWrapper>
    );

    // Simulate multiple retries by re-rendering multiple times
    for (let i = 0; i < 3; i++) {
      if (screen.queryByRole('button', { name: /Try Again/ })) {
        fireEvent.click(screen.getByRole('button', { name: /Try Again/ }));
      }
      rerender(
        <TestWrapper>
          <OnboardingStepErrorBoundary
            step={1}
            stepName="Welcome"
            onRetry={mockOnRetry}
          >
            <ThrowingComponent />
          </OnboardingStepErrorBoundary>
        </TestWrapper>
      );
    }

    // After max retries, should show different message
    expect(screen.getByText(/We've tried several times but the error persists/)).toBeInTheDocument();
  });

  it('handles network errors with auto-retry', async () => {
    vi.useFakeTimers();

    render(
      <TestWrapper>
        <OnboardingStepErrorBoundary
          step={1}
          stepName="Welcome"
          onRetry={mockOnRetry}
        >
          <NetworkErrorComponent />
        </OnboardingStepErrorBoundary>
      </TestWrapper>
    );

    expect(screen.getByText(/Oops! Something went wrong/)).toBeInTheDocument();

    // Fast-forward time to trigger auto-retry
    vi.advanceTimersByTime(2000);

    await waitFor(() => {
      expect(mockOnRetry).toHaveBeenCalled();
    });

    vi.useRealTimers();
  });

  it('stores error details for debugging', () => {
    const originalGetItem = localStorage.getItem;
    const originalSetItem = localStorage.setItem;
    const mockGetItem = vi.fn().mockReturnValue('[]');
    const mockSetItem = vi.fn();

    localStorage.getItem = mockGetItem;
    localStorage.setItem = mockSetItem;

    render(
      <TestWrapper>
        <OnboardingStepErrorBoundary
          step={1}
          stepName="Welcome"
        >
          <ThrowingComponent />
        </OnboardingStepErrorBoundary>
      </TestWrapper>
    );

    expect(mockSetItem).toHaveBeenCalledWith(
      'corner-league-onboarding-errors',
      expect.stringContaining('Test error')
    );

    localStorage.getItem = originalGetItem;
    localStorage.setItem = originalSetItem;
  });
});

describe('withOnboardingErrorBoundary HOC', () => {
  it('wraps component with error boundary', () => {
    const TestComponent = () => <div data-testid="test-component">Test</div>;
    const WrappedComponent = withOnboardingErrorBoundary(TestComponent, {
      step: 1,
      stepName: 'Test Step',
    });

    render(
      <TestWrapper>
        <WrappedComponent />
      </TestWrapper>
    );

    expect(screen.getByTestId('test-component')).toBeInTheDocument();
  });

  it('handles errors in wrapped component', () => {
    const WrappedThrowingComponent = withOnboardingErrorBoundary(ThrowingComponent, {
      step: 1,
      stepName: 'Test Step',
    });

    render(
      <TestWrapper>
        <WrappedThrowingComponent />
      </TestWrapper>
    );

    expect(screen.getByText(/Oops! Something went wrong/)).toBeInTheDocument();
  });

  it('preserves component displayName', () => {
    const TestComponent = () => <div>Test</div>;
    TestComponent.displayName = 'TestComponent';

    const WrappedComponent = withOnboardingErrorBoundary(TestComponent, {
      step: 1,
      stepName: 'Test Step',
    });

    expect(WrappedComponent.displayName).toBe('withOnboardingErrorBoundary(TestComponent)');
  });

  it('configures back button based on step', () => {
    // Step 1 - should not show back button
    const WrappedComponent1 = withOnboardingErrorBoundary(ThrowingComponent, {
      step: 1,
      stepName: 'Welcome',
    });

    const { rerender } = render(
      <TestWrapper>
        <WrappedComponent1 />
      </TestWrapper>
    );

    expect(screen.queryByRole('button', { name: /Go Back/ })).not.toBeInTheDocument();

    // Step 2 - should show back button
    const WrappedComponent2 = withOnboardingErrorBoundary(ThrowingComponent, {
      step: 2,
      stepName: 'Sports Selection',
    });

    rerender(
      <TestWrapper>
        <WrappedComponent2 />
      </TestWrapper>
    );

    expect(screen.getByRole('button', { name: /Go Back/ })).toBeInTheDocument();
  });

  it('handles custom retry logic', () => {
    const mockCustomRetry = vi.fn();
    const WrappedComponent = withOnboardingErrorBoundary(ThrowingComponent, {
      step: 1,
      stepName: 'Test Step',
      retryHandler: mockCustomRetry,
    });

    render(
      <TestWrapper>
        <WrappedComponent />
      </TestWrapper>
    );

    fireEvent.click(screen.getByRole('button', { name: /Try Again/ }));

    expect(mockCustomRetry).toHaveBeenCalledTimes(1);
  });
});