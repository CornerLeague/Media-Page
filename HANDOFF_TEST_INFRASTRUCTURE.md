# Test Infrastructure Agent - Handoff Documentation

## MISSION
Fix all TypeScript `any` type violations in test files and establish proper type definitions for test infrastructure.

## SCOPE & OWNERSHIP
**Files Under Your Control:**
- `/src/test-setup.tsx` (18 any violations)
- `/src/__tests__/onboarding.test.tsx` (1 any violation)
- `/e2e/onboarding.spec.ts` (1 any violation)

**DO NOT MODIFY:** Any other files during your phase

## REQUIRED TYPE CONTRACTS

### 1. Test Setup Mock State Types
Replace lines 12-13 in `/src/test-setup.tsx`:
```typescript
// BEFORE (any types)
let mockOnboardingState: any = null;
let mockUserPreferences: any = null;

// AFTER (proper types)
interface OnboardingMockState {
  currentStep: 'welcome' | 'sports' | 'teams' | 'preferences' | 'complete';
  isCompleted: boolean;
  preferences: UserPreferences | null;
  completedSteps: string[];
}

interface UserPreferencesMock {
  sports: string[];
  teams: { id: string; name: string; league: string }[];
  location?: { city: string; state: string; country: string };
  notifications: boolean;
  theme: 'light' | 'dark' | 'system';
}

let mockOnboardingState: OnboardingMockState | null = null;
let mockUserPreferences: UserPreferencesMock | null = null;
```

### 2. Global Test Utilities Types
Add proper typing for test utility functions (around lines 68-295):
```typescript
// Mock function types
interface MockFunction<T extends (...args: any[]) => any> {
  (...args: Parameters<T>): ReturnType<T>;
  mockImplementation: (fn: T) => MockFunction<T>;
  mockReturnValue: (value: ReturnType<T>) => MockFunction<T>;
  mockClear: () => void;
}

// Replace all `any` with proper generic types
interface TestUtilityConfig {
  timeout?: number;
  retries?: number;
  skipCleanup?: boolean;
}
```

### 3. Vitest Testing Library Integration
Add proper types for testing globals:
```typescript
// At top of file, add proper vitest type declarations
declare global {
  const describe: (name: string, fn: () => void) => void;
  const it: (name: string, fn: () => void | Promise<void>) => void;
  const expect: typeof import('vitest').expect;
  const beforeEach: (fn: () => void | Promise<void>) => void;
  const afterEach: (fn: () => void | Promise<void>) => void;
  const beforeAll: (fn: () => void | Promise<void>) => void;
  const afterAll: (fn: () => void | Promise<void>) => void;
}
```

## QUALITY GATES BEFORE COMPLETION

### Pre-Implementation Checks:
1. Run `npm run test` - ensure all tests pass (baseline)
2. Run `npm run lint` - confirm current error count (86 errors baseline)
3. Run `npm run typecheck` - ensure no compilation errors

### Post-Implementation Validation:
1. **Zero any violations in modified files:**
   - `/src/test-setup.tsx`: 0 any types (down from 18)
   - `/src/__tests__/onboarding.test.tsx`: 0 any types (down from 1)
   - `/e2e/onboarding.spec.ts`: 0 any types (down from 1)

2. **Test functionality maintained:**
   - All existing tests continue to pass
   - Mock implementations work correctly
   - No breaking changes to test utilities

3. **TypeScript compliance:**
   - `npm run typecheck` passes without new errors
   - ESLint error count reduced by exactly 20 errors
   - No new warnings introduced

## ROLLBACK PLAN
If any quality gate fails:
1. Revert all changes to affected files
2. Document specific blocking issue encountered
3. Escalate to Delegation Policy Agent for contract revision

## HANDOFF CRITERIA TO NEXT PHASE
✅ All 20 test infrastructure any violations resolved
✅ Test suite passes completely
✅ No TypeScript compilation errors
✅ ESLint errors reduced to ≤ 66 total

**Next Phase Trigger:** Success confirmation allows UI Components Agent to begin Phase 2