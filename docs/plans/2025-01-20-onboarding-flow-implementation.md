# 5-Step Onboarding Flow Implementation Plan
*Generated: 2025-01-20*

## Executive Summary

This plan details the implementation of a comprehensive 5-step onboarding flow for the Corner League Media sports platform, integrating with existing FastAPI backend infrastructure and React frontend. The implementation prioritizes progressive data saving, accessibility compliance, and seamless Firebase authentication integration.

## Architecture Overview

### Current Infrastructure Analysis
- **Backend**: FastAPI with Firebase authentication, PostgreSQL with comprehensive user preference models
- **Frontend**: React 18 + TypeScript + Vite with shadcn/ui components
- **Authentication**: Firebase Auth with custom JWT middleware
- **Database**: Complete sports/teams data seeded, user preference tables ready
- **API**: `/me/preferences` endpoints for sports and teams already implemented

### Data Flow Architecture
```
User Registration → Firebase Auth → User Creation → Onboarding Flow → Progressive Preference Saving → Completion Timestamp → Dashboard Access
```

## Technical Implementation Plan

### Phase 1: Backend API Enhancements (fastapi-backend-architect)

#### 1.1 Onboarding API Endpoints
**Priority: HIGH**

**New Endpoints Required:**
```python
# Onboarding status and progress tracking
GET /api/onboarding/status
POST /api/onboarding/complete
GET /api/onboarding/progress

# Enhanced preference endpoints for onboarding
POST /api/onboarding/sports-preferences
POST /api/onboarding/team-preferences
POST /api/onboarding/notification-preferences
```

**Schemas to Create:**
```python
# backend/api/schemas/onboarding.py
class OnboardingStatus(BaseModel):
    is_completed: bool
    completed_at: Optional[datetime]
    current_step: int
    steps_completed: List[int]

class OnboardingCompletion(BaseModel):
    completed_at: datetime
    final_preferences: Dict[str, Any]

class OnboardingSportsRequest(BaseModel):
    sports: List[SportPreferenceUpdate]

class OnboardingTeamsRequest(BaseModel):
    teams: List[TeamPreferenceUpdate]
```

#### 1.2 User Model Enhancement
**Modify:** `/backend/models/users.py`

```python
# Add onboarding progress tracking
onboarding_step: Mapped[int] = mapped_column(
    Integer,
    default=0,
    nullable=False,
    doc="Current onboarding step (0-5)"
)

onboarding_data: Mapped[Optional[dict]] = mapped_column(
    JSON,
    doc="Temporary onboarding progress data"
)
```

#### 1.3 Service Layer Enhancement
**Modify:** `/backend/api/services/user_service.py`

```python
class OnboardingService:
    async def get_onboarding_status(user: User) -> OnboardingStatus
    async def update_onboarding_step(user: User, step: int) -> User
    async def complete_onboarding(user: User) -> User
    async def save_onboarding_progress(user: User, step_data: dict) -> User
```

### Phase 2: Frontend Component Architecture (nextjs-frontend-dev)

#### 2.1 Onboarding Layout Structure
```typescript
// src/components/onboarding/OnboardingLayout.tsx
interface OnboardingLayoutProps {
  currentStep: number;
  totalSteps: number;
  children: React.ReactNode;
  onNext?: () => void;
  onPrevious?: () => void;
  canProceed: boolean;
  isLoading?: boolean;
}
```

#### 2.2 Step Components
**Components to Create:**

1. **WelcomeStep** (`src/components/onboarding/steps/WelcomeStep.tsx`)
   - Welcome message
   - Feature highlights (Personalized Content, Community Insights, Real-time Updates, Premium Features)
   - "Get Started" button
   - Progress: Step 1 of 5

2. **SportsSelectionStep** (`src/components/onboarding/steps/SportsSelectionStep.tsx`)
   - Sports list with icons (NFL, NBA, MLB, NHL, MLS, College Football, College Basketball, Formula 1, Golf, Tennis)
   - Drag-to-reorder functionality
   - Multi-select with ranking
   - Progress: Step 2 of 5

