import { useState, useEffect } from "react";
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
import {
  useSortable,
  SortableContext as SortableContextType,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { toast } from "@/components/ui/use-toast";
import { GripVertical, Check, AlertCircle } from "lucide-react";
import { OnboardingLayout } from "./OnboardingLayout";
import { createApiQueryClient, type OnboardingSport, apiClient } from "@/lib/api-client";
import { useFirebaseAuth } from "@/contexts/FirebaseAuthContext";
import { AVAILABLE_SPORTS } from "@/data/sports";
import { updateLocalOnboardingStep, getLocalOnboardingStatus } from "@/lib/onboarding-storage";
import { cn } from "@/lib/utils";

interface SportItem extends OnboardingSport {
  isSelected: boolean;
  rank: number;
}

/**
 * Validate sport rankings for integrity
 * Checks for duplicate ranks, missing ranks, and other inconsistencies
 */
function validateRankIntegrity(sports: SportItem[]): {
  isValid: boolean;
  errors: string[];
} {
  const errors: string[] = [];
  const selectedSports = sports.filter(sport => sport.isSelected);

  if (selectedSports.length === 0) {
    return { isValid: true, errors: [] };
  }

  // Check for duplicate ranks
  const ranks = selectedSports.map(sport => sport.rank);
  const uniqueRanks = new Set(ranks);
  if (ranks.length !== uniqueRanks.size) {
    errors.push('Duplicate ranks detected');
  }

  // Check for invalid rank values
  const invalidRanks = selectedSports.filter(sport =>
    sport.rank <= 0 || sport.rank > selectedSports.length || !Number.isInteger(sport.rank)
  );
  if (invalidRanks.length > 0) {
    errors.push('Invalid rank values detected');
  }

  // Check for missing ranks in sequence
  const sortedRanks = [...ranks].sort((a, b) => a - b);
  for (let i = 0; i < sortedRanks.length; i++) {
    if (sortedRanks[i] !== i + 1) {
      errors.push('Missing ranks in sequence');
      break;
    }
  }

  // Check that unselected sports have rank 0
  const unselectedWithRank = sports.filter(sport => !sport.isSelected && sport.rank !== 0);
  if (unselectedWithRank.length > 0) {
    errors.push('Unselected sports have non-zero ranks');
  }

  return {
    isValid: errors.length === 0,
    errors
  };
}

/**
 * Centralized utility function to normalize sport rankings
 * Ensures selected sports have consecutive ranks starting from 1
 * Preserves rank order for selected sports and sets rank to 0 for unselected
 */
function normalizeRanks(sports: SportItem[]): SportItem[] {
  // First validate the current state
  const validation = validateRankIntegrity(sports);
  if (!validation.isValid) {
    console.warn('Rank integrity issues detected before normalization:', validation.errors);
  }

  const selectedSports = sports.filter(sport => sport.isSelected);

  // Sort selected sports by their current rank to preserve order
  const sortedSelected = selectedSports.sort((a, b) => {
    // Handle case where ranks might be 0 or invalid
    if (a.rank === 0 && b.rank === 0) return 0;
    if (a.rank === 0) return 1;
    if (b.rank === 0) return -1;
    return a.rank - b.rank;
  });

  const normalizedSports = sports.map(sport => {
    if (!sport.isSelected) {
      // Only create new object if rank actually needs to change
      return sport.rank === 0 ? sport : { ...sport, rank: 0 };
    }

    const newRank = sortedSelected.findIndex(s => s.id === sport.id) + 1;
    // Only create new object if rank actually needs to change
    return sport.rank === newRank ? sport : { ...sport, rank: newRank };
  });

  // Validate the normalized result
  const postValidation = validateRankIntegrity(normalizedSports);
  if (!postValidation.isValid) {
    console.error('Rank normalization failed - integrity issues remain:', postValidation.errors);
    // In a production environment, you might want to throw an error or provide fallback logic
  }

  return normalizedSports;
}

interface SortableSportItemProps {
  sport: SportItem;
  onToggle: (sportId: string) => void;
}

function SortableSportItem({ sport, onToggle }: SortableSportItemProps) {
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

  const handleCardClick = (event: React.MouseEvent) => {
    // Prevent card click when dragging or clicking on drag handle
    if (isDragging) return;

    // Check if click originated from drag handle
    const target = event.target as HTMLElement;
    if (target.closest('[data-drag-handle="true"]')) return;

    onToggle(sport.id);
  };

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      onToggle(sport.id);
    }
  };

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
        aria-label={`${sport.isSelected ? 'Deselect' : 'Select'} ${sport.name}${sport.isSelected ? `, currently ranked #${sport.rank}` : ''}`}
        onClick={handleCardClick}
        onKeyDown={handleKeyDown}
        className={cn(
          "transition-all duration-200 hover:shadow-md cursor-pointer focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2",
          sport.isSelected
            ? "ring-2 ring-primary bg-primary/5 hover:bg-primary/10"
            : "hover:bg-muted/50 hover:border-primary/20"
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
              title={sport.isSelected ? "Drag to reorder" : "Drag to select and reorder"}
            >
              <GripVertical className={cn(
                "h-5 w-5 transition-colors",
                sport.isSelected
                  ? "text-muted-foreground"
                  : "text-muted-foreground/60 hover:text-muted-foreground"
              )} />
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
                  {sport.rank === 1 ? '1st' : sport.rank === 2 ? '2nd' : sport.rank === 3 ? '3rd' : `${sport.rank}th`}
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
        </CardContent>
      </Card>
    </div>
  );
}

export function SportsSelectionStep() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { isAuthenticated, getIdToken, user } = useFirebaseAuth();

  const [sports, setSports] = useState<SportItem[]>([]);
  const [selectedCount, setSelectedCount] = useState(0);
  const [isApiAvailable, setIsApiAvailable] = useState(true);

  // Set up API client with Firebase authentication
  const queryConfigs = createApiQueryClient(
    isAuthenticated ? { getIdToken, isAuthenticated: true, userId: user?.uid } : undefined
  );

  // Fetch sports data with fallback
  const {
    data: sportsData,
    isLoading,
    error,
  } = useQuery({
    ...queryConfigs.getOnboardingSports(),
    retry: 2, // Limit retries for faster fallback
    retryDelay: 1000, // Shorter delay for faster fallback
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
    }
  }, [error]);

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

      const sportsWithSelection = activeSportsData.map((sport, index) => {
        const previousSelection = previousSelections.find(s => s.sportId === sport.id);
        return {
          ...sport,
          isSelected: !!previousSelection,
          rank: previousSelection?.rank || 0,
        };
      });

      // Sort sports to preserve user's rank preferences:
      // 1. Selected sports sorted by rank (ascending)
      // 2. Unselected sports in original API order
      const sortedSports = [...sportsWithSelection].sort((a, b) => {
        // If both are selected, sort by rank
        if (a.isSelected && b.isSelected) {
          return a.rank - b.rank;
        }

        // Selected sports come first
        if (a.isSelected && !b.isSelected) {
          return -1;
        }

        if (!a.isSelected && b.isSelected) {
          return 1;
        }

        // For unselected sports, maintain original API order
        const aOriginalIndex = activeSportsData.findIndex(s => s.id === a.id);
        const bOriginalIndex = activeSportsData.findIndex(s => s.id === b.id);
        return aOriginalIndex - bOriginalIndex;
      });

      setSports(sortedSports);
    }
  }, [activeSportsData]);

  // Update selected count
  useEffect(() => {
    setSelectedCount(sports.filter(sport => sport.isSelected).length);
  }, [sports]);

  // Configure drag and drop sensors
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const handleToggleSport = (sportId: string) => {
    setSports(prevSports => {
      const currentSelected = prevSports.filter(s => s.isSelected);
      const targetSport = prevSports.find(s => s.id === sportId);

      // If trying to select and already at maximum (5), show warning
      if (!targetSport?.isSelected && currentSelected.length >= 5) {
        toast({
          title: "Maximum 5 Sports",
          description: "You can select a maximum of 5 sports. Please deselect one first.",
          variant: "destructive",
        });
        return prevSports;
      }

      // Single atomic update: toggle selection state and normalize ranks
      const updatedSports = prevSports.map(sport => {
        if (sport.id === sportId) {
          const newIsSelected = !sport.isSelected;
          if (newIsSelected) {
            // Assign temporary rank that will be normalized
            return { ...sport, isSelected: true, rank: currentSelected.length + 1 };
          } else {
            // Remove from selection
            return { ...sport, isSelected: false, rank: 0 };
          }
        }
        return sport;
      });

      // Apply rank normalization to ensure consistent consecutive ranks
      const normalizedSports = normalizeRanks(updatedSports);

      // Immediately save toggle changes to localStorage
      try {
        const selectedSportsData = normalizedSports
          .filter(sport => sport.isSelected)
          .map(sport => ({
            sportId: sport.id,
            rank: sport.rank,
          }));

        updateLocalOnboardingStep(2, { selectedSports: selectedSportsData });
      } catch (error) {
        console.warn('Failed to save toggle changes to localStorage:', error);
        toast({
          title: "Save Warning",
          description: "Changes may not be preserved. Please try again.",
          variant: "destructive",
        });
      }

      return normalizedSports;
    });
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (over && active.id !== over.id) {
      setSports(items => {
        const activeSport = items.find(sport => sport.id === active.id);
        const overSport = items.find(sport => sport.id === over.id);

        if (!activeSport || !overSport) {
          return items;
        }

        // Auto-select the dragged sport if it's not already selected
        let updatedItems = items;
        if (!activeSport.isSelected) {
          // Check if we can select more sports (max 5)
          const currentSelected = items.filter(s => s.isSelected);
          if (currentSelected.length >= 5) {
            toast({
              title: "Maximum 5 Sports",
              description: "You can select a maximum of 5 sports. Please deselect one first.",
              variant: "destructive",
            });
            return items;
          }

          // Auto-select the dragged sport
          updatedItems = items.map(sport => {
            if (sport.id === active.id) {
              return { ...sport, isSelected: true, rank: currentSelected.length + 1 };
            }
            return sport;
          });
        }

        // Now handle the reordering logic
        const selectedSports = updatedItems.filter(sport => sport.isSelected);
        const oldIndex = selectedSports.findIndex(sport => sport.id === active.id);
        const newIndex = selectedSports.findIndex(sport => sport.id === over.id);

        if (oldIndex !== -1 && newIndex !== -1) {
          const newSelectedOrder = arrayMove(selectedSports, oldIndex, newIndex);

          // Update sports with new drag order, then normalize ranks
          const finalItems = updatedItems.map(sport => {
            if (sport.isSelected) {
              const newRankIndex = newSelectedOrder.findIndex(s => s.id === sport.id);
              return { ...sport, rank: newRankIndex + 1 };
            }
            return sport;
          });

          // Apply normalization to ensure consistency
          const normalizedItems = normalizeRanks(finalItems);

          // Immediately save changes to localStorage after drag operation
          try {
            const selectedSportsData = normalizedItems
              .filter(sport => sport.isSelected)
              .map(sport => ({
                sportId: sport.id,
                rank: sport.rank,
              }));

            updateLocalOnboardingStep(2, { selectedSports: selectedSportsData });
          } catch (error) {
            console.warn('Failed to save drag changes to localStorage:', error);
            toast({
              title: "Save Warning",
              description: "Changes may not be preserved. Please try again.",
              variant: "destructive",
            });
          }

          return normalizedItems;
        }

        // If we auto-selected but couldn't reorder, still apply normalization and save
        const normalizedItems = normalizeRanks(updatedItems);

        // Save auto-selection to localStorage
        try {
          const selectedSportsData = normalizedItems
            .filter(sport => sport.isSelected)
            .map(sport => ({
              sportId: sport.id,
              rank: sport.rank,
            }));

          updateLocalOnboardingStep(2, { selectedSports: selectedSportsData });
        } catch (error) {
          console.warn('Failed to save auto-selection to localStorage:', error);
        }

        return normalizedItems;
      });
    }
  };

  const handleSelectAll = () => {
    setSports(prevSports => {
      const updatedSports = prevSports.map(sport => ({
        ...sport,
        isSelected: true,
        rank: sport.rank || 1, // Preserve existing rank or default to 1
      }));

      // Use normalizeRanks to ensure proper consecutive ranking
      const normalizedSports = normalizeRanks(updatedSports);

      // Immediately save changes to localStorage
      try {
        const selectedSportsData = normalizedSports
          .filter(sport => sport.isSelected)
          .map(sport => ({
            sportId: sport.id,
            rank: sport.rank,
          }));

        updateLocalOnboardingStep(2, { selectedSports: selectedSportsData });
      } catch (error) {
        console.warn('Failed to save select all changes to localStorage:', error);
      }

      return normalizedSports;
    });
  };

  const handleClearAll = () => {
    setSports(prevSports => {
      const updatedSports = prevSports.map(sport => ({
        ...sport,
        isSelected: false,
        rank: 0,
      }));

      // Use normalizeRanks for consistency (though all ranks will be 0)
      const normalizedSports = normalizeRanks(updatedSports);

      // Immediately save changes to localStorage
      try {
        const selectedSportsData = normalizedSports
          .filter(sport => sport.isSelected)
          .map(sport => ({
            sportId: sport.id,
            rank: sport.rank,
          }));

        updateLocalOnboardingStep(2, { selectedSports: selectedSportsData });
      } catch (error) {
        console.warn('Failed to save clear all changes to localStorage:', error);
      }

      return normalizedSports;
    });
  };

  const handleSelectPopular = () => {
    setSports(prevSports => {
      // First, select all popular sports and give them priority ranking
      const updatedSports = prevSports.map(sport => {
        if (sport.isPopular) {
          return {
            ...sport,
            isSelected: true,
            rank: 1, // Will be properly ranked by normalizeRanks
          };
        } else {
          return {
            ...sport,
            isSelected: false,
            rank: 0,
          };
        }
      });

      // Use normalizeRanks to ensure proper consecutive ranking for popular sports
      const normalizedSports = normalizeRanks(updatedSports);

      // Immediately save changes to localStorage
      try {
        const selectedSportsData = normalizedSports
          .filter(sport => sport.isSelected)
          .map(sport => ({
            sportId: sport.id,
            rank: sport.rank,
          }));

        updateLocalOnboardingStep(2, { selectedSports: selectedSportsData });
      } catch (error) {
        console.warn('Failed to save select popular changes to localStorage:', error);
      }

      return normalizedSports;
    });
  };

  const handleContinue = async () => {
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
        await apiClient.updateOnboardingStep({
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

    // Navigate to next step
    navigate("/onboarding/step/3");
  };

  const selectedSports = sports.filter(sport => sport.isSelected);
  const sortedSelectedSports = selectedSports.sort((a, b) => a.rank - b.rank);

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
        <div className="flex justify-center py-12" data-testid="loading-sports">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      </OnboardingLayout>
    );
  }

  // Error state when API fails and no fallback data
  if (error && !activeSportsData.length) {
    return (
      <OnboardingLayout
        step={2}
        totalSteps={5}
        title="Choose Your Sports"
        subtitle="Error loading sports"
        showProgress={true}
        completedSteps={1}
      >
        <div className="text-center py-12">
          <p className="text-red-600 dark:text-red-400">
            Error loading sports. Please try again.
          </p>
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
        <div className="text-center py-12">
          <p className="text-muted-foreground">
            No sports available at this time.
          </p>
        </div>
      </OnboardingLayout>
    );
  }

  return (
    <OnboardingLayout
      step={2}
      totalSteps={5}
      title="Choose Your Sports"
      subtitle="Select and rank your favorite sports"
      showProgress={true}
      completedSteps={1}
      onNext={handleContinue}
      isNextDisabled={selectedCount === 0}
    >
      <div className="space-y-6">
        {/* Offline indicator */}
        {!isApiAvailable && (
          <div className="bg-orange-50 dark:bg-orange-950/30 border border-orange-200 dark:border-orange-800 rounded-lg p-4">
            <div className="flex items-center gap-3">
              <AlertCircle className="h-5 w-5 text-orange-600 dark:text-orange-400" />
              <div className="text-sm">
                <p className="font-medium text-orange-800 dark:text-orange-200">
                  Working Offline
                </p>
                <p className="text-orange-700 dark:text-orange-300">
                  Your selections are being saved locally and will sync when connection is restored.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Instructions */}
        <div className="text-center space-y-4">
          <p className="text-lg font-body text-muted-foreground">
            Click to select sports or drag them to select and reorder by preference.
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
            {selectedCount > 0 && (
              <Check className="h-4 w-4 text-primary" />
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
                  />
                ))}
              </div>
            </SortableContext>
          </DndContext>
        </div>

        {/* Tip */}
        {selectedCount > 0 && (
          <div className="bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
            <p className="text-sm text-blue-800 dark:text-blue-200 font-body">
              <strong>Tip:</strong> {selectedCount === 1
                ? "Select more sports and drag to rank them by your interest level."
                : "Drag sports up or down to rank them by your interest level."
              } Your #1 choice will get priority in your personalized feed.
            </p>
          </div>
        )}
      </div>
    </OnboardingLayout>
  );
}

export default SportsSelectionStep;