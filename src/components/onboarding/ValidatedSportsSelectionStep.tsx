/**
 * Validated Sports Selection Step
 *
 * Enhanced sports selection component with comprehensive validation,
 * error handling, and recovery mechanisms.
 */

import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from "@dnd-kit/core";
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { toast } from "@/components/ui/use-toast";
import { GripVertical, Check, AlertCircle, Loader2 } from "lucide-react";

import { OnboardingLayout } from "@/pages/onboarding/OnboardingLayout";
import { createApiQueryClient, type OnboardingSport, apiClient } from "@/lib/api-client";
import { useFirebaseAuth } from "@/contexts/FirebaseAuthContext";
import { AVAILABLE_SPORTS } from "@/data/sports";
import { updateLocalOnboardingStep, getLocalOnboardingStatus } from "@/lib/onboarding-storage";
import { cn } from "@/lib/utils";

// Validation imports
import { useSportsSelectionValidation } from "@/hooks/useOnboardingValidation";
import { ErrorAlert, FieldError, RecoveryGuidance } from "@/components/error-boundaries/ErrorRecoveryComponents";
import { SportsSelectionSkeleton } from "@/components/fallback/OnboardingFallbackUI";
import { reportOnboardingError, reportValidationError } from "@/lib/error-reporting";
import { retryableFetch } from "@/lib/api-retry";

// Types
interface SportItem extends OnboardingSport {
  isSelected: boolean;
  rank: number;
}

interface ValidationState {
  isValidating: boolean;
  showValidationErrors: boolean;
  hasBeenSubmitted: boolean;
}

interface SortableSportItemProps {
  sport: SportItem;
  onToggle: (sportId: string) => void;
  hasError?: boolean;
  errorMessage?: string;
}

/**
 * Sortable Sport Item Component with Validation
 */
