# Application Logic Agent - Handoff Documentation

## MISSION
Fix all TypeScript `any` type violations in application logic, hooks, and business logic components while establishing proper type safety for core application functionality.

## SCOPE & OWNERSHIP
**Files Under Your Control:**
- `/src/hooks/useTouch.ts` (2 any violations)
- `/src/components/onboarding/FirstTimeExperience.tsx` (1 any violation)
- `/src/lib/types/supabase-types.ts` (1 any violation)
- `/src/data/teams.ts` (prefer-const violation, related type improvements)

**DO NOT MODIFY:** UI components or test files during your phase

## COORDINATION PROTOCOL
- **Parallel Execution:** Can run simultaneously with UI Components Agent
- **File Separation:** No overlapping file ownership
- **Dependency Management:** Coordinate any shared type definitions

## REQUIRED TYPE CONTRACTS

### 1. Touch Hook Interface (`/src/hooks/useTouch.ts`)
Replace any types around lines 53-57:
```typescript
// BEFORE (any types)
const handleTouchStart = (e: any) => { ... }
const handleTouchMove = (e: any) => { ... }

// AFTER (proper touch event types)
interface TouchEventHandlers {
  onTouchStart: (event: TouchEvent) => void;
  onTouchMove: (event: TouchEvent) => void;
  onTouchEnd: (event: TouchEvent) => void;
}

interface TouchHookConfig {
  threshold?: number;
  timeout?: number;
  preventDefault?: boolean;
  stopPropagation?: boolean;
}

interface TouchHookReturn {
  handlers: TouchEventHandlers;
  isActive: boolean;
  direction: 'horizontal' | 'vertical' | null;
  distance: { x: number; y: number };
}

const useTouch = (config: TouchHookConfig = {}): TouchHookReturn => {
  const handleTouchStart = (event: TouchEvent) => { ... }
  const handleTouchMove = (event: TouchEvent) => { ... }
  // ... proper implementations
}
```

### 2. Onboarding Component Types (`/src/components/onboarding/FirstTimeExperience.tsx`)
Fix any type around line 23:
```typescript
// BEFORE (any type)
const someVariable: any = ...

// AFTER (proper onboarding types)
interface OnboardingStepData {
  step: 'welcome' | 'sports' | 'teams' | 'preferences' | 'complete';
  data: Record<string, unknown>;
  isValid: boolean;
  errors: ValidationError[];
}

interface FirstTimeExperienceProps {
  userId?: string;
  onComplete: (data: OnboardingStepData) => void;
  onSkip?: () => void;
  initialStep?: OnboardingStepData['step'];
}
```

### 3. Supabase Types (`/src/lib/types/supabase-types.ts`)
Replace any type around line 505:
```typescript
// BEFORE (any type)
export type SomeSupabaseType = any;

// AFTER (proper database schema types)
export interface Database {
  public: {
    Tables: {
      users: {
        Row: {
          id: string;
          email: string;
          created_at: string;
          updated_at: string;
          preferences: UserPreferences | null;
        };
        Insert: {
          id?: string;
          email: string;
          preferences?: UserPreferences | null;
        };
        Update: {
          email?: string;
          preferences?: UserPreferences | null;
        };
      };
      // Add other table definitions as needed
    };
    Views: Record<string, never>;
    Functions: Record<string, never>;
    Enums: Record<string, never>;
  };
}

export type DatabaseUser = Database['public']['Tables']['users']['Row'];
export type DatabaseUserInsert = Database['public']['Tables']['users']['Insert'];
export type DatabaseUserUpdate = Database['public']['Tables']['users']['Update'];
```

### 4. Sports and Teams Data Types (`/src/data/teams.ts`)
Fix prefer-const violation and add proper typing:
```typescript
// BEFORE (let declaration)
let teams = [ ... ];

// AFTER (const with proper typing)
interface TeamData {
  id: string;
  name: string;
  league: string;
  sport: string;
  city: string;
  state: string;
  country: string;
  logo?: string;
  colors: {
    primary: string;
    secondary: string;
  };
}

interface LeagueData {
  id: string;
  name: string;
  sport: string;
  teams: TeamData[];
}

const teams: readonly TeamData[] = [ ... ];
const leagues: readonly LeagueData[] = [ ... ];
```

## BUSINESS LOGIC TYPE CONTRACTS

### 1. User Preferences Schema
```typescript
interface UserPreferences {
  sports: string[];
  teams: TeamData[];
  notifications: {
    email: boolean;
    push: boolean;
    gameReminders: boolean;
    newsUpdates: boolean;
  };
  location?: {
    city: string;
    state: string;
    country: string;
    timezone: string;
  };
  theme: 'light' | 'dark' | 'system';
  language: string;
}
```

### 2. API Response Types
```typescript
interface ApiResponse<T = unknown> {
  data: T;
  status: number;
  message: string;
  timestamp: string;
}

interface ApiError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}
```

## QUALITY GATES BEFORE COMPLETION

### Pre-Implementation Checks:
1. **Dependency Validation:** Confirm Test Infrastructure Agent has completed Phase 1
2. **Type Dependency Mapping:** Document any shared types with UI Components Agent
3. **API Contract Review:** Ensure type definitions match backend API schemas

### Post-Implementation Validation:
1. **Zero Any Violations in Application Logic:**
   - `/src/hooks/useTouch.ts`: 0 any types (down from 2)
   - `/src/components/onboarding/FirstTimeExperience.tsx`: 0 any types (down from 1)
   - `/src/lib/types/supabase-types.ts`: 0 any types (down from 1)
   - `/src/data/teams.ts`: prefer-const issue resolved

2. **Functional Validation:**
   - All hooks continue to work with proper type inference
   - Onboarding flow maintains functionality
   - Database operations have proper type safety
   - No runtime errors introduced

3. **Type Safety Verification:**
   - TypeScript autocomplete works correctly
   - No implicit any warnings
   - Proper type checking for function parameters and returns

## ROLLBACK PLAN
If any quality gate fails:
1. Revert changes to affected business logic files
2. Document specific integration issues with types
3. Coordinate with UI Components Agent if shared type definitions affected

## COORDINATION REQUIREMENTS
- **Type Sharing:** If UI Components Agent needs shared types, coordinate through shared type definition files
- **API Integration:** Ensure Supabase types align with actual database schema
- **Business Logic Consistency:** Maintain type consistency across onboarding flow

## HANDOFF CRITERIA FOR NEXT PHASE
✅ All any violations in application logic files resolved
✅ Business logic maintains functionality with proper typing
✅ Shared type definitions documented and accessible
✅ No TypeScript compilation errors in application logic

**Parallel Coordination:** Work proceeds with UI Components Agent until both phases complete