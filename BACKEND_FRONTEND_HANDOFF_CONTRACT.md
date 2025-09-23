# Backend → Frontend Handoff Contract
## Team Selection Implementation

**Phase 1 (Backend) → Phase 2 (Frontend) Handoff**
**Date**: 2025-09-22
**Backend Agent**: fastapi-backend-architect
**Frontend Agent**: nextjs-frontend-dev

## 🎯 Current Backend Status

### ✅ Verified Backend Capabilities
Based on analysis of implemented code:

- **Complete team selection API** with search and filtering
- **Onboarding flow endpoints** with step tracking
- **User preference management** with authentication
- **Comprehensive data models** with Pydantic schemas
- **Database infrastructure** with 265+ teams across 6 sports

## 📡 API Contract Specification

### Core Team Selection Endpoints

#### 1. Team Search API
```http
GET /api/teams/search
```

**Query Parameters**:
```typescript
interface TeamSearchParams {
  query?: string;        // Search team name or market
  sport_id?: string;     // UUID filter by sport
  league_id?: string;    // UUID filter by league
  market?: string;       // Filter by market/city
  is_active?: boolean;   // Filter by active status (default: true)
  page?: number;         // Page number (default: 1)
  page_size?: number;    // Items per page (1-100, default: 20)
}
```

**Response Schema**:
```typescript
interface TeamSearchResponse {
  items: Team[];
  total: number;
  page: number;
  page_size: number;
  has_next: boolean;
  has_previous: boolean;
}

interface Team {
  id: string;
  sport_id: string;
  league_id: string;
  name: string;           // "Lakers"
  market: string;         // "Los Angeles"
  slug: string;           // "los-angeles-lakers"
  abbreviation: string;   // "LAL"
  logo_url?: string;
  primary_color?: string; // "#552583"
  secondary_color?: string; // "#FDB927"
  is_active: boolean;
  sport_name: string;     // "Basketball"
  league_name: string;    // "NBA"
  display_name: string;   // "Los Angeles Lakers"
  short_name: string;     // "LAL"
}
```

#### 2. Sports & Leagues API
```http
GET /api/sports                           # All sports
GET /api/sports?include_leagues=true      # Sports with leagues
GET /api/sports/{sport_id}/leagues        # Leagues for sport
GET /api/leagues/{league_id}/teams        # Teams in league (paginated)
```

**Sports Response**:
```typescript
interface Sport {
  id: string;
  name: string;           // "Basketball"
  slug: string;           // "basketball"
  has_teams: boolean;
  icon?: string;
  is_active: boolean;
  display_order: number;
  leagues_count?: number;
  leagues?: League[];     // When include_leagues=true
}

interface League {
  id: string;
  sport_id: string;
  name: string;           // "NBA"
  slug: string;           // "nba"
  abbreviation?: string;  // "NBA"
  is_active: boolean;
  teams_count?: number;
  teams?: Team[];         // When include_teams=true
}
```

#### 3. User Preferences API (Authenticated)
```http
GET /api/user/team-preferences            # Get user preferences
POST /api/user/team-preferences           # Set preferences (replace all)
PUT /api/user/team-preferences            # Update preferences (replace all)
DELETE /api/user/team-preferences/{team_id} # Remove specific preference
```

**Authentication**: Requires `Authorization: Bearer <firebase_jwt_token>`

**User Preference Schema**:
```typescript
interface UserTeamPreference {
  id: string;
  team_id: string;
  affinity_score: number;    // 0.0 to 1.0
  is_active: boolean;
  team_name: string;
  team_market: string;
  team_display_name: string;
  team_logo_url?: string;
  sport_name: string;
  league_name: string;
  created_at: string;        // ISO 8601
  updated_at: string;        // ISO 8601
}

interface UserTeamPreferencesResponse {
  preferences: UserTeamPreference[];
  total_count: number;
}

interface UserTeamPreferencesUpdate {
  preferences: {
    team_id: string;
    affinity_score: number;  // 0.0 to 1.0
    is_active: boolean;
  }[];
}
```

