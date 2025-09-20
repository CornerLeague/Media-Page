# Testing Guidelines: Fixing Strict Mode Selector Violations

## Overview

This document provides comprehensive guidelines for writing tests that avoid Strict Mode violations, specifically addressing the issue where selectors match multiple elements when they should match exactly one.

## Common Selector Conflicts and Solutions

### 1. Text-Based Conflicts

#### Problem: Multiple elements with same text
```tsx
// ❌ PROBLEMATIC - This could match heading, button, and link
screen.getByText('Sign In')
```

#### Solutions:

**A. Use getByRole() with specific role and name:**
```tsx
// ✅ SPECIFIC - Targets only the heading
screen.getByRole('heading', { name: 'Sign In' })

// ✅ SPECIFIC - Targets only the submit button
screen.getByRole('button', { name: 'Sign In' })

// ✅ SPECIFIC - Targets only the link button
screen.getByRole('button', { name: 'Sign up' })
```

**B. Use data-testid for unique identification:**
```tsx
// ✅ UNIQUE - Each element has distinct test ID
screen.getByTestId('auth-form-title')        // heading
screen.getByTestId('sign-in-submit')         // submit button
screen.getByTestId('auth-mode-toggle')       // toggle link
```

**C. Use within() for scoped queries:**
```tsx
// ✅ SCOPED - Query within specific containers
const form = screen.getByTestId('email-auth-form');
within(form).getByRole('button', { name: 'Sign In' });
```

### 2. Component-Specific Examples

#### FirebaseSignIn Component

The FirebaseSignIn component has multiple elements with the same text. Here's how to target each specifically:

```tsx
// Sign In Mode
expect(screen.getByRole('heading', { name: 'Sign In' })).toBeInTheDocument();
expect(screen.getByRole('button', { name: 'Sign In' })).toBeInTheDocument();
expect(screen.getByRole('button', { name: 'Sign up' })).toBeInTheDocument();

// Sign Up Mode (after toggling)
expect(screen.getByRole('heading', { name: 'Create Account' })).toBeInTheDocument();
expect(screen.getByRole('button', { name: 'Create Account' })).toBeInTheDocument();
expect(screen.getByRole('button', { name: 'Sign in' })).toBeInTheDocument();
```

#### Using data-testid attributes:
```tsx
// More reliable for automated testing
expect(screen.getByTestId('auth-form-title')).toHaveTextContent('Sign In');
expect(screen.getByTestId('sign-in-submit')).toBeInTheDocument();
expect(screen.getByTestId('auth-mode-toggle')).toHaveTextContent('Sign up');
```

## Best Practices

### 1. Selector Priority Order

Use selectors in this order of preference:

1. **Accessible queries (getByRole, getByLabelText)**
   - Mirrors how users interact with the application
   - Tests accessibility compliance
   ```tsx
   screen.getByRole('button', { name: 'Submit' })
   screen.getByLabelText('Email address')
   ```

2. **Semantic queries (getByPlaceholderText, getByDisplayValue)**
   ```tsx
   screen.getByPlaceholderText('Enter email')
   screen.getByDisplayValue('user@example.com')
   ```

3. **Test ID queries (getByTestId)**
   - Use sparingly, for complex scenarios
   ```tsx
   screen.getByTestId('complex-component-submit')
   ```

4. **Text queries (getByText) - Last resort**
   - Only when text is truly unique
   ```tsx
   screen.getByText('This is unique descriptive text')
   ```

### 2. Data-TestId Naming Conventions

Use descriptive, hierarchical naming:

```tsx
// Component-action-element pattern
data-testid="auth-form-title"
data-testid="auth-form-submit"
data-testid="auth-mode-toggle"
data-testid="user-profile-edit-button"
data-testid="navigation-menu-toggle"
```

### 3. Form Testing Patterns

```tsx
// ✅ Good form testing pattern
const emailInput = screen.getByLabelText('Email') || screen.getByPlaceholderText('Email address');
const passwordInput = screen.getByLabelText('Password') || screen.getByPlaceholderText('Password');
const submitButton = screen.getByRole('button', { name: /sign in|submit/i });

await user.type(emailInput, 'test@example.com');
await user.type(passwordInput, 'password123');
await user.click(submitButton);
```

### 4. Handling Dynamic Content

For content that changes based on state:

```tsx
// ✅ Handle both states explicitly
if (isSignUpMode) {
  expect(screen.getByRole('heading', { name: 'Create Account' })).toBeInTheDocument();
  expect(screen.getByRole('button', { name: 'Create Account' })).toBeInTheDocument();
} else {
  expect(screen.getByRole('heading', { name: 'Sign In' })).toBeInTheDocument();
  expect(screen.getByRole('button', { name: 'Sign In' })).toBeInTheDocument();
}
```

## Testing Strategies

### 1. Component Testing

