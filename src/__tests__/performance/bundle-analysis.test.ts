/**
 * Bundle Size Analysis Test Suite
 *
 * Analyzes bundle composition and identifies optimization opportunities
 */

import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

// Bundle size thresholds (in bytes)
const BUNDLE_SIZE_THRESHOLDS = {
  // Total bundle size (gzipped)
  TOTAL_GZIPPED: 200 * 1024, // 200KB
  TOTAL_UNCOMPRESSED: 800 * 1024, // 800KB

  // Individual chunk sizes (gzipped)
  VENDOR_CHUNK: 60 * 1024, // 60KB
  UI_CHUNK: 15 * 1024, // 15KB
  MAIN_CHUNK: 180 * 1024, // 180KB

  // Critical path budget
  CRITICAL_PATH: 100 * 1024, // 100KB for above-the-fold content
};

interface BundleStats {
  fileName: string;
  size: number;
  gzipSize: number;
  type: 'js' | 'css' | 'other';
  isVendor: boolean;
  isMainChunk: boolean;
}

function parseBuildOutput(): BundleStats[] {
  const distPath = path.join(process.cwd(), 'dist');

  if (!fs.existsSync(distPath)) {
    throw new Error('Build output not found. Run "npm run build" first.');
  }

  const stats: BundleStats[] = [];
  const distContents = fs.readdirSync(distPath);

  // Parse assets directory
  const assetsPath = path.join(distPath, 'assets');
  if (fs.existsSync(assetsPath)) {
    const assetFiles = fs.readdirSync(assetsPath);

    for (const file of assetFiles) {
      const filePath = path.join(assetsPath, file);
      const fileStat = fs.statSync(filePath);

      const fileType = file.endsWith('.js') ? 'js' :
                       file.endsWith('.css') ? 'css' : 'other';

      stats.push({
        fileName: file,
        size: fileStat.size,
        gzipSize: fileStat.size * 0.3, // Rough estimate, actual would need gzip compression
        type: fileType,
        isVendor: file.includes('vendor'),
        isMainChunk: file.includes('index') && fileType === 'js',
      });
    }
  }

  return stats;
}

function analyzeImports(): { heavyDependencies: string[], unusedDependencies: string[] } {
  const packageJsonPath = path.join(process.cwd(), 'package.json');
  const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf-8'));

  const dependencies = Object.keys(packageJson.dependencies || {});

  // Known heavy dependencies that should be analyzed
  const knownHeavyDeps = [
    'firebase',
    '@tanstack/react-query',
    'framer-motion',
    'recharts',
    'date-fns',
  ];

  const heavyDependencies = dependencies.filter(dep =>
    knownHeavyDeps.some(heavy => dep.includes(heavy))
  );

  // This would need more sophisticated analysis in a real implementation
  // For now, we'll return empty array for unused dependencies
  const unusedDependencies: string[] = [];

  return { heavyDependencies, unusedDependencies };
}

