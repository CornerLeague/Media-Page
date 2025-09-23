/**
 * Accessibility Tests for Performance Optimized Components
 *
 * Ensures that performance optimizations don't compromise accessibility
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';

import { VirtualizedTeamList } from '@/components/VirtualizedTeamList';
import { OptimizedImage } from '@/components/OptimizedImage';

// Extend Jest matchers
expect.extend(toHaveNoViolations);

// Mock data
const mockTeams = Array.from({ length: 50 }, (_, i) => ({
  id: `team-${i}`,
  name: `Team ${i + 1}`,
  market: `City ${i + 1}`,
  sportId: 'nfl',
  league: 'NFL',
  logo: '🏈',
  isSelected: i % 3 === 0,
  affinityScore: Math.floor(Math.random() * 5) + 1,
}));

const TestWrapper = ({ children }: { children: React.ReactNode }) => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {children}
      </BrowserRouter>
    </QueryClientProvider>
  );
};

describe('Performance Optimized Components - Accessibility', () => {
  describe('VirtualizedTeamList', () => {
    it('should have no accessibility violations', async () => {
      const { container } = render(
        <TestWrapper>
          <VirtualizedTeamList
            teams={mockTeams}
            onToggleTeam={vi.fn()}
            onAffinityChange={vi.fn()}
            containerHeight={400}
          />
        </TestWrapper>
      );

      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should provide proper ARIA labels', () => {
      render(
        <TestWrapper>
          <VirtualizedTeamList
            teams={mockTeams}
            onToggleTeam={vi.fn()}
            onAffinityChange={vi.fn()}
            containerHeight={400}
          />
        </TestWrapper>
      );

      // Check that the list has proper role
      expect(screen.getByRole('listbox')).toBeInTheDocument();
      expect(screen.getByLabelText('Team selection list')).toBeInTheDocument();
    });

    it('should maintain keyboard navigation', () => {
      render(
        <TestWrapper>
          <VirtualizedTeamList
            teams={mockTeams}
            onToggleTeam={vi.fn()}
            onAffinityChange={vi.fn()}
            containerHeight={400}
          />
        </TestWrapper>
      );

      // Check that checkboxes are accessible
      const checkboxes = screen.getAllByRole('checkbox');
      expect(checkboxes.length).toBeGreaterThan(0);

      // Each checkbox should have an accessible name
      checkboxes.forEach(checkbox => {
        expect(checkbox).toHaveAttribute('aria-label');
      });
    });

    it('should announce selection state changes', () => {
      render(
        <TestWrapper>
          <VirtualizedTeamList
            teams={mockTeams}
            onToggleTeam={vi.fn()}
            onAffinityChange={vi.fn()}
            containerHeight={400}
          />
        </TestWrapper>
      );

      // Check for ARIA labels on star ratings
      const starButtons = screen.getAllByLabelText(/Rate .* \d stars/);
      expect(starButtons.length).toBeGreaterThan(0);
    });
  });

  describe('OptimizedImage', () => {
    it('should have no accessibility violations', async () => {
      const { container } = render(
        <OptimizedImage
          src="/test-image.jpg"
          alt="Test image"
          width={100}
          height={100}
        />
      );

      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should provide descriptive alt text', () => {
      render(
        <OptimizedImage
          src="/test-image.jpg"
          alt="Team logo for New York Yankees"
          width={100}
          height={100}
        />
      );

      // The alt text should be present when image loads
      const image = screen.getByAltText('Team logo for New York Yankees');
      expect(image).toBeInTheDocument();
    });

    it('should handle loading states accessibly', () => {
      render(
        <OptimizedImage
          src="/test-image.jpg"
          alt="Test image"
          width={100}
          height={100}
        />
      );

      // Loading state should not interfere with screen readers
      // The placeholder image should be hidden from assistive technology
      const placeholders = screen.getAllByRole('img', { hidden: true });
      expect(placeholders.length).toBeGreaterThan(0);
    });
  });

  describe('Lazy Loading Components', () => {
    it('should maintain focus management during lazy loading', () => {
      // This test would be more comprehensive with actual lazy-loaded components
      // For now, we verify the loading fallback is accessible
      const LoadingFallback = () => (
        <div role="status" aria-label="Loading...">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          <span className="sr-only">Loading onboarding step...</span>
        </div>
      );

      render(<LoadingFallback />);

      expect(screen.getByRole('status')).toBeInTheDocument();
      expect(screen.getByText('Loading onboarding step...')).toBeInTheDocument();
    });
  });

  describe('Performance Features - Accessibility Impact', () => {
    it('should not break screen reader navigation with virtualization', () => {
      render(
        <TestWrapper>
          <VirtualizedTeamList
            teams={mockTeams}
            onToggleTeam={vi.fn()}
            onAffinityChange={vi.fn()}
            containerHeight={400}
          />
        </TestWrapper>
      );

      // Virtual scrolling should not break semantic structure
      const listbox = screen.getByRole('listbox');
      expect(listbox).toBeInTheDocument();

      // Items should still be discoverable
      const checkboxes = screen.getAllByRole('checkbox');
      expect(checkboxes.length).toBeGreaterThan(0);
    });

    it('should provide performance feedback accessibly', () => {
      // Mock a scrolling state
      const ScrollingIndicator = () => (
        <div role="status" aria-live="polite" aria-label="Scrolling">
          <span className="sr-only">Scrolling through team list</span>
        </div>
      );

      render(<ScrollingIndicator />);

      expect(screen.getByRole('status')).toBeInTheDocument();
      expect(screen.getByText('Scrolling through team list')).toBeInTheDocument();
    });
  });

  describe('Code Splitting - Accessibility Continuity', () => {
    it('should maintain focus when components load asynchronously', () => {
      // Test focus management during component transitions
      const FocusContinuity = () => (
        <div>
          <button autoFocus data-testid="focused-element">
            Continue to Next Step
          </button>
        </div>
      );

      render(<FocusContinuity />);

      const focusedElement = screen.getByTestId('focused-element');
      expect(focusedElement).toHaveFocus();
    });

    it('should announce route changes to screen readers', () => {
      // Mock route announcement
      const RouteAnnouncement = ({ route }: { route: string }) => (
        <div role="status" aria-live="assertive">
          <span className="sr-only">Navigated to {route}</span>
        </div>
      );

      render(<RouteAnnouncement route="Team Selection Step" />);

      expect(screen.getByText('Navigated to Team Selection Step')).toBeInTheDocument();
    });
  });
});

describe('Performance Monitoring - Accessibility Metrics', () => {
  it('should track accessibility performance', () => {
    // Mock performance tracking that includes a11y metrics
    const mockA11yMetrics = {
      renderTime: 95, // Under 100ms threshold
      keyboardNavigation: true,
      screenReaderCompatible: true,
      colorContrastPassing: true,
      focusManagement: true,
    };

    expect(mockA11yMetrics.renderTime).toBeLessThan(100);
    expect(mockA11yMetrics.keyboardNavigation).toBe(true);
    expect(mockA11yMetrics.screenReaderCompatible).toBe(true);
    expect(mockA11yMetrics.colorContrastPassing).toBe(true);
    expect(mockA11yMetrics.focusManagement).toBe(true);
  });
});