/**
 * Firebase Firestore React Hooks
 *
 * Custom hooks for integrating Firestore operations with React components.
 * Provides state management, loading states, and error handling.
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { Unsubscribe } from 'firebase/firestore';
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
  CollectionName,
  COLLECTIONS,
} from '@/lib/types/firebase-types';
import { firestoreService } from '@/lib/firestore';
import { useFirebaseAuth } from '@/contexts/FirebaseAuthContext';

// =================================================================
// HOOK STATE INTERFACES
// =================================================================

interface UseDocumentState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

interface UseCollectionState<T> {
  data: T[];
  loading: boolean;
  error: string | null;
  hasMore: boolean;
  loadMore: () => Promise<void>;
  refresh: () => Promise<void>;
}

interface UseFirestoreOperationState {
  loading: boolean;
  error: string | null;
  success: boolean;
}

// =================================================================
// DOCUMENT HOOKS
// =================================================================

/**
 * Hook for real-time document subscription
 */
export function useDocument<T extends BaseDocument>(
  collectionName: CollectionName,
  documentId: string | null,
  dependencies: any[] = []
): UseDocumentState<T> {
  const [state, setState] = useState<UseDocumentState<T>>({
    data: null,
    loading: true,
    error: null,
  });

  const unsubscribeRef = useRef<Unsubscribe | null>(null);

  useEffect(() => {
    if (!documentId) {
      setState({ data: null, loading: false, error: null });
      return;
    }

    setState(prev => ({ ...prev, loading: true, error: null }));

    // Subscribe to document changes
    unsubscribeRef.current = firestoreService.subscribeToDocument<T>(
      collectionName,
      documentId,
      (data) => {
        setState({ data, loading: false, error: null });
      },
      (error) => {
        setState({ data: null, loading: false, error: error.message });
      }
    );

    // Cleanup subscription
    return () => {
      if (unsubscribeRef.current) {
        unsubscribeRef.current();
        unsubscribeRef.current = null;
      }
    };
  }, [collectionName, documentId, ...dependencies]);

  return state;
}

/**
 * Hook for fetching a single document (one-time)
 */
export function useDocumentOnce<T extends BaseDocument>(
  collectionName: CollectionName,
  documentId: string | null
): UseDocumentState<T> & { refetch: () => Promise<void> } {
  const [state, setState] = useState<UseDocumentState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const fetchDocument = useCallback(async () => {
    if (!documentId) {
      setState({ data: null, loading: false, error: null });
      return;
    }

    setState(prev => ({ ...prev, loading: true, error: null }));

    const result = await firestoreService.getDocument<T>(collectionName, documentId);

    if (result.success) {
      setState({ data: result.data || null, loading: false, error: null });
    } else {
      setState({ data: null, loading: false, error: result.error?.message || 'Unknown error' });
    }
  }, [collectionName, documentId]);

  useEffect(() => {
    fetchDocument();
  }, [fetchDocument]);

  return { ...state, refetch: fetchDocument };
}

// =================================================================
// COLLECTION HOOKS
// =================================================================

/**
 * Hook for real-time collection subscription
 */
export function useCollection<T extends BaseDocument>(
  collectionName: CollectionName,
  filters: QueryFilters = {},
  dependencies: any[] = []
): UseCollectionState<T> {
  const [state, setState] = useState<UseCollectionState<T>>({
    data: [],
    loading: true,
    error: null,
    hasMore: false,
    loadMore: async () => {},
    refresh: async () => {},
  });

  const unsubscribeRef = useRef<Unsubscribe | null>(null);

  const refresh = useCallback(async () => {
    setState(prev => ({ ...prev, loading: true, error: null }));
  }, []);

  useEffect(() => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    // Subscribe to collection changes
    unsubscribeRef.current = firestoreService.subscribeToCollection<T>(
      collectionName,
      filters,
      (data) => {
        setState(prev => ({
          ...prev,
          data,
          loading: false,
          error: null,
          hasMore: false, // Real-time subscriptions don't support pagination
          loadMore: async () => {},
          refresh,
        }));
      },
      (error) => {
        setState(prev => ({
          ...prev,
          data: [],
          loading: false,
          error: error.message,
          hasMore: false,
          loadMore: async () => {},
          refresh,
        }));
      }
    );

    // Cleanup subscription
    return () => {
      if (unsubscribeRef.current) {
        unsubscribeRef.current();
        unsubscribeRef.current = null;
      }
    };
  }, [collectionName, JSON.stringify(filters), ...dependencies]);

  return state;
}

