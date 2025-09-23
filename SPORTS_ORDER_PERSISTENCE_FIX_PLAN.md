# Sports Order Persistence Fix Plan

## Issue Summary
The drag and drop functionality for sports selection works (sports are draggable), but the dragged position changes don't persist when users navigate through the onboarding flow. The user can drag sports around, but the position changes revert to their original state.

## Root Cause Analysis

### 1. State Persistence Gap
**Primary Issue**: The sports order changes are correctly handled in the local component state during drag operations, but they are not being properly persisted to localStorage when the drag ends.

**Current Implementation Analysis**:
- `handleDragEnd` function correctly updates ranks for reordered sports (lines 312-372)
- `normalizeRanks` function ensures consistent rank ordering (lines 46-66)
- `handleContinue` saves to localStorage with `updateLocalOnboardingStep` (line 434)

**The Problem**: The drag order changes are only saved to localStorage when the user clicks "Continue" to move to the next step. If the user drags sports around but doesn't immediately proceed, the changes exist only in local component state and are lost on page reload or navigation.

### 2. State Restoration Issue
**Secondary Issue**: When the component mounts, it restores sports selection from localStorage but may not be preserving the exact order that was dragged.

**Current Implementation Analysis** (lines 244-262):
```typescript
const sportsWithSelection = activeSportsData.map((sport, index) => {
  const previousSelection = previousSelections.find(s => s.sportId === sport.id);
  return {
    ...sport,
    isSelected: !!previousSelection,
    rank: previousSelection?.rank || 0,
  };
});
```

**The Problem**: The restoration logic relies on the `activeSportsData` array order from the API/fallback, which may not match the user's dragged order. The sports are restored based on their original API order, not their dragged order.

### 3. Rank Corruption Risk
**Tertiary Issue**: As documented in `SPORTS_RANKING_CORRUPTION_ANALYSIS.md`, there are potential ranking logic corruption issues that could affect drag order persistence.

## Proposed Solution Architecture

### Phase 1: Immediate Save on Drag End
**Objective**: Save drag order changes immediately to localStorage, not just on "Continue"

**Implementation**:
1. Modify `handleDragEnd` to call `updateLocalOnboardingStep` after rank normalization
2. Ensure drag changes persist without requiring navigation to next step
3. Add error handling for localStorage failures

### Phase 2: Proper State Restoration
**Objective**: Restore sports in their dragged order, not API order

**Implementation**:
1. Modify sports initialization to sort by rank before mapping to component state
2. Ensure sports are displayed in rank order, with unselected sports following
3. Preserve exact user drag order on component mount

### Phase 3: Rank Integrity Validation
**Objective**: Prevent rank corruption during drag operations

**Implementation**:
1. Add validation functions to ensure rank integrity after drag operations
2. Implement safeguards against duplicate or missing ranks
3. Add debugging helpers for rank state validation

## Technical Implementation Plan

### Task 1: Enhance handleDragEnd Persistence
**Agent**: frontend-nextjs-dev
**Estimated Time**: 1-2 hours
**Files to Modify**:
- `/src/pages/onboarding/SportsSelectionStep.tsx`

**Changes**:
```typescript
const handleDragEnd = (event: DragEndEvent) => {
  // ... existing drag logic ...

  // ADDITION: Save immediately after drag completes
  const finalSelectedSports = finalItems.filter(sport => sport.isSelected)
    .map(sport => ({
      sportId: sport.id,
      rank: sport.rank,
    }));

  // Save to localStorage immediately
  updateLocalOnboardingStep(2, { selectedSports: finalSelectedSports });

  // Optionally save to API if available
  if (isApiAvailable && isAuthenticated) {
    try {
      apiClient.updateOnboardingStep({
        step: 2,
        data: { sports: finalSelectedSports }
      });
    } catch (error) {
      console.warn('Failed to save drag order to API:', error);
    }
  }
};
```

### Task 2: Fix State Restoration Order
**Agent**: frontend-nextjs-dev
**Estimated Time**: 1 hour
**Files to Modify**:
- `/src/pages/onboarding/SportsSelectionStep.tsx`