3. **TeamSelectionStep** (`src/components/onboarding/steps/TeamSelectionStep.tsx`)
   - Dynamic team loading based on selected sports
   - Team cards with logos and colors
   - Affinity score selection
   - Progress: Step 3 of 5

4. **PreferencesSetupStep** (`src/components/onboarding/steps/PreferencesSetupStep.tsx`)
   - Notification preferences
   - Content frequency settings
   - Privacy settings
   - Progress: Step 4 of 5

5. **CompletionStep** (`src/components/onboarding/steps/CompletionStep.tsx`)
   - Congratulations message
   - Summary of selected preferences
   - "Enter Corner League Media" button
   - Progress: Step 5 of 5

#### 2.3 State Management Strategy
```typescript
// src/hooks/useOnboardingFlow.ts
interface OnboardingState {
  currentStep: number;
  sports: SportPreference[];
  teams: TeamPreference[];
  preferences: UserPreferences;
  isLoading: boolean;
  errors: Record<string, string>;
}

const useOnboardingFlow = () => {
  // Progressive saving to backend
  // Validation logic
  // Step navigation
  // Error handling
};
```

#### 2.4 Routing Integration
**Modify:** `src/App.tsx`

```typescript
// Add onboarding routes
<Route
  path="/onboarding/*"
  element={
    <ProtectedRoute>
      <OnboardingFlow />
    </ProtectedRoute>
  }
/>

// Add onboarding redirect logic
function OnboardingRedirect() {
  const { user } = useFirebaseAuth();
  const { data: onboardingStatus } = useQuery(getOnboardingStatus);

  if (!onboardingStatus?.is_completed) {
    return <Navigate to="/onboarding" replace />;
  }

  return <DashboardPage />;
}
```

### Phase 3: State Management & Data Flow

#### 3.1 API Client Enhancement
**Modify:** `src/lib/api-client.ts`

```typescript
// Add onboarding API methods
export const onboardingApi = {
  getStatus: () => apiClient.get('/api/onboarding/status'),
  updateSportsPreferences: (data: OnboardingSportsRequest) =>
    apiClient.post('/api/onboarding/sports-preferences', data),
  updateTeamPreferences: (data: OnboardingTeamsRequest) =>
    apiClient.post('/api/onboarding/team-preferences', data),
  completeOnboarding: () => apiClient.post('/api/onboarding/complete'),
};
```

#### 3.2 React Query Integration
```typescript
// src/hooks/queries/useOnboardingQueries.ts
export const useOnboardingQueries = () => {
  return {
    onboardingStatus: useQuery({
      queryKey: ['onboarding', 'status'],
      queryFn: onboardingApi.getStatus,
    }),

    updateSports: useMutation({
      mutationFn: onboardingApi.updateSportsPreferences,
      onSuccess: () => queryClient.invalidateQueries(['onboarding']),
    }),

    updateTeams: useMutation({
      mutationFn: onboardingApi.updateTeamPreferences,
      onSuccess: () => queryClient.invalidateQueries(['onboarding']),
    }),
  };
};
```

### Phase 4: Authentication & Route Protection

#### 4.1 Onboarding Protection Logic
```typescript
// src/components/auth/OnboardingGate.tsx
export function OnboardingGate({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useFirebaseAuth();
  const { data: onboardingStatus, isLoading: statusLoading } = useQuery(getOnboardingStatus);

  if (isLoading || statusLoading) return <AuthLoading />;

  if (!isAuthenticated) return <Navigate to="/auth/sign-in" replace />;

  if (!onboardingStatus?.is_completed) {
    return <Navigate to="/onboarding" replace />;
  }

  return <>{children}</>;
}
```

