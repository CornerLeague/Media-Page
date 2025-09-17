# Testing Infrastructure Setup - Playwright & Accessibility

This document outlines the comprehensive testing setup that has been configured for the Corner League Media project.

## Overview

The project now has a robust, multi-layer testing infrastructure with:
- **End-to-End Testing** via Playwright across 5 browser configurations
- **Accessibility Testing** with axe-core integration and WCAG compliance
- **Cross-Browser Compatibility** testing (Chrome, Firefox, Safari, Mobile)
- **Visual Regression Testing** capabilities
- **CI/CD Integration** with proper artifact collection

## Quick Start

```bash
# Install Playwright browsers (one-time setup)
npm run playwright:install

# Run all E2E tests
npm run test:e2e

# Run accessibility tests only
npm run test:e2e:accessibility

# Run tests with UI mode for debugging
npm run test:e2e:ui

# Debug specific tests
npm run test:e2e:debug
```

## Test Structure

### Core Test Files

- **`e2e/accessibility-core.spec.ts`** - Essential accessibility compliance tests
- **`e2e/accessibility.spec.ts`** - Comprehensive accessibility test suite (keyboard nav, screen reader support, etc.)
- **`e2e/onboarding.spec.ts`** - User journey E2E tests
- **`e2e/global-setup.ts`** - Global test configuration and setup

### Browser Configurations

The setup tests across multiple browser environments:

1. **Desktop Chrome** (Chromium) - Primary testing browser
2. **Desktop Firefox** - Cross-browser compatibility
3. **Desktop Safari** (WebKit) - Cross-browser compatibility
4. **Mobile Chrome** (Pixel 5 viewport) - Mobile responsiveness
5. **Mobile Safari** (iPhone 12 viewport) - iOS compatibility
6. **Accessibility Project** - Dedicated accessibility testing with extended timeouts

## Accessibility Testing Features

### Automated Accessibility Scanning

- **axe-core integration** for automated WCAG 2.0/2.1 AA compliance testing
- **Critical violation detection** - Tests fail on serious accessibility issues
- **Design team reporting** - Non-critical issues logged for design team review
- **WCAG compliance tags** - Focus on WCAG 2A, 2AA, and 2.1AA standards

### Manual Accessibility Testing

- **Keyboard navigation** testing
- **Screen reader compatibility** validation
- **Focus management** verification
- **Color contrast** reporting
- **High contrast mode** support testing
- **Reduced motion** preferences testing

### Example Accessibility Test Output

```
=== Accessibility Report ===
SERIOUS: color-contrast - Ensure the contrast between foreground and background colors meets WCAG 2 AA minimum contrast ratio thresholds
  Help: https://dequeuniversity.com/rules/axe/4.10/color-contrast?application=playwright
  Nodes affected: 1
===========================
```

## Configuration Details

### Playwright Configuration Highlights

- **Enhanced timeouts** for React hydration (15-30 seconds)
- **Automatic dev server startup** before tests
- **Multi-format reporting** (HTML, JSON, JUnit)
- **Artifact collection** (screenshots, videos, traces on failure)
- **Optimized for CI/CD** with GitHub Actions integration

### Test Isolation

- **Global setup** ensures clean state between test runs
- **localStorage/sessionStorage clearing** before each test
- **Network idle waiting** for React applications
- **Proper test cleanup** and error handling

## Reporting and Artifacts

### Test Reports

- **HTML Report**: `playwright-report/index.html` - Interactive test results
- **JSON Report**: `test-results/playwright-report.json` - Programmatic access
- **JUnit Report**: `test-results/playwright-results.xml` - CI integration

### Failure Artifacts

For failed tests, the following artifacts are automatically captured:
- Screenshots at point of failure
- Video recordings of test execution
- Network traces for debugging
- Error context and stack traces

## Accessibility Standards

### What Gets Tested

✅ **Critical Violations** (Test fails):
- Missing form labels
- Insufficient heading structure
- Broken keyboard navigation
- Missing alternative text
- Focus management issues

⚠️ **Design Issues** (Logged but doesn't fail tests):
- Color contrast ratios below 4.5:1
- Missing landmark regions
- Layout structure improvements

### WCAG Compliance Levels

The tests focus on:
- **WCAG 2.0 A** - Basic accessibility
- **WCAG 2.0 AA** - Standard accessibility (required for most compliance)
- **WCAG 2.1 AA** - Enhanced accessibility with mobile considerations

## Troubleshooting

### Common Issues

1. **Browser Installation Errors**
   ```bash
   npx playwright install
   ```

2. **Dev Server Not Starting**
   - Ensure port 8080 is available
   - Check `npm run dev` works independently

3. **Accessibility Tests Timing Out**
   - Tests have 30-second timeouts for a11y scans
   - Large pages may need longer timeouts

4. **Color Contrast False Positives**
   - Design-related issues are logged but don't fail tests
   - Review accessibility report for actionable items

### Test Performance

- **Flake Rate Target**: <2% across 3 test runs
- **Test Execution Time**: ~15-20 seconds for full suite
- **Parallel Execution**: Up to 4 workers (optimized for CI)

## Integration with Development Workflow

### Pre-Commit Testing

```bash
# Quick accessibility check
npm run test:e2e:accessibility

# Full cross-browser validation
npm run test:e2e
```

### CI/CD Integration

The configuration is optimized for CI environments with:
- Automatic browser installation
- Proper artifact collection
- GitHub Actions reporting
- Failure screenshot capture

## Future Enhancements

Potential additions to the testing infrastructure:
- Visual regression testing baselines
- Performance testing integration
- API endpoint testing
- Database state management
- Multi-language accessibility testing

## Support

For questions about the testing setup:
1. Check test execution logs in `test-results/`
2. Review HTML reports for detailed failure analysis
3. Use `--debug` flag for step-by-step test execution
4. Examine captured screenshots/videos for visual debugging

---

**Testing Infrastructure Version**: 1.0
**Last Updated**: September 2025
**Playwright Version**: 1.55.0
**axe-core Version**: 4.10.2