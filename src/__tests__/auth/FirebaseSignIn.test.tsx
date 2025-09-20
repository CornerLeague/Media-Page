/**
 * FirebaseSignIn Component Tests
 *
 * Tests for proper selector specificity to avoid Strict Mode violations.
 * This test file demonstrates how to fix ambiguous selectors that match
 * multiple elements by using more specific selector strategies.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import { vi } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from '@/components/ThemeProvider';

import { FirebaseSignIn } from '@/components/auth/FirebaseSignIn';

// Mock Firebase auth context
const mockSignInWithGoogle = vi.fn();
const mockSignInWithEmail = vi.fn();
const mockCreateAccountWithEmail = vi.fn();

vi.mock('@/contexts/FirebaseAuthContext', () => ({
  useFirebaseAuth: () => ({
    signInWithGoogle: mockSignInWithGoogle,
    signInWithEmail: mockSignInWithEmail,
    createAccountWithEmail: mockCreateAccountWithEmail,
    user: null,
    isLoading: false,
    isAuthenticated: false,
  }),
}));

// Mock PasswordReset component
vi.mock('@/components/auth/PasswordReset', () => ({
  PasswordReset: ({ onBackToSignIn }: { onBackToSignIn: () => void }) => (
    <div>
      <h2>Reset Password</h2>
      <button onClick={onBackToSignIn}>Back to Sign In</button>
    </div>
  ),
}));

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider defaultTheme="light" storageKey="test-theme">
        {children}
      </ThemeProvider>
    </QueryClientProvider>
  );
};

describe('FirebaseSignIn - Strict Mode Selector Fixes', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Sign In Mode (default)', () => {
    it('should distinguish between heading and button with same text', async () => {
      render(
        <TestWrapper>
          <FirebaseSignIn />
        </TestWrapper>
      );

      // PROBLEM: getByText('Sign In') would match multiple elements
      // SOLUTION: Use getByRole with specific roles and names

      // Check heading specifically
      expect(screen.getByRole('heading', { name: 'Sign In' })).toBeInTheDocument();

      // Check submit button specifically
      expect(screen.getByRole('button', { name: 'Sign In' })).toBeInTheDocument();

      // Check toggle link button specifically (note the lowercase 'in')
      expect(screen.getByRole('button', { name: 'Sign up' })).toBeInTheDocument();

      // Verify Google sign-in button
      expect(screen.getByRole('button', { name: /continue with google/i })).toBeInTheDocument();
    });

    it('should handle form submission with specific button selector', async () => {
      const user = userEvent.setup();
      mockSignInWithEmail.mockResolvedValueOnce(undefined);

      render(
        <TestWrapper>
          <FirebaseSignIn />
        </TestWrapper>
      );

      // Fill form fields
      await user.type(screen.getByPlaceholderText('Email address'), 'test@example.com');
      await user.type(screen.getByPlaceholderText('Password'), 'password123');

      // Use specific button selector instead of ambiguous text
      await user.click(screen.getByRole('button', { name: 'Sign In' }));

      await waitFor(() => {
        expect(mockSignInWithEmail).toHaveBeenCalledWith('test@example.com', 'password123');
      });
    });

    it('should toggle to sign up mode with specific link selector', async () => {
      const user = userEvent.setup();

      render(
        <TestWrapper>
          <FirebaseSignIn />
        </TestWrapper>
      );

      // Use specific role and name instead of ambiguous text
      await user.click(screen.getByRole('button', { name: 'Sign up' }));

      // After clicking, verify mode changed
      expect(screen.getByRole('heading', { name: 'Create Account' })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Create Account' })).toBeInTheDocument();
    });
  });

  describe('Sign Up Mode', () => {
    it('should distinguish between heading and button in sign up mode', async () => {
      const user = userEvent.setup();

      render(
        <TestWrapper>
          <FirebaseSignIn />
        </TestWrapper>
      );

      // Switch to sign up mode first
      await user.click(screen.getByRole('button', { name: 'Sign up' }));

      // PROBLEM: getByText('Create Account') would match multiple elements
      // SOLUTION: Use getByRole with specific roles

      // Check heading specifically
      expect(screen.getByRole('heading', { name: 'Create Account' })).toBeInTheDocument();

      // Check submit button specifically
      expect(screen.getByRole('button', { name: 'Create Account' })).toBeInTheDocument();

      // Check toggle link button specifically
      expect(screen.getByRole('button', { name: 'Sign in' })).toBeInTheDocument();
    });

    it('should handle account creation with specific selectors', async () => {
      const user = userEvent.setup();
      mockCreateAccountWithEmail.mockResolvedValueOnce(undefined);

      render(
        <TestWrapper>
          <FirebaseSignIn />
        </TestWrapper>
      );

      // Switch to sign up mode
      await user.click(screen.getByRole('button', { name: 'Sign up' }));

      // Fill form fields
      await user.type(screen.getByPlaceholderText('Email address'), 'test@example.com');
      await user.type(screen.getByPlaceholderText('Password'), 'password123');
      await user.type(screen.getByPlaceholderText('Confirm password'), 'password123');

      // Use specific button selector
      await user.click(screen.getByRole('button', { name: 'Create Account' }));

      await waitFor(() => {
        expect(mockCreateAccountWithEmail).toHaveBeenCalledWith('test@example.com', 'password123');
      });
    });
  });

  describe('Alternative Selector Strategies', () => {
    it('should use form context for submit buttons when available', async () => {
      render(
        <TestWrapper>
          <FirebaseSignIn />
        </TestWrapper>
      );

      // Alternative: Use button type and context
      const submitButton = screen.getByRole('button', { name: 'Sign In' });
      expect(submitButton).toHaveAttribute('type', 'submit');
    });

    it('should use data-testid for reliable element targeting', async () => {
      render(
        <TestWrapper>
          <FirebaseSignIn />
        </TestWrapper>
      );

      // Using data-testid attributes for more reliable selection
      expect(screen.getByTestId('auth-form-title')).toHaveTextContent('Sign In');
      expect(screen.getByTestId('sign-in-submit')).toBeInTheDocument();
      expect(screen.getByTestId('auth-mode-toggle')).toHaveTextContent('Sign up');
      expect(screen.getByTestId('google-signin-button')).toBeInTheDocument();
    });

    it('should use within() for scoped queries', async () => {
      render(
        <TestWrapper>
          <FirebaseSignIn />
        </TestWrapper>
      );

      // Query within specific form context
      const form = screen.getByTestId('email-auth-form');
      expect(within(form).getByRole('button', { name: 'Sign In' })).toBeInTheDocument();
    });

    it('should handle Google sign in with distinctive text', async () => {
      const user = userEvent.setup();
      mockSignInWithGoogle.mockResolvedValueOnce(undefined);

      render(
        <TestWrapper>
          <FirebaseSignIn />
        </TestWrapper>
      );

      // This button has unique text, so it's safe to use
      await user.click(screen.getByRole('button', { name: /continue with google/i }));

      await waitFor(() => {
        expect(mockSignInWithGoogle).toHaveBeenCalled();
      });
    });
  });

  describe('Accessibility and Error States', () => {
    it('should maintain accessibility while using specific selectors', async () => {
      const user = userEvent.setup();

      render(
        <TestWrapper>
          <FirebaseSignIn />
        </TestWrapper>
      );

      // Verify proper heading hierarchy
      const heading = screen.getByRole('heading', { name: 'Sign In' });
      expect(heading).toHaveClass('text-2xl');

      // Verify button accessibility - initially disabled due to validation
      const signInButton = screen.getByRole('button', { name: 'Sign In' });
      expect(signInButton).toBeDisabled(); // Disabled until form is filled

      // Fill form to enable button
      await user.type(screen.getByPlaceholderText('Email address'), 'test@example.com');
      await user.type(screen.getByPlaceholderText('Password'), 'password123');

      // Now button should be enabled
      expect(signInButton).not.toBeDisabled();
    });

    it('should handle error states with specific selectors', async () => {
      const user = userEvent.setup();
      mockSignInWithEmail.mockRejectedValueOnce(new Error('Invalid credentials'));

      render(
        <TestWrapper>
          <FirebaseSignIn />
        </TestWrapper>
      );

      await user.type(screen.getByPlaceholderText('Email address'), 'test@example.com');
      await user.type(screen.getByPlaceholderText('Password'), 'wrongpassword');
      await user.click(screen.getByRole('button', { name: 'Sign In' }));

      await waitFor(() => {
        expect(screen.getByText('Invalid credentials')).toBeInTheDocument();
      });
    });
  });

  describe('Password Reset Flow', () => {
    it('should navigate to password reset with specific selector', async () => {
      const user = userEvent.setup();

      render(
        <TestWrapper>
          <FirebaseSignIn />
        </TestWrapper>
      );

      // Use specific text that won't conflict
      await user.click(screen.getByRole('button', { name: /forgot your password/i }));

      expect(screen.getByRole('heading', { name: 'Reset Password' })).toBeInTheDocument();
    });
  });
});

/**
 * Best Practices for Avoiding Selector Conflicts:
 *
 * 1. Use getByRole() with specific name/accessible name:
 *    ✅ screen.getByRole('button', { name: 'Sign In' })
 *    ❌ screen.getByText('Sign In')
 *
 * 2. Use unique placeholder text or labels:
 *    ✅ screen.getByPlaceholderText('Email address')
 *    ✅ screen.getByLabelText('Email')
 *
 * 3. Use data-testid for complex scenarios:
 *    ✅ screen.getByTestId('sign-in-submit-button')
 *
 * 4. Combine selectors for specificity:
 *    ✅ screen.getByRole('button', { name: 'Sign In' }) + toHaveAttribute('type', 'submit')
 *
 * 5. Use within() for scoped queries:
 *    ✅ within(screen.getByRole('form')).getByRole('button', { name: 'Sign In' })
 */