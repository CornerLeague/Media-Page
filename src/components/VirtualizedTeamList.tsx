/**
 * VirtualizedTeamList Component
 *
 * High-performance virtualized list for handling 1000+ teams
 * without performance degradation. Uses intersection observer
 * and viewport optimization for smooth scrolling.
 *
 * Enhanced with progressive loading support for better UX.
 */

import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Star, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Skeleton } from '@/components/ui/skeleton';

interface Team {
  id: string;
  name: string;
  market?: string;
  sportId: string;
  league: string;
  logo?: string;
  isSelected: boolean;
  affinityScore: number;
}

interface VirtualizedTeamListProps {
  teams: Team[];
  onToggleTeam: (teamId: string) => void;
  onAffinityChange: (teamId: string, affinity: number) => void;
  itemHeight?: number;
  containerHeight?: number;
  overscan?: number;
  className?: string;
  // Progressive loading props
  isLoading?: boolean;
  loadedCount?: number;
  totalCount?: number;
  onLoadMore?: () => void;
  loadingChunkSize?: number;
}

interface VirtualItem {
  index: number;
  start: number;
  end: number;
  team: Team;
}

// Skeleton component for loading team items
const TeamItemSkeleton = React.memo(({ style }: { style: React.CSSProperties }) => (
  <div style={style} className="px-3 py-2">
    <Card>
      <CardContent className="p-4">
        <div className="flex items-center gap-4">
          <Skeleton className="w-8 h-8 rounded-full flex-shrink-0" />
          <div className="flex-1 space-y-2">
            <Skeleton className="h-4 w-32" />
            <div className="flex items-center gap-2">
              <Skeleton className="h-3 w-12" />
              <Skeleton className="h-3 w-16" />
            </div>
          </div>
          <div className="flex items-center gap-3 flex-shrink-0">
            <div className="flex items-center gap-1">
              {[1, 2, 3, 4, 5].map((i) => (
                <Skeleton key={i} className="w-3 h-3" />
              ))}
            </div>
            <Skeleton className="w-4 h-4 rounded" />
          </div>
        </div>
      </CardContent>
    </Card>
  </div>
));

TeamItemSkeleton.displayName = 'TeamItemSkeleton';

