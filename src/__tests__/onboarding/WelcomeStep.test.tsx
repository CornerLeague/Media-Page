/**
 * Tests for WelcomeStep component
 */

import { screen, fireEvent, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import { renderWithProviders } from '@/test-setup';
import { WelcomeStep } from '@/pages/onboarding/WelcomeStep';

// Mock the navigation
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useParams: () => ({ step: '1' }),
  };
});

// Mock the API client
vi.mock('@/lib/api-client', () => ({
  apiClient: {
    updateOnboardingStep: vi.fn().mockResolvedValue({ currentStep: 2 }),
  },
}));

describe('WelcomeStep', () => {
  beforeEach(() => {
    mockNavigate.mockClear();
    vi.clearAllMocks();
  });

  it('renders welcome content', () => {
    renderWithProviders(<WelcomeStep />);

    expect(screen.getByText(/welcome/i)).toBeInTheDocument();
    // Use more specific selector for button
    expect(screen.getByRole('button', { name: /get started/i })).toBeInTheDocument();
  });

  it('shows onboarding layout with correct step', () => {
    renderWithProviders(<WelcomeStep />);

    expect(screen.getByText('Step 1 of 5')).toBeInTheDocument();
    expect(screen.getByText('20% complete')).toBeInTheDocument();
  });

  it('displays continue button', () => {
    renderWithProviders(<WelcomeStep />);

    const continueButton = screen.getByRole('button', { name: /continue|get started/i });
    expect(continueButton).toBeInTheDocument();
    expect(continueButton).not.toBeDisabled();
  });

  it('does not show back button on first step', () => {
    renderWithProviders(<WelcomeStep />);

    expect(screen.queryByRole('button', { name: /back/i })).not.toBeInTheDocument();
  });

  it('navigates to next step when continue is clicked', async () => {
    renderWithProviders(<WelcomeStep />);

    const continueButton = screen.getByRole('button', { name: /continue|get started/i });
    fireEvent.click(continueButton);

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/onboarding/step/2');
    });
  });

  it('has accessible structure', async () => {
    const { container } = renderWithProviders(<WelcomeStep />);

    // Check for heading structure
    const headings = screen.getAllByRole('heading');
    expect(headings.length).toBeGreaterThan(0);

    // Check progress bar accessibility
    const progressbar = screen.getByRole('progressbar');
    expect(progressbar).toHaveAttribute('aria-valuemin', '0');
    expect(progressbar).toHaveAttribute('aria-valuemax', '100');
    expect(progressbar).toHaveAttribute('aria-valuenow', '20');
  });

  it('renders without crashing on different screen sizes', () => {
    // Test mobile viewport
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 375,
    });
    window.dispatchEvent(new Event('resize'));

    renderWithProviders(<WelcomeStep />);
    expect(screen.getByText(/welcome/i)).toBeInTheDocument();

    // Test desktop viewport
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 1920,
    });
    window.dispatchEvent(new Event('resize'));

    expect(screen.getByText(/welcome/i)).toBeInTheDocument();
  });

  it('handles keyboard navigation', async () => {
    renderWithProviders(<WelcomeStep />);

    const continueButton = screen.getByRole('button', { name: /continue|get started/i });

    // Tab to the button
    continueButton.focus();
    expect(continueButton).toHaveFocus();

    // Press Enter
    fireEvent.keyDown(continueButton, { key: 'Enter', code: 'Enter' });

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/onboarding/step/2');
    });
  });

  it('displays proper loading state during navigation', async () => {
    // Mock a delayed navigation
    mockNavigate.mockImplementation(() =>
      new Promise(resolve => setTimeout(resolve, 100))
    );

    renderWithProviders(<WelcomeStep />);

    const continueButton = screen.getByRole('button', { name: /continue|get started/i });
    fireEvent.click(continueButton);

    // Button should be disabled during navigation
    expect(continueButton).toBeDisabled();

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalled();
    });
  });
});