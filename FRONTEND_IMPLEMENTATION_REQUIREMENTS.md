# Frontend Implementation Requirements
## Searchable Team Dropdown for Onboarding Flow

**Phase 2**: Frontend UI Implementation
**Agent**: nextjs-frontend-dev
**Dependencies**: Backend API contract verified ✅

## 🎯 Implementation Overview

### Core Requirement
Implement a searchable, multi-select team dropdown component that integrates with the existing onboarding flow to solve the issue where "teams can't be selected in the onboarding flow."

### User Experience Goals
1. **Fast Search**: Responsive team search with <300ms debounced queries
2. **Multi-Sport Support**: Filter teams by selected sports from Step 2
3. **Visual Clarity**: Display team logos, colors, and league information
4. **Accessibility**: Full keyboard navigation and screen reader support
5. **Mobile Responsive**: Works seamlessly on all device sizes

## 🏗️ Component Architecture

### 1. TeamSelector Component
```typescript
// /src/components/TeamSelector.tsx
interface TeamSelectorProps {
  selectedTeams: Team[];
  onTeamSelect: (teams: Team[]) => void;
  sportIds?: string[];           // Filter by selected sports
  multiSelect?: boolean;         // Default: true
  placeholder?: string;          // Default: "Search for teams..."
  maxSelections?: number;        // Default: unlimited
  disabled?: boolean;
  error?: string;
  className?: string;
}

// Key features:
// - Radix UI Combobox as base component
// - React Query for API data management
// - Virtualized scrolling for 100+ teams
// - Debounced search with AbortController
// - Keyboard navigation (arrow keys, enter, escape)
// - Loading states and error handling
```

### 2. TeamSelectionAPI Client
```typescript
// /src/lib/api/teamSelection.ts
class TeamSelectionAPI {
  private baseURL: string;
  private authToken?: string;

  async searchTeams(params: TeamSearchParams): Promise<TeamSearchResponse>
  async getSports(includeLeagues?: boolean): Promise<Sport[]>
  async getOnboardingSports(): Promise<OnboardingSportResponse[]>
  async getOnboardingTeams(sportIds: string[]): Promise<OnboardingTeamResponse[]>
  async getUserPreferences(): Promise<UserTeamPreferencesResponse>
  async updateUserPreferences(update: UserTeamPreferencesUpdate): Promise<UserTeamPreferencesResponse>
}

// Error handling:
// - Automatic retry for 5xx errors (exponential backoff)
// - Request cancellation for search queries
// - User-friendly error messages
// - Network failure detection
```

### 3. State Management with React Query
```typescript
// /src/hooks/useTeamSelection.ts
export function useTeamSelection(sportIds?: string[]) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTeams, setSelectedTeams] = useState<Team[]>([]);

  // Debounced team search
  const {
    data: searchResults,
    isLoading: isSearching,
    error: searchError
  } = useQuery({
    queryKey: ['teams', 'search', searchQuery, sportIds],
    queryFn: () => teamAPI.searchTeams({
      query: searchQuery,
      sport_id: sportIds?.join(','),
      page_size: 50
    }),
    enabled: searchQuery.length >= 2,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Sports data for filtering
  const { data: sports } = useQuery({
    queryKey: ['onboarding', 'sports'],
    queryFn: () => teamAPI.getOnboardingSports(),
    staleTime: 60 * 60 * 1000, // 1 hour
  });

  return {
    searchQuery,
    setSearchQuery,
    selectedTeams,
    setSelectedTeams,
    searchResults,
    isSearching,
    searchError,
    sports
  };
}
```

## 🎨 UI/UX Design Specifications

### Visual Design Requirements
Based on existing shadcn/ui design system:

```css
/* Team dropdown styling */
.team-selector {
  @apply relative w-full;
}

.team-search-input {
  @apply flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50;
}

.team-option {
  @apply relative flex cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none aria-selected:bg-accent aria-selected:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50;
}

.team-logo {
  @apply h-6 w-6 rounded-full object-cover mr-3;
}

.team-colors {
  @apply flex gap-1 ml-auto;
}

.team-color-swatch {
  @apply h-3 w-3 rounded-full border border-border;
}
```

