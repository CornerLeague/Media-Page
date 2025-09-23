# Coordinated TeamSelector Execution Strategy

**Date:** September 22, 2025
**Status:** Active Execution
**Priority:** CRITICAL → HIGH
**Total Timeline:** 6.5 hours across 2 major phases

## Executive Summary

Coordinated execution of three related TeamSelector plans with **CRITICAL infinite re-render loop fix prioritized first**, followed by search implementation enhancement. The infinite loop at TeamSelector.tsx:177 is blocking the entire onboarding flow and must be resolved immediately before any other work can proceed.

## Root Cause Identified

**Critical Issue Location:** `/src/components/TeamSelector.tsx:177-178`

**Problematic Code:**
```typescript
useEffect(() => {
  setInternalSelectedTeams(selectedTeams);
}, [selectedTeams, setInternalSelectedTeams]); // ← setInternalSelectedTeams causing infinite loop
```

**Root Cause:** `setSelectedTeams` function from `useTeamSelection` hook (line 107) is **not memoized**, causing new function reference on every render, triggering infinite useEffect cycle.

## Phase 1: CRITICAL INFINITE LOOP FIX
**Duration:** 30 minutes
**Agent Assignment:** nextjs-frontend-dev (immediate)
**Status:** BLOCKING ALL OTHER WORK

### Immediate Fix Required

**1. Fix TeamSelector.tsx Line 177-178:**
```typescript
// BEFORE (problematic):
useEffect(() => {
  setInternalSelectedTeams(selectedTeams);
}, [selectedTeams, setInternalSelectedTeams]); // Remove setInternalSelectedTeams

// AFTER (fixed):
useEffect(() => {
  setInternalSelectedTeams(selectedTeams);
}, [selectedTeams]); // Only depend on the actual data
```

**2. Fix useTeamSelection.ts Line 107:**
```typescript
// BEFORE (missing memoization):
setSelectedTeams,

// AFTER (add memoization):
const setSelectedTeams = useCallback((teams: Team[] | ((prev: Team[]) => Team[])) => {
  setSelectedTeamsInternal(teams);
}, []);
```

### Quality Gate (Phase 1 → Phase 2)
- [ ] Infinite loop eliminated (no "Maximum update depth exceeded" errors)
- [ ] Onboarding flow functional end-to-end
- [ ] No new console errors or warnings
- [ ] Team selection/deselection working correctly

## Phase 2: SEARCH IMPLEMENTATION ENHANCEMENT
**Duration:** 6 hours total
**Status:** Pending Phase 1 completion

### Sub-Phase 2A: Backend Integration (1.5 hours)
**Agent:** fastapi-backend-architect
**Dependencies:** Phase 1 complete

**Tasks:**
- [ ] Verify `/api/teams/search` endpoint performance
- [ ] Enhance search response format with metadata
- [ ] Add typed search methods to API client
- [ ] Implement debounced search requests

### Sub-Phase 2B: Frontend UI Enhancement (3 hours)
**Agent:** nextjs-frontend-dev
**Dependencies:** Sub-Phase 2A complete

**Tasks:**
- [ ] Add search input component with debouncing
- [ ] Implement filter dropdown (league/sport)
- [ ] Enhance team display logic with real-time filtering
- [ ] Add 10-team selection limits with clear feedback

### Sub-Phase 2C: Performance & Testing (1.5 hours)
**Agent:** validation-testing
**Dependencies:** Sub-Phase 2B complete

**Tasks:**
- [ ] Implement virtualization for large team lists
- [ ] Add comprehensive test coverage
- [ ] Validate accessibility compliance
- [ ] Performance benchmarking

## Agent Assignment Matrix

| Phase | Primary Agent | Supporting | Duration | Critical Path |
|-------|---------------|------------|----------|---------------|
| **1: Critical Fix** | nextjs-frontend-dev | planner | 30 min | YES - BLOCKING |
| **2A: Backend** | fastapi-backend-architect | planner | 1.5 hr | No |
| **2B: Frontend UI** | nextjs-frontend-dev | general-purpose | 3 hr | No |
| **2C: Testing** | validation-testing | nextjs-frontend-dev | 1.5 hr | No |

## Coordination Protocols

### Immediate Escalation (Phase 1)
- **Critical Fix must be completed within 30 minutes**
- Any issues require immediate all-hands escalation
- No other work proceeds until infinite loop is resolved

### Standard Handoffs (Phase 2)
- 15-minute briefing at start of each sub-phase
- Quality gate validation before proceeding
- Documentation of all changes and decisions

### Risk Mitigation
- **Rollback Plan:** Immediate revert to last working commit if critical fix fails
- **Alternative Approach:** If primary fix fails, implement setTimeout workaround
- **Quality Assurance:** Each phase validated independently before proceeding

## Success Metrics

### Phase 1 (Critical):
- [ ] Zero "Maximum update depth exceeded" errors
- [ ] Onboarding completion rate restored
- [ ] All existing functionality preserved

### Phase 2 (Enhancement):
- [ ] Search response time < 100ms for UI filtering
- [ ] Team discovery within 3 user interactions
- [ ] 100% test coverage for new functionality
- [ ] WCAG 2.1 AA accessibility compliance

## Next Steps - IMMEDIATE ACTION REQUIRED

1. **RIGHT NOW:** Delegate Phase 1 critical fix to nextjs-frontend-dev agent
2. **After 30 min:** Validate fix and proceed to Phase 2 if successful
3. **Schedule:** Phase 2 execution over next 6 hours with proper agent coordination
4. **Monitor:** Real-time validation that infinite loop is resolved

## Emergency Contacts
- **Technical Issues:** nextjs-frontend-dev (primary implementer)
- **Coordination Issues:** feature-planner (escalation)
- **Quality Issues:** validation-testing (verification)

---

**CRITICAL NOTE:** The infinite loop is completely blocking the onboarding flow. This fix takes priority over ALL other work and must be completed successfully before any search enhancement work can begin.