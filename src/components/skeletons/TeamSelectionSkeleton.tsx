/**
 * TeamSelectionSkeleton Component
 *
 * Provides loading skeletons for team selection during onboarding.
 * Shows animated placeholders while team data is being fetched.
 */

import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface TeamSelectionSkeletonProps {
  /** Number of skeleton items to show per sport */
  itemsPerSport?: number;
  /** Sports to show skeletons for */
  sports?: Array<{ sportId: string; name: string }>;
  /** Whether to show the virtualized list skeleton */
  showVirtualized?: boolean;
  /** Custom className */
  className?: string;
}

/**
 * Single team card skeleton
 */
export function TeamCardSkeleton({ className }: { className?: string }) {
  return (
    <Card className={cn("animate-pulse", className)}>
      <CardContent className="p-4">
        <div className="flex items-center gap-4">
          {/* Logo skeleton */}
          <Skeleton className="w-8 h-8 rounded-full flex-shrink-0" />

          {/* Team info skeleton */}
          <div className="flex-1 space-y-2">
            <Skeleton className="h-5 w-32 sm:w-40" />
            <div className="flex items-center gap-2">
              <Skeleton className="h-4 w-12" />
              <Skeleton className="h-4 w-16" />
            </div>
          </div>

          {/* Rating and checkbox skeleton */}
          <div className="flex items-center gap-3 flex-shrink-0">
            <div className="flex items-center gap-1">
              {[1, 2, 3, 4, 5].map((i) => (
                <Skeleton key={i} className="w-4 h-4 rounded-sm" />
              ))}
            </div>
            <Skeleton className="w-4 h-4 rounded" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

/**
 * Progressive loading skeleton for virtualized lists
 */
export function VirtualizedTeamListSkeleton({
  containerHeight = 400,
  itemHeight = 120,
  className
}: {
  containerHeight?: number;
  itemHeight?: number;
  className?: string;
}) {
  const visibleItems = Math.ceil(containerHeight / itemHeight);

  return (
    <div
      className={cn("overflow-hidden border rounded-lg", className)}
      style={{ height: containerHeight }}
    >
      <div className="space-y-3 p-3">
        {Array.from({ length: visibleItems }, (_, i) => (
          <TeamCardSkeleton key={i} />
        ))}
      </div>

      {/* Progressive loading indicator */}
      <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2">
        <div className="bg-background/90 backdrop-blur-sm rounded-full px-3 py-1 border">
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <div className="animate-spin rounded-full h-3 w-3 border-b border-primary"></div>
            <span>Loading teams...</span>
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * Sport section skeleton
 */
export function SportSectionSkeleton({
  sportName,
  itemCount = 3,
  showVirtualized = false,
  className
}: {
  sportName?: string;
  itemCount?: number;
  showVirtualized?: boolean;
  className?: string;
}) {
  return (
    <div className={cn("space-y-3", className)}>
      {/* Sport header skeleton */}
      <div className="flex items-center gap-2">
        <Skeleton className="h-6 w-24" />
        <Skeleton className="h-4 w-8 rounded-full" />
      </div>

      {/* Teams skeleton */}
      {showVirtualized ? (
        <VirtualizedTeamListSkeleton />
      ) : (
        <div className="space-y-3">
          {Array.from({ length: itemCount }, (_, i) => (
            <TeamCardSkeleton key={i} />
          ))}
        </div>
      )}
    </div>
  );
}

/**
 * Main team selection skeleton component
 */
export function TeamSelectionSkeleton({
  itemsPerSport = 3,
  sports = [
    { sportId: 'nfl', name: 'NFL' },
    { sportId: 'nba', name: 'NBA' },
    { sportId: 'mlb', name: 'MLB' }
  ],
  showVirtualized = false,
  className
}: TeamSelectionSkeletonProps) {
  return (
    <div className={cn("space-y-6", className)}>
      {/* Instructions skeleton */}
      <div className="text-center space-y-2">
        <Skeleton className="h-6 w-80 mx-auto" />
        <Skeleton className="h-4 w-96 mx-auto" />
      </div>

      {/* Sports sections */}
      <div className="space-y-6">
        {sports.map((sport, index) => (
          <SportSectionSkeleton
            key={sport.sportId}
            sportName={sport.name}
            itemCount={itemsPerSport}
            showVirtualized={showVirtualized && index === 0} // Only show virtualized for first sport
            className="animate-pulse"
            style={{
              animationDelay: `${index * 200}ms` // Stagger animations
            } as React.CSSProperties}
          />
        ))}
      </div>

      {/* Selection counter skeleton */}
      <div className="text-center">
        <Skeleton className="h-6 w-32 mx-auto" />
      </div>

      {/* Loading tip skeleton */}
      <div className="bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
        <div className="space-y-2">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-3/4" />
        </div>
      </div>
    </div>
  );
}

/**
 * Chunked loading skeleton - shows teams loading in batches
 */
export function ChunkedTeamLoadingSkeleton({
  totalTeams,
  loadedTeams = 0,
  chunkSize = 10,
  className
}: {
  totalTeams: number;
  loadedTeams?: number;
  chunkSize?: number;
  className?: string;
}) {
  const progress = Math.min(100, (loadedTeams / totalTeams) * 100);
  const isLoading = loadedTeams < totalTeams;

  return (
    <div className={cn("space-y-4", className)}>
      {/* Progress indicator */}
      <div className="flex items-center gap-3 text-sm text-muted-foreground">
        <div className="flex-1 bg-muted rounded-full h-2">
          <div
            className="bg-primary h-2 rounded-full transition-all duration-500 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>
        <span className="tabular-nums">
          {loadedTeams} / {totalTeams}
        </span>
      </div>

      {isLoading && (
        <div className="flex items-center justify-center py-6">
          <div className="flex items-center gap-3 text-sm text-muted-foreground">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></div>
            <span>Loading teams in batches...</span>
          </div>
        </div>
      )}
    </div>
  );
}

export default TeamSelectionSkeleton;