### Team Option Display Format
```tsx
// Each team option shows:
<div className="team-option">
  <img src={team.logo_url} alt="" className="team-logo" />
  <div className="flex-1">
    <div className="font-medium">{team.display_name}</div>
    <div className="text-sm text-muted-foreground">
      {team.league_name} • {team.sport_name}
    </div>
  </div>
  <div className="team-colors">
    {team.primary_color && (
      <div
        className="team-color-swatch"
        style={{ backgroundColor: team.primary_color }}
      />
    )}
    {team.secondary_color && (
      <div
        className="team-color-swatch"
        style={{ backgroundColor: team.secondary_color }}
      />
    )}
  </div>
  {isSelected && <Check className="h-4 w-4" />}
</div>
```

### Selected Teams Display
```tsx
// Compact chips showing selected teams
<div className="selected-teams">
  {selectedTeams.map(team => (
    <div key={team.id} className="team-chip">
      <img src={team.logo_url} alt="" className="h-4 w-4" />
      <span className="text-sm">{team.name}</span>
      <button onClick={() => removeTeam(team.id)}>
        <X className="h-3 w-3" />
      </button>
    </div>
  ))}
</div>
```

## 🔄 Integration with Onboarding Flow

### Step 3: Team Selection Integration
```typescript
// /src/pages/onboarding/Step3TeamSelection.tsx
export default function Step3TeamSelection() {
  const { selectedSports } = useOnboardingStore(); // From Step 2
  const { selectedTeams, setSelectedTeams } = useOnboardingStore();

  const sportIds = selectedSports.map(sport => sport.id);

  const handleTeamSelect = async (teams: Team[]) => {
    setSelectedTeams(teams);

    // Auto-save preferences if user is authenticated
    if (user?.uid) {
      try {
        await teamAPI.updateUserPreferences({
          preferences: teams.map(team => ({
            team_id: team.id,
            affinity_score: 0.8, // Default affinity
            is_active: true
          }))
        });
      } catch (error) {
        console.warn('Failed to save preferences:', error);
        // Don't block UI - preferences can be saved later
      }
    }
  };

  return (
    <OnboardingLayout
      step={3}
      title="Select Your Favorite Teams"
      description="Choose the teams you want to follow for personalized content"
    >
      <TeamSelector
        selectedTeams={selectedTeams}
        onTeamSelect={handleTeamSelect}
        sportIds={sportIds}
        multiSelect={true}
        placeholder="Search for your favorite teams..."
        maxSelections={10}
      />

      <OnboardingNavigation
        canContinue={selectedTeams.length > 0}
        onNext={() => navigateToStep(4)}
        onBack={() => navigateToStep(2)}
      />
    </OnboardingLayout>
  );
}
```

### Onboarding State Management
```typescript
// /src/stores/onboardingStore.ts
interface OnboardingState {
  currentStep: number;
  selectedSports: Sport[];      // Step 2
  selectedTeams: Team[];        // Step 3
  preferences: any;             // Step 4
  notifications: any;           // Step 5
  isLoading: boolean;
  error?: string;
}

export const useOnboardingStore = create<OnboardingState>((set) => ({
  currentStep: 1,
  selectedSports: [],
  selectedTeams: [],
  preferences: {},
  notifications: {},
  isLoading: false,

  setSelectedTeams: (teams) => set({ selectedTeams: teams }),
  nextStep: () => set((state) => ({ currentStep: state.currentStep + 1 })),
  previousStep: () => set((state) => ({ currentStep: Math.max(1, state.currentStep - 1) })),
}));
```

## ⚡ Performance Optimization

### Search Optimization
```typescript
// Debounced search with cancellation
const [searchQuery, setSearchQuery] = useState('');
const [abortController, setAbortController] = useState<AbortController>();

const debouncedSearch = useDebouncedCallback(
  async (query: string) => {
    // Cancel previous request
    abortController?.abort();

    if (query.length < 2) return;

    const newController = new AbortController();
    setAbortController(newController);

    try {
      const results = await teamAPI.searchTeams(
        { query, sport_id: sportIds?.join(',') },
        { signal: newController.signal }
      );
      setSearchResults(results);
    } catch (error) {
      if (error.name !== 'AbortError') {
        setSearchError(error.message);
      }
    }
  },
  300 // 300ms delay
);
```