export function VirtualizedTeamList({
  teams,
  onToggleTeam,
  onAffinityChange,
  itemHeight = 120,
  containerHeight = 600,
  overscan = 5,
  className,
  isLoading = false,
  loadedCount,
  totalCount,
  onLoadMore,
  loadingChunkSize = 20,
}: VirtualizedTeamListProps) {
  const [scrollTop, setScrollTop] = useState(0);
  const [isScrolling, setIsScrolling] = useState(false);
  const scrollElementRef = useRef<HTMLDivElement>(null);
  const scrollTimeoutRef = useRef<NodeJS.Timeout>();
  const loadMoreTriggerRef = useRef<HTMLDivElement>(null);

  // Calculate visible range based on scroll position
  const visibleRange = useMemo(() => {
    const containerTop = Math.floor(scrollTop / itemHeight);
    const containerBottom = Math.min(
      teams.length - 1,
      Math.ceil((scrollTop + containerHeight) / itemHeight)
    );

    return {
      start: Math.max(0, containerTop - overscan),
      end: Math.min(teams.length - 1, containerBottom + overscan),
    };
  }, [scrollTop, itemHeight, containerHeight, teams.length, overscan]);

  // Generate virtual items for rendering
  const virtualItems = useMemo((): VirtualItem[] => {
    const items: VirtualItem[] = [];

    for (let i = visibleRange.start; i <= visibleRange.end; i++) {
      items.push({
        index: i,
        start: i * itemHeight,
        end: (i + 1) * itemHeight,
        team: teams[i],
      });
    }

    return items;
  }, [visibleRange, itemHeight, teams]);

  // Handle scroll events with debouncing
  const handleScroll = useCallback((event: React.UIEvent<HTMLDivElement>) => {
    const scrollTop = event.currentTarget.scrollTop;
    setScrollTop(scrollTop);
    setIsScrolling(true);

    // Clear existing timeout
    if (scrollTimeoutRef.current) {
      clearTimeout(scrollTimeoutRef.current);
    }

    // Set scrolling to false after scroll ends
    scrollTimeoutRef.current = setTimeout(() => {
      setIsScrolling(false);
    }, 150);
  }, []);

  // Progressive loading with intersection observer
  useEffect(() => {
    if (!onLoadMore || !loadMoreTriggerRef.current || isLoading) return;

    const observer = new IntersectionObserver(
      (entries) => {
        const entry = entries[0];
        if (entry.isIntersecting && loadedCount !== undefined && totalCount !== undefined) {
          if (loadedCount < totalCount) {
            onLoadMore();
          }
        }
      },
      {
        root: scrollElementRef.current,
        rootMargin: '100px', // Trigger loading 100px before reaching the trigger
        threshold: 0.1,
      }
    );

    observer.observe(loadMoreTriggerRef.current);

    return () => observer.disconnect();
  }, [onLoadMore, loadedCount, totalCount, isLoading]);

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current);
      }
    };
  }, []);

  // Memoized team item component to prevent unnecessary re-renders
  const TeamItem = React.memo(({ team, style }: { team: Team; style: React.CSSProperties }) => (
    <div style={style} className="px-3 py-2">
      <Card
        className={cn(
          "hover:shadow-md transition-all duration-200",
          team.isSelected && "ring-2 ring-primary bg-primary/5",
          isScrolling && "pointer-events-none" // Disable interactions while scrolling
        )}
      >
        <CardContent className="p-4">
          <div className="flex items-center gap-4">
            <div className="text-2xl flex-shrink-0">{team.logo || '🏆'}</div>
            <div className="flex-1 min-w-0">
              <h4 className="font-display font-semibold text-sm md:text-base truncate">
                {team.name}
              </h4>
              <div className="flex items-center gap-2 mt-1">
                <Badge variant="secondary" className="text-xs">
                  {team.league}
                </Badge>
                {team.market && (
                  <Badge variant="outline" className="text-xs">
                    {team.market}
                  </Badge>
                )}
              </div>
            </div>
            <div className="flex items-center gap-3 flex-shrink-0">
              {team.isSelected && (
                <div className="flex items-center gap-1">
                  {[1, 2, 3, 4, 5].map(rating => (
                    <button
                      key={rating}
                      onClick={() => onAffinityChange(team.id, rating)}
                      className={cn(
                        "w-4 h-4 transition-colors",
                        rating <= team.affinityScore
                          ? "text-yellow-400"
                          : "text-gray-300"
                      )}
                      aria-label={`Rate ${team.name} ${rating} stars`}
                    >
                      <Star className="w-full h-full fill-current" />
                    </button>
                  ))}
                </div>
              )}
              <input
                type="checkbox"
                checked={team.isSelected}
                onChange={() => onToggleTeam(team.id)}
                className="w-4 h-4 text-primary border-gray-300 rounded focus:ring-primary"
                aria-label={`Toggle ${team.name}`}
              />
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  ));

  TeamItem.displayName = 'TeamItem';

  // Calculate total height including skeleton items for progressive loading
  const skeletonItemsCount = isLoading && loadedCount !== undefined && totalCount !== undefined
    ? Math.min(loadingChunkSize, totalCount - loadedCount)
    : 0;
  const totalHeight = (teams.length + skeletonItemsCount) * itemHeight;

  // Progressive loading calculations
  const showProgressiveLoading = totalCount !== undefined && loadedCount !== undefined;
  const hasMoreToLoad = showProgressiveLoading && loadedCount < totalCount;

  // Show empty state if no teams and not loading
  if (teams.length === 0 && !isLoading) {
    return (
      <div
        className={cn("flex items-center justify-center text-center p-8", className)}
        style={{ height: containerHeight }}
        data-testid="teams-container"
        role="listbox"
        aria-label="Team selection list"
      >
        <div className="text-muted-foreground">
          No teams available for the selected sports.
        </div>
      </div>
    );
  }

  return (
    <div
      ref={scrollElementRef}
      className={cn("overflow-auto", className)}
      style={{ height: containerHeight }}
      onScroll={handleScroll}
      data-testid="teams-container"
      role="listbox"
      aria-label="Team selection list"
    >
      {/* Spacer for total height */}
      <div style={{ height: totalHeight, position: 'relative' }}>
        {/* Rendered virtual items */}
        {virtualItems.map(({ index, start, team }) => (
          <TeamItem
            key={team.id}
            team={team}
            style={{
              position: 'absolute',
              top: start,
              left: 0,
              right: 0,
              height: itemHeight,
            }}
          />
        ))}

        {/* Skeleton items for progressive loading */}
        {isLoading && skeletonItemsCount > 0 && (
          <>
            {Array.from({ length: skeletonItemsCount }, (_, skeletonIndex) => {
              const itemIndex = teams.length + skeletonIndex;
              const itemTop = itemIndex * itemHeight;

              // Only render skeleton if it's in the visible area
              if (itemTop >= scrollTop - overscan * itemHeight &&
                  itemTop <= scrollTop + containerHeight + overscan * itemHeight) {
                return (
                  <TeamItemSkeleton
                    key={`skeleton-${skeletonIndex}`}
                    style={{
                      position: 'absolute',
                      top: itemTop,
                      left: 0,
                      right: 0,
                      height: itemHeight,
                    }}
                  />
                );
              }
              return null;
            })}
          </>
        )}

        {/* Load more trigger for intersection observer */}
        {hasMoreToLoad && !isLoading && onLoadMore && (
          <div
            ref={loadMoreTriggerRef}
            style={{
              position: 'absolute',
              top: totalHeight - itemHeight * 2, // Position near the end
              left: 0,
              right: 0,
              height: itemHeight,
              pointerEvents: 'none',
            }}
          />
        )}
      </div>

      {/* Loading indicator for scroll performance */}
      {isScrolling && (
        <div className="absolute top-2 right-2 bg-background/80 backdrop-blur-sm rounded-md px-2 py-1">
          <div className="text-xs text-muted-foreground">Scrolling...</div>
        </div>
      )}

      {/* Progressive loading status */}
      {showProgressiveLoading && (
        <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2">
          <div className="bg-background/90 backdrop-blur-sm rounded-full px-4 py-2 border shadow-sm">
            {isLoading ? (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Loader2 className="h-3 w-3 animate-spin" />
                <span>Loading teams...</span>
                <span className="text-xs tabular-nums">
                  {loadedCount} / {totalCount}
                </span>
              </div>
            ) : hasMoreToLoad ? (
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <span>Scroll down to load more</span>
                <span className="tabular-nums">
                  {loadedCount} / {totalCount}
                </span>
              </div>
            ) : (
              <div className="text-xs text-muted-foreground">
                All {totalCount} teams loaded
              </div>
            )}
          </div>
        </div>
      )}

      {/* Initial loading state for empty list */}
      {teams.length === 0 && isLoading && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="flex flex-col items-center gap-3 text-center">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <div className="space-y-1">
              <p className="text-sm font-medium">Loading teams...</p>
              <p className="text-xs text-muted-foreground">
                {totalCount ? `Preparing ${totalCount} teams` : 'Fetching team data'}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Performance monitoring wrapper
export function PerformanceMonitoredTeamList(props: VirtualizedTeamListProps) {
  const renderStartTime = useRef(performance.now());

  useEffect(() => {
    const renderTime = performance.now() - renderStartTime.current;

    if (renderTime > 16) { // More than one frame (60fps)
      console.warn(`VirtualizedTeamList render took ${renderTime.toFixed(2)}ms`);
    }

    // Log performance metrics for teams > 100
    if (props.teams.length > 100) {
      console.log(`Rendered ${props.teams.length} teams in ${renderTime.toFixed(2)}ms`);
    }
  }, [props.teams.length]);

  return <VirtualizedTeamList {...props} />;
}

export default VirtualizedTeamList;