function SortableSportItem({ sport, onToggle, hasError, errorMessage }: SortableSportItemProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: sport.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  const handleCardClick = useCallback((event: React.MouseEvent) => {
    // Prevent card click when dragging or clicking on drag handle
    if (isDragging) return;

    // Check if click originated from drag handle
    const target = event.target as HTMLElement;
    if (target.closest('[data-drag-handle="true"]')) return;

    onToggle(sport.id);
  }, [isDragging, onToggle, sport.id]);

  const handleKeyDown = useCallback((event: React.KeyboardEvent) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      onToggle(sport.id);
    }
  }, [onToggle, sport.id]);

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={cn(
        "touch-none",
        isDragging && "opacity-50"
      )}
    >
      <Card
        data-testid={`sport-card-${sport.id}`}
        data-selected={sport.isSelected}
        role="button"
        tabIndex={0}
        aria-selected={sport.isSelected}
        aria-invalid={hasError}
        aria-describedby={hasError ? `${sport.id}-error` : undefined}
        aria-label={`${sport.isSelected ? 'Deselect' : 'Select'} ${sport.name}${sport.isSelected ? `, currently ranked #${sport.rank}` : ''}`}
        onClick={handleCardClick}
        onKeyDown={handleKeyDown}
        className={cn(
          "transition-all duration-200 hover:shadow-md cursor-pointer focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2",
          sport.isSelected
            ? "ring-2 ring-primary bg-primary/5 hover:bg-primary/10"
            : "hover:bg-muted/50 hover:border-primary/20",
          hasError && "border-red-300 bg-red-50/50 dark:border-red-800 dark:bg-red-950/30"
        )}
      >
        <CardContent className="p-4">
          <div className="flex items-center gap-4">
            {/* Drag handle */}
            <div
              {...attributes}
              {...listeners}
              data-drag-handle="true"
              className="flex-shrink-0 cursor-grab active:cursor-grabbing p-1 hover:bg-muted rounded transition-colors"
              onClick={(e) => e.stopPropagation()}
              title="Drag to reorder"
            >
              <GripVertical className="h-5 w-5 text-muted-foreground" />
            </div>

            {/* Sport icon */}
            <div className="text-2xl flex-shrink-0" aria-hidden="true">
              {sport.icon}
            </div>

            {/* Sport info */}
            <div className="flex-1 space-y-1 pointer-events-none">
              <div className="flex items-center gap-3">
                <h3 className="font-display font-semibold text-foreground">
                  {sport.name}
                </h3>
                {sport.isPopular && (
                  <Badge variant="secondary" className="text-xs">
                    Popular
                  </Badge>
                )}
              </div>
              {sport.isSelected && (
                <p className="text-sm text-primary font-medium">
                  {sport.rank === 1 ? '1st' : sport.rank === 2 ? '2nd' : sport.rank === 3 ? '3rd' : `${sport.rank}th`} choice
                </p>
              )}
            </div>

            {/* Selection indicator */}
            <div className="flex-shrink-0 pointer-events-none">
              <div className={cn(
                "h-5 w-5 rounded border-2 flex items-center justify-center transition-colors",
                sport.isSelected
                  ? "bg-primary border-primary text-primary-foreground"
                  : "border-muted-foreground"
              )}>
                {sport.isSelected && (
                  <Check className="h-3 w-3" />
                )}
              </div>
            </div>
          </div>

          {/* Error message for this specific sport */}
          {hasError && errorMessage && (
            <div id={`${sport.id}-error`} className="mt-2">
              <FieldError
                error={errorMessage}
                field={sport.id}
                severity="error"
              />
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

/**
 * Enhanced Sports Selection Step with Validation
 */
export function ValidatedSportsSelectionStep() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { isAuthenticated, getIdToken, user } = useFirebaseAuth();

  // Component state
  const [sports, setSports] = useState<SportItem[]>([]);
  const [selectedCount, setSelectedCount] = useState(0);
  const [isApiAvailable, setIsApiAvailable] = useState(true);
  const [validationState, setValidationState] = useState<ValidationState>({
    isValidating: false,
    showValidationErrors: false,
    hasBeenSubmitted: false,
  });

  // Validation hook
  const validation = useSportsSelectionValidation();

  // Set up API client with Firebase authentication
  const queryConfigs = createApiQueryClient(
    isAuthenticated ? { getIdToken, isAuthenticated: true, userId: user?.uid } : undefined
  );

  // Fetch sports data with enhanced error handling
  const {
    data: sportsData,
    isLoading,
    error,
    refetch: refetchSports,
  } = useQuery({
    ...queryConfigs.getOnboardingSports(),
    retry: (failureCount, error) => {
      // Custom retry logic for sports fetching
      if (failureCount >= 3) return false;

      // Don't retry on 4xx errors
      const status = (error as any)?.status;
      if (status >= 400 && status < 500) return false;

      return true;
    },
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    onError: (error) => {
      reportOnboardingError(
        2,
        'Failed to fetch sports data',
        error instanceof Error ? error : new Error(String(error)),
        { userId: user?.uid }
      );
    },
  });

  // Track API availability
  useEffect(() => {
    if (error) {
      setIsApiAvailable(false);
      console.warn('Sports API unavailable, using fallback data:', error);
      toast({
        title: "Working Offline",
        description: "Using offline mode. Your progress will be saved.",
        variant: "default",
      });
    } else if (sportsData) {
      setIsApiAvailable(true);
    }
  }, [error, sportsData]);

  // Convert existing sports data to API format as fallback
  const fallbackSportsData: OnboardingSport[] = AVAILABLE_SPORTS.map(sport => ({
    id: sport.id,
    name: sport.name,
    icon: sport.icon || '🏃',
    hasTeams: sport.hasTeams,
    isPopular: ['nfl', 'nba', 'mlb', 'nhl'].includes(sport.id),
  }));

  // Use API data if available, otherwise use fallback
  const activeSportsData = sportsData || fallbackSportsData;

  // Initialize sports state when data loads
  useEffect(() => {
    if (activeSportsData) {
      // Try to restore previous selections from localStorage
      const localStatus = getLocalOnboardingStatus();
      const previousSelections = localStatus?.selectedSports || [];

      const sportsWithSelection = activeSportsData.map((sport) => {
        const previousSelection = previousSelections.find(s => s.sportId === sport.id);
        return {
          ...sport,
          isSelected: !!previousSelection,
          rank: previousSelection?.rank || 0,
        };
      });

      setSports(sportsWithSelection);
    }
  }, [activeSportsData]);

  // Update selected count and validate when sports change
  useEffect(() => {
    const selected = sports.filter(sport => sport.isSelected);
    setSelectedCount(selected.length);

    // Validate in real-time if user has attempted submission
    if (validationState.hasBeenSubmitted || validationState.showValidationErrors) {
      validation.validateSportsArray(sports);
    }
  }, [sports, validationState.hasBeenSubmitted, validationState.showValidationErrors, validation]);

  // Configure drag and drop sensors
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  // Toggle sport selection with validation
  const handleToggleSport = useCallback((sportId: string) => {
    setSports(prevSports => {
      const targetSport = prevSports.find(s => s.id === sportId);
      if (!targetSport) {
        return prevSports;
      }

      const orderedSelectedIds = prevSports
        .map((sport, index) => ({ sport, index }))
        .filter(({ sport }) => sport.isSelected)
        .sort((a, b) => {
          if (a.sport.rank && b.sport.rank) {
            return a.sport.rank - b.sport.rank;
          }
          if (a.sport.rank) return -1;
          if (b.sport.rank) return 1;
          return a.index - b.index;
        })
        .map(({ sport }) => sport.id);

      const isSelecting = !targetSport.isSelected;

      // Validate selection limit
      if (isSelecting && orderedSelectedIds.length >= 5) {
        validation.setFieldError('selectedSports', 'You can select a maximum of 5 sports. Please deselect one first.');
        toast({
          title: "Maximum 5 Sports",
          description: "You can select a maximum of 5 sports. Please deselect one first.",
          variant: "destructive",
        });
        return prevSports;
      }

      // Clear validation errors when making valid selections
      validation.clearFieldError('selectedSports');

      let nextSelectedOrder = orderedSelectedIds.filter(id => id !== sportId);
      if (isSelecting) {
        nextSelectedOrder = [...nextSelectedOrder, sportId];
      }

      return prevSports.map(sport => {
        const nextIndex = nextSelectedOrder.indexOf(sport.id);
        return {
          ...sport,
          isSelected: nextIndex !== -1,
          rank: nextIndex !== -1 ? nextIndex + 1 : 0,
        };
      });
    });

    // Mark as dirty for validation
    validation.touch();
  }, [validation]);

  // Handle drag end for reordering
  const handleDragEnd = useCallback((event: DragEndEvent) => {
    const { active, over } = event;

    if (over && active.id !== over.id) {
      setSports(items => {
        const selectedSports = items.filter(sport => sport.isSelected);
        const oldIndex = selectedSports.findIndex(sport => sport.id === active.id);
        const newIndex = selectedSports.findIndex(sport => sport.id === over.id);

        if (oldIndex !== -1 && newIndex !== -1) {
          const newSelectedOrder = arrayMove(selectedSports, oldIndex, newIndex);

          // Update ranks for reordered sports
          const updatedItems = items.map(sport => {
            if (sport.isSelected) {
              const newRankIndex = newSelectedOrder.findIndex(s => s.id === sport.id);
              return { ...sport, rank: newRankIndex + 1 };
            }
            return sport;
          });

          return updatedItems;
        }

        return items;
      });

      // Mark as dirty for validation
      validation.touch();
    }
  }, [validation]);

  // Quick selection actions
  const handleSelectAll = useCallback(() => {
    setSports(prevSports => {
      const existingSelection = prevSports
        .filter(sport => sport.isSelected)
        .sort((a, b) => {
          if (a.rank && b.rank) {
            return a.rank - b.rank;
          }
          if (a.rank) return -1;
          if (b.rank) return 1;
          return 0;
        })
        .map(sport => sport.id);

      const nextSelectedIds = [...existingSelection];

      for (const sport of prevSports) {
        if (nextSelectedIds.length >= 5) break;
        if (!nextSelectedIds.includes(sport.id)) {
          nextSelectedIds.push(sport.id);
        }
      }

      return prevSports.map(sport => {
        const index = nextSelectedIds.indexOf(sport.id);
        return {
          ...sport,
          isSelected: index !== -1,
          rank: index !== -1 ? index + 1 : 0,
        };
      });
    });

    validation.touch();
    validation.clearFieldError('selectedSports');
  }, [validation]);

  const handleClearAll = useCallback(() => {
    setSports(prevSports =>
      prevSports.map(sport => ({
        ...sport,
        isSelected: false,
        rank: 0,
      }))
    );

    validation.touch();
  }, [validation]);

  const handleSelectPopular = useCallback(() => {
    setSports(prevSports => {
      const popularRanks = new Map<string, number>();

      prevSports
        .filter(sport => sport.isPopular)
        .forEach((sport, index) => {
          popularRanks.set(sport.id, index + 1);
        });

      return prevSports.map(sport => ({
        ...sport,
        isSelected: sport.isPopular,
        rank: popularRanks.get(sport.id) ?? 0,
      }));
    });

    validation.touch();
    validation.clearFieldError('selectedSports');
  }, [validation]);

  // Enhanced submission with validation
  const handleContinue = useCallback(async () => {
    setValidationState(prev => ({
      ...prev,
      isValidating: true,
      hasBeenSubmitted: true,
      showValidationErrors: true,
    }));

    try {
      // Validate current selections
      const isValid = await validation.validateSportsData(sports);

      if (!isValid) {
        setValidationState(prev => ({ ...prev, isValidating: false }));
        toast({
          title: "Validation Error",
          description: "Please fix the errors below and try again.",
          variant: "destructive",
        });
        return;
      }

      const selectedSports = sports.filter(sport => sport.isSelected);

      // Convert to API format
      const sportsData = selectedSports.map(sport => ({
        sportId: sport.id,
        rank: sport.rank,
      }));

      // Always save to localStorage first
      updateLocalOnboardingStep(2, { selectedSports: sportsData });

      // Try to save to API if available
      if (isApiAvailable && isAuthenticated) {
        try {
          await retryableFetch.post('/api/onboarding/step', {
            step: 2,
            data: { sports: sportsData }
          });
          console.log('Sports selection saved to API');
        } catch (error) {
          console.warn('Failed to save sports to API, continuing with localStorage:', error);
          toast({
            title: "Saved Offline",
            description: "Your sports selection has been saved locally.",
            variant: "default",
          });
        }
      }

      // Navigation success
      setValidationState(prev => ({ ...prev, isValidating: false }));
      navigate("/onboarding/step/3");

    } catch (error) {
      setValidationState(prev => ({ ...prev, isValidating: false }));

      reportOnboardingError(
        2,
        'Failed to submit sports selection',
        error instanceof Error ? error : new Error(String(error)),
        { selectedCount, userId: user?.uid }
      );

      toast({
        title: "Submission Failed",
        description: "Failed to save your sports selection. Please try again.",
        variant: "destructive",
      });
    }
  }, [
    validation,
    sports,
    isApiAvailable,
    isAuthenticated,
    selectedCount,
    user?.uid,
    navigate
  ]);

  // Loading state
  if (isLoading && !activeSportsData.length) {
    return (
      <OnboardingLayout
        step={2}
        totalSteps={5}
        title="Choose Your Sports"
        subtitle="Loading sports..."
        showProgress={true}
        completedSteps={1}
      >
        <SportsSelectionSkeleton />
      </OnboardingLayout>
    );
  }

  // Error state when API fails and no fallback data
  if (error && !activeSportsData.length) {
    const recoverySteps = [
      'Check your internet connection',
      'Try refreshing the page',
      'If the problem persists, contact support',
    ];

    return (
      <OnboardingLayout
        step={2}
        totalSteps={5}
        title="Choose Your Sports"
        subtitle="Error loading sports"
        showProgress={true}
        completedSteps={1}
      >
        <div className="space-y-6">
          <ErrorAlert
            title="Failed to Load Sports"
            message="We couldn't load the sports data. Please try again."
            severity="error"
            recoveryActions={[
              {
                label: 'Retry',
                action: () => refetchSports(),
                variant: 'default',
                icon: Loader2,
              },
            ]}
          />
          <RecoveryGuidance steps={recoverySteps} />
        </div>
      </OnboardingLayout>
    );
  }

  // Empty state
  if (activeSportsData.length === 0) {
    return (
      <OnboardingLayout
        step={2}
        totalSteps={5}
        title="Choose Your Sports"
        subtitle="No sports available"
        showProgress={true}
        completedSteps={1}
      >
        <ErrorAlert
          title="No Sports Available"
          message="No sports data is available at this time."
          severity="warning"
        />
      </OnboardingLayout>
    );
  }

  // Main render
  return (
    <OnboardingLayout
      step={2}
      totalSteps={5}
      title="Choose Your Sports"
      subtitle="Select and rank your favorite sports"
      showProgress={true}
      completedSteps={1}
      onNext={handleContinue}
      isNextDisabled={selectedCount === 0 || validationState.isValidating}
    >
      <div className="space-y-6">
        {/* Offline indicator */}
        {!isApiAvailable && (
          <ErrorAlert
            title="Working Offline"
            message="Your selections are being saved locally and will sync when connection is restored."
            severity="warning"
          />
        )}

        {/* Validation errors */}
        {validationState.showValidationErrors && validation.hasErrors && (
          <ErrorAlert
            title="Please Fix These Issues"
            message="There are some issues with your selections that need to be fixed."
            severity="error"
          />
        )}

        {/* Field-level errors */}
        {validation.fieldErrors.selectedSports && (
          <FieldError
            error={validation.fieldErrors.selectedSports}
            field="selectedSports"
            severity="error"
            onClear={() => validation.clearFieldError('selectedSports')}
            helpText="You can select between 1 and 5 sports. Each sport will be ranked by your preference."
          />
        )}

        {/* Instructions */}
        <div className="text-center space-y-4">
          <p className="text-lg font-body text-muted-foreground">
            Choose your favorite sports and drag to reorder them by preference.
          </p>

          {/* Action buttons */}
          <div className="flex flex-wrap justify-center gap-3">
            <Button variant="outline" onClick={handleSelectPopular}>
              Popular Sports
            </Button>
            <Button variant="outline" onClick={handleSelectAll}>
              Select All
            </Button>
            <Button variant="outline" onClick={handleClearAll}>
              Clear All
            </Button>
          </div>

          {/* Status */}
          <div className="flex items-center justify-center gap-2">
            <span className="font-display font-semibold text-primary">
              {selectedCount} sports selected
            </span>
            {selectedCount > 0 && !validation.hasErrors && (
              <Check className="h-4 w-4 text-primary" />
            )}
            {validation.hasErrors && (
              <AlertCircle className="h-4 w-4 text-red-500" />
            )}
          </div>
        </div>

        {/* Sports list */}
        <div className="space-y-4">
          <DndContext
            sensors={sensors}
            collisionDetection={closestCenter}
            onDragEnd={handleDragEnd}
          >
            <SortableContext
              items={sports.map(sport => sport.id)}
              strategy={verticalListSortingStrategy}
            >
              <div className="space-y-3">
                {sports.map(sport => (
                  <SortableSportItem
                    key={sport.id}
                    sport={sport}
                    onToggle={handleToggleSport}
                    hasError={validation.fieldErrors.selectedSports && !sport.isSelected && selectedCount === 0}
                    errorMessage={validation.fieldErrors.selectedSports}
                  />
                ))}
              </div>
            </SortableContext>
          </DndContext>
        </div>

        {/* Help tip */}
        {selectedCount > 1 && (
          <div className="bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
            <p className="text-sm text-blue-800 dark:text-blue-200 font-body">
              <strong>Tip:</strong> Drag sports up or down to rank them by your interest level.
              Your #1 choice will get priority in your personalized feed.
            </p>
          </div>
        )}

        {/* Continue button state */}
        {validationState.isValidating && (
          <div className="flex justify-center">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Validating your selections...</span>
            </div>
          </div>
        )}
      </div>
    </OnboardingLayout>
  );
}

export default ValidatedSportsSelectionStep;