/**
 * Hook for paginated collection queries
 */
export function usePaginatedCollection<T extends BaseDocument>(
  collectionName: CollectionName,
  filters: QueryFilters = {},
  initialPagination: PaginationParams = { limit: 10 }
): UseCollectionState<T> {
  const [state, setState] = useState<UseCollectionState<T>>({
    data: [],
    loading: true,
    error: null,
    hasMore: false,
    loadMore: async () => {},
    refresh: async () => {},
  });

  const [pagination, setPagination] = useState(initialPagination);
  const [lastDoc, setLastDoc] = useState<any>(null);

  const fetchData = useCallback(async (isLoadMore = false) => {
    setState(prev => ({ ...prev, loading: !isLoadMore, error: null }));

    const currentPagination = isLoadMore && lastDoc
      ? { ...pagination, startAfter: lastDoc }
      : pagination;

    const result = await firestoreService.queryDocuments<T>(
      collectionName,
      filters,
      currentPagination
    );

    if (result.success && result.data) {
      setState(prev => ({
        ...prev,
        data: isLoadMore ? [...prev.data, ...result.data!.data] : result.data!.data,
        loading: false,
        error: null,
        hasMore: result.data!.hasMore,
      }));

      if (result.data.lastDoc) {
        setLastDoc(result.data.lastDoc);
      }
    } else {
      setState(prev => ({
        ...prev,
        data: isLoadMore ? prev.data : [],
        loading: false,
        error: result.error?.message || 'Unknown error',
        hasMore: false,
      }));
    }
  }, [collectionName, JSON.stringify(filters), JSON.stringify(pagination), lastDoc]);

  const loadMore = useCallback(async () => {
    if (state.hasMore && !state.loading) {
      await fetchData(true);
    }
  }, [state.hasMore, state.loading, fetchData]);

  const refresh = useCallback(async () => {
    setLastDoc(null);
    await fetchData(false);
  }, [fetchData]);

  useEffect(() => {
    setState(prev => ({ ...prev, loadMore, refresh }));
  }, [loadMore, refresh]);

  useEffect(() => {
    fetchData(false);
  }, [fetchData]);

  return state;
}

// =================================================================
// OPERATION HOOKS
// =================================================================

/**
 * Hook for document creation operations
 */
export function useCreateDocument<T extends BaseDocument>() {
  const [state, setState] = useState<UseFirestoreOperationState>({
    loading: false,
    error: null,
    success: false,
  });

  const createDocument = useCallback(async (
    collectionName: CollectionName,
    data: CreateDocument<T>,
    customId?: string
  ): Promise<FirebaseOperationResult<T>> => {
    setState({ loading: true, error: null, success: false });

    const result = await firestoreService.createDocument<T>(collectionName, data, customId);

    setState({
      loading: false,
      error: result.success ? null : result.error?.message || 'Unknown error',
      success: result.success,
    });

    return result;
  }, []);

  return { ...state, createDocument };
}

/**
 * Hook for document update operations
 */
export function useUpdateDocument<T extends BaseDocument>() {
  const [state, setState] = useState<UseFirestoreOperationState>({
    loading: false,
    error: null,
    success: false,
  });

  const updateDocument = useCallback(async (
    collectionName: CollectionName,
    documentId: string,
    data: UpdateDocument<T>
  ): Promise<FirebaseOperationResult<T>> => {
    setState({ loading: true, error: null, success: false });

    const result = await firestoreService.updateDocument<T>(collectionName, documentId, data);

    setState({
      loading: false,
      error: result.success ? null : result.error?.message || 'Unknown error',
      success: result.success,
    });

    return result;
  }, []);

  return { ...state, updateDocument };
}

/**
 * Hook for document deletion operations
 */
