/**
 * Firestore Database Service
 *
 * Provides typed database operations for Corner League Media.
 * Includes CRUD operations, queries, and real-time subscriptions.
 */

import {
  collection,
  doc,
  addDoc,
  setDoc,
  getDoc,
  getDocs,
  updateDoc,
  deleteDoc,
  query,
  where,
  orderBy,
  limit,
  startAfter,
  onSnapshot,
  serverTimestamp,
  writeBatch,
  QueryConstraint,
  Unsubscribe,
  DocumentData,
  QueryDocumentSnapshot,
  FieldValue,
} from 'firebase/firestore';
import { db } from './firebase';
import {
  BaseDocument,
  UserProfile,
  Team,
  Sport,
  Article,
  CreateDocument,
  UpdateDocument,
  FirestoreQueryResult,
  PaginationParams,
  QueryFilters,
  FirebaseOperationResult,
  BatchOperationResult,
  COLLECTIONS,
  CollectionName,
  FirebaseErrorCode,
  FIREBASE_ERROR_MESSAGES,
} from './types/firebase-types';

// =================================================================
// GENERIC FIRESTORE OPERATIONS
// =================================================================

/**
 * Create a new document in a collection
 */
export async function createDocument<T extends BaseDocument>(
  collectionName: CollectionName,
  data: CreateDocument<T>,
  customId?: string
): Promise<FirebaseOperationResult<T>> {
  try {
    const now = serverTimestamp() as FieldValue;
    const documentData = {
      ...data,
      createdAt: now,
      updatedAt: now,
    };

    let docRef;
    if (customId) {
      docRef = doc(db, collectionName, customId);
      await setDoc(docRef, documentData);
    } else {
      docRef = await addDoc(collection(db, collectionName), documentData);
    }

    return {
      success: true,
      data: { ...documentData, id: docRef.id } as T,
      message: 'Document created successfully',
    };
  } catch (error: any) {
    console.error(`Error creating document in ${collectionName}:`, error);
    return {
      success: false,
      error: {
        code: error.code || 'unknown',
        message: FIREBASE_ERROR_MESSAGES[error.code as FirebaseErrorCode] || error.message,
        details: error,
      },
    };
  }
}

/**
 * Get a document by ID
 */
export async function getDocument<T extends BaseDocument>(
  collectionName: CollectionName,
  documentId: string
): Promise<FirebaseOperationResult<T>> {
  try {
    const docRef = doc(db, collectionName, documentId);
    const docSnap = await getDoc(docRef);

    if (docSnap.exists()) {
      const data = { id: docSnap.id, ...docSnap.data() } as T;
      return {
        success: true,
        data,
        message: 'Document retrieved successfully',
      };
    } else {
      return {
        success: false,
        error: {
          code: FirebaseErrorCode.NOT_FOUND,
          message: 'Document not found',
        },
      };
    }
  } catch (error: any) {
    console.error(`Error getting document from ${collectionName}:`, error);
    return {
      success: false,
      error: {
        code: error.code || 'unknown',
        message: FIREBASE_ERROR_MESSAGES[error.code as FirebaseErrorCode] || error.message,
        details: error,
      },
    };
  }
}

/**
 * Update a document
 */
export async function updateDocument<T extends BaseDocument>(
  collectionName: CollectionName,
  documentId: string,
  data: UpdateDocument<T>
): Promise<FirebaseOperationResult<T>> {
  try {
    const docRef = doc(db, collectionName, documentId);
    const updateData = {
      ...data,
      updatedAt: serverTimestamp(),
    };

    await updateDoc(docRef, updateData);

    return {
      success: true,
      data: { id: documentId, ...updateData } as T,
      message: 'Document updated successfully',
    };
  } catch (error: any) {
    console.error(`Error updating document in ${collectionName}:`, error);
    return {
      success: false,
      error: {
        code: error.code || 'unknown',
        message: FIREBASE_ERROR_MESSAGES[error.code as FirebaseErrorCode] || error.message,
        details: error,
      },
    };
  }
}

/**
 * Delete a document
 */
export async function deleteDocument(
  collectionName: CollectionName,
  documentId: string
): Promise<FirebaseOperationResult<void>> {
  try {
    const docRef = doc(db, collectionName, documentId);
    await deleteDoc(docRef);

    return {
      success: true,
      message: 'Document deleted successfully',
    };
  } catch (error: any) {
    console.error(`Error deleting document from ${collectionName}:`, error);
    return {
      success: false,
      error: {
        code: error.code || 'unknown',
        message: FIREBASE_ERROR_MESSAGES[error.code as FirebaseErrorCode] || error.message,
        details: error,
      },
    };
  }
}