```tsx
describe('AuthComponent', () => {
  it('should distinguish between heading and button with same text', () => {
    render(<AuthComponent />);

    // Test each element specifically
    expect(screen.getByRole('heading', { name: 'Sign In' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Sign In' })).toBeInTheDocument();

    // Verify they are different elements
    const heading = screen.getByRole('heading', { name: 'Sign In' });
    const button = screen.getByRole('button', { name: 'Sign In' });
    expect(heading).not.toBe(button);
  });
});
```

### 2. Integration Testing

```tsx
describe('Authentication Flow', () => {
  it('should complete sign in flow with specific selectors', async () => {
    const user = userEvent.setup();
    render(<App />);

    // Navigate to sign in
    await user.click(screen.getByRole('link', { name: 'Sign In' }));

    // Fill form using specific selectors
    await user.type(screen.getByPlaceholderText('Email address'), 'test@example.com');
    await user.type(screen.getByPlaceholderText('Password'), 'password123');
    await user.click(screen.getByRole('button', { name: 'Sign In' }));

    // Verify success
    await waitFor(() => {
      expect(screen.getByText('Welcome back!')).toBeInTheDocument();
    });
  });
});
```

### 3. Accessibility Testing

```tsx
import { runAccessibilityAudit } from '@/lib/accessibility';

describe('Accessibility', () => {
  it('should pass accessibility audit with specific selectors', async () => {
    const { container } = render(<AuthComponent />);

    // Test keyboard navigation
    const firstButton = screen.getByRole('button', { name: 'Continue with Google' });
    const secondButton = screen.getByRole('button', { name: 'Sign In' });

    firstButton.focus();
    expect(document.activeElement).toBe(firstButton);

    // Run accessibility audit
    const results = await runAccessibilityAudit(container);
    expect(results.violations).toHaveLength(0);
  });
});
```

## Anti-Patterns to Avoid

### ❌ Avoid These Patterns

```tsx
// Don't use ambiguous text selectors
screen.getByText('Submit');           // Could match multiple buttons
screen.getByText('Save');             // Could match button and status text
screen.getByText('Cancel');           // Could match button and error message

// Don't use overly generic test IDs
screen.getByTestId('button');         // Too generic
screen.getByTestId('text');           // Not descriptive

// Don't rely on CSS classes for testing
screen.getByClassName('btn-primary'); // Implementation detail
```

### ✅ Use These Instead

```tsx
// Use specific role-based selectors
screen.getByRole('button', { name: 'Submit form' });
screen.getByRole('button', { name: 'Save changes' });
screen.getByRole('button', { name: 'Cancel operation' });

// Use descriptive test IDs
screen.getByTestId('form-submit-button');
screen.getByTestId('user-profile-save-button');
screen.getByTestId('modal-cancel-button');

// Use semantic HTML and accessibility attributes
screen.getByLabelText('Email address');
screen.getByRole('textbox', { name: 'Email' });
```

## Debugging Selector Issues

### Finding Conflicting Elements

```tsx
// Use screen.debug() to see rendered HTML
screen.debug();

// Use getAllBy* to see all matching elements
const allSignInTexts = screen.getAllByText('Sign In');
console.log('Found', allSignInTexts.length, 'elements with "Sign In" text');

// Inspect each element
allSignInTexts.forEach((element, index) => {
  console.log(`Element ${index}:`, element.tagName, element.textContent);
});
```

### Using Testing Library Queries

```tsx
// Use screen.logTestingPlaygroundURL() for interactive debugging
screen.logTestingPlaygroundURL();

// This logs a URL you can open to see suggested selectors
```

## Testing Configuration

### Vitest Configuration for Strict Mode

```typescript
// vitest.config.ts
export default defineConfig({
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test-setup.ts'],
    globals: true,
  },
});
```

### Test Setup File

```typescript
// src/test-setup.ts
import '@testing-library/jest-dom';
import { configure } from '@testing-library/react';

// Configure testing library for stricter queries
configure({
  // Throw errors for multiple matches
  throwSuggestions: true,
  // Show better error messages
  getElementError: (message, container) => {
    const error = new Error(message);
    error.name = 'TestingLibraryElementError';
    return error;
  },
});
```

## Migration Checklist

When fixing existing tests:

- [ ] Replace `getByText()` with `getByRole()` where possible
- [ ] Add `data-testid` attributes to components with ambiguous text
- [ ] Use `within()` for scoped queries when needed
- [ ] Test both UI states (sign in/sign up modes)
- [ ] Verify accessibility with role-based selectors
- [ ] Run tests in Strict Mode to catch violations
- [ ] Document any remaining ambiguous selectors

## Conclusion

By following these guidelines, you can:

1. **Eliminate Strict Mode violations** by ensuring selectors match exactly one element
2. **Improve test reliability** by using specific, semantic selectors
3. **Enhance accessibility testing** by using role-based queries
4. **Make tests more maintainable** by following consistent patterns

Remember: Good tests should mirror how users interact with your application, using semantic selectors that test both functionality and accessibility.