export function useDeleteDocument() {
  const [state, setState] = useState<UseFirestoreOperationState>({
    loading: false,
    error: null,
    success: false,
  });

  const deleteDocument = useCallback(async (
    collectionName: CollectionName,
    documentId: string
  ): Promise<FirebaseOperationResult<void>> => {
    setState({ loading: true, error: null, success: false });

    const result = await firestoreService.deleteDocument(collectionName, documentId);

    setState({
      loading: false,
      error: result.success ? null : result.error?.message || 'Unknown error',
      success: result.success,
    });

    return result;
  }, []);

  return { ...state, deleteDocument };
}

// =================================================================
// USER-SPECIFIC HOOKS
// =================================================================

/**
 * Hook for current user's profile
 */
export function useUserProfile() {
  const { user, isAuthenticated } = useFirebaseAuth();

  return useDocument<UserProfile>(
    COLLECTIONS.USERS,
    isAuthenticated && user ? user.uid : null,
    [user?.uid, isAuthenticated]
  );
}

/**
 * Hook for updating user profile
 */
export function useUpdateUserProfile() {
  const { user } = useFirebaseAuth();
  const { updateDocument, ...state } = useUpdateDocument<UserProfile>();

  const updateProfile = useCallback(async (data: UpdateDocument<UserProfile>) => {
    if (!user) {
      throw new Error('User must be authenticated to update profile');
    }
    return updateDocument(COLLECTIONS.USERS, user.uid, data);
  }, [user, updateDocument]);

  return { ...state, updateProfile };
}

// =================================================================
// CONTENT HOOKS
// =================================================================

/**
 * Hook for getting articles based on user preferences
 */
export function useUserArticles(sports: string[], teams: string[]) {
  const [state, setState] = useState<UseCollectionState<Article>>({
    data: [],
    loading: true,
    error: null,
    hasMore: false,
    loadMore: async () => {},
    refresh: async () => {},
  });

  const [lastDoc, setLastDoc] = useState<any>(null);

  const fetchArticles = useCallback(async (isLoadMore = false) => {
    setState(prev => ({ ...prev, loading: !isLoadMore, error: null }));

    const pagination: PaginationParams = {
      limit: 10,
      ...(isLoadMore && lastDoc ? { startAfter: lastDoc } : {}),
    };

    const result = await firestoreService.getArticlesForUser(sports, teams, pagination);

    if (result.success && result.data) {
      setState(prev => ({
        ...prev,
        data: isLoadMore ? [...prev.data, ...result.data!.data] : result.data!.data,
        loading: false,
        error: null,
        hasMore: result.data!.hasMore,
      }));

      if (result.data.lastDoc) {
        setLastDoc(result.data.lastDoc);
      }
    } else {
      setState(prev => ({
        ...prev,
        data: isLoadMore ? prev.data : [],
        loading: false,
        error: result.error?.message || 'Unknown error',
        hasMore: false,
      }));
    }
  }, [sports, teams, lastDoc]);

  const loadMore = useCallback(async () => {
    if (state.hasMore && !state.loading) {
      await fetchArticles(true);
    }
  }, [state.hasMore, state.loading, fetchArticles]);

  const refresh = useCallback(async () => {
    setLastDoc(null);
    await fetchArticles(false);
  }, [fetchArticles]);

  useEffect(() => {
    setState(prev => ({ ...prev, loadMore, refresh }));
  }, [loadMore, refresh]);

  useEffect(() => {
    fetchArticles(false);
  }, [fetchArticles]);

  return state;
}

/**
 * Hook for getting all teams
 */
export function useTeams() {
  const [teams, setTeams] = useState<Team[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTeams = async () => {
      setLoading(true);
      setError(null);

      const result = await firestoreService.getActiveTeams();

      if (result.success) {
        setTeams(result.data || []);
      } else {
        setError(result.error?.message || 'Failed to fetch teams');
      }

      setLoading(false);
    };

    fetchTeams();
  }, []);

  return { teams, loading, error };
}

/**
 * Hook for getting all sports
 */
export function useSports() {
  const [sports, setSports] = useState<Sport[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSports = async () => {
      setLoading(true);
      setError(null);

      const result = await firestoreService.getActiveSports();

      if (result.success) {
        setSports(result.data || []);
      } else {
        setError(result.error?.message || 'Failed to fetch sports');
      }

      setLoading(false);
    };

    fetchSports();
  }, []);

  return { sports, loading, error };
}