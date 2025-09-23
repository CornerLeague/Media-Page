import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { OnboardingLayout } from "@/pages/onboarding/OnboardingLayout";

// Mock the useNavigate hook
const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useParams: () => ({ step: "2" }),
  };
});

describe("OnboardingLayout Navigation Race Conditions", () => {
  const defaultProps = {
    step: 2,
    totalSteps: 5,
    title: "Test Title",
    subtitle: "Test Subtitle",
  };

  const renderWithRouter = (children: React.ReactNode) => {
    return render(
      <BrowserRouter>
        {children}
      </BrowserRouter>
    );
  };

  beforeEach(() => {
    mockNavigate.mockClear();
  });

  it("prevents multiple rapid navigation calls", async () => {
    renderWithRouter(
      <OnboardingLayout {...defaultProps}>
        <div>Test Content</div>
      </OnboardingLayout>
    );

    const nextButton = screen.getByText("Continue");

    // Rapidly click the button multiple times
    fireEvent.click(nextButton);
    fireEvent.click(nextButton);
    fireEvent.click(nextButton);

    // Should only navigate once despite multiple clicks
    expect(mockNavigate).toHaveBeenCalledTimes(1);
    expect(mockNavigate).toHaveBeenCalledWith("/onboarding/step/3");
  });

  it("disables navigation buttons while navigating", async () => {
    renderWithRouter(
      <OnboardingLayout {...defaultProps}>
        <div>Test Content</div>
      </OnboardingLayout>
    );

    const nextButton = screen.getByText("Continue");
    const backButton = screen.getByText("Back");

    // Click next button
    fireEvent.click(nextButton);

    // Both buttons should be disabled immediately after click
    expect(nextButton).toBeDisabled();
    expect(backButton).toBeDisabled();

    // Wait for navigation timeout to reset (300ms)
    await waitFor(
      () => {
        expect(nextButton).not.toBeDisabled();
        expect(backButton).not.toBeDisabled();
      },
      { timeout: 500 }
    );
  });

  it("respects custom onNext handler and prevents race conditions", async () => {
    const mockOnNext = vi.fn();

    renderWithRouter(
      <OnboardingLayout {...defaultProps} onNext={mockOnNext}>
        <div>Test Content</div>
      </OnboardingLayout>
    );

    const nextButton = screen.getByText("Continue");

    // Rapidly click the button multiple times
    fireEvent.click(nextButton);
    fireEvent.click(nextButton);
    fireEvent.click(nextButton);

    // Custom handler should only be called once
    expect(mockOnNext).toHaveBeenCalledTimes(1);
    // Navigate should not be called when custom handler is provided
    expect(mockNavigate).not.toHaveBeenCalled();
  });

  it("respects custom onBack handler and prevents race conditions", async () => {
    const mockOnBack = vi.fn();

    renderWithRouter(
      <OnboardingLayout {...defaultProps} onBack={mockOnBack}>
        <div>Test Content</div>
      </OnboardingLayout>
    );

    const backButton = screen.getByText("Back");

    // Rapidly click the button multiple times
    fireEvent.click(backButton);
    fireEvent.click(backButton);
    fireEvent.click(backButton);

    // Custom handler should only be called once
    expect(mockOnBack).toHaveBeenCalledTimes(1);
    // Navigate should not be called when custom handler is provided
    expect(mockNavigate).not.toHaveBeenCalled();
  });
});