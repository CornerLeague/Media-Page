/**
 * SportsEditSection Component
 *
 * Reusable sports selection component for preferences editing.
 * Based on the existing SportsSelectionStep from onboarding.
 */

import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { toast } from '@/components/ui/use-toast';
import { GripVertical, Check, Save, Plus, AlertCircle } from 'lucide-react';
import { createApiQueryClient, type OnboardingSport } from '@/lib/api-client';
import { useFirebaseAuth } from '@/contexts/FirebaseAuthContext';
import { AVAILABLE_SPORTS } from '@/data/sports';
import { type SportPreference } from '@/hooks/usePreferences';
import { cn } from '@/lib/utils';

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
    if (isDragging) return;
    const target = event.target as HTMLElement;
    if (target.closest('[data-drag-handle="true"]')) return;
    onToggle(sport.id);
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={cn('touch-none', isDragging && 'opacity-50')}
    >
      <Card
        data-testid={`sport-card-${sport.id}`}
        data-selected={sport.isSelected}
        role="button"
        tabIndex={0}
        aria-selected={sport.isSelected}
        onClick={handleCardClick}
        className={cn(
          'transition-all duration-200 hover:shadow-md cursor-pointer focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2',
          sport.isSelected
            ? 'ring-2 ring-primary bg-primary/5 hover:bg-primary/10'
            : 'hover:bg-muted/50 hover:border-primary/20'
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
                'h-5 w-5 rounded border-2 flex items-center justify-center transition-colors',
                sport.isSelected
                  ? 'bg-primary border-primary text-primary-foreground'
                  : 'border-muted-foreground'
              )}>
                {sport.isSelected && <Check className="h-3 w-3" />}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

interface SportsEditSectionProps {
  sports: SportPreference[];
  onSportsChange: (sports: SportPreference[]) => void;
  onSave: () => Promise<void>;
  isSaving: boolean;
  error: Error | null;
}

