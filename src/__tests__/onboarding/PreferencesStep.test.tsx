/**
 * Tests for PreferencesStep component
 * Tests user preference configuration for news types, notifications, content frequency
 */

import { screen, fireEvent, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';
import { renderWithProviders } from '@/test-setup';
import { PreferencesStep } from '@/pages/onboarding/PreferencesStep';

// Mock the navigation
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useParams: () => ({ step: '4' }),
  };
});

// Mock API client
const mockUpdateOnboardingStep = vi.fn();

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    updateOnboardingStep: mockUpdateOnboardingStep,
  },
}));

// Mock React Query
const mockUseMutation = vi.fn();

vi.mock('@tanstack/react-query', async () => {
  const actual = await vi.importActual('@tanstack/react-query');
  return {
    ...actual,
    useMutation: mockUseMutation,
  };
});

describe('PreferencesStep', () => {
  const user = userEvent.setup();

  beforeEach(() => {
    mockNavigate.mockClear();
    mockUpdateOnboardingStep.mockClear();
    vi.clearAllMocks();

    mockUseMutation.mockReturnValue({
      mutate: mockUpdateOnboardingStep,
      isLoading: false,
      error: null,
      isError: false,
    });
  });

  it('renders preferences configuration interface', () => {
    renderWithProviders(<PreferencesStep />);

    expect(screen.getByText('Step 4 of 5')).toBeInTheDocument();
    expect(screen.getByText(/preferences/i)).toBeInTheDocument();
    expect(screen.getByText(/customize.*experience/i)).toBeInTheDocument();
  });

  it('displays news type preferences section', () => {
    renderWithProviders(<PreferencesStep />);

    expect(screen.getByText(/news.*types/i)).toBeInTheDocument();

    // Check default news types
    expect(screen.getByLabelText(/injuries/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/trades/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/roster.*changes/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/game.*results/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/analysis/i)).toBeInTheDocument();
  });

  it('displays notification preferences section', () => {
    renderWithProviders(<PreferencesStep />);

    expect(screen.getByText(/notifications/i)).toBeInTheDocument();

    // Check notification options
    expect(screen.getByLabelText(/push.*notifications/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/email.*notifications/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/game.*reminders/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/news.*alerts/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/score.*updates/i)).toBeInTheDocument();
  });

  it('displays content frequency preferences', () => {
    renderWithProviders(<PreferencesStep />);

    expect(screen.getByText(/content.*frequency/i)).toBeInTheDocument();

    // Check frequency options
    expect(screen.getByLabelText(/minimal/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/standard/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/comprehensive/i)).toBeInTheDocument();
  });

  it('allows toggling news type preferences', async () => {
    renderWithProviders(<PreferencesStep />);

    const injuriesToggle = screen.getByLabelText(/injuries/i);
    const tradesToggle = screen.getByLabelText(/trades/i);

    // Initially, some may be checked by default
    const initialInjuriesState = injuriesToggle.checked;
    const initialTradesState = tradesToggle.checked;

    // Toggle injuries preference
    await user.click(injuriesToggle);
    expect(injuriesToggle.checked).toBe(!initialInjuriesState);

    // Toggle trades preference
    await user.click(tradesToggle);
    expect(tradesToggle.checked).toBe(!initialTradesState);
  });

  it('allows setting priority for enabled news types', async () => {
    renderWithProviders(<PreferencesStep />);

    // Enable injuries news type
    const injuriesToggle = screen.getByLabelText(/injuries/i);
    if (!injuriesToggle.checked) {
      await user.click(injuriesToggle);
    }

    // Priority slider should appear
    const prioritySlider = screen.getByTestId('priority-slider-injuries');
    expect(prioritySlider).toBeInTheDocument();
    expect(prioritySlider).toHaveAttribute('min', '1');
    expect(prioritySlider).toHaveAttribute('max', '5');

    // Change priority
    fireEvent.change(prioritySlider, { target: { value: '4' } });
    expect(prioritySlider).toHaveValue('4');
  });

  it('hides priority slider for disabled news types', async () => {
    renderWithProviders(<PreferencesStep />);

    const injuriesToggle = screen.getByLabelText(/injuries/i);

    // Ensure toggle is unchecked
    if (injuriesToggle.checked) {
      await user.click(injuriesToggle);
    }

    // Priority slider should not be visible
    expect(screen.queryByTestId('priority-slider-injuries')).not.toBeInTheDocument();
  });

  it('allows toggling notification preferences', async () => {
    renderWithProviders(<PreferencesStep />);

    const pushToggle = screen.getByLabelText(/push.*notifications/i);
    const emailToggle = screen.getByLabelText(/email.*notifications/i);

    // Toggle push notifications
    const initialPushState = pushToggle.checked;
    await user.click(pushToggle);
    expect(pushToggle.checked).toBe(!initialPushState);

    // Toggle email notifications
    const initialEmailState = emailToggle.checked;
    await user.click(emailToggle);
    expect(emailToggle.checked).toBe(!initialEmailState);
  });

  it('allows selecting content frequency', async () => {
    renderWithProviders(<PreferencesStep />);

    const minimalRadio = screen.getByLabelText(/minimal/i);
    const standardRadio = screen.getByLabelText(/standard/i);
    const comprehensiveRadio = screen.getByLabelText(/comprehensive/i);

    // Select minimal
    await user.click(minimalRadio);
    expect(minimalRadio).toBeChecked();
    expect(standardRadio).not.toBeChecked();
    expect(comprehensiveRadio).not.toBeChecked();

    // Select comprehensive
    await user.click(comprehensiveRadio);
    expect(comprehensiveRadio).toBeChecked();
    expect(minimalRadio).not.toBeChecked();
    expect(standardRadio).not.toBeChecked();
  });

  it('shows description for each content frequency option', () => {
    renderWithProviders(<PreferencesStep />);

    expect(screen.getByText(/essential.*updates.*only/i)).toBeInTheDocument();
    expect(screen.getByText(/balanced.*mix.*content/i)).toBeInTheDocument();
    expect(screen.getByText(/detailed.*coverage.*analysis/i)).toBeInTheDocument();
  });

  it('enables continue button when preferences are set', async () => {
    renderWithProviders(<PreferencesStep />);

    // Initial state - button should be enabled (has defaults)
    const continueButton = screen.getByRole('button', { name: /continue/i });
    expect(continueButton).not.toBeDisabled();

    // Change some preferences
    await user.click(screen.getByLabelText(/injuries/i));
    await user.click(screen.getByLabelText(/push.*notifications/i));
    await user.click(screen.getByLabelText(/standard/i));

    expect(continueButton).not.toBeDisabled();
  });

  it('saves preferences and navigates to next step', async () => {
    mockUpdateOnboardingStep.mockResolvedValue({ currentStep: 5 });

    renderWithProviders(<PreferencesStep />);

    // Set specific preferences
    await user.click(screen.getByLabelText(/injuries/i));
    await user.click(screen.getByLabelText(/trades/i));
    await user.click(screen.getByLabelText(/push.*notifications/i));
    await user.click(screen.getByLabelText(/game.*reminders/i));
    await user.click(screen.getByLabelText(/standard/i));

    // Click continue
    const continueButton = screen.getByRole('button', { name: /continue/i });
    await user.click(continueButton);

    await waitFor(() => {
      expect(mockUpdateOnboardingStep).toHaveBeenCalledWith({
        step: 5,
        data: {
          preferences: expect.objectContaining({
            newsTypes: expect.any(Array),
            notifications: expect.any(Object),
            contentFrequency: 'standard',
          }),
        },
      });
      expect(mockNavigate).toHaveBeenCalledWith('/onboarding/step/5');
    });
  });

  it('handles API error during save', async () => {
    mockUpdateOnboardingStep.mockRejectedValue(new Error('API Error'));

    renderWithProviders(<PreferencesStep />);

    // Click continue
    const continueButton = screen.getByRole('button', { name: /continue/i });
    await user.click(continueButton);

    await waitFor(() => {
      expect(screen.getByText(/error.*saving/i)).toBeInTheDocument();
    });
  });

  it('shows loading state during save', async () => {
    // Mock delayed response
    mockUpdateOnboardingStep.mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve({ currentStep: 5 }), 100))
    );

    mockUseMutation.mockReturnValue({
      mutate: mockUpdateOnboardingStep,
      isLoading: true,
      error: null,
      isError: false,
    });

    renderWithProviders(<PreferencesStep />);

    const continueButton = screen.getByRole('button', { name: /continue/i });

    expect(continueButton).toBeDisabled();
    expect(screen.getByText(/saving/i)).toBeInTheDocument();
  });

  it('shows preview of selected preferences', async () => {
    renderWithProviders(<PreferencesStep />);

    // Enable specific news types
    await user.click(screen.getByLabelText(/injuries/i));
    await user.click(screen.getByLabelText(/trades/i));

    // Enable notifications
    await user.click(screen.getByLabelText(/push.*notifications/i));

    // Select frequency
    await user.click(screen.getByLabelText(/comprehensive/i));

    // Check preview section
    const previewSection = screen.getByTestId('preferences-preview');
    expect(within(previewSection).getByText(/injuries/i)).toBeInTheDocument();
    expect(within(previewSection).getByText(/trades/i)).toBeInTheDocument();
    expect(within(previewSection).getByText(/push.*notifications/i)).toBeInTheDocument();
    expect(within(previewSection).getByText(/comprehensive/i)).toBeInTheDocument();
  });

  it('provides reset to defaults functionality', async () => {
    renderWithProviders(<PreferencesStep />);

    // Change some preferences from defaults
    await user.click(screen.getByLabelText(/injuries/i));
    await user.click(screen.getByLabelText(/comprehensive/i));

    // Click reset button
    const resetButton = screen.getByRole('button', { name: /reset.*defaults/i });
    await user.click(resetButton);

    // Should restore default values
    const standardRadio = screen.getByLabelText(/standard/i);
    expect(standardRadio).toBeChecked();
  });

  it('shows back button and handles back navigation', async () => {
    renderWithProviders(<PreferencesStep />);

    const backButton = screen.getByRole('button', { name: /back/i });
    expect(backButton).toBeInTheDocument();

    await user.click(backButton);
    expect(mockNavigate).toHaveBeenCalledWith('/onboarding/step/3');
  });

  it('has proper accessibility attributes', async () => {
    renderWithProviders(<PreferencesStep />);

    // Check form structure
    const form = screen.getByRole('form');
    expect(form).toBeInTheDocument();

    // Check fieldsets for grouped options
    const newsFieldset = screen.getByRole('group', { name: /news.*types/i });
    const notificationsFieldset = screen.getByRole('group', { name: /notifications/i });
    const frequencyFieldset = screen.getByRole('group', { name: /content.*frequency/i });

    expect(newsFieldset).toBeInTheDocument();
    expect(notificationsFieldset).toBeInTheDocument();
    expect(frequencyFieldset).toBeInTheDocument();

    // Check checkbox accessibility
    const injuriesToggle = screen.getByLabelText(/injuries/i);
    expect(injuriesToggle).toHaveAttribute('type', 'checkbox');
    expect(injuriesToggle).toHaveAttribute('aria-describedby');

    // Check radio button accessibility
    const standardRadio = screen.getByLabelText(/standard/i);
    expect(standardRadio).toHaveAttribute('type', 'radio');
    expect(standardRadio).toHaveAttribute('name', 'contentFrequency');
  });

  it('supports keyboard navigation', async () => {
    renderWithProviders(<PreferencesStep />);

    const injuriesToggle = screen.getByLabelText(/injuries/i);
    const pushToggle = screen.getByLabelText(/push.*notifications/i);

    // Tab navigation
    injuriesToggle.focus();
    expect(injuriesToggle).toHaveFocus();

    // Space to toggle
    await user.keyboard(' ');
    expect(injuriesToggle.checked).toBe(true);

    // Tab to next control
    await user.keyboard('{Tab}');
    // Focus should move to next control in tab order
  });

  it('validates that at least one news type is selected', async () => {
    renderWithProviders(<PreferencesStep />);

    // Uncheck all news types
    const newsTypeCheckboxes = screen.getAllByRole('checkbox', { name: /injuries|trades|roster|game|analysis/i });

    for (const checkbox of newsTypeCheckboxes) {
      if (checkbox.checked) {
        await user.click(checkbox);
      }
    }

    // Click continue
    const continueButton = screen.getByRole('button', { name: /continue/i });
    await user.click(continueButton);

    // Should show validation error
    expect(screen.getByText(/select.*least.*one.*news.*type/i)).toBeInTheDocument();
  });

  it('provides helpful tooltips for preference options', async () => {
    renderWithProviders(<PreferencesStep />);

    // Hover over a preference option
    const injuriesLabel = screen.getByLabelText(/injuries/i);
    await user.hover(injuriesLabel);

    await waitFor(() => {
      expect(screen.getByText(/injury.*reports.*updates/i)).toBeInTheDocument();
    });
  });

  it('persists form state during component re-renders', async () => {
    const { rerender } = renderWithProviders(<PreferencesStep />);

    // Make some selections
    await user.click(screen.getByLabelText(/injuries/i));
    await user.click(screen.getByLabelText(/comprehensive/i));

    // Rerender component
    rerender(<PreferencesStep />);

    // Selections should persist
    expect(screen.getByLabelText(/injuries/i)).toBeChecked();
    expect(screen.getByLabelText(/comprehensive/i)).toBeChecked();
  });

  it('displays progress bar with correct value', () => {
    renderWithProviders(<PreferencesStep />);

    const progressBar = screen.getByRole('progressbar');
    expect(progressBar).toHaveAttribute('aria-valuenow', '80');
    expect(screen.getByText('80% complete')).toBeInTheDocument();
  });

  it('handles form submission via Enter key', async () => {
    mockUpdateOnboardingStep.mockResolvedValue({ currentStep: 5 });

    renderWithProviders(<PreferencesStep />);

    // Focus on form and press Enter
    const form = screen.getByRole('form');
    form.focus();
    await user.keyboard('{Enter}');

    await waitFor(() => {
      expect(mockUpdateOnboardingStep).toHaveBeenCalled();
    });
  });
});