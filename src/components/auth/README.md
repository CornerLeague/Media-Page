# Firebase Authentication System

A comprehensive Firebase authentication system built with React, TypeScript, and modern React patterns.

## Overview

This authentication system provides a complete solution for user authentication in React applications using Firebase Auth. It includes context providers, custom hooks, UI components, and error handling utilities.

## Architecture

### Core Components

- **FirebaseAuthContext**: Main authentication context with provider
- **firebase.ts**: Firebase configuration and service methods
- **firebase-errors.ts**: Error handling utilities and user-friendly messages

### UI Components

- **FirebaseSignIn**: Main sign-in/sign-up component with Google OAuth
- **PasswordReset**: Standalone password reset form
- **UserProfile**: Comprehensive user profile management with tabs
- **ProtectedRoute**: Route protection with loading states

### Custom Hooks

- **useFirebaseAuth**: Main authentication hook
- **useAuthUser**: User state only
- **useAuthMethods**: Authentication methods only
- **useAuthToken**: Token management
- **usePasswordReset**: Password reset functionality
- **useEmailVerification**: Email verification management
- **useProfileManagement**: Profile update functionality
- **usePasswordManagement**: Password change with reauthentication
- **useUserStatus**: User metadata and status information

## Features

### Authentication Methods
- ✅ Google OAuth sign-in
- ✅ Email/password sign-in
- ✅ Account creation with email/password
- ✅ Secure sign-out

### Account Management
- ✅ Password reset via email
- ✅ Email verification
- ✅ Profile updates (display name, photo URL)
- ✅ Password changes with reauthentication
- ✅ User metadata access

### Security Features
- ✅ User-friendly error messages
- ✅ Input validation
- ✅ Loading states
- ✅ Proper error boundaries
- ✅ Test mode bypass for E2E testing

### UI/UX Features
- ✅ Responsive design with shadcn/ui
- ✅ Dark/light theme support
- ✅ Loading skeletons
- ✅ Accessible components
- ✅ Comprehensive profile management dialog

## Usage

### Basic Setup

```tsx
import { FirebaseAuthProvider } from '@/contexts/FirebaseAuthContext';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';

function App() {
  return (
    <FirebaseAuthProvider>
      <Routes>
        <Route path="/signin" element={<SignInPage />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
      </Routes>
    </FirebaseAuthProvider>
  );
}
```

### Using Authentication Hooks

```tsx
import { useFirebaseAuth, useAuthUser, usePasswordReset } from '@/contexts/FirebaseAuthContext';

function MyComponent() {
  // Full authentication context
  const { user, signOut, signInWithGoogle } = useFirebaseAuth();

  // User state only
  const { user, isLoading, isAuthenticated } = useAuthUser();

  // Password reset functionality
  const { resetPassword, isLoading, error, success } = usePasswordReset();

  return (
    <div>
      {isAuthenticated ? (
        <div>
          <p>Welcome, {user?.displayName}!</p>
          <button onClick={signOut}>Sign Out</button>
        </div>
      ) : (
        <button onClick={signInWithGoogle}>Sign In with Google</button>
      )}
    </div>
  );
}
```

### Components

#### FirebaseSignIn
Complete sign-in component with Google OAuth and email/password authentication:

```tsx
import { FirebaseSignIn } from '@/components/auth/FirebaseSignIn';

function SignInPage() {
  return (
    <div className="flex justify-center items-center min-h-screen">
      <FirebaseSignIn onSuccess={() => navigate('/dashboard')} />
    </div>
  );
}
```

#### UserProfile
Comprehensive profile management with dropdown menu:

```tsx
import { UserProfile } from '@/components/auth/UserProfile';

function TopNavBar() {
  return (
    <nav>
      <div className="flex items-center gap-4">
        <span>My App</span>
        <UserProfile />
      </div>
    </nav>
  );
}
```

#### PasswordReset
Standalone password reset form:

```tsx
import { PasswordReset } from '@/components/auth/PasswordReset';

function ForgotPasswordPage() {
  return (
    <div className="flex justify-center items-center min-h-screen">
      <PasswordReset onBackToSignIn={() => navigate('/signin')} />
    </div>
  );
}
```

