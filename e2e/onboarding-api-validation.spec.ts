import { test, expect } from '@playwright/test';

/**
 * API Validation Test for Onboarding Error
 *
 * This test validates the root cause of the "Failed to save preferences" error
 * by testing the actual API endpoints that the onboarding flow attempts to use.
 */

test.describe('Onboarding API Validation', () => {
  test('Validate API endpoints for onboarding completion', async ({ page }) => {
    console.log('🔍 Testing API endpoints used in onboarding completion...');

    // Test 1: Check if the POST /api/v1/users endpoint exists (this is the failing one)
    const createUserTest = await page.evaluate(async () => {
      try {
        const testData = {
          clerkUserId: 'test-user-123',
          sports: [{ sportId: 'nfl', name: 'NFL', rank: 1, hasTeams: true }],
          teams: [{ teamId: 'team-1', name: 'Test Team', sportId: 'nfl', league: 'NFL', affinityScore: 85 }],
          preferences: {
            newsTypes: [{ type: 'general', enabled: true, priority: 1 }],
            notifications: {
              push: false,
              email: false,
              gameReminders: false,
              newsAlerts: false,
              scoreUpdates: false,
            },
            contentFrequency: 'standard'
          }
        };

        const response = await fetch('http://localhost:8000/api/v1/users', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(testData)
        });

        const responseText = await response.text();
        let data;
        try {
          data = JSON.parse(responseText);
        } catch {
          data = responseText;
        }

        return {
          endpoint: 'POST /api/v1/users',
          status: response.status,
          statusText: response.statusText,
          ok: response.ok,
          data
        };
      } catch (error) {
        return {
          endpoint: 'POST /api/v1/users',
          error: error.message
        };
      }
    });

    console.log('❌ CREATE USER TEST:', createUserTest);

    // Test 2: Check if PUT /api/v1/users/me exists (this might be the correct endpoint)
    const updateUserTest = await page.evaluate(async () => {
      try {
        const testData = {
          displayName: 'Test User',
          sports: [{ sportId: 'nfl', name: 'NFL', rank: 1, hasTeams: true }],
          teams: [{ teamId: 'team-1', name: 'Test Team', sportId: 'nfl', league: 'NFL', affinityScore: 85 }],
          preferences: {
            newsTypes: [{ type: 'general', enabled: true, priority: 1 }],
            notifications: {
              push: false,
              email: false,
              gameReminders: false,
              newsAlerts: false,
              scoreUpdates: false,
            },
            contentFrequency: 'standard'
          }
        };

        const response = await fetch('http://localhost:8000/api/v1/users/me', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            // Note: This will fail without auth, but we can see if the endpoint exists
          },
          body: JSON.stringify(testData)
        });

        const responseText = await response.text();
        let data;
        try {
          data = JSON.parse(responseText);
        } catch {
          data = responseText;
        }

        return {
          endpoint: 'PUT /api/v1/users/me',
          status: response.status,
          statusText: response.statusText,
          ok: response.ok,
          data
        };
      } catch (error) {
        return {
          endpoint: 'PUT /api/v1/users/me',
          error: error.message
        };
      }
    });

    console.log('✅ UPDATE USER TEST:', updateUserTest);

    // Test 3: Check available endpoints
    const availableEndpoints = await page.evaluate(async () => {
      try {
        const response = await fetch('http://localhost:8000/openapi.json');
        const openapi = await response.json();
        return {
          userEndpoints: Object.keys(openapi.paths).filter(path => path.includes('/users')),
          allEndpoints: Object.keys(openapi.paths)
        };
      } catch (error) {
        return { error: error.message };
      }
    });

    console.log('📋 AVAILABLE ENDPOINTS:', availableEndpoints);

    // Test 4: Check authentication endpoints
    const authTest = await page.evaluate(async () => {
      try {
        const response = await fetch('http://localhost:8000/api/v1/auth/me', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          }
        });

        const responseText = await response.text();
        let data;
        try {
          data = JSON.parse(responseText);
        } catch {
          data = responseText;
        }

        return {
          endpoint: 'GET /api/v1/auth/me',
          status: response.status,
          statusText: response.statusText,
          ok: response.ok,
          data
        };
      } catch (error) {
        return {
          endpoint: 'GET /api/v1/auth/me',
          error: error.message
        };
      }
    });

    console.log('🔐 AUTH TEST:', authTest);

    // Generate diagnosis
    console.log('\n🩺 DIAGNOSIS:');
    console.log('=============');

    if (createUserTest.status === 404) {
      console.log('❌ PROBLEM FOUND: POST /api/v1/users endpoint does not exist');
      console.log('   This is the endpoint the onboarding flow is trying to use');
      console.log('   The useOnboarding hook calls apiClient.createUser() which posts to this non-existent endpoint');
    }

    if (updateUserTest.status === 401 || updateUserTest.status === 403) {
      console.log('✅ POTENTIAL SOLUTION: PUT /api/v1/users/me endpoint exists but requires authentication');
      console.log('   This might be the correct endpoint to use instead');
    }

    if (authTest.status === 401 || authTest.status === 403) {
      console.log('⚠️  AUTHENTICATION: Auth endpoints exist but authentication is not working');
      console.log('   This could be due to Clerk configuration issues');
    }

    console.log('\n💡 RECOMMENDED FIXES:');
    console.log('1. Update api-client.ts to use PUT /api/v1/users/me instead of POST /api/v1/users');
    console.log('2. Ensure proper Clerk authentication is working');
    console.log('3. Update the onboarding flow to handle authentication properly');
    console.log('4. Add proper error handling for API failures');
  });

  test('Test Clerk authentication integration', async ({ page }) => {
    console.log('🔐 Testing Clerk authentication...');

    await page.goto('http://localhost:8080');
    await page.waitForTimeout(3000);

    // Check Clerk status
    const clerkStatus = await page.evaluate(() => {
      return {
        clerkExists: typeof window.Clerk !== 'undefined',
        isLoaded: window.Clerk?.loaded || false,
        isSignedIn: window.Clerk?.user !== null,
        user: window.Clerk?.user ? {
          id: window.Clerk.user.id,
          primaryEmailAddress: window.Clerk.user.primaryEmailAddress?.emailAddress
        } : null,
        publishableKey: document.querySelector('script[src*="clerk"]')?.src || 'Not found'
      };
    });

    console.log('Clerk Status:', clerkStatus);

    if (!clerkStatus.clerkExists) {
      console.log('❌ Clerk is not loaded properly');
    } else if (!clerkStatus.isSignedIn) {
      console.log('⚠️  User is not signed in - this will cause API calls to fail');
    } else {
      console.log('✅ User is signed in:', clerkStatus.user);
    }
  });
});