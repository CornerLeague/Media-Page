/**
 * Basic Reset Onboarding Flow Test
 *
 * Simple test suite for the reset onboarding functionality focusing on
 * component rendering and basic interactions.
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { ResetOnboardingDialog } from '@/components/preferences/ResetOnboardingDialog';

// Mock the useResetOnboarding hook
const mockResetOnboarding = vi.fn();
const mockUseResetOnboarding = {
  resetOnboarding: mockResetOnboarding,
  isResetting: false,
  error: null,
  reset: vi.fn(),
};

vi.mock('@/hooks/useResetOnboarding', () => ({
  useResetOnboarding: () => mockUseResetOnboarding,
}));

describe('ResetOnboardingDialog', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseResetOnboarding.isResetting = false;
    mockUseResetOnboarding.error = null;
  });

  it('renders trigger button and opens dialog when clicked', async () => {
    render(
      <ResetOnboardingDialog>
        <button>Reset Onboarding</button>
      </ResetOnboardingDialog>
    );

    const triggerButton = screen.getByText('Reset Onboarding');
    expect(triggerButton).toBeInTheDocument();

    fireEvent.click(triggerButton);

    await waitFor(() => {
      expect(screen.getByText('Reset Onboarding?')).toBeInTheDocument();
    });

    expect(screen.getByText(/This action will permanently delete/)).toBeInTheDocument();
    expect(screen.getByText(/Selected sports and their rankings/)).toBeInTheDocument();
    expect(screen.getByText(/Favorite teams and affinity scores/)).toBeInTheDocument();
    expect(screen.getByText(/Content preferences and notification settings/)).toBeInTheDocument();
  });

  it('cancels reset when cancel button is clicked', async () => {
    render(
      <ResetOnboardingDialog>
        <button>Reset Onboarding</button>
      </ResetOnboardingDialog>
    );

    fireEvent.click(screen.getByText('Reset Onboarding'));

    await waitFor(() => {
      expect(screen.getByText('Reset Onboarding?')).toBeInTheDocument();
    });

    const cancelButton = screen.getByText('Cancel');
    fireEvent.click(cancelButton);

    await waitFor(() => {
      expect(screen.queryByText('Reset Onboarding?')).not.toBeInTheDocument();
    });

    expect(mockResetOnboarding).not.toHaveBeenCalled();
  });

  it('calls reset function when confirmed', async () => {
    mockResetOnboarding.mockResolvedValue();

    render(
      <ResetOnboardingDialog>
        <button>Reset Onboarding</button>
      </ResetOnboardingDialog>
    );

    fireEvent.click(screen.getByText('Reset Onboarding'));

    await waitFor(() => {
      expect(screen.getByText('Reset Onboarding?')).toBeInTheDocument();
    });

    const confirmButton = screen.getByRole('button', { name: /Reset Onboarding/ });
    fireEvent.click(confirmButton);

    await waitFor(() => {
      expect(mockResetOnboarding).toHaveBeenCalledOnce();
    });
  });

  it('shows loading state during reset operation', async () => {
    mockUseResetOnboarding.isResetting = true;

    render(
      <ResetOnboardingDialog>
        <button>Reset Onboarding</button>
      </ResetOnboardingDialog>
    );

    fireEvent.click(screen.getByText('Reset Onboarding'));

    await waitFor(() => {
      expect(screen.getByText('Reset Onboarding?')).toBeInTheDocument();
    });

    expect(screen.getByText('Resetting...')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Cancel/ })).toBeDisabled();
  });

  it('displays proper warning message and destructive styling', async () => {
    render(
      <ResetOnboardingDialog>
        <button>Reset Onboarding</button>
      </ResetOnboardingDialog>
    );

    fireEvent.click(screen.getByText('Reset Onboarding'));

    await waitFor(() => {
      expect(screen.getByText('Reset Onboarding?')).toBeInTheDocument();
    });

    // Check for warning content
    expect(screen.getByText(/permanently delete all your current preferences/)).toBeInTheDocument();
    expect(screen.getByText(/You will be redirected to the onboarding flow/)).toBeInTheDocument();

    // Check for destructive button styling
    const confirmButton = screen.getByRole('button', { name: /Reset Onboarding/ });
    expect(confirmButton).toHaveClass('bg-destructive');
  });
});