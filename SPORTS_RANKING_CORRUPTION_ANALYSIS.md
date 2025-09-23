# Sports Ranking Logic Corruption Analysis

## Overview
Critical ranking algorithm corruption identified in `SportsSelectionStep.tsx` that causes sport ordering inconsistencies and data integrity issues.

## Identified Issues

### 1. Race Condition in Toggle Logic (Lines 273-282)
**Problem**: The re-ranking logic in `handleToggleSport` creates a race condition where the current state is read while being modified.

```typescript
// BROKEN: Lines 276-278
const selectedSports = prevSports.filter(s => s.isSelected || (s.id === sportId && !prevSports.find(ps => ps.id === sportId)?.isSelected));
const currentIndex = selectedSports.findIndex(s => s.id === sport.id);
return { ...sport, rank: currentIndex + 1 };
```

**Impact**: Sports get incorrect ranks, causing display order corruption.

### 2. Inconsistent Ranking Logic (Lines 264-282)
**Problem**: The algorithm attempts to rank sports in two separate map operations, leading to inconsistent state.

**Corruption Pattern**:
1. First map operation sets initial rank (lines 264-271)
2. Second map operation re-ranks ALL selected sports (lines 273-282)
3. This creates conflicting rank assignments

### 3. Drag-and-Drop Ranking Mismatch (Lines 285-312)
**Problem**: The `handleDragEnd` function correctly updates ranks for reordered sports, but the display logic doesn't consistently reflect these changes.

**Issue**: Lines 294-306 correctly implement arrayMove and rank updates, but the component state update pattern differs from the toggle logic.

### 4. Bulk Operation Inconsistencies (Lines 314-342)
**Problem**: `handleSelectAll` and `handleSelectPopular` use array index + 1 for ranking instead of proper selection order logic.

```typescript
// PROBLEMATIC: Line 319
rank: index + 1, // Uses array index, not selection order
```

### 5. State Update Timing Issues
**Problem**: Multiple state updates in `handleToggleSport` can cause intermediate invalid states where ranks are duplicated or out of sequence.

## Corruption Scenarios

### Scenario A: Toggle Selection Corruption
1. User selects Sport A (gets rank 1)
2. User selects Sport B (gets rank 2)
3. User deselects Sport A
4. **BUG**: Sport B keeps rank 2 instead of updating to rank 1

### Scenario B: Drag Reorder Corruption
1. User selects 3 sports (ranks 1, 2, 3)
2. User drags rank 3 to position 1
3. **BUG**: Ranking logic may assign duplicate ranks or skip ranks

### Scenario C: Bulk Operation Corruption
1. User clicks "Select All"
2. **BUG**: Ranks assigned by array index instead of logical selection order
3. Popular sports don't get priority ranking

## Root Cause Analysis

### Primary Issues:
1. **Dual State Updates**: The toggle function performs two map operations on the same array
2. **Stale Closure References**: Previous state references become stale during async updates
3. **Inconsistent Ranking Strategies**: Different functions use different ranking logic
4. **Missing Rank Normalization**: No function ensures ranks are consecutive integers starting from 1

### Secondary Issues:
1. Complex nested logic in toggle function makes debugging difficult
2. No validation of rank integrity after state updates
3. Inconsistent handling of edge cases (empty selections, max selections)

## Recommended Solution Architecture

### 1. Centralized Ranking Function
Create a pure function that handles all ranking logic:
```typescript
function normalizeRanks(sports: SportItem[]): SportItem[] {
  const selected = sports.filter(s => s.isSelected);
  // Sort by current rank, then assign consecutive ranks
  const ranked = selected.sort((a, b) => a.rank - b.rank);

  return sports.map(sport => {
    if (!sport.isSelected) return { ...sport, rank: 0 };
    const newRank = ranked.findIndex(s => s.id === sport.id) + 1;
    return { ...sport, rank: newRank };
  });
}
```

### 2. Simplified Toggle Logic
```typescript
function handleToggleSport(sportId: string): SportItem[] {
  // 1. Toggle selection state
  // 2. Apply rank normalization
  // 3. Return consistent state
}
```

### 3. Consistent Bulk Operations
All bulk operations should use the same ranking normalization function.

## Test Cases Required
1. Sequential selection/deselection maintains proper rank order
2. Drag-and-drop preserves rank integrity
3. Bulk operations assign logical ranks
4. Edge cases: max selection, empty selection, single selection
5. Concurrent user interactions don't corrupt state

## Priority: CRITICAL
This corruption affects core user experience and data integrity in the onboarding flow.