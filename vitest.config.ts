/// <reference types="vitest" />
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react-swc';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test-setup.tsx'],
    css: true,
    reporters: ['verbose', 'json'],
    outputFile: {
      json: './test-results/vitest-report.json',
      html: './test-results/vitest-report.html',
    },

    // Exclude e2e tests from vitest (they should use playwright)
    include: ['src/**/*.{test,spec}.{js,ts,tsx}'],
    exclude: [
      'node_modules',
      'dist',
      'e2e/**/*',
      'src/**/*.e2e.{test,spec}.{js,ts,tsx}',
      'src/**/*.performance.{test,spec}.{js,ts,tsx}',
    ],

    // Enhanced coverage configuration
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov', 'clover'],
      reportsDirectory: './coverage',
      exclude: [
        'node_modules/',
        'src/test-setup.tsx',
        'src/test-utils.tsx',
        'src/**/*.stories.{js,ts,tsx}',
        'src/**/*.d.ts',
        'src/**/*.config.*',
        'src/**/*.test.{js,ts,tsx}',
        'src/**/*.spec.{js,ts,tsx}',
        'dist/',
        'e2e/',
        'coverage/',
        'test-results/',
        'public/',
        'src/vite-env.d.ts',
        // Exclude specific files that shouldn't be tested
        'src/main.tsx', // Entry point
        'src/App.tsx', // Just a wrapper
      ],
      include: [
        'src/**/*.{js,ts,tsx}',
      ],

      // Coverage thresholds
      thresholds: {
        global: {
          branches: 80,
          functions: 80,
          lines: 80,
          statements: 80,
        },
        // Per-file thresholds for critical components
        'src/lib/api-client.ts': {
          branches: 90,
          functions: 90,
          lines: 90,
          statements: 90,
        },
        'src/pages/onboarding/**': {
          branches: 85,
          functions: 85,
          lines: 85,
          statements: 85,
        },
        'src/components/ui/**': {
          branches: 75,
          functions: 75,
          lines: 75,
          statements: 75,
        },
      },

      // Watermarks for coverage colors in HTML report
      watermarks: {
        statements: [70, 85],
        functions: [70, 85],
        branches: [70, 85],
        lines: [70, 85],
      },
    },

    // Enhanced timeout configurations for different scenarios
    testTimeout: process.env.CI ? 20000 : 15000,  // Longer timeout in CI
    hookTimeout: process.env.CI ? 10000 : 8000,
    teardownTimeout: process.env.CI ? 5000 : 3000,

    // Pool options for better performance and stability
    pool: 'forks',
    poolOptions: {
      forks: {
        singleFork: false,
        isolate: true,
        execArgv: ['--experimental-vm-modules'],
      },
    },

    // Fail fast configuration
    bail: process.env.CI ? 5 : 1,

    // Retry configuration for flaky tests
    retry: process.env.CI ? 2 : 0,

    // Watch mode configuration
    watch: !process.env.CI,
    watchExclude: [
      '**/node_modules/**',
      '**/dist/**',
      '**/coverage/**',
      '**/test-results/**',
      '**/e2e/**',
    ],

    // Performance monitoring
    benchmark: {
      include: ['src/**/*.bench.{js,ts,tsx}'],
      exclude: ['node_modules/**', 'dist/**'],
      reporters: ['default', 'json'],
      outputFile: {
        json: './test-results/benchmark-report.json',
      },
    },

    // Reporter configuration
    outputTruncateLength: process.env.CI ? 0 : 80,

    // Environment variables for tests
    env: {
      NODE_ENV: 'test',
      VITE_API_URL: 'http://localhost:8000',
      // Add any other test-specific environment variables
    },

    // Mock configuration
    deps: {
      external: [
        // External dependencies that should not be mocked
        'react',
        'react-dom',
        '@testing-library/react',
        '@testing-library/jest-dom',
        '@testing-library/user-event',
      ],
    },

    // Snapshot configuration
    snapshotFormat: {
      escapeString: true,
      printBasicPrototype: true,
    },

    // Custom matchers and utilities
    globals: {
      // Make test utilities available globally if needed
      __TEST_TIMEOUT__: process.env.CI ? 20000 : 15000,
      __BENCHMARK_ITERATIONS__: process.env.CI ? 100 : 10,
    },

    // Test categorization with custom test names
    testNamePattern: process.env.TEST_NAME_PATTERN,

    // Threads configuration
    maxThreads: process.env.CI ? 2 : 4,
    minThreads: 1,

    // File watching and change detection
    forceRerunTriggers: [
      '**/package.json/**',
      '**/vitest.config.*/**',
      '**/vite.config.*/**',
    ],

    // Silent mode for CI
    silent: !!process.env.CI,

    // CSS handling in tests
    css: {
      modules: {
        classNameStrategy: 'stable',
      },
    },
  },

  // Extend esbuild options for test builds
  esbuild: {
    target: 'node14',
    sourcemap: true,
  },

  // Define test-specific build optimizations
  define: {
    __TEST__: true,
    __DEV__: false,
    __PROD__: false,
  },
});