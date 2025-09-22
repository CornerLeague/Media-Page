# Comprehensive Onboarding Flow Playwright Tests

This directory contains a complete test suite for the onboarding flow with special focus on sports selection interactions. The test infrastructure provides comprehensive coverage for accessibility, mobile responsiveness, drag-and-drop functionality, and user interactions.

## Test Files Created

### 1. Core Sports Selection Tests
**File:** `onboarding-sports-selection.spec.ts`

This file contains the main test suite with the following test categories:

#### Core Functionality Tests
- ✅ Page loading and structure verification
- ✅ Sports card clickability and visual feedback
- ✅ Multiple sport selection with ranking
- ✅ Deselection functionality
- ✅ Quick action buttons (Select All, Clear All, Popular Sports)
- ✅ Navigation flow testing

#### Drag and Drop Tests
- ✅ Sports reordering via drag and drop
- ✅ Drag handle separation from click areas
- ✅ Ranking updates after reordering

#### Accessibility Tests
- ✅ WCAG 2.1 AA compliance checking
- ✅ Keyboard navigation support
- ✅ ARIA labels and roles verification
- ✅ Focus management during interactions
- ✅ Screen reader compatibility

#### Mobile and Responsive Tests
- ✅ Mobile viewport testing (375x667)
- ✅ Touch interaction support
- ✅ Multiple screen size adaptation
- ✅ Touch target size verification

#### Error Handling Tests
- ✅ API failure graceful handling
- ✅ Network interruption scenarios
- ✅ Offline mode functionality

#### Performance Tests
- ✅ Page load time measurement
- ✅ Interaction response time testing
- ✅ Rapid interaction handling

#### Visual Regression Tests
- ✅ Initial state baseline
- ✅ Selected sports visual state
- ✅ Mobile layout screenshots
- ✅ Dark mode visual testing

### 2. Comprehensive Accessibility Tests
**File:** `accessibility-onboarding.spec.ts`

Dedicated accessibility testing with:
- ✅ WCAG 2.1 AA compliance verification
- ✅ Heading structure validation
- ✅ Focus order checking
- ✅ ARIA attributes verification
- ✅ Color contrast testing
- ✅ Screen reader simulation
- ✅ High contrast mode support
- ✅ Reduced motion preference handling

### 3. Test Utilities and Helpers
**File:** `test-utils/onboarding-helpers.ts`

Comprehensive helper classes including:

#### SportsSelectionHelpers
- Sport card interaction methods
- Selection state verification
- Drag and drop utilities
- Action button interactions

#### OnboardingFlowHelpers
- Step navigation
- Progress tracking
- Flow validation

#### AccessibilityHelpers
- Focus order testing
- Keyboard navigation
- ARIA label verification

#### ResponsiveHelpers
- Viewport management
- Touch interaction testing
- Target size verification

#### ErrorHandlingHelpers
- Network error simulation
- Slow network testing
- Error state verification

#### VisualTestHelpers
- Screenshot capture
- Theme switching
- Visual baseline management

#### PerformanceHelpers
- Load time measurement
- Interaction timing
- Metrics collection

## Test Features

### Sports Selection Specific Testing
The tests specifically focus on the sports selection interaction with:

1. **Card Clickability Testing**
   - Verifies sports cards respond to clicks
   - Checks visual feedback on selection
   - Validates selection state changes

2. **Ranking System Testing**
   - Tests automatic ranking assignment
   - Verifies ranking display (1st, 2nd, 3rd, 4th)
   - Validates reordering functionality

3. **Drag and Drop Testing**
   - Tests sports reordering via drag handles
   - Verifies drag handle isolation from click areas
   - Validates ranking updates after reordering

4. **Quick Actions Testing**
   - "Select All" button functionality
   - "Clear All" button functionality
   - "Popular Sports" selection
   - Maximum selection limits (5 sports)

### API Mocking Strategy
All tests use comprehensive API mocks:

```typescript
const MOCK_SPORTS = [
  { id: 'nfl', name: 'Football', icon: '🏈', isPopular: true, hasTeams: true },
  { id: 'nba', name: 'Basketball', icon: '🏀', isPopular: true, hasTeams: true },
  // ... more sports
];
```

### Error Handling and Resilience
Tests cover various failure scenarios:
- API unavailability with fallback data
- Network timeouts
- Slow network conditions
- Offline mode functionality

## Running the Tests

### Basic Test Execution
```bash
# Run all onboarding sports selection tests
npm run test:e2e -- --grep "Onboarding Sports Selection"

# Run specific test group
npm run test:e2e -- --grep "sports cards are clickable"

# Run accessibility tests only
npm run test:e2e:accessibility

# Run on specific browser
npm run test:e2e -- --project=chromium
```

### Debug Mode
```bash
# Run with debug mode (opens browser)
npm run test:e2e:debug -- --grep "sports selection"

# Run with headed mode
npm run test:e2e -- --headed --grep "sports selection"
```

### Mobile Testing
```bash
# Run mobile tests specifically
npm run test:e2e -- --project="Mobile Chrome" --grep "sports selection"
```

### Visual Testing
```bash
# Update visual baselines
npm run test:e2e -- --update-snapshots --grep "visual regression"
```

## Test Structure and Page Objects

### SportsSelectionPageObject
Provides methods for:
- `goto(step)` - Navigate to onboarding step
- `clickSportCard(sportId)` - Click a specific sport
- `isSportSelected(sportId)` - Check selection state
- `getSportRank(sportId)` - Get sport ranking
- `getSelectedSportsCount()` - Count selected sports
- `dragSportToSport(from, to)` - Drag and drop reordering

### Test Data Management
Consistent mock data across all tests:
- 7 different sports with varying popularity
- Team data for sports that have teams
- Proper API response structures

## Expected Test Outcomes

### Passing Tests Should Verify:
1. ✅ Sports cards load and display correctly
2. ✅ Clicking sports cards toggles selection state
3. ✅ Selected sports show proper visual feedback
4. ✅ Rankings are assigned and displayed correctly
5. ✅ Drag and drop reordering works
6. ✅ Navigation between steps functions
7. ✅ Accessibility standards are met
8. ✅ Mobile responsiveness is maintained
9. ✅ Error states are handled gracefully
10. ✅ Performance meets expectations

### Test Coverage Areas:
- **Functional Testing**: Core sports selection interactions
- **Accessibility Testing**: WCAG 2.1 AA compliance
- **Visual Testing**: UI consistency across states
- **Performance Testing**: Load times and responsiveness
- **Error Handling**: Graceful failure scenarios
- **Mobile Testing**: Touch interactions and responsive design

## Troubleshooting

### Common Issues:
1. **Page Not Loading**: Ensure dev server is running on port 8080
2. **Authentication Errors**: Tests should use `__PLAYWRIGHT_TEST__` flag
3. **API Mocking**: Verify mock routes are set up in beforeEach
4. **Timeout Issues**: Increase timeout for slower environments

### Debug Commands:
```bash
# Check what's on the page
await page.screenshot({ path: 'debug.png' });
await page.locator('body').textContent();
```

## Integration with CI/CD

The tests are configured to work in CI environments with:
- Retry logic for flaky tests
- Artifact collection (screenshots, videos)
- Multiple browser testing
- Performance budget validation

This comprehensive test suite ensures the onboarding flow, particularly the sports selection step, provides an excellent user experience across all devices and accessibility needs.