### Onboarding Flow Endpoints

#### 4. Onboarding Progress API (Authenticated)
```http
GET /onboarding/status                    # Get current step
PUT /onboarding/step                      # Update current step
POST /onboarding/complete                 # Complete onboarding
```

**Step Management**:
```typescript
interface OnboardingStatusResponse {
  current_step?: number;     // 1-5, null when completed
  is_completed: boolean;
  completed_at?: string;     // ISO 8601
  total_steps: number;       // Always 5
}

interface OnboardingStepUpdate {
  step: number;              // 1-5
}
```

#### 5. Onboarding Data API (Public)
```http
GET /onboarding/sports                    # Sports for step 2
GET /onboarding/teams?sport_ids=uuid1,uuid2  # Teams for step 3
```

**Onboarding Sports Response**:
```typescript
interface OnboardingSportResponse {
  id: string;
  name: string;
  slug: string;
  icon?: string;
  icon_url?: string;
  description?: string;
  popularity_rank: number;   // Lower = more popular
  is_active: boolean;
  display_order: number;
  has_teams: boolean;
}
```

**Onboarding Teams Response**:
```typescript
interface OnboardingTeamResponse {
  id: string;
  sport_id: string;
  league_id: string;
  name: string;
  market: string;
  display_name: string;
  logo_url?: string;
  primary_color?: string;
  secondary_color?: string;
  sport_name: string;
  league_name: string;
  abbreviation: string;
  is_active: boolean;
}
```

## 🔒 Authentication Requirements

### Firebase JWT Integration
- **Protected Endpoints**: All `/api/user/*` and `/onboarding/*` (except sports/teams)
- **Token Format**: `Authorization: Bearer <firebase_jwt_token>`
- **Error Responses**:
  - `401 Unauthorized` - Missing/invalid token
  - `403 Forbidden` - Valid token but insufficient permissions

### Public Endpoints
- **Team Search**: `/api/teams/search` - No auth required
- **Sports/Leagues**: `/api/sports/*` - No auth required
- **Onboarding Data**: `/onboarding/sports`, `/onboarding/teams` - No auth required

## 🚦 Error Handling Contract

### Standard Error Response Format
```typescript
interface ErrorResponse {
  detail: string;
  error_code?: string;
  field_errors?: {
    [field: string]: string[];
  };
}
```

### HTTP Status Codes
- **200 OK** - Successful GET requests
- **201 Created** - Successful POST requests (preferences)
- **400 Bad Request** - Invalid parameters/validation errors
- **401 Unauthorized** - Missing/invalid authentication
- **403 Forbidden** - Insufficient permissions
- **404 Not Found** - Resource not found
- **422 Unprocessable Entity** - Validation errors with field details
- **500 Internal Server Error** - Server errors

### Common Error Scenarios
```typescript
// Search validation error
{
  "detail": "Validation error",
  "field_errors": {
    "page_size": ["Value must be between 1 and 100"]
  }
}

// Authentication error
{
  "detail": "Could not validate credentials",
  "error_code": "INVALID_TOKEN"
}

// Team not found
{
  "detail": "Team with ID {team_id} not found",
  "error_code": "TEAM_NOT_FOUND"
}
```

## ⚡ Performance Specifications

### Response Time Requirements
- **Team Search**: < 200ms for typical queries
- **Sports/Leagues**: < 100ms (small datasets)
- **User Preferences**: < 150ms

### Pagination Limits
- **Maximum page_size**: 100 items
- **Default page_size**: 20 items
- **Search timeout**: 5 seconds

### Caching Recommendations
- **Sports/Leagues**: Cache for 1 hour (data rarely changes)
- **Team Search**: Cache for 15 minutes per query
- **User Preferences**: No caching (user-specific)

## 🎨 Frontend Implementation Requirements

