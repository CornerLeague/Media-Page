import React, { useState, useEffect } from 'react';
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  TouchSensor,
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
import {
  useSortable,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { GripVertical, Trophy, Users, ChevronRight } from 'lucide-react';
import { useOnboarding } from '@/hooks/useOnboarding';
import { useDeviceCapabilities, useTouchOptimizedButton } from '@/hooks/useTouch';
import { AVAILABLE_SPORTS } from '@/data/sports';
import { SportPreference } from '@/lib/types/onboarding-types';

interface SortableSportItemProps {
  sport: SportPreference;
  index: number;
  isSelected: boolean;
  onToggle: (sportId: string) => void;
}

const SortableSportItem: React.FC<SortableSportItemProps> = ({
  sport,
  index,
  isSelected,
  onToggle,
}) => {
  const { isTouchDevice } = useDeviceCapabilities();
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: sport.sportId });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  const sportData = AVAILABLE_SPORTS.find(s => s.id === sport.sportId);

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`${isDragging ? 'opacity-50' : ''} ${
        isDragging ? 'z-10 scale-105' : ''
      } transition-all duration-200`}
    >
      <Card className={`cursor-pointer transition-all ${
        isSelected ? 'border-primary bg-primary/5' : 'hover:border-muted-foreground/50'
      } ${isDragging ? 'shadow-lg' : ''} active:scale-[0.98]`}>
        <CardContent className={`${isTouchDevice ? 'p-5' : 'p-4'} min-h-[60px] flex items-center`}>
          <div className="flex items-center space-x-3 w-full">
            {/* Drag handle */}
            <button
              {...attributes}
              {...listeners}
              className={`text-muted-foreground hover:text-foreground touch-manipulation ${
                isTouchDevice ? 'p-2 -m-2' : ''
              }`}
              aria-label={`Reorder ${sport.name}`}
              style={{ touchAction: 'none' }}
            >
              <GripVertical className={`${isTouchDevice ? 'h-5 w-5' : 'h-4 w-4'}`} />
            </button>

            {/* Sport icon */}
            <div className="text-2xl">
              {sportData?.icon || '🏆'}
            </div>

            {/* Sport info */}
            <div className="flex-1">
              <div className="flex items-center space-x-2">
                <h3 className="font-semibold">{sport.name}</h3>
                {sport.hasTeams && (
                  <Badge variant="secondary" className="text-xs">
                    <Users className="h-3 w-3 mr-1" />
                    Teams
                  </Badge>
                )}
              </div>
              <p className="text-sm text-muted-foreground">
                Rank #{sport.rank}
              </p>
            </div>

            {/* Selection checkbox */}
            <div className={`${isTouchDevice ? 'p-2 -m-2' : ''} touch-manipulation`}>
              <Checkbox
                checked={isSelected}
                onCheckedChange={() => onToggle(sport.sportId)}
                aria-label={`${isSelected ? 'Deselect' : 'Select'} ${sport.name}`}
                className={isTouchDevice ? 'h-5 w-5' : ''}
              />
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

