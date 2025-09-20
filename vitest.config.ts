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
    reporters: ['verbose'],
    // Exclude e2e tests from vitest (they should use playwright)
    include: ['src/**/*.{test,spec}.{js,ts,tsx}'],
    exclude: ['node_modules', 'dist', 'e2e/**/*'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/test-setup.tsx',
        '**/*.d.ts',
        '**/*.config.*',
        'dist/',
        'e2e/',
      ],
      thresholds: {
        global: {
          branches: 70,
          functions: 70,
          lines: 70,
          statements: 70,
        },
      },
    },
    // Prevent hanging tests
    testTimeout: 5000,
    hookTimeout: 5000,
    // Pool options for better stability
    pool: 'forks',
    isolate: true,
    // Fail fast on hanging tests
    bail: 3,
  },
});