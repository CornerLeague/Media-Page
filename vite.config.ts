import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import { componentTagger } from "lovable-tagger";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  server: {
    host: "::",
    port: 8080,
  },
  plugins: [react(), mode === "development" && componentTagger()].filter(Boolean),
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: (id) => {
          // Vendor chunk for React and core libraries
          if (id.includes('react') || id.includes('react-dom') || id.includes('react-router-dom')) {
            return 'vendor';
          }

          // Firebase chunk for authentication
          if (id.includes('firebase')) {
            return 'firebase';
          }

          // UI chunk for shadcn/ui and Radix components
          if (id.includes('@radix-ui') || id.includes('lucide-react')) {
            return 'ui';
          }

          // Query chunk for data fetching
          if (id.includes('@tanstack/react-query')) {
            return 'query';
          }

          // Form chunk for form handling
          if (id.includes('react-hook-form') || id.includes('@hookform') || id.includes('zod')) {
            return 'form';
          }

          // Animation chunk for motion libraries
          if (id.includes('framer-motion')) {
            return 'animation';
          }

          // Charts chunk for visualization
          if (id.includes('recharts')) {
            return 'charts';
          }

          // Onboarding chunk for onboarding-specific code
          if (id.includes('/pages/onboarding/') || id.includes('/hooks/useAuth') ||
              id.includes('/hooks/useOnboarding') || id.includes('/hooks/usePreferences') ||
              id.includes('/hooks/useOnboardingPrefetch')) {
            return 'onboarding';
          }

          // Performance chunk for virtualization and optimization components
          if (id.includes('react-window') || id.includes('VirtualizedTeamList') ||
              id.includes('OptimizedImage')) {
            return 'performance';
          }

          // Profile chunk for profile/preferences pages
          if (id.includes('/pages/profile/') || id.includes('/components/preferences/')) {
            return 'profile';
          }

          // Utility chunk for utility libraries
          if (id.includes('clsx') || id.includes('class-variance-authority') ||
              id.includes('tailwind-merge') || id.includes('date-fns')) {
            return 'utils';
          }

          // Node modules vendor chunks
          if (id.includes('node_modules')) {
            return 'vendor';
          }
        }
      }
    },
    // Optimize chunk size limit
    chunkSizeWarningLimit: 500,
    // Enable source maps for debugging
    sourcemap: mode === 'development',
    // Minify for production
    minify: mode === 'production' ? 'esbuild' : false,
    // Enable tree shaking
    treeshake: {
      moduleSideEffects: false,
      propertyReadSideEffects: false,
      tryCatchDeoptimization: false,
    },
    // Additional optimizations
    target: 'es2020',
    assetsDir: 'assets',
    cssCodeSplit: true,
  }
}));