const SportsSelection: React.FC = () => {
  const { userPreferences, updateSports, setError, clearErrors } = useOnboarding();
  const { isTouchDevice, screenSize } = useDeviceCapabilities();
  const [availableSports, setAvailableSports] = useState<SportPreference[]>([]);
  const [selectedSportIds, setSelectedSportIds] = useState<Set<string>>(new Set());

  // Initialize available sports and selected sports
  useEffect(() => {
    const initialSports: SportPreference[] = AVAILABLE_SPORTS.map((sport, index) => ({
      sportId: sport.id,
      name: sport.name,
      rank: index + 1,
      hasTeams: sport.hasTeams,
    }));

    setAvailableSports(initialSports);

    // Set selected sports from user preferences
    if (userPreferences.sports) {
      const selectedIds = new Set(userPreferences.sports.map(s => s.sportId));
      setSelectedSportIds(selectedIds);
    }
  }, [userPreferences.sports]);

  // Update user preferences when selection changes
  useEffect(() => {
    const selectedSports = availableSports.filter(sport =>
      selectedSportIds.has(sport.sportId)
    );
    updateSports(selectedSports);

    // Clear errors when selection changes
    if (selectedSports.length > 0) {
      clearErrors();
    }
  }, [selectedSportIds, availableSports, updateSports, clearErrors]);

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (over && active.id !== over.id) {
      setAvailableSports((sports) => {
        const oldIndex = sports.findIndex(sport => sport.sportId === active.id);
        const newIndex = sports.findIndex(sport => sport.sportId === over.id);

        const newSports = arrayMove(sports, oldIndex, newIndex);

        // Update ranks
        return newSports.map((sport, index) => ({
          ...sport,
          rank: index + 1,
        }));
      });
    }
  };

  const handleToggleSport = (sportId: string) => {
    setSelectedSportIds(prev => {
      const newSet = new Set(prev);
      if (newSet.has(sportId)) {
        newSet.delete(sportId);
      } else {
        newSet.add(sportId);
      }
      return newSet;
    });
  };

  const handleSelectPopular = () => {
    const popularSports = ['nfl', 'nba', 'mlb', 'nhl'];
    setSelectedSportIds(new Set(popularSports));
  };

  const handleSelectAll = () => {
    const allSportIds = availableSports.map(sport => sport.sportId);
    setSelectedSportIds(new Set(allSportIds));
  };

  const handleClearAll = () => {
    setSelectedSportIds(new Set());
  };

  // Touch-optimized button handlers
  const popularButtonProps = useTouchOptimizedButton(handleSelectPopular, {
    hapticFeedback: 'light',
    preventDoubleClick: true,
  });

  const selectAllButtonProps = useTouchOptimizedButton(handleSelectAll, {
    hapticFeedback: 'light',
    preventDoubleClick: true,
  });

  const clearAllButtonProps = useTouchOptimizedButton(handleClearAll, {
    hapticFeedback: 'medium',
    preventDoubleClick: true,
  });

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: isTouchDevice ? 10 : 3, // Increase distance for touch devices
      },
    }),
    useSensor(TouchSensor, {
      activationConstraint: {
        delay: 200, // Add delay for touch to distinguish from scroll
        tolerance: 5,
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const selectedCount = selectedSportIds.size;
  const hasMinimumSelection = selectedCount >= 1;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center space-y-2">
        <div className="flex justify-center mb-4">
          <Trophy className="h-8 w-8 text-primary" />
        </div>
        <p className="text-muted-foreground">
          Select and rank your favorite sports. You can drag to reorder by preference.
        </p>
      </div>

      {/* Quick actions */}
      <div className="flex flex-wrap gap-2 justify-center">
        <Button
          {...popularButtonProps}
          variant="outline"
          size={screenSize === 'mobile' ? 'default' : 'sm'}
          className={`text-xs ${isTouchDevice ? 'min-h-[44px] px-4' : ''}`}
        >
          Popular Sports
        </Button>
        <Button
          {...selectAllButtonProps}
          variant="outline"
          size={screenSize === 'mobile' ? 'default' : 'sm'}
          className={`text-xs ${isTouchDevice ? 'min-h-[44px] px-4' : ''}`}
        >
          Select All
        </Button>
        <Button
          {...clearAllButtonProps}
          variant="outline"
          size={screenSize === 'mobile' ? 'default' : 'sm'}
          className={`text-xs ${isTouchDevice ? 'min-h-[44px] px-4' : ''}`}
        >
          Clear All
        </Button>
      </div>

      {/* Selection status */}
      <div className="text-center">
        <p className="text-sm text-muted-foreground">
          {selectedCount === 0 ? (
            <span className="text-destructive">Please select at least one sport</span>
          ) : (
            <span>
              {selectedCount} sport{selectedCount !== 1 ? 's' : ''} selected
            </span>
          )}
        </p>
      </div>

      {/* Sports list with drag and drop */}
      <div className="max-w-2xl mx-auto">
        <DndContext
          sensors={sensors}
          collisionDetection={closestCenter}
          onDragEnd={handleDragEnd}
        >
          <SortableContext
            items={availableSports.map(sport => sport.sportId)}
            strategy={verticalListSortingStrategy}
          >
            <div className="space-y-3">
              {availableSports.map((sport, index) => (
                <SortableSportItem
                  key={sport.sportId}
                  sport={sport}
                  index={index}
                  isSelected={selectedSportIds.has(sport.sportId)}
                  onToggle={handleToggleSport}
                />
              ))}
            </div>
          </SortableContext>
        </DndContext>
      </div>

      {/* Instructions */}
      <div className="text-center max-w-md mx-auto">
        <Card className="bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800">
          <CardContent className="p-4">
            <div className="flex items-start space-x-2">
              <ChevronRight className="h-4 w-4 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
              <p className="text-sm text-blue-800 dark:text-blue-200">
                <strong>Tip:</strong> Drag sports up or down to rank them by your interest level.
                Your #1 choice will get priority in your personalized feed.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Validation message */}
      {!hasMinimumSelection && (
        <div className="text-center">
          <p className="text-sm text-destructive">
            Select at least one sport to continue
          </p>
        </div>
      )}
    </div>
  );
};

export default SportsSelection;