#### 4.2 Route Structure
```
/auth/sign-in -> Firebase Authentication
/onboarding/welcome -> Step 1: Welcome Screen
/onboarding/sports -> Step 2: Sports Selection
/onboarding/teams -> Step 3: Team Selection
/onboarding/preferences -> Step 4: Preferences Setup
/onboarding/complete -> Step 5: Completion
/ -> Dashboard (protected by onboarding completion)
```

### Phase 5: UI/UX Implementation Details

#### 5.1 Design System Integration
- Use existing shadcn/ui components (Button, Card, Progress, Checkbox, etc.)
- Maintain current color scheme and typography
- Implement drag-and-drop with `@dnd-kit/sortable`
- Use Lucide React icons for sports

#### 5.2 Responsive Design
- Mobile-first approach
- Breakpoints: sm (640px), md (768px), lg (1024px)
- Touch-friendly drag interactions
- Accessible focus states

#### 5.3 Accessibility Requirements
- ARIA labels for all interactive elements
- Screen reader support for drag-and-drop
- Keyboard navigation
- Color contrast compliance
- Focus management between steps

### Phase 6: Testing Strategy

#### 6.1 Unit Testing (validation-testing)
```typescript
// Tests to implement
describe('OnboardingFlow', () => {
  test('renders welcome step initially');
  test('validates sports selection');
  test('saves progress at each step');
  test('handles navigation between steps');
  test('completes onboarding successfully');
});
```

#### 6.2 E2E Testing
```typescript
// Playwright tests
test('complete onboarding flow', async ({ page }) => {
  // Navigate through all 5 steps
  // Verify data persistence
  // Test drag-and-drop functionality
  // Validate final redirect to dashboard
});
```

#### 6.3 API Testing
```python
# FastAPI tests
def test_onboarding_endpoints():
    # Test all new onboarding endpoints
    # Validate data persistence
    # Test error handling
    # Verify authentication requirements
```

### Phase 7: Performance Considerations

#### 7.1 Optimization Strategies
- Lazy load team data based on selected sports
- Implement optimistic updates for better UX
- Use React.memo for expensive components
- Debounce drag-and-drop operations

#### 7.2 Loading States
- Progressive loading for each step
- Skeleton components for data fetching
- Smooth transitions between steps
- Error boundaries for robust error handling

### Phase 8: Error Handling & Edge Cases

#### 8.1 Error Scenarios
- Network connectivity issues
- Firebase authentication failures
- Backend service unavailability
- Invalid user input validation
- Incomplete onboarding recovery

#### 8.2 Recovery Mechanisms
- Auto-save onboarding progress
- Resume from last completed step
- Graceful degradation for API failures
- Clear error messaging and retry options

## Database Considerations

### Migration Requirements
```sql
-- Add onboarding tracking columns
ALTER TABLE users ADD COLUMN onboarding_step INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN onboarding_data JSONB;

-- Create indexes for performance
CREATE INDEX idx_users_onboarding_step ON users(onboarding_step);
CREATE INDEX idx_users_onboarding_completed ON users(onboarding_completed_at)
  WHERE onboarding_completed_at IS NOT NULL;
```

### Data Integrity
- Ensure user preferences are atomic across steps
- Implement database constraints for preference validation
- Add cascading deletes for cleanup
- Foreign key constraints for data relationships

## Development Phases & Dependencies

### Phase 1: Foundation (1-2 days)
**Owner: fastapi-backend-architect**
- [ ] Create onboarding API endpoints
- [ ] Enhance user model with onboarding fields
- [ ] Implement onboarding service layer
- [ ] Create database migrations

### Phase 2: Core Components (2-3 days)
**Owner: nextjs-frontend-dev**
- [ ] Build onboarding layout and step components
- [ ] Implement routing and navigation
- [ ] Create state management hooks
- [ ] Integrate with API client

### Phase 3: Advanced Features (1-2 days)
**Owner: nextjs-frontend-dev**
- [ ] Implement drag-and-drop functionality
- [ ] Add progressive data saving
- [ ] Create validation logic
- [ ] Implement error handling

