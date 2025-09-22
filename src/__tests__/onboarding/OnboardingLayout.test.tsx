import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { OnboardingLayout } from "@/pages/onboarding/OnboardingLayout";

// Mock the useNavigate hook
const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useParams: () => ({ step: "1" }),
  };
});

describe("OnboardingLayout", () => {
  const defaultProps = {
    step: 1,
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

  it("renders the basic layout with title and subtitle", () => {
    renderWithRouter(
      <OnboardingLayout {...defaultProps}>
        <div>Test Content</div>
      </OnboardingLayout>
    );

    expect(screen.getByText("Test Title")).toBeInTheDocument();
    expect(screen.getByText("Test Subtitle")).toBeInTheDocument();
    expect(screen.getByText("Test Content")).toBeInTheDocument();
  });

  it("displays correct step information", () => {
    renderWithRouter(
      <OnboardingLayout {...defaultProps}>
        <div>Test Content</div>
      </OnboardingLayout>
    );

    expect(screen.getByText("Step 1 of 5")).toBeInTheDocument();
    expect(screen.getByText("20% complete")).toBeInTheDocument();
  });

  it("displays progress bar with correct value", () => {
    renderWithRouter(
      <OnboardingLayout {...defaultProps}>
        <div>Test Content</div>
      </OnboardingLayout>
    );

    const progressBar = screen.getByRole("progressbar");
    expect(progressBar).toHaveAttribute("data-value", "20");
  });

  it("shows continue button when not on last step", () => {
    renderWithRouter(
      <OnboardingLayout {...defaultProps}>
        <div>Test Content</div>
      </OnboardingLayout>
    );

    expect(screen.getByText("Continue")).toBeInTheDocument();
  });

  it("shows back button when not on first step", () => {
    renderWithRouter(
      <OnboardingLayout {...defaultProps} step={2}>
        <div>Test Content</div>
      </OnboardingLayout>
    );

    expect(screen.getByText("Back")).toBeInTheDocument();
  });

  it("does not show back button on first step", () => {
    renderWithRouter(
      <OnboardingLayout {...defaultProps} step={1}>
        <div>Test Content</div>
      </OnboardingLayout>
    );

    expect(screen.queryByText("Back")).not.toBeInTheDocument();
  });

  it("disables continue button when isNextDisabled is true", () => {
    renderWithRouter(
      <OnboardingLayout {...defaultProps} isNextDisabled={true}>
        <div>Test Content</div>
      </OnboardingLayout>
    );

    const continueButton = screen.getByText("Continue");
    expect(continueButton).toBeDisabled();
  });
});