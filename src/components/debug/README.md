# Debug System Integration Guide

This directory contains comprehensive debugging utilities for the Corner League Media application. The debug system provides error reporting, API logging, performance monitoring, and development tools.

## Components

### DebugProvider
The main provider component that wraps your application to enable debugging features.

### DebugPanel
A visual debugging interface that shows error reports, API logs, performance metrics, and debugging tools.

## Quick Setup

### 1. Wrap your App with DebugProvider

```tsx
// src/App.tsx
import { DebugProvider } from '@/components/debug/DebugProvider';

function App() {
  return (
    <DebugProvider>
      {/* Your existing app components */}
      <Router>
        <Routes>
          {/* Your routes */}
        </Routes>
      </Router>
    </DebugProvider>
  );
}
```

### 2. Use Debug Hooks in Components

```tsx
// In any component
import { useDebug, useOnboardingDebug } from '@/hooks/useDebug';

function MyComponent() {
  const debug = useDebug('MyComponent');

  const handleError = (error: Error) => {
    debug.reportComponentError('MyComponent', error, {
      additionalContext: 'Some context'
    });
  };

  const handleStateChange = (newState: any) => {
    debug.logStateChange('MyComponent', previousState, newState);
  };

  return (
    <div>
      {/* Your component JSX */}
    </div>
  );
}
```

### 3. Onboarding-Specific Debugging

```tsx
// In onboarding components
import { useOnboardingDebug } from '@/hooks/useDebug';

function OnboardingStep({ step }: { step: number }) {
  const debug = useOnboardingDebug(step, 'OnboardingStep');

  const handleStepComplete = (data: any) => {
    debug.logOnboardingAction('step_complete', data);
  };

  const handleError = (error: Error) => {
    debug.reportOnboardingError('Failed to complete step', error);
  };

  return (
    <div>
      {/* Your onboarding step JSX */}
    </div>
  );
}
```

## Keyboard Shortcuts (Development Only)

- **Ctrl/Cmd + Shift + D**: Toggle Debug Panel
- **Ctrl/Cmd + Shift + E**: Export Debug Data
- **Ctrl/Cmd + Shift + C**: Clear Debug Data

## Browser Console Access

In development, debugging utilities are available globally:

```javascript
// Access debug manager
window.__cornerLeagueDebug.debugManager

// Export all debug data
window.__cornerLeagueDebug.exportDebugData()

// Clear debug data
window.__cornerLeagueDebug.clearDebugData()

// Access error reporting
window.__cornerLeagueDebug.errorReporting.getMetrics()
```

## Features

### Error Reporting
- Automatic error capture and categorization
- Stack trace collection
- Context-aware error reporting
- Error metrics and trends

### API Logging
- Request/response logging
- Performance timing
- Error tracking
- Retry attempt logging

### Performance Monitoring
- Component render times
- API response times
- Memory usage tracking
- Performance threshold alerts

### Development Tools
- Visual debug panel
- Error report browser
- Debug data export
- Session tracking

## Configuration

The debug system is automatically enabled in development and disabled in production. You can configure it further:

```tsx
<DebugProvider
  enableKeyboardShortcuts={true}
  enableGlobalErrorBoundary={true}
>
  {/* Your app */}
</DebugProvider>
```

## Integration with Existing Error Reporting

The debug system integrates with the existing error reporting system at `/src/lib/error-reporting.ts` and enhances it with:

- Development-friendly logging
- Visual debugging interface
- Component-specific error tracking
- Enhanced context collection

## Production Safety

All debug utilities are automatically disabled in production builds:
- No debug logging
- No debug panel
- No global debug objects
- Minimal performance impact

The debug provider returns a no-op wrapper in production, ensuring zero impact on production performance.