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

      setSports(sportsWithSelection);
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

      if (isSelecting && orderedSelectedIds.length >= 5) {
        toast({
          title: "Maximum 5 Sports",
          description: "You can select a maximum of 5 sports. Please deselect one first.",
          variant: "destructive",
        });
        return prevSports;
      }

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
  };

  const handleDragEnd = (event: DragEndEvent) => {
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
    }
  };

  const handleSelectAll = () => {
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
  };

  const handleClearAll = () => {
    setSports(prevSports =>
      prevSports.map(sport => ({
        ...sport,
        isSelected: false,
        rank: 0,
      }))
    );
  };

  const handleSelectPopular = () => {
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
        {selectedCount > 1 && (
          <div className="bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
            <p className="text-sm text-blue-800 dark:text-blue-200 font-body">
              <strong>Tip:</strong> Drag sports up or down to rank them by your interest level.
              Your #1 choice will get priority in your personalized feed.
            </p>
          </div>
        )}
      </div>
    </OnboardingLayout>
  );
}

export default SportsSelectionStep;