**Changes**:
```typescript
useEffect(() => {
  if (activeSportsData) {
    const localStatus = getLocalOnboardingStatus();
    const previousSelections = localStatus?.selectedSports || [];

    // Create sports with selection state
    const sportsWithSelection = activeSportsData.map((sport) => {
      const previousSelection = previousSelections.find(s => s.sportId === sport.id);
      return {
        ...sport,
        isSelected: !!previousSelection,
        rank: previousSelection?.rank || 0,
      };
    });

    // ADDITION: Sort to preserve user's drag order
    const sortedSports = sportsWithSelection.sort((a, b) => {
      // Selected sports first, sorted by rank
      if (a.isSelected && b.isSelected) {
        return a.rank - b.rank;
      }
      if (a.isSelected && !b.isSelected) return -1;
      if (!a.isSelected && b.isSelected) return 1;

      // Unselected sports maintain original API order
      const aIndex = activeSportsData.findIndex(s => s.id === a.id);
      const bIndex = activeSportsData.findIndex(s => s.id === b.id);
      return aIndex - bIndex;
    });

    setSports(sortedSports);
  }
}, [activeSportsData]);
```

### Task 3: Add Rank Validation Utilities
**Agent**: frontend-nextjs-dev
**Estimated Time**: 30 minutes
**Files to Modify**:
- `/src/pages/onboarding/SportsSelectionStep.tsx`

**Changes**:
```typescript
// Add validation function
const validateRankIntegrity = (sports: SportItem[]): boolean => {
  const selectedSports = sports.filter(s => s.isSelected);
  const ranks = selectedSports.map(s => s.rank).sort((a, b) => a - b);

  // Check for consecutive ranks starting from 1
  for (let i = 0; i < ranks.length; i++) {
    if (ranks[i] !== i + 1) {
      console.error('Rank integrity violation:', { expected: i + 1, actual: ranks[i], sports: selectedSports });
      return false;
    }
  }
  return true;
};

// Add to handleDragEnd and other rank-modifying functions
if (!validateRankIntegrity(finalItems)) {
  console.warn('Rank corruption detected, applying emergency normalization');
  return normalizeRanks(finalItems);
}
```

### Task 4: Testing and Validation
**Agent**: validation-testing
**Estimated Time**: 1 hour
**Files to Create/Modify**:
- Test files for drag persistence behavior

**Test Cases**:
1. Drag sports to new positions → verify localStorage saves immediately
2. Refresh page → verify sports maintain dragged order
3. Navigate away and back → verify order persistence
4. Drag operations maintain rank integrity
5. Error handling for localStorage failures

## Quality Gates

### Pre-Implementation Checklist
- [ ] Archon research on existing drag/drop implementation patterns
- [ ] Review current state management architecture
- [ ] Confirm localStorage schema compatibility

### Implementation Checklist
- [ ] handleDragEnd saves immediately to localStorage
- [ ] State restoration preserves user drag order
- [ ] Rank integrity validation prevents corruption
- [ ] Error handling for localStorage failures
- [ ] API sync remains functional when available

### Post-Implementation Validation
- [ ] Unit tests pass for drag persistence
- [ ] Integration tests validate order preservation
- [ ] Manual testing confirms fix works across navigation
- [ ] Semgrep security scan clean
- [ ] No accessibility regressions

## Success Criteria

### Primary Goals
1. **Immediate Persistence**: Drag order changes save to localStorage instantly
2. **Order Preservation**: Sports maintain dragged order across page reloads
3. **Navigation Stability**: Order persists when navigating between onboarding steps

### Secondary Goals
1. **Rank Integrity**: No duplicate or missing ranks after drag operations
2. **Error Resilience**: Graceful handling of localStorage failures
3. **API Compatibility**: Changes sync with backend when available

## Rollback Plan

If issues arise during implementation:
1. Revert handleDragEnd changes and restore save-on-continue behavior
2. Revert state restoration changes and use original API order
3. Remove validation functions if they cause performance issues
4. Fall back to existing localStorage-only persistence

## Dependencies

- No new package dependencies required
- Uses existing localStorage utilities
- Compatible with current API client structure
- Maintains Firebase authentication integration

## Timeline

**Total Estimated Time**: 4-5 hours
- Task 1 (handleDragEnd): 1-2 hours
- Task 2 (State Restoration): 1 hour
- Task 3 (Validation): 30 minutes
- Task 4 (Testing): 1 hour
- Buffer for integration: 30 minutes

**Recommended Implementation Order**:
1. Task 3 (Validation) - establish safety mechanisms
2. Task 1 (handleDragEnd) - fix immediate persistence
3. Task 2 (State Restoration) - fix order preservation
4. Task 4 (Testing) - validate complete solution

This plan addresses the core issue while maintaining code quality and implementing proper safeguards against the ranking corruption issues identified in the codebase.