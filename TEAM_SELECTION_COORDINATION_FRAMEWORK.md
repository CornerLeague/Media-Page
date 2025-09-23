# Team Selection Fix - Multi-Agent Coordination Framework

## Project Overview

**Issue**: Teams cannot be selected in the onboarding flow - need to implement searchable dropdown for team selection

**Current State Analysis**: Comprehensive backend infrastructure already exists with robust team selection APIs. Need frontend implementation and coordination across specialized agents.

## 🎯 4-Phase Implementation Strategy

### Phase 1: Backend Enhancement & Verification
**Agent**: fastapi-backend-architect
**Status**: Backend APIs exist - verification and enhancement needed

### Phase 2: Frontend UI Implementation
**Agent**: nextjs-frontend-dev
**Status**: Pending backend handoff

### Phase 3: Performance & State Management
**Agent**: nextjs-frontend-dev
**Status**: Pending Phase 2 completion

### Phase 4: Testing & Validation
**Agent**: validation-testing
**Status**: Pending Phase 3 completion

## 🔒 Quality Gates & Handoff Contracts

### Phase 1 → Phase 2 Handoff Contract

#### Backend API Contract Verification
**Required Documentation**:
- OpenAPI 3.0 specification for all team selection endpoints
- Database schema validation with migration version numbers
- Error response schema documentation
- Rate limiting and authentication requirements

**API Endpoints to Verify**:
```typescript
// Core team selection endpoints
GET /api/teams/search?query={searchTerm}&sport_id={uuid}&page={number}&page_size={number}
GET /api/sports?include_leagues=true
GET /api/user/team-preferences
POST /api/user/team-preferences
PUT /api/user/team-preferences
DELETE /api/user/team-preferences/{team_id}

// Onboarding flow endpoints
GET /onboarding/sports
GET /onboarding/teams?sport_ids={uuid1,uuid2}
PUT /onboarding/step
POST /onboarding/complete
```

**Response Schema Requirements**:
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

interface UserTeamPreference {
  id: string;
  team_id: string;
  affinity_score: number; // 0.0-1.0
  is_active: boolean;
  team_name: string;
  team_market: string;
  team_display_name: string;
  team_logo_url?: string;
  sport_name: string;
  league_name: string;
}
```

#### Quality Gate Checklist for Phase 1
- [ ] All 8 required API endpoints return proper HTTP status codes
- [ ] Search endpoint supports pagination (1-100 items per page)
- [ ] Team search supports fuzzy matching on name and market fields
- [ ] Firebase JWT authentication working for protected endpoints
- [ ] Error responses include proper error codes and messages
- [ ] Database performance validated for team search queries
- [ ] OpenAPI documentation generates correctly
- [ ] No security vulnerabilities (Semgrep scan clean)

### Phase 2 → Phase 3 Handoff Contract

#### Frontend UI Implementation Requirements
**Component Specifications**:
```typescript
// Searchable team dropdown component
interface TeamSelectorProps {
  selectedTeams: Team[];
  onTeamSelect: (teams: Team[]) => void;
  sportIds?: string[];
  multiSelect?: boolean;
  placeholder?: string;
  maxSelections?: number;
}

