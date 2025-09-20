/**
 * Firebase TypeScript Types
 *
 * Comprehensive type definitions for Firebase services used in Corner League Media.
 * Includes types for Authentication, Firestore, and application-specific data models.
 */

import { User } from 'firebase/auth';
import { Timestamp, DocumentReference, QuerySnapshot, DocumentSnapshot } from 'firebase/firestore';

// =================================================================
// AUTHENTICATION TYPES
// =================================================================

/**
 * Enhanced user type that combines Firebase User with application-specific data
 */
export interface AppUser extends User {
  // Firebase User properties are inherited
  // Add any additional app-specific user properties here
}

/**
 * Authentication state interface
 */
export interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  error: string | null;
}

/**
 * Authentication error types
 */
export interface AuthError {
  code: string;
  message: string;
  details?: any;
}

// =================================================================
// FIRESTORE TYPES
// =================================================================

/**
 * Base document interface with common Firestore fields
 */
export interface BaseDocument {
  id: string;
  createdAt: Timestamp;
  updatedAt: Timestamp;
  createdBy?: string; // User ID
  updatedBy?: string; // User ID
}

/**
 * User profile document stored in Firestore
 */
export interface UserProfile extends BaseDocument {
  uid: string; // Firebase Auth UID
  email: string;
  displayName?: string;
  photoURL?: string;
  preferences: UserPreferences;
  lastLoginAt: Timestamp;
  isActive: boolean;
}

/**
 * User preferences configuration
 */
export interface UserPreferences {
  sports: string[];
  teams: string[];
  aiSummaryLevel: number; // 1-5 scale
  notifications: NotificationPreferences;
  theme: 'light' | 'dark' | 'system';
  language: string; // ISO language code
  timezone: string; // IANA timezone identifier
}

/**
 * Notification preferences
 */
export interface NotificationPreferences {
  gameAlerts: boolean;
  newsDigest: boolean;
  tradingUpdates: boolean;
  scoreUpdates: boolean;
  injuryReports: boolean;
  email: boolean;
  push: boolean;
  frequency: 'instant' | 'daily' | 'weekly';
}

/**
 * Sports team information
 */
export interface Team extends BaseDocument {
  name: string;
  city: string;
  sport: string;
  league: string;
  abbreviation: string;
  logoUrl?: string;
  colors: {
    primary: string;
    secondary: string;
  };
  isActive: boolean;
}

/**
 * Sports information
 */
export interface Sport extends BaseDocument {
  name: string;
  displayName: string;
  category: 'professional' | 'college' | 'international';
  season: {
    start: string; // ISO date
    end: string; // ISO date
  };
  isActive: boolean;
}

/**
 * News article/content
 */
export interface Article extends BaseDocument {
  title: string;
  content: string;
  summary?: string;
  author: string;
  sourceUrl?: string;
  imageUrl?: string;
  tags: string[];
  sports: string[]; // Sport IDs
  teams: string[]; // Team IDs
  category: 'news' | 'analysis' | 'opinion' | 'recap';
  priority: 'low' | 'medium' | 'high' | 'breaking';
  publishedAt: Timestamp;
  isPublished: boolean;
  viewCount: number;
  likeCount: number;
}

// =================================================================
// FIRESTORE COLLECTION REFERENCES
// =================================================================

/**
 * Firestore collection names as constants
 */
export const COLLECTIONS = {
  USERS: 'users',
  TEAMS: 'teams',
  SPORTS: 'sports',
  ARTICLES: 'articles',
  USER_PREFERENCES: 'userPreferences',
  FEEDBACK: 'feedback',
  ANALYTICS: 'analytics',
} as const;

/**
 * Type for collection names
 */
export type CollectionName = typeof COLLECTIONS[keyof typeof COLLECTIONS];

// =================================================================
// QUERY TYPES
// =================================================================

/**
 * Generic Firestore query result
 */
export interface FirestoreQueryResult<T> {
  data: T[];
  hasMore: boolean;
  lastDoc?: DocumentSnapshot;
  total?: number;
}

/**
 * Pagination parameters
 */
export interface PaginationParams {
  limit: number;
  startAfter?: DocumentSnapshot;
  orderBy?: {
    field: string;
    direction: 'asc' | 'desc';
  };
}

/**
 * Query filters
 */
export interface QueryFilters {
  [key: string]: any;
}

// =================================================================
// API RESPONSE TYPES
// =================================================================

/**
 * Firebase operation result
 */
export interface FirebaseOperationResult<T = any> {
  success: boolean;
  data?: T;
  error?: AuthError;
  message?: string;
}

/**
 * Batch operation result
 */
