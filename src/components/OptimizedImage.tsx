/**
 * OptimizedImage Component
 *
 * High-performance image loading with lazy loading, WebP support,
 * and progressive enhancement for better Core Web Vitals.
 */

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { cn } from '@/lib/utils';

interface OptimizedImageProps {
  src: string;
  alt: string;
  width?: number;
  height?: number;
  className?: string;
  placeholder?: string;
  priority?: boolean;
  onLoad?: () => void;
  onError?: () => void;
  sizes?: string;
  quality?: number;
}

interface ImageState {
  isLoaded: boolean;
  isLoading: boolean;
  hasError: boolean;
  currentSrc: string | null;
}

// WebP support detection
const supportsWebP = (() => {
  if (typeof window === 'undefined') return false;

  try {
    const canvas = document.createElement('canvas');
    canvas.width = 1;
    canvas.height = 1;
    const dataURL = canvas.toDataURL('image/webp');
    return dataURL && dataURL.indexOf('data:image/webp') === 0;
  } catch (error) {
    // Fallback for test environments or unsupported browsers
    return false;
  }
})();

// Generate optimized image URLs
function getOptimizedImageUrl(
  src: string,
  width?: number,
  height?: number,
  quality: number = 80,
  format?: 'webp' | 'jpeg' | 'png'
): string {
  // If it's already an optimized URL or external URL, return as-is
  if (src.startsWith('http') || src.includes('?')) {
    return src;
  }

  // For local images, we would typically use a service like Cloudinary or ImageKit
  // For now, we'll return the original URL with query parameters
  const params = new URLSearchParams();

  if (width) params.set('w', width.toString());
  if (height) params.set('h', height.toString());
  if (quality !== 80) params.set('q', quality.toString());
  if (format) params.set('f', format);

  const queryString = params.toString();
  return queryString ? `${src}?${queryString}` : src;
}

export function OptimizedImage({
  src,
  alt,
  width,
  height,
  className,
  placeholder = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjI0IiBoZWlnaHQ9IjI0IiBmaWxsPSIjZjNmNGY2Ii8+CjxwYXRoIGQ9Ik0xMiAxNmMtMi4yMSAwLTQtMS43OS00LTRzMS43OS00IDQtNCA0IDEuNzkgNCA0LTEuNzkgNC00IDR6bTAtNmMtMS4xIDAtMiAuOS0yIDJzLjkgMiAyIDIgMi0uOSAyLTItLjktMi0yLTJ6IiBmaWxsPSIjOWNhM2FmIi8+Cjwvc3ZnPgo=',
  priority = false,
  onLoad,
  onError,
  sizes,
  quality = 80,
}: OptimizedImageProps) {
  const [imageState, setImageState] = useState<ImageState>({
    isLoaded: false,
    isLoading: false,
    hasError: false,
    currentSrc: null,
  });

  const imgRef = useRef<HTMLImageElement>(null);
  const observerRef = useRef<IntersectionObserver | null>(null);

  // Generate source URLs with WebP fallback
  const optimizedSrc = getOptimizedImageUrl(
    src,
    width,
    height,
    quality,
    supportsWebP ? 'webp' : undefined
  );

  const fallbackSrc = getOptimizedImageUrl(src, width, height, quality);

  // Lazy loading with Intersection Observer
  const setupLazyLoading = useCallback(() => {
    if (!imgRef.current || priority) return;

    observerRef.current = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && !imageState.isLoading && !imageState.isLoaded) {
            loadImage();
          }
        });
      },
      {
        rootMargin: '50px',
        threshold: 0.1,
      }
    );

    observerRef.current.observe(imgRef.current);
  }, [priority, imageState.isLoading, imageState.isLoaded]);

  // Image loading function with error handling
  const loadImage = useCallback(() => {
    if (imageState.isLoading || imageState.isLoaded) return;

    setImageState(prev => ({ ...prev, isLoading: true }));

    const img = new Image();

    img.onload = () => {
      setImageState({
        isLoaded: true,
        isLoading: false,
        hasError: false,
        currentSrc: img.src,
      });
      onLoad?.();
    };

    img.onerror = () => {
      // Try fallback if WebP fails
      if (img.src === optimizedSrc && optimizedSrc !== fallbackSrc) {
        img.src = fallbackSrc;
        return;
      }

      setImageState({
        isLoaded: false,
        isLoading: false,
        hasError: true,
        currentSrc: null,
      });
      onError?.();
    };

    // Set sizes for responsive images
    if (sizes) {
      img.sizes = sizes;
    }

    img.src = optimizedSrc;
  }, [optimizedSrc, fallbackSrc, imageState.isLoading, imageState.isLoaded, onLoad, onError, sizes]);

  // Set up lazy loading or immediate loading
  useEffect(() => {
    if (priority) {
      loadImage();
    } else {
      setupLazyLoading();
    }

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, [priority, loadImage, setupLazyLoading]);

  // Performance monitoring
  useEffect(() => {
    if (imageState.isLoaded && imageState.currentSrc) {
      // Log loading performance for monitoring
      const loadTime = performance.now();
      console.log(`Image loaded: ${src} in ${loadTime.toFixed(2)}ms`);
    }
  }, [imageState.isLoaded, imageState.currentSrc, src]);

  return (
    <div
      className={cn('relative overflow-hidden', className)}
      style={{ width, height }}
    >
      {/* Placeholder/skeleton */}
      {!imageState.isLoaded && !imageState.hasError && (
        <img
          src={placeholder}
          alt=""
          className="absolute inset-0 w-full h-full object-cover blur-sm transition-opacity duration-300"
          aria-hidden="true"
        />
      )}

      {/* Loading state */}
      {imageState.isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-muted">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
        </div>
      )}

      {/* Error state */}
      {imageState.hasError && (
        <div className="absolute inset-0 flex items-center justify-center bg-muted text-muted-foreground">
          <svg
            className="w-8 h-8"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
            />
          </svg>
        </div>
      )}

      {/* Main image */}
      <img
        ref={imgRef}
        src={imageState.currentSrc || undefined}
        alt={alt}
        width={width}
        height={height}
        className={cn(
          'w-full h-full object-cover transition-opacity duration-300',
          imageState.isLoaded ? 'opacity-100' : 'opacity-0'
        )}
        loading={priority ? 'eager' : 'lazy'}
        decoding="async"
        sizes={sizes}
      />
    </div>
  );
}

// High-performance avatar component for team logos
export function TeamLogo({
  team,
  size = 40,
  className,
}: {
  team: { logo?: string; name: string };
  size?: number;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "rounded-full bg-muted flex items-center justify-center overflow-hidden",
        className
      )}
      style={{ width: size, height: size }}
    >
      {team.logo ? (
        <OptimizedImage
          src={team.logo}
          alt={`${team.name} logo`}
          width={size}
          height={size}
          className="w-full h-full"
          quality={90}
        />
      ) : (
        <span className="text-lg select-none" style={{ fontSize: size * 0.5 }}>
          🏆
        </span>
      )}
    </div>
  );
}

export default OptimizedImage;