### Advanced Usage

#### Profile Management
```tsx
import { useProfileManagement } from '@/contexts/FirebaseAuthContext';

function ProfileEditor() {
  const { updateProfile, isLoading, error, success } = useProfileManagement();

  const handleSubmit = async (data: { displayName: string }) => {
    await updateProfile(data);
  };

  return (
    <form onSubmit={handleSubmit}>
      <input name="displayName" placeholder="Display Name" />
      <button type="submit" disabled={isLoading}>
        {isLoading ? 'Updating...' : 'Update Profile'}
      </button>
      {error && <p className="error">{error}</p>}
      {success && <p className="success">Profile updated!</p>}
    </form>
  );
}
```

#### Email Verification
```tsx
import { useEmailVerification } from '@/contexts/FirebaseAuthContext';

function EmailVerificationBanner() {
  const { sendVerification, isEmailVerified, isLoading, error, success } = useEmailVerification();

  if (isEmailVerified) return null;

  return (
    <div className="banner">
      <p>Please verify your email address</p>
      <button onClick={sendVerification} disabled={isLoading}>
        {isLoading ? 'Sending...' : 'Send Verification Email'}
      </button>
      {error && <p className="error">{error}</p>}
      {success && <p className="success">Verification email sent!</p>}
    </div>
  );
}
```

## Configuration

### Environment Variables
Required Firebase configuration variables in `.env`:

```env
VITE_FIREBASE_API_KEY=your_api_key
VITE_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your_project_id
VITE_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
VITE_FIREBASE_APP_ID=your_app_id

# Optional: Enable Firebase emulator for development
VITE_FIREBASE_USE_EMULATOR=true
```

### Testing Configuration
For E2E tests, the system supports test mode bypass:

```tsx
// Set test mode via environment variable
VITE_TEST_MODE=true

// Or via URL parameter
window.location.search.includes('test=true')

// Or via global window property
(window as any).__PLAYWRIGHT_TEST__ = true
```

## Error Handling

The system includes comprehensive error handling with user-friendly messages:

```tsx
import { getFirebaseErrorMessage } from '@/lib/firebase-errors';

try {
  await signInWithEmail(email, password);
} catch (error) {
  const friendlyMessage = getFirebaseErrorMessage(error);
  console.error(friendlyMessage); // "Incorrect password. Please try again."
}
```

## TypeScript Support

All components and hooks are fully typed with TypeScript interfaces:

```tsx
interface FirebaseAuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  signInWithGoogle: () => Promise<User>;
  signInWithEmail: (email: string, password: string) => Promise<User>;
  // ... more methods
}
```

## Best Practices

1. **Always wrap your app with FirebaseAuthProvider**
2. **Use ProtectedRoute for authenticated routes**
3. **Handle loading and error states appropriately**
4. **Clear error states when user starts typing**
5. **Use appropriate hooks for specific functionality**
6. **Implement proper input validation**
7. **Test authentication flows thoroughly**

## Security Considerations

- Password validation (minimum 6 characters)
- Email format validation
- Reauthentication required for sensitive operations
- Secure token management
- Proper error message handling (no sensitive information leaked)
- Input sanitization and validation

## Testing

The authentication system is designed to be testable:

- Test mode bypass for E2E tests
- Mockable Firebase services
- Isolated hook testing
- Component testing with React Testing Library
- Accessibility testing with axe-core

## Dependencies

- `firebase`: Firebase SDK
- `react`: React 18+
- `@radix-ui/*`: Accessible UI components
- `lucide-react`: Icons
- `tailwindcss`: Styling
- `zod`: Schema validation (optional)

## Migration from Other Auth Systems

If migrating from other authentication systems:

1. Replace existing auth context with FirebaseAuthContext
2. Update components to use new hooks
3. Update route protection logic
4. Migrate user data to Firebase Auth
5. Test authentication flows thoroughly

This system provides a solid foundation for Firebase authentication in React applications with excellent TypeScript support, comprehensive error handling, and modern React patterns.