export interface BatchOperationResult {
  success: boolean;
  successCount: number;
  errorCount: number;
  errors: Array<{
    item: any;
    error: string;
  }>;
}

// =================================================================
// UTILITY TYPES
// =================================================================

/**
 * Convert Firestore Timestamp to Date for type safety
 */
export type WithDates<T> = {
  [K in keyof T]: T[K] extends Timestamp ? Date : T[K];
};

/**
 * Make Firebase document fields optional for creation
 */
export type CreateDocument<T extends BaseDocument> = Omit<
  T,
  'id' | 'createdAt' | 'updatedAt'
> & {
  id?: string;
  createdAt?: Timestamp;
  updatedAt?: Timestamp;
};

/**
 * Make Firebase document fields optional for updates
 */
export type UpdateDocument<T extends BaseDocument> = Partial<
  Omit<T, 'id' | 'createdAt' | 'createdBy'>
> & {
  updatedAt?: Timestamp;
  updatedBy?: string;
};

// =================================================================
// ERROR HANDLING
// =================================================================

/**
 * Firebase error codes that we handle
 */
export enum FirebaseErrorCode {
  // Auth errors
  INVALID_EMAIL = 'auth/invalid-email',
  USER_DISABLED = 'auth/user-disabled',
  USER_NOT_FOUND = 'auth/user-not-found',
  WRONG_PASSWORD = 'auth/wrong-password',
  EMAIL_ALREADY_IN_USE = 'auth/email-already-in-use',
  WEAK_PASSWORD = 'auth/weak-password',
  NETWORK_REQUEST_FAILED = 'auth/network-request-failed',
  TOO_MANY_REQUESTS = 'auth/too-many-requests',

  // Firestore errors
  PERMISSION_DENIED = 'permission-denied',
  NOT_FOUND = 'not-found',
  ALREADY_EXISTS = 'already-exists',
  FAILED_PRECONDITION = 'failed-precondition',
  ABORTED = 'aborted',
  OUT_OF_RANGE = 'out-of-range',
  UNIMPLEMENTED = 'unimplemented',
  INTERNAL = 'internal',
  UNAVAILABLE = 'unavailable',
  DATA_LOSS = 'data-loss',
  UNAUTHENTICATED = 'unauthenticated',
}

/**
 * User-friendly error messages
 */
export const FIREBASE_ERROR_MESSAGES: Record<FirebaseErrorCode, string> = {
  [FirebaseErrorCode.INVALID_EMAIL]: 'Please enter a valid email address.',
  [FirebaseErrorCode.USER_DISABLED]: 'This account has been disabled.',
  [FirebaseErrorCode.USER_NOT_FOUND]: 'No account found with this email.',
  [FirebaseErrorCode.WRONG_PASSWORD]: 'Incorrect password.',
  [FirebaseErrorCode.EMAIL_ALREADY_IN_USE]: 'An account already exists with this email.',
  [FirebaseErrorCode.WEAK_PASSWORD]: 'Password must be at least 6 characters long.',
  [FirebaseErrorCode.NETWORK_REQUEST_FAILED]: 'Network error. Please check your connection.',
  [FirebaseErrorCode.TOO_MANY_REQUESTS]: 'Too many attempts. Please try again later.',
  [FirebaseErrorCode.PERMISSION_DENIED]: 'You do not have permission to perform this action.',
  [FirebaseErrorCode.NOT_FOUND]: 'The requested document was not found.',
  [FirebaseErrorCode.ALREADY_EXISTS]: 'A document with this ID already exists.',
  [FirebaseErrorCode.FAILED_PRECONDITION]: 'Operation failed due to a precondition.',
  [FirebaseErrorCode.ABORTED]: 'Operation was aborted.',
  [FirebaseErrorCode.OUT_OF_RANGE]: 'Value is out of valid range.',
  [FirebaseErrorCode.UNIMPLEMENTED]: 'This operation is not implemented.',
  [FirebaseErrorCode.INTERNAL]: 'Internal server error.',
  [FirebaseErrorCode.UNAVAILABLE]: 'Service is currently unavailable.',
  [FirebaseErrorCode.DATA_LOSS]: 'Data loss occurred.',
  [FirebaseErrorCode.UNAUTHENTICATED]: 'You must be signed in to perform this action.',
};

// =================================================================
// EXPORT TYPES FOR CONVENIENCE
// =================================================================

export type {
  User,
  Timestamp,
  DocumentReference,
  QuerySnapshot,
  DocumentSnapshot,
} from 'firebase/firestore';

export type {
  Auth,
  GoogleAuthProvider,
} from 'firebase/auth';