### Virtualization for Large Lists
```typescript
// Using react-window for 100+ teams
import { FixedSizeList as List } from 'react-window';

const TeamVirtualList = ({ teams, onSelect }) => {
  const Row = ({ index, style }) => (
    <div style={style}>
      <TeamOption
        team={teams[index]}
        onSelect={onSelect}
      />
    </div>
  );

  return (
    <List
      height={300}
      itemCount={teams.length}
      itemSize={60}
      overscanCount={5}
    >
      {Row}
    </List>
  );
};
```

## ♿ Accessibility Implementation

### Keyboard Navigation
```typescript
// Arrow key navigation
const handleKeyDown = (e: KeyboardEvent) => {
  switch (e.key) {
    case 'ArrowDown':
      e.preventDefault();
      setFocusedIndex(prev => Math.min(prev + 1, teams.length - 1));
      break;
    case 'ArrowUp':
      e.preventDefault();
      setFocusedIndex(prev => Math.max(prev - 1, 0));
      break;
    case 'Enter':
      e.preventDefault();
      if (focusedIndex >= 0) {
        handleTeamSelect(teams[focusedIndex]);
      }
      break;
    case 'Escape':
      setIsOpen(false);
      break;
  }
};
```

### ARIA Labels and Screen Reader Support
```tsx
<div
  role="combobox"
  aria-expanded={isOpen}
  aria-haspopup="listbox"
  aria-label="Select teams"
>
  <input
    ref={inputRef}
    type="text"
    value={searchQuery}
    onChange={(e) => setSearchQuery(e.target.value)}
    onKeyDown={handleKeyDown}
    aria-autocomplete="list"
    aria-controls="team-list"
    aria-activedescendant={focusedIndex >= 0 ? `team-${teams[focusedIndex]?.id}` : undefined}
    placeholder="Search for teams..."
  />

  {isOpen && (
    <ul
      id="team-list"
      role="listbox"
      aria-label="Team options"
    >
      {teams.map((team, index) => (
        <li
          key={team.id}
          id={`team-${team.id}`}
          role="option"
          aria-selected={selectedTeams.some(t => t.id === team.id)}
          data-focused={index === focusedIndex}
          onClick={() => handleTeamSelect(team)}
        >
          {/* Team option content */}
        </li>
      ))}
    </ul>
  )}
</div>
```

## 🧪 Testing Requirements

### Unit Tests
```typescript
// /src/components/__tests__/TeamSelector.test.tsx
describe('TeamSelector', () => {
  it('should search teams with debouncing', async () => {
    render(<TeamSelector {...props} />);

    const input = screen.getByRole('combobox');
    fireEvent.change(input, { target: { value: 'Lakers' } });

    // Should not search immediately
    expect(mockSearchTeams).not.toHaveBeenCalled();

    // Should search after debounce delay
    await waitFor(() => {
      expect(mockSearchTeams).toHaveBeenCalledWith({
        query: 'Lakers',
        sport_id: undefined
      });
    }, { timeout: 400 });
  });

  it('should filter teams by sport', async () => {
    render(<TeamSelector sportIds={['basketball-id']} {...props} />);

    const input = screen.getByRole('combobox');
    fireEvent.change(input, { target: { value: 'Lakers' } });

    await waitFor(() => {
      expect(mockSearchTeams).toHaveBeenCalledWith({
        query: 'Lakers',
        sport_id: 'basketball-id'
      });
    });
  });

  it('should handle keyboard navigation', () => {
    render(<TeamSelector {...props} />);

    const input = screen.getByRole('combobox');
    fireEvent.keyDown(input, { key: 'ArrowDown' });

    // Should focus first option
    expect(screen.getByRole('option', { name: /first team/i }))
      .toHaveAttribute('data-focused', 'true');
  });
});
```

### Integration Tests
```typescript
// /src/pages/onboarding/__tests__/Step3TeamSelection.test.tsx
describe('Step 3 Team Selection', () => {
  it('should complete onboarding flow with team selection', async () => {
    const user = userEvent.setup();
    render(<OnboardingFlow />);

    // Navigate to step 3
    await user.click(screen.getByText('Next'));
    await user.click(screen.getByText('Next'));

    // Search and select teams
    const searchInput = screen.getByPlaceholderText('Search for teams...');
    await user.type(searchInput, 'Lakers');

    await waitFor(() => {
      expect(screen.getByText('Los Angeles Lakers')).toBeInTheDocument();
    });

    await user.click(screen.getByText('Los Angeles Lakers'));

    // Should enable continue button
    expect(screen.getByText('Continue')).not.toBeDisabled();

    // Should save preferences
    await user.click(screen.getByText('Continue'));
    expect(mockUpdatePreferences).toHaveBeenCalledWith({
      preferences: [{ team_id: 'lakers-id', affinity_score: 0.8, is_active: true }]
    });
  });
});
```