// Team selection state management
interface TeamSelectionState {
  searchQuery: string;
  selectedSports: Sport[];
  selectedTeams: Team[];
  searchResults: TeamSearchResponse;
  isLoading: boolean;
  error?: string;
}
```

#### Quality Gate Checklist for Phase 2
- [ ] Searchable dropdown component with debounced search (300ms)
- [ ] Multi-select functionality with visual indicators
- [ ] Sport filtering integration
- [ ] Team logos and colors displayed correctly
- [ ] Responsive design works on mobile and desktop
- [ ] Loading states and error handling implemented
- [ ] Accessibility compliance (axe-core 0 serious/critical violations)
- [ ] TypeScript type safety maintained
- [ ] Component unit tests with >80% coverage

### Phase 3 → Phase 4 Handoff Contract

#### Performance & State Optimization
**Requirements**:
- Search result caching (React Query)
- Optimistic updates for team preferences
- Virtualization for large team lists (>100 teams)
- Search debouncing and request cancellation
- State persistence across onboarding steps

#### Quality Gate Checklist for Phase 3
- [ ] Search performance <200ms for typical queries
- [ ] Memory usage optimized for 1000+ teams
- [ ] Network request optimization (caching, batching)
- [ ] Smooth scrolling for virtualized lists
- [ ] State persistence working correctly
- [ ] Performance tests pass benchmarks
- [ ] Bundle size impact <50KB additional

### Phase 4 Validation Requirements

#### Testing & Integration Validation
**Test Coverage Requirements**:
- Unit tests: Component logic and API integration
- Integration tests: Full onboarding flow with team selection
- E2E tests: Cross-browser team selection workflow
- Performance tests: Search and selection under load
- Accessibility tests: Screen reader and keyboard navigation

#### Quality Gate Checklist for Phase 4
- [ ] All unit tests pass with >90% coverage
- [ ] Integration tests cover happy path and error scenarios
- [ ] E2E tests pass in Chrome, Firefox, Safari
- [ ] Performance benchmarks met
- [ ] Accessibility audit clean (WCAG 2.1 AA)
- [ ] Security scan clean (no XSS, injection vulnerabilities)
- [ ] Code review completed and approved

## 🤝 Inter-Agent Communication Protocols

### Handoff Documentation Requirements
Each phase completion must include:

1. **Technical Handoff Document**
   - Implementation summary with key decisions
   - Updated OpenAPI specs or component interfaces
   - Known issues and limitations
   - Performance metrics and benchmarks

2. **Quality Validation Report**
   - All quality gate checklist items completed
   - Test results and coverage reports
   - Security scan results
   - Performance benchmark results

3. **Next Phase Requirements**
   - Specific requirements for receiving agent
   - Dependencies and blockers
   - Success criteria and acceptance tests

### Communication Channels
- **Documentation**: Shared markdown files in project root
- **Quality Gates**: Checklist validation before handoff
- **Issues**: GitHub issues for cross-phase blockers
- **Code Reviews**: Required for all implementations

## 🚨 Coordination Conflicts & Resolution

### Preventing Parallel File Edits
- **Backend Phase**: Owns `/backend/api/` directory
- **Frontend Phase**: Owns `/src/components/` and `/src/pages/` directories
- **Testing Phase**: Owns `/tests/` and test configuration files
- **Shared Files**: Requires coordination via this framework

### Escalation Protocol
1. **Agent-to-Agent**: Direct communication via handoff documents
2. **Coordination Agent**: Intervention for blocking issues
3. **Project Lead**: Final escalation for architectural decisions

## 📋 Current Backend Assessment

Based on analysis of existing codebase:

### ✅ Existing Backend Capabilities
- **Team Selection API**: Comprehensive endpoints implemented
- **Search Functionality**: Advanced filtering with pagination
- **Authentication**: Firebase JWT integration working
- **Data Models**: Complete Pydantic schemas for all entities
- **Database**: Sports, leagues, teams data properly seeded
- **Onboarding Flow**: 7 endpoints with step tracking

### 🔍 Verification Needed for Phase 1
- **API Performance**: Load testing for search endpoints
- **Error Handling**: Validation of all error scenarios
- **Data Completeness**: Verify all teams have required metadata
- **Security**: Updated security scan for recent changes
- **Documentation**: Ensure OpenAPI specs are complete and accurate

## 🚀 Implementation Kickoff

### Immediate Next Steps
1. **Coordinate with fastapi-backend-architect** for Phase 1 verification
2. **Document API contract** with complete TypeScript interfaces
3. **Validate quality gates** for backend handoff readiness
4. **Prepare frontend requirements** for seamless handoff

### Success Metrics
- **Phase 1**: All API endpoints validated and documented
- **Phase 2**: Searchable team selection UI implemented
- **Phase 3**: Performance optimized and state managed
- **Phase 4**: Full testing coverage and validation complete

## 📁 Related Files

### Backend Infrastructure
- `/backend/api/routers/team_selection.py` - Main team selection router
- `/backend/api/services/team_selection_service.py` - Business logic service
- `/backend/api/schemas/sports.py` - Pydantic data models
- `/backend/api/routers/onboarding.py` - Onboarding flow router

### Documentation
- `/TEAM_SELECTION_API_SUMMARY.md` - Complete API documentation
- `/ONBOARDING_BACKEND_IMPLEMENTATION.md` - Onboarding flow details

### Migration Files
- `/backend/migrations/onboarding_enhancements_migration.py` - Database schema updates

This coordination framework ensures smooth handoffs between specialized agents while maintaining quality and preventing integration failures.