### Phase 4: Integration & Testing (1-2 days)
**Owner: validation-testing**
- [ ] Write comprehensive unit tests
- [ ] Implement E2E test scenarios
- [ ] Perform accessibility audits
- [ ] Validate API integration

### Phase 5: Polish & Deployment (1 day)
**Owner: All teams**
- [ ] Performance optimization
- [ ] Final UI/UX refinements
- [ ] Security review
- [ ] Deployment preparation

## Quality Gates

### Backend Quality Checklist
- [ ] All API endpoints return proper HTTP status codes
- [ ] Database migrations are reversible
- [ ] Services include comprehensive error handling
- [ ] Authentication middleware properly protects endpoints
- [ ] OpenAPI documentation is complete and accurate

### Frontend Quality Checklist
- [ ] All components are fully accessible (WCAG 2.1 AA)
- [ ] Responsive design works across all breakpoints
- [ ] Loading states provide appropriate user feedback
- [ ] Error boundaries handle unexpected failures gracefully
- [ ] State management is predictable and debuggable

### Integration Quality Checklist
- [ ] End-to-end onboarding flow completes successfully
- [ ] Data persistence works reliably across steps
- [ ] Authentication integrates seamlessly with Firebase
- [ ] API error handling provides meaningful user feedback
- [ ] Performance meets acceptable benchmarks (<2s step transitions)

## Success Criteria

### Functional Requirements
1. ✅ User can complete 5-step onboarding flow
2. ✅ Progress is saved automatically at each step
3. ✅ Sports selection supports drag-to-reorder functionality
4. ✅ Team selection loads dynamically based on selected sports
5. ✅ Onboarding completion sets `onboarding_completed_at` timestamp
6. ✅ Users are redirected to dashboard after completion
7. ✅ Incomplete onboarding redirects to appropriate step

### Non-Functional Requirements
1. ✅ Page load times under 2 seconds
2. ✅ Mobile responsive design (iOS/Android)
3. ✅ WCAG 2.1 AA accessibility compliance
4. ✅ Zero critical security vulnerabilities
5. ✅ 95%+ uptime reliability
6. ✅ Browser compatibility (Chrome, Firefox, Safari, Edge)

## Risk Assessment & Mitigation

### High-Risk Areas
1. **Drag-and-drop complexity on mobile**
   - Mitigation: Provide alternative reordering mechanism
   - Fallback: Simple up/down arrows for ranking

2. **Firebase authentication timing issues**
   - Mitigation: Implement robust loading states
   - Fallback: Retry mechanism with exponential backoff

3. **Large sports/teams dataset performance**
   - Mitigation: Implement pagination and lazy loading
   - Fallback: Virtualized lists for large datasets

### Monitoring & Observability
- Track onboarding completion rates
- Monitor step-by-step drop-off rates
- Log authentication failure patterns
- Measure API response times
- Track user satisfaction metrics

## Post-Launch Iteration Plan

### Phase 1 Enhancements (Post-MVP)
- [ ] Advanced team recommendation engine
- [ ] Social onboarding features (friend recommendations)
- [ ] Personalization based on location
- [ ] Gamification elements (progress badges)

### Phase 2 Enhancements
- [ ] Voice-guided onboarding
- [ ] Integration with external sports data
- [ ] Advanced analytics and insights
- [ ] A/B testing framework for optimization

## Conclusion

This implementation plan provides a comprehensive roadmap for building a robust, accessible, and scalable 5-step onboarding flow. The phased approach ensures quality at each stage while maintaining development velocity. Success depends on close coordination between backend, frontend, and testing teams, with clear handoff criteria and quality gates.

The plan leverages existing infrastructure investments while providing a foundation for future enhancements. Progressive data saving and robust error handling ensure a reliable user experience, while accessibility compliance and responsive design provide inclusive access across all devices and user capabilities.