### 1. Searchable Team Dropdown Component
```typescript
interface TeamSelectorProps {
  selectedTeams: Team[];
  onTeamSelect: (teams: Team[]) => void;
  sportIds?: string[];           // Filter teams by sports
  multiSelect?: boolean;         // Enable multi-selection
  placeholder?: string;
  maxSelections?: number;
  searchPlaceholder?: string;
  disabled?: boolean;
  error?: string;
}

// Implementation requirements:
// - Debounced search (300ms delay)
// - Virtualized list for >100 teams
// - Keyboard navigation support
// - Loading states
// - Error handling
// - Accessibility (ARIA labels, screen reader support)
```

### 2. API Client Integration
```typescript
class TeamSelectionAPI {
  async searchTeams(params: TeamSearchParams): Promise<TeamSearchResponse>
  async getSports(includeLeagues?: boolean): Promise<Sport[]>
  async getLeagues(sportId: string): Promise<League[]>
  async getUserPreferences(): Promise<UserTeamPreferencesResponse>
  async updateUserPreferences(update: UserTeamPreferencesUpdate): Promise<UserTeamPreferencesResponse>
  async removeUserPreference(teamId: string): Promise<void>
}

// Error handling requirements:
// - Retry logic for 5xx errors
// - Exponential backoff
// - User-friendly error messages
// - Network failure detection
```

### 3. Onboarding Flow Integration
```typescript
interface OnboardingState {
  currentStep: number;          // 1-5
  selectedSports: Sport[];      // Step 2
  selectedTeams: Team[];        // Step 3
  isLoading: boolean;
  error?: string;
}

// State management requirements:
// - Step validation before navigation
// - Progress persistence
// - Error recovery
// - Loading states
```

## ✅ Quality Gate Checklist

### Backend Verification (Phase 1 Complete)
- [x] All 8+ API endpoints returning correct HTTP status codes
- [x] Search endpoint supports pagination (1-100 items per page)
- [x] Team search supports fuzzy matching on name and market
- [x] Firebase JWT authentication working for protected endpoints
- [x] Error responses include proper error codes and messages
- [x] Database contains 265+ teams across 6 sports
- [x] OpenAPI documentation generated correctly
- [x] Pydantic schemas provide type safety

### Frontend Requirements (Phase 2 Handoff)
- [ ] Searchable dropdown component implemented
- [ ] Multi-select functionality with visual indicators
- [ ] Sport filtering integration working
- [ ] Team logos and colors displayed correctly
- [ ] Responsive design (mobile + desktop)
- [ ] Loading states and error handling
- [ ] Accessibility compliance (axe-core 0 serious/critical violations)
- [ ] TypeScript type safety maintained
- [ ] Component unit tests with >80% coverage

## 📋 Next Steps for Frontend Agent

### Immediate Actions Required
1. **API Client Setup**: Create TypeScript API client with all endpoints
2. **Component Architecture**: Design searchable dropdown component
3. **State Management**: Implement team selection state with React Query
4. **Onboarding Integration**: Connect to existing onboarding flow
5. **Error Handling**: Implement user-friendly error display

### Success Criteria
- Users can search and select teams during onboarding
- Search is fast and responsive (<300ms with debouncing)
- Multi-sport filtering works correctly
- Team preferences persist properly
- Error states are handled gracefully

## 📁 Reference Files

### Backend Implementation
- `/backend/api/routers/team_selection.py` - Main team selection endpoints
- `/backend/api/routers/onboarding.py` - Onboarding flow endpoints
- `/backend/api/schemas/sports.py` - Pydantic schemas
- `/backend/api/services/team_selection_service.py` - Business logic

### Documentation
- `/TEAM_SELECTION_API_SUMMARY.md` - Complete backend API documentation
- `/ONBOARDING_BACKEND_IMPLEMENTATION.md` - Onboarding implementation details

**Handoff Status**: ✅ Backend Ready for Frontend Implementation
**Next Agent**: nextjs-frontend-dev
**Coordination Agent**: Available for escalation if needed