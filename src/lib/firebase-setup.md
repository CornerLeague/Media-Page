# Firebase Setup Guide for Corner League Media

This guide explains how to set up Firebase for the Corner League Media React TypeScript application.

## Overview

The application uses Firebase for:
- **Authentication**: User sign-in/sign-up with Google and email/password
- **Firestore**: NoSQL database for user profiles, preferences, and content
- **Real-time Updates**: Live data synchronization

## Setup Instructions

### 1. Firebase Project Setup

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Create a new project or select existing project
3. Enable Authentication and Firestore Database

### 2. Authentication Configuration

1. In Firebase Console, go to **Authentication > Sign-in method**
2. Enable the following providers:
   - **Email/Password**: For basic authentication
   - **Google**: For social authentication
3. Add your domain to authorized domains (for production)

### 3. Firestore Database Setup

1. In Firebase Console, go to **Firestore Database**
2. Create database in **production mode** or **test mode**
3. Set up security rules (see [Security Rules](#security-rules) below)

### 4. Web App Configuration

1. In Firebase Console, go to **Project Settings > General**
2. Scroll to "Your apps" section
3. Click "Add app" and select "Web"
4. Register your app and copy the configuration

### 5. Environment Variables

Copy the Firebase configuration values to your `.env` file:

```bash
# Firebase Web App Configuration
VITE_FIREBASE_API_KEY=your-api-key-here
VITE_FIREBASE_AUTH_DOMAIN=your-project-id.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your-messaging-sender-id
VITE_FIREBASE_APP_ID=your-app-id

# Optional: For local development with emulators
VITE_FIREBASE_USE_EMULATOR=false
```

## Architecture

### File Structure

```
src/
├── lib/
│   ├── firebase.ts              # Firebase initialization and auth service
│   ├── firestore.ts             # Firestore database operations
│   └── types/
│       └── firebase-types.ts    # TypeScript type definitions
├── contexts/
│   └── FirebaseAuthContext.tsx  # React context for authentication
└── hooks/
    └── useFirestore.ts          # Custom hooks for Firestore operations
```

### Core Components

#### 1. Firebase Configuration (`src/lib/firebase.ts`)
- Initializes Firebase app with environment variables
- Sets up Authentication and Firestore
- Provides auth service with helper methods
- Handles emulator connections for development

#### 2. Firebase Types (`src/lib/types/firebase-types.ts`)
- Comprehensive TypeScript definitions
- User profiles, preferences, and content types
- Error handling and operation result types
- Firestore collection and document interfaces

#### 3. Firestore Service (`src/lib/firestore.ts`)
- Generic CRUD operations for all collections
- User-specific operations (profiles, preferences)
- Content operations (articles, teams, sports)
- Real-time subscriptions and batch operations

#### 4. Authentication Context (`src/contexts/FirebaseAuthContext.tsx`)
- React context for auth state management
- Authentication methods (Google, email/password)
- User information helpers
- Loading and error states

#### 5. Firestore Hooks (`src/hooks/useFirestore.ts`)
- Custom React hooks for database operations
- Real-time document and collection subscriptions
- Paginated queries with load more functionality
- User-specific hooks for profiles and content

## Usage Examples

### Authentication

```typescript
import { useFirebaseAuth } from '@/contexts/FirebaseAuthContext';

function MyComponent() {
  const { user, isAuthenticated, signInWithGoogle, signOut } = useFirebaseAuth();

  if (!isAuthenticated) {
    return <button onClick={signInWithGoogle}>Sign In with Google</button>;
  }

  return (
    <div>
      <p>Welcome, {user?.displayName}!</p>
      <button onClick={signOut}>Sign Out</button>
    </div>
  );
}
```

### User Profile

```typescript
import { useUserProfile, useUpdateUserProfile } from '@/hooks/useFirestore';

function UserProfile() {
  const { data: profile, loading } = useUserProfile();
  const { updateProfile, loading: updating } = useUpdateUserProfile();

  const handleUpdatePreferences = async () => {
    await updateProfile({
      preferences: {
        ...profile?.preferences,
        sports: ['football', 'basketball'],
      },
    });
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h2>User Profile</h2>
      <p>Email: {profile?.email}</p>
      <button onClick={handleUpdatePreferences} disabled={updating}>
        Update Preferences
      </button>
    </div>
  );
}
```

### Real-time Data

```typescript
import { useCollection } from '@/hooks/useFirestore';
import { COLLECTIONS, Article } from '@/lib/types/firebase-types';

function NewsFeed() {
  const { data: articles, loading, error } = useCollection<Article>(
    COLLECTIONS.ARTICLES,
    { isPublished: true }
  );

  if (loading) return <div>Loading articles...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      {articles.map(article => (
        <div key={article.id}>
          <h3>{article.title}</h3>
          <p>{article.summary}</p>
        </div>
      ))}
    </div>
  );
}
```

### Paginated Content

```typescript
import { useUserArticles } from '@/hooks/useFirestore';

function PersonalizedFeed() {
  const { data: articles, loading, hasMore, loadMore } = useUserArticles(
    ['football', 'basketball'], // sports
    ['team1', 'team2']         // teams
  );

  return (
    <div>
      {articles.map(article => (
        <div key={article.id}>{article.title}</div>
      ))}
      {hasMore && (
        <button onClick={loadMore} disabled={loading}>
          Load More
        </button>
      )}
    </div>
  );
}
```

## Security Rules

### Firestore Security Rules

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can read/write their own profile
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }

    // Anyone can read public content (teams, sports, articles)
    match /teams/{teamId} {
      allow read: if true;
      allow write: if request.auth != null; // Only authenticated users can write
    }

    match /sports/{sportId} {
      allow read: if true;
      allow write: if request.auth != null;
    }

    match /articles/{articleId} {
      allow read: if resource.data.isPublished == true;
      allow write: if request.auth != null;
    }
  }
}
```

## Local Development with Emulators

### 1. Install Firebase CLI

```bash
npm install -g firebase-tools
```

### 2. Login and Initialize

```bash
firebase login
firebase init emulators
```

### 3. Configure Emulators

Select:
- Authentication Emulator (port 9099)
- Firestore Emulator (port 8080)

### 4. Start Emulators

```bash
firebase emulators:start
```

### 5. Enable Emulator Mode

Set in your `.env` file:

```bash
VITE_FIREBASE_USE_EMULATOR=true
```

## Deployment Considerations

### Production Environment Variables

Ensure all production Firebase config values are set:

```bash
VITE_FIREBASE_API_KEY=prod-api-key
VITE_FIREBASE_AUTH_DOMAIN=your-prod-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-prod-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-prod-project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=prod-sender-id
VITE_FIREBASE_APP_ID=prod-app-id
VITE_FIREBASE_USE_EMULATOR=false
```

### Security

1. **Never commit** `.env` files to version control
2. Use **environment-specific** Firebase projects (dev, staging, prod)
3. Set up **proper Firestore security rules**
4. Enable **App Check** for production (optional but recommended)

### Performance

1. Use **indexes** for complex queries
2. Implement **pagination** for large datasets
3. Use **real-time listeners** sparingly
4. Consider **caching** strategies for static data

## Troubleshooting

### Common Issues

1. **Missing environment variables**: Check `.env` file and restart dev server
2. **Emulator connection errors**: Ensure emulators are running and ports are correct
3. **Permission denied**: Check Firestore security rules
4. **Authentication errors**: Verify auth providers are enabled in Firebase Console

### Debugging

Enable Firebase debug mode:

```typescript
// In development
if (import.meta.env.DEV) {
  // Enable Firestore logging
  import('firebase/firestore').then(({ enableNetwork, connectFirestoreEmulator }) => {
    console.log('Firebase debugging enabled');
  });
}
```

## Best Practices

1. **Type Safety**: Use TypeScript types for all Firebase operations
2. **Error Handling**: Always handle errors and provide user feedback
3. **Loading States**: Show loading indicators for async operations
4. **Optimistic Updates**: Update UI optimistically where appropriate
5. **Data Validation**: Validate data both client and server-side
6. **Cleanup**: Unsubscribe from real-time listeners to prevent memory leaks

## Support

For Firebase-specific issues:
- [Firebase Documentation](https://firebase.google.com/docs)
- [Firebase Support](https://firebase.google.com/support)

For application-specific issues:
- Check the existing codebase patterns
- Review the type definitions in `firebase-types.ts`
- Use the provided hooks and services for consistency