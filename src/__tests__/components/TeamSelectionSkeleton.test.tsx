/**
 * @jest-environment jsdom
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import {
  TeamSelectionSkeleton,
  TeamCardSkeleton,
  VirtualizedTeamListSkeleton,
  SportSectionSkeleton,
  ChunkedTeamLoadingSkeleton
} from '@/components/skeletons/TeamSelectionSkeleton';

describe('TeamSelectionSkeleton', () => {
  it('renders skeleton loading state', () => {
    render(<TeamSelectionSkeleton />);

    // Should have animated skeleton elements
    const skeletonElements = document.querySelectorAll('.animate-pulse');
    expect(skeletonElements.length).toBeGreaterThan(0);
  });

  it('renders with custom sports', () => {
    const customSports = [
      { sportId: 'nfl', name: 'NFL' },
      { sportId: 'nba', name: 'NBA' }
    ];

    render(<TeamSelectionSkeleton sports={customSports} itemsPerSport={3} />);

    // Should render skeleton elements for each sport
    expect(document.querySelectorAll('.animate-pulse').length).toBeGreaterThan(0);
  });
});

describe('TeamCardSkeleton', () => {
  it('renders team card skeleton structure', () => {
    render(<TeamCardSkeleton />);

    // Should have skeleton elements for logo, name, badges, and controls
    const skeletonElements = document.querySelectorAll('.animate-pulse');
    expect(skeletonElements.length).toBeGreaterThan(0);
  });
});

describe('VirtualizedTeamListSkeleton', () => {
  it('renders virtualized list skeleton with loading indicator', () => {
    render(<VirtualizedTeamListSkeleton containerHeight={400} />);

    // Should show loading indicator
    expect(screen.getByText('Loading teams...')).toBeInTheDocument();

    // Should have skeleton cards
    const skeletonElements = document.querySelectorAll('.animate-pulse');
    expect(skeletonElements.length).toBeGreaterThan(0);
  });
});

describe('SportSectionSkeleton', () => {
  it('renders sport section skeleton', () => {
    render(<SportSectionSkeleton sportName="NFL" itemCount={3} />);

    const skeletonElements = document.querySelectorAll('.animate-pulse');
    expect(skeletonElements.length).toBeGreaterThan(0);
  });

  it('renders with virtualized option', () => {
    render(<SportSectionSkeleton sportName="NFL" showVirtualized={true} />);

    expect(screen.getByText('Loading teams...')).toBeInTheDocument();
  });
});

describe('ChunkedTeamLoadingSkeleton', () => {
  it('renders progress indicator', () => {
    render(
      <ChunkedTeamLoadingSkeleton
        totalTeams={100}
        loadedTeams={50}
        chunkSize={10}
      />
    );

    // Should show progress
    expect(screen.getByText('50 / 100')).toBeInTheDocument();
    expect(screen.getByText('Loading teams in batches...')).toBeInTheDocument();
  });

  it('shows completed state when all teams loaded', () => {
    render(
      <ChunkedTeamLoadingSkeleton
        totalTeams={100}
        loadedTeams={100}
        chunkSize={10}
      />
    );

    expect(screen.getByText('100 / 100')).toBeInTheDocument();
    expect(screen.queryByText('Loading teams in batches...')).not.toBeInTheDocument();
  });
});