export function SportsEditSection({
  sports,
  onSportsChange,
  onSave,
  isSaving,
  error,
}: SportsEditSectionProps) {
  const { isAuthenticated, getIdToken, user } = useFirebaseAuth();
  const [sportsState, setSportsState] = useState<SportItem[]>([]);
  const [isApiAvailable, setIsApiAvailable] = useState(true);

  // Set up API client
  const queryConfigs = createApiQueryClient(
    isAuthenticated ? { getIdToken, isAuthenticated: true, userId: user?.uid } : undefined
  );

  // Fetch available sports
  const {
    data: availableSportsData,
    isLoading,
    error: apiError,
  } = useQuery({
    ...queryConfigs.getOnboardingSports(),
    retry: 2,
    retryDelay: 1000,
  });

  // Track API availability
  useEffect(() => {
    if (apiError) {
      setIsApiAvailable(false);
      console.warn('Sports API unavailable, using fallback data:', apiError);
    }
  }, [apiError]);

  // Fallback sports data
  const fallbackSportsData: OnboardingSport[] = AVAILABLE_SPORTS.map(sport => ({
    id: sport.id,
    name: sport.name,
    icon: sport.icon || '🏃',
    hasTeams: sport.hasTeams,
    isPopular: ['nfl', 'nba', 'mlb', 'nhl'].includes(sport.id),
  }));

  const activeSportsData = availableSportsData || fallbackSportsData;

  // Initialize sports state
  useEffect(() => {
    if (activeSportsData.length > 0) {
      const sportsWithSelection = activeSportsData.map((sport) => {
        const existingSport = sports.find(s => s.sportId === sport.id);
        return {
          ...sport,
          isSelected: !!existingSport,
          rank: existingSport?.rank || 0,
        };
      });

      setSportsState(sportsWithSelection);
    }
  }, [activeSportsData, sports]);

  // Configure drag and drop sensors
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const handleToggleSport = (sportId: string) => {
    setSportsState(prevSports => {
      const targetSport = prevSports.find(s => s.id === sportId);
      if (!targetSport) return prevSports;

      const orderedSelectedIds = prevSports
        .filter(sport => sport.isSelected)
        .sort((a, b) => a.rank - b.rank)
        .map(sport => sport.id);

      const isSelecting = !targetSport.isSelected;

      if (isSelecting && orderedSelectedIds.length >= 5) {
        toast({
          title: 'Maximum 5 Sports',
          description: 'You can select a maximum of 5 sports. Please deselect one first.',
          variant: 'destructive',
        });
        return prevSports;
      }

      let nextSelectedOrder = orderedSelectedIds.filter(id => id !== sportId);
      if (isSelecting) {
        nextSelectedOrder = [...nextSelectedOrder, sportId];
      }

      const updatedSports = prevSports.map(sport => {
        const nextIndex = nextSelectedOrder.indexOf(sport.id);
        return {
          ...sport,
          isSelected: nextIndex !== -1,
          rank: nextIndex !== -1 ? nextIndex + 1 : 0,
        };
      });

      // Update parent component
      const selectedSports: SportPreference[] = updatedSports
        .filter(sport => sport.isSelected)
        .map(sport => ({
          sportId: sport.id,
          name: sport.name,
          rank: sport.rank,
          hasTeams: sport.hasTeams,
        }));

      onSportsChange(selectedSports);
      return updatedSports;
    });
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (over && active.id !== over.id) {
      setSportsState(items => {
        const selectedSports = items.filter(sport => sport.isSelected);
        const oldIndex = selectedSports.findIndex(sport => sport.id === active.id);
        const newIndex = selectedSports.findIndex(sport => sport.id === over.id);

        if (oldIndex !== -1 && newIndex !== -1) {
          const newSelectedOrder = arrayMove(selectedSports, oldIndex, newIndex);

          const updatedItems = items.map(sport => {
            if (sport.isSelected) {
              const newRankIndex = newSelectedOrder.findIndex(s => s.id === sport.id);
              return { ...sport, rank: newRankIndex + 1 };
            }
            return sport;
          });

          // Update parent component
          const selectedSportsPrefs: SportPreference[] = newSelectedOrder.map((sport, index) => ({
            sportId: sport.id,
            name: sport.name,
            rank: index + 1,
            hasTeams: sport.hasTeams,
          }));

          onSportsChange(selectedSportsPrefs);
          return updatedItems;
        }

        return items;
      });
    }
  };

  const selectedCount = sportsState.filter(sport => sport.isSelected).length;

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Sports Preferences</CardTitle>
          <CardDescription>Loading available sports...</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              Sports Preferences
              <Badge variant="outline">{selectedCount} selected</Badge>
            </CardTitle>
            <CardDescription>
              Select and rank your favorite sports (maximum 5)
            </CardDescription>
          </div>
          <Button
            onClick={onSave}
            disabled={isSaving || selectedCount === 0}
            size="sm"
          >
            {isSaving ? (
              <>
                <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                Saving...
              </>
            ) : (
              <>
                <Save className="mr-2 h-4 w-4" />
                Save Sports
              </>
            )}
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {!isApiAvailable && (
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              Working offline. Your changes will be saved when connection is restored.
            </AlertDescription>
          </Alert>
        )}

        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error.message}</AlertDescription>
          </Alert>
        )}

        <div className="text-center">
          <p className="text-sm text-muted-foreground mb-4">
            Drag sports to reorder them by preference. Your #1 choice gets priority in your feed.
          </p>
        </div>

        <DndContext
          sensors={sensors}
          collisionDetection={closestCenter}
          onDragEnd={handleDragEnd}
        >
          <SortableContext
            items={sportsState.map(sport => sport.id)}
            strategy={verticalListSortingStrategy}
          >
            <div className="space-y-3">
              {sportsState.map(sport => (
                <SortableSportItem
                  key={sport.id}
                  sport={sport}
                  onToggle={handleToggleSport}
                />
              ))}
            </div>
          </SortableContext>
        </DndContext>

        {selectedCount > 1 && (
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              <strong>Tip:</strong> Drag sports up or down to rank them by your interest level.
              Your #1 choice will get priority in your personalized feed.
            </AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  );
}