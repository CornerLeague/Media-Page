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
        manualChunks: {
          // Vendor chunk for React and core libraries
          vendor: ['react', 'react-dom', 'react-router-dom'],
          // UI chunk for shadcn/ui and related components
          ui: ['@radix-ui/react-progress', '@radix-ui/react-slot', '@radix-ui/react-toast', 'lucide-react'],
          // Query chunk for data fetching
          query: ['@tanstack/react-query'],
          // Form chunk for form handling
          form: ['react-hook-form', '@hookform/resolvers', 'zod'],
          // Utility chunk for utility libraries
          utils: ['clsx', 'class-variance-authority', 'tailwind-merge', 'date-fns']
        }
      }
    },
    // Optimize chunk size limit
    chunkSizeWarningLimit: 1000,
    // Enable source maps for debugging
    sourcemap: mode === 'development',
    // Minify for production
    minify: mode === 'production' ? 'esbuild' : false
  }
}));