/**
 * Query documents with filters and pagination
 */
export async function queryDocuments<T extends BaseDocument>(
  collectionName: CollectionName,
  filters: QueryFilters = {},
  pagination: PaginationParams = { limit: 10 }
): Promise<FirebaseOperationResult<FirestoreQueryResult<T>>> {
  try {
    const constraints: QueryConstraint[] = [];

    // Add filters
    Object.entries(filters).forEach(([field, value]) => {
      if (value !== undefined && value !== null) {
        constraints.push(where(field, '==', value));
      }
    });

    // Add ordering
    if (pagination.orderBy) {
      constraints.push(orderBy(pagination.orderBy.field, pagination.orderBy.direction));
    }

    // Add pagination
    if (pagination.startAfter) {
      constraints.push(startAfter(pagination.startAfter));
    }
    constraints.push(limit(pagination.limit));

    const q = query(collection(db, collectionName), ...constraints);
    const querySnapshot = await getDocs(q);

    const data: T[] = [];
    querySnapshot.forEach((doc) => {
      data.push({ id: doc.id, ...doc.data() } as T);
    });

    const lastDoc = querySnapshot.docs[querySnapshot.docs.length - 1];
    const hasMore = querySnapshot.docs.length === pagination.limit;

    return {
      success: true,
      data: {
        data,
        hasMore,
        lastDoc,
        total: querySnapshot.size,
      },
      message: `Retrieved ${data.length} documents`,
    };
  } catch (error: any) {
    console.error(`Error querying documents from ${collectionName}:`, error);
    return {
      success: false,
      error: {
        code: error.code || 'unknown',
        message: FIREBASE_ERROR_MESSAGES[error.code as FirebaseErrorCode] || error.message,
        details: error,
      },
    };
  }
}

/**
 * Subscribe to real-time document updates
 */
export function subscribeToDocument<T extends BaseDocument>(
  collectionName: CollectionName,
  documentId: string,
  callback: (data: T | null) => void,
  onError?: (error: any) => void
): Unsubscribe {
  const docRef = doc(db, collectionName, documentId);

  return onSnapshot(
    docRef,
    (doc) => {
      if (doc.exists()) {
        const data = { id: doc.id, ...doc.data() } as T;
        callback(data);
      } else {
        callback(null);
      }
    },
    (error) => {
      console.error(`Error in document subscription for ${collectionName}/${documentId}:`, error);
      if (onError) {
        onError(error);
      }
    }
  );
}

/**
 * Subscribe to real-time collection updates
 */
export function subscribeToCollection<T extends BaseDocument>(
  collectionName: CollectionName,
  filters: QueryFilters = {},
  callback: (data: T[]) => void,
  onError?: (error: any) => void
): Unsubscribe {
  const constraints: QueryConstraint[] = [];

  // Add filters
  Object.entries(filters).forEach(([field, value]) => {
    if (value !== undefined && value !== null) {
      constraints.push(where(field, '==', value));
    }
  });

  const q = query(collection(db, collectionName), ...constraints);

  return onSnapshot(
    q,
    (querySnapshot) => {
      const data: T[] = [];
      querySnapshot.forEach((doc) => {
        data.push({ id: doc.id, ...doc.data() } as T);
      });
      callback(data);
    },
    (error) => {
      console.error(`Error in collection subscription for ${collectionName}:`, error);
      if (onError) {
        onError(error);
      }
    }
  );
}

// =================================================================
// BATCH OPERATIONS
// =================================================================

/**
 * Batch create multiple documents
 */
export async function batchCreateDocuments<T extends BaseDocument>(
  collectionName: CollectionName,
  documents: CreateDocument<T>[]
): Promise<BatchOperationResult> {
  const batch = writeBatch(db);
  const results: { success: boolean; id?: string; error?: string }[] = [];

  try {
    documents.forEach((docData) => {
      const docRef = doc(collection(db, collectionName));
      const documentData = {
        ...docData,
        createdAt: serverTimestamp(),
        updatedAt: serverTimestamp(),
      };
      batch.set(docRef, documentData);
      results.push({ success: true, id: docRef.id });
    });

    await batch.commit();

    return {
      success: true,
      successCount: results.length,
      errorCount: 0,
      errors: [],
    };
  } catch (error: any) {
    console.error(`Error in batch create for ${collectionName}:`, error);
    return {
      success: false,
      successCount: 0,
      errorCount: documents.length,
      errors: documents.map((doc, index) => ({
        item: doc,
        error: error.message,
      })),
    };
  }
}