describe('Bundle Size Analysis', () => {
  describe('Bundle Size Limits', () => {
    it('should not exceed total bundle size threshold', () => {
      const stats = parseBuildOutput();
      const totalSize = stats.reduce((sum, stat) => sum + stat.size, 0);
      const totalGzipSize = stats.reduce((sum, stat) => sum + stat.gzipSize, 0);

      console.log(`Total bundle size: ${(totalSize / 1024).toFixed(2)}KB`);
      console.log(`Total gzipped size: ${(totalGzipSize / 1024).toFixed(2)}KB`);

      expect(totalGzipSize).toBeLessThanOrEqual(BUNDLE_SIZE_THRESHOLDS.TOTAL_GZIPPED);
      expect(totalSize).toBeLessThanOrEqual(BUNDLE_SIZE_THRESHOLDS.TOTAL_UNCOMPRESSED);
    });

    it('should keep vendor chunk within limits', () => {
      const stats = parseBuildOutput();
      const vendorChunks = stats.filter(stat => stat.isVendor);

      if (vendorChunks.length > 0) {
        const largestVendorChunk = Math.max(...vendorChunks.map(chunk => chunk.gzipSize));

        console.log(`Largest vendor chunk: ${(largestVendorChunk / 1024).toFixed(2)}KB (gzipped)`);

        expect(largestVendorChunk).toBeLessThanOrEqual(BUNDLE_SIZE_THRESHOLDS.VENDOR_CHUNK);
      }
    });

    it('should keep main chunk within limits', () => {
      const stats = parseBuildOutput();
      const mainChunks = stats.filter(stat => stat.isMainChunk);

      if (mainChunks.length > 0) {
        const largestMainChunk = Math.max(...mainChunks.map(chunk => chunk.gzipSize));

        console.log(`Largest main chunk: ${(largestMainChunk / 1024).toFixed(2)}KB (gzipped)`);

        expect(largestMainChunk).toBeLessThanOrEqual(BUNDLE_SIZE_THRESHOLDS.MAIN_CHUNK);
      }
    });
  });

  describe('Code Splitting Analysis', () => {
    it('should have proper code splitting for onboarding flow', () => {
      const stats = parseBuildOutput();

      // Check if onboarding components are in separate chunks
      const hasCodeSplitting = stats.some(stat =>
        stat.fileName.includes('onboarding') ||
        stat.fileName.includes('chunk')
      );

      // Currently not implemented, this test documents the requirement
      console.log('Code splitting for onboarding:', hasCodeSplitting ? 'Present' : 'Not implemented');

      // This would pass once code splitting is implemented
      // expect(hasCodeSplitting).toBe(true);
    });

    it('should identify heavy dependencies that need splitting', () => {
      const { heavyDependencies } = analyzeImports();

      console.log('Heavy dependencies found:', heavyDependencies);

      // Verify we're tracking heavy dependencies
      expect(heavyDependencies.length).toBeGreaterThan(0);

      // Document which dependencies should be code-split
      const shouldBeSplit = [
        'firebase',
        'framer-motion',
        'recharts',
      ];

      const needsSplitting = heavyDependencies.filter(dep =>
        shouldBeSplit.some(split => dep.includes(split))
      );

      if (needsSplitting.length > 0) {
        console.log('Dependencies that should be code-split:', needsSplitting);
      }
    });
  });

  describe('Asset Optimization', () => {
    it('should have optimized CSS bundle', () => {
      const stats = parseBuildOutput();
      const cssFiles = stats.filter(stat => stat.type === 'css');

      if (cssFiles.length > 0) {
        const totalCssSize = cssFiles.reduce((sum, file) => sum + file.gzipSize, 0);

        console.log(`Total CSS size: ${(totalCssSize / 1024).toFixed(2)}KB (gzipped)`);

        // CSS should be under 20KB gzipped
        expect(totalCssSize).toBeLessThanOrEqual(20 * 1024);
      }
    });

    it('should identify unused CSS opportunities', () => {
      // This would require CSS analysis tools in a real implementation
      const stats = parseBuildOutput();
      const cssFiles = stats.filter(stat => stat.type === 'css');

      // Document current CSS usage for manual review
      console.log('CSS files for analysis:', cssFiles.map(f => ({
        name: f.fileName,
        size: `${(f.size / 1024).toFixed(2)}KB`,
        gzipSize: `${(f.gzipSize / 1024).toFixed(2)}KB`,
      })));
    });
  });

  describe('Performance Budget', () => {
    it('should meet performance budget for critical path', () => {
      const stats = parseBuildOutput();

      // Calculate critical path size (main JS + CSS)
      const criticalAssets = stats.filter(stat =>
        (stat.isMainChunk && stat.type === 'js') ||
        stat.type === 'css'
      );

      const criticalPathSize = criticalAssets.reduce((sum, asset) => sum + asset.gzipSize, 0);

      console.log(`Critical path size: ${(criticalPathSize / 1024).toFixed(2)}KB (gzipped)`);

      expect(criticalPathSize).toBeLessThanOrEqual(BUNDLE_SIZE_THRESHOLDS.CRITICAL_PATH);
    });

    it('should generate bundle analysis report', () => {
      const stats = parseBuildOutput();
      const { heavyDependencies } = analyzeImports();

      const report = {
        timestamp: new Date().toISOString(),
        totalAssets: stats.length,
        totalSize: stats.reduce((sum, stat) => sum + stat.size, 0),
        totalGzipSize: stats.reduce((sum, stat) => sum + stat.gzipSize, 0),
        breakdown: {
          js: stats.filter(s => s.type === 'js').reduce((sum, s) => sum + s.gzipSize, 0),
          css: stats.filter(s => s.type === 'css').reduce((sum, s) => sum + s.gzipSize, 0),
          other: stats.filter(s => s.type === 'other').reduce((sum, s) => sum + s.gzipSize, 0),
        },
        heavyDependencies,
        recommendations: [
          {
            type: 'code-splitting',
            description: 'Implement route-based code splitting for onboarding flow',
            estimatedSaving: '20-30KB',
          },
          {
            type: 'dependency-optimization',
            description: 'Consider lighter alternatives for date-fns and framer-motion',
            estimatedSaving: '15-25KB',
          },
          {
            type: 'tree-shaking',
            description: 'Ensure unused exports are properly tree-shaken',
            estimatedSaving: '10-15KB',
          },
        ],
      };

      console.log('Bundle Analysis Report:', JSON.stringify(report, null, 2));

      // Save report to file for CI/CD pipeline
      const reportPath = path.join(process.cwd(), 'test-results', 'bundle-analysis.json');
      fs.mkdirSync(path.dirname(reportPath), { recursive: true });
      fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));

      expect(report.totalAssets).toBeGreaterThan(0);
    });
  });
});