## 📱 Mobile Responsiveness

### Touch Optimization
```css
/* Mobile-first responsive design */
@media (max-width: 768px) {
  .team-selector {
    @apply w-full;
  }

  .team-option {
    @apply py-3 px-4; /* Larger touch targets */
  }

  .team-logo {
    @apply h-8 w-8; /* Larger logos on mobile */
  }

  .selected-teams {
    @apply grid grid-cols-2 gap-2; /* Stack selected teams */
  }
}

/* Touch-friendly scrolling */
.team-list {
  @apply overflow-auto;
  -webkit-overflow-scrolling: touch;
}
```

### Virtual Keyboard Handling
```typescript
// Handle mobile virtual keyboard
useEffect(() => {
  const handleResize = () => {
    if (window.visualViewport) {
      const viewportHeight = window.visualViewport.height;
      const windowHeight = window.innerHeight;
      const isKeyboardOpen = viewportHeight < windowHeight * 0.75;

      if (isKeyboardOpen) {
        // Adjust dropdown height when keyboard is open
        setDropdownMaxHeight(viewportHeight * 0.4);
      } else {
        setDropdownMaxHeight(300);
      }
    }
  };

  window.visualViewport?.addEventListener('resize', handleResize);
  return () => window.visualViewport?.removeEventListener('resize', handleResize);
}, []);
```

## ✅ Acceptance Criteria

### Functional Requirements
- [ ] Users can search for teams with fuzzy matching
- [ ] Search is debounced and performs well with 265+ teams
- [ ] Teams are filtered by selected sports from Step 2
- [ ] Multiple teams can be selected and deselected
- [ ] Selected teams display with logos and colors
- [ ] Team preferences are saved to backend API
- [ ] Error states are handled gracefully
- [ ] Loading states provide feedback

### Performance Requirements
- [ ] Search results appear within 300ms of typing
- [ ] Smooth scrolling with virtualization for 100+ teams
- [ ] Bundle size increase <50KB
- [ ] Mobile performance maintains 60fps

### Accessibility Requirements
- [ ] Full keyboard navigation (arrow keys, enter, escape)
- [ ] Screen reader compatibility (ARIA labels)
- [ ] Focus management and visual indicators
- [ ] Color contrast meets WCAG 2.1 AA standards

### Quality Requirements
- [ ] Unit test coverage >80%
- [ ] Integration tests cover happy path and errors
- [ ] TypeScript strict mode compliance
- [ ] ESLint and Prettier compliance
- [ ] Mobile responsive design verified

## 🚀 Implementation Plan

### Week 1: Core Component
1. Create TeamSelector component with basic search
2. Implement API client with React Query
3. Add debounced search with cancellation
4. Basic styling with shadcn/ui components

### Week 2: Integration & Polish
1. Integrate with onboarding flow (Step 3)
2. Add virtualization for large lists
3. Implement keyboard navigation
4. Add accessibility features

### Week 3: Testing & Optimization
1. Write comprehensive unit tests
2. Add integration tests for onboarding flow
3. Performance optimization and bundle analysis
4. Mobile responsiveness testing

## 📁 File Structure

```
src/
├── components/
│   ├── TeamSelector.tsx           # Main component
│   ├── TeamOption.tsx             # Individual team option
│   ├── TeamChip.tsx               # Selected team display
│   └── __tests__/
│       └── TeamSelector.test.tsx
├── hooks/
│   └── useTeamSelection.ts        # State management hook
├── lib/
│   └── api/
│       └── teamSelection.ts       # API client
├── pages/
│   └── onboarding/
│       └── Step3TeamSelection.tsx # Onboarding integration
└── stores/
    └── onboardingStore.ts         # Global onboarding state
```

**Implementation Status**: ✅ Ready for nextjs-frontend-dev Agent
**Estimated Effort**: 2-3 weeks
**Priority**: High (blocking onboarding flow completion)