// =================================================================
// USER-SPECIFIC OPERATIONS
// =================================================================

/**
 * Get user profile by Firebase Auth UID
 */
export async function getUserProfile(uid: string): Promise<FirebaseOperationResult<UserProfile>> {
  return getDocument<UserProfile>(COLLECTIONS.USERS, uid);
}

/**
 * Create or update user profile
 */
export async function saveUserProfile(
  uid: string,
  profileData: CreateDocument<UserProfile>
): Promise<FirebaseOperationResult<UserProfile>> {
  return createDocument<UserProfile>(COLLECTIONS.USERS, profileData, uid);
}

/**
 * Update user preferences
 */
export async function updateUserPreferences(
  uid: string,
  preferences: Partial<UserProfile['preferences']>
): Promise<FirebaseOperationResult<UserProfile>> {
  return updateDocument<UserProfile>(COLLECTIONS.USERS, uid, { preferences });
}

// =================================================================
// CONTENT OPERATIONS
// =================================================================

/**
 * Get articles for specific sports/teams
 */
export async function getArticlesForUser(
  sports: string[],
  teams: string[],
  pagination: PaginationParams = { limit: 10 }
): Promise<FirebaseOperationResult<FirestoreQueryResult<Article>>> {
  try {
    const constraints: QueryConstraint[] = [];

    // Filter by sports or teams
    if (sports.length > 0) {
      constraints.push(where('sports', 'array-contains-any', sports));
    }
    if (teams.length > 0) {
      constraints.push(where('teams', 'array-contains-any', teams));
    }

    // Only published articles
    constraints.push(where('isPublished', '==', true));

    // Order by published date (newest first)
    constraints.push(orderBy('publishedAt', 'desc'));

    // Add pagination
    if (pagination.startAfter) {
      constraints.push(startAfter(pagination.startAfter));
    }
    constraints.push(limit(pagination.limit));

    const q = query(collection(db, COLLECTIONS.ARTICLES), ...constraints);
    const querySnapshot = await getDocs(q);

    const data: Article[] = [];
    querySnapshot.forEach((doc) => {
      data.push({ id: doc.id, ...doc.data() } as Article);
    });

    const lastDoc = querySnapshot.docs[querySnapshot.docs.length - 1];
    const hasMore = querySnapshot.docs.length === pagination.limit;

    return {
      success: true,
      data: {
        data,
        hasMore,
        lastDoc,
        total: querySnapshot.size,
      },
      message: `Retrieved ${data.length} articles`,
    };
  } catch (error: any) {
    console.error('Error getting articles for user:', error);
    return {
      success: false,
      error: {
        code: error.code || 'unknown',
        message: FIREBASE_ERROR_MESSAGES[error.code as FirebaseErrorCode] || error.message,
        details: error,
      },
    };
  }
}

/**
 * Get all active teams
 */
export async function getActiveTeams(): Promise<FirebaseOperationResult<Team[]>> {
  const result = await queryDocuments<Team>(
    COLLECTIONS.TEAMS,
    { isActive: true },
    { limit: 1000, orderBy: { field: 'name', direction: 'asc' } }
  );

  if (result.success && result.data) {
    return {
      success: true,
      data: result.data.data,
      message: result.message,
    };
  }

  return result as FirebaseOperationResult<Team[]>;
}

/**
 * Get all active sports
 */
export async function getActiveSports(): Promise<FirebaseOperationResult<Sport[]>> {
  const result = await queryDocuments<Sport>(
    COLLECTIONS.SPORTS,
    { isActive: true },
    { limit: 100, orderBy: { field: 'displayName', direction: 'asc' } }
  );

  if (result.success && result.data) {
    return {
      success: true,
      data: result.data.data,
      message: result.message,
    };
  }

  return result as FirebaseOperationResult<Sport[]>;
}

// =================================================================
// EXPORT DEFAULT SERVICE OBJECT
// =================================================================

export const firestoreService = {
  // Generic operations
  createDocument,
  getDocument,
  updateDocument,
  deleteDocument,
  queryDocuments,
  subscribeToDocument,
  subscribeToCollection,

  // Batch operations
  batchCreateDocuments,

  // User operations
  getUserProfile,
  saveUserProfile,
  updateUserPreferences,

  // Content operations
  getArticlesForUser,
  getActiveTeams,
  getActiveSports,
};

export default firestoreService;