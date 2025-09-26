/**
 * Sport ID Mapping Service
 *
 * Provides utilities for converting between sport slugs (frontend) and UUIDs (backend).
 * This resolves the Sport ID Format Mismatch issue where the frontend uses slugs
 * like 'football', 'basketball' while the backend expects UUIDs.
 */

// TypeScript type definitions
export interface SportMapping {
  slug: string;
  uuid: string;
  name: string;
  hasTeams: boolean;
  teamCount: number;
}

// UUID to Slug mapping (source: SPORTS_UUID_SLUG_MAPPING.md)
export const SPORT_UUID_MAPPING: Record<string, string> = {
  'baseball': '23df2010-047e-417a-a036-ee6c2e7b5717',
  'basketball': '498127a1-e061-4386-89ce-a5f00692004c',
  'college-basketball': 'e70de2db-56de-4890-ad67-e2fcc3eab913',
  'college-football': '62524246-a88d-4839-9c11-884c1af721c6',
  'football': '2350948d-f6d4-4a85-9358-b76ed505aea2',
  'hockey': '21e46a6d-7373-4c53-bc42-0a7f33a7ef49',
  'soccer': '61a964ee-563b-4ccd-b277-b429ec1c57ab',
};

// Reverse mapping (UUID to Slug)
export const SPORT_SLUG_MAPPING: Record<string, string> = {
  '23df2010-047e-417a-a036-ee6c2e7b5717': 'baseball',
  '498127a1-e061-4386-89ce-a5f00692004c': 'basketball',
  'e70de2db-56de-4890-ad67-e2fcc3eab913': 'college-basketball',
  '62524246-a88d-4839-9c11-884c1af721c6': 'college-football',
  '2350948d-f6d4-4a85-9358-b76ed505aea2': 'football',
  '21e46a6d-7373-4c53-bc42-0a7f33a7ef49': 'hockey',
  '61a964ee-563b-4ccd-b277-b429ec1c57ab': 'soccer',
};

// Complete sport mappings with metadata
export const SPORT_MAPPINGS: SportMapping[] = [
  { slug: 'baseball', uuid: '23df2010-047e-417a-a036-ee6c2e7b5717', name: 'Baseball', hasTeams: true, teamCount: 30 },
  { slug: 'basketball', uuid: '498127a1-e061-4386-89ce-a5f00692004c', name: 'Basketball', hasTeams: true, teamCount: 30 },
  { slug: 'college-basketball', uuid: 'e70de2db-56de-4890-ad67-e2fcc3eab913', name: 'College Basketball', hasTeams: false, teamCount: 0 },
  { slug: 'college-football', uuid: '62524246-a88d-4839-9c11-884c1af721c6', name: 'College Football', hasTeams: true, teamCount: 16 },
  { slug: 'football', uuid: '2350948d-f6d4-4a85-9358-b76ed505aea2', name: 'Football', hasTeams: true, teamCount: 32 },
  { slug: 'hockey', uuid: '21e46a6d-7373-4c53-bc42-0a7f33a7ef49', name: 'Hockey', hasTeams: true, teamCount: 32 },
  { slug: 'soccer', uuid: '61a964ee-563b-4ccd-b277-b429ec1c57ab', name: 'Soccer', hasTeams: true, teamCount: 125 },
];

/**
 * Cache for sport mappings to avoid repeated lookups
 */
const mappingCache = new Map<string, string>();

// Helper function to add items to cache
function addToCache(key: string, value: string): void {
  mappingCache.set(key, value);
}

// Helper function to get from cache
function getFromCache(key: string): string | undefined {
  return mappingCache.get(key);
}

/**
 * Convert a single sport slug to UUID
 */
export function sportSlugToUuid(slug: string): string | null {
  // Check cache first
  const cacheKey = `slug-to-uuid:${slug}`;
  const cached = getFromCache(cacheKey);
  if (cached) {
    return cached;
  }

  // Get from mapping
  const uuid = SPORT_UUID_MAPPING[slug] || null;

  // Cache result if found
  if (uuid) {
    addToCache(cacheKey, uuid);
  }

  return uuid;
}

/**
 * Convert a single UUID to sport slug
 */
export function sportUuidToSlug(uuid: string): string | null {
  // Check cache first
  const cacheKey = `uuid-to-slug:${uuid}`;
  const cached = getFromCache(cacheKey);
  if (cached) {
    return cached;
  }

  // Get from mapping
  const slug = SPORT_SLUG_MAPPING[uuid] || null;

  // Cache result if found
  if (slug) {
    addToCache(cacheKey, slug);
  }

  return slug;
}

/**
 * Convert multiple sport slugs to UUIDs
 * Filters out invalid slugs and returns only valid UUIDs
 */
export function sportSlugsToUuids(slugs: string[]): string[] {
  return slugs
    .map(slug => sportSlugToUuid(slug))
    .filter((uuid): uuid is string => uuid !== null);
}

/**
 * Convert multiple UUIDs to sport slugs
 * Filters out invalid UUIDs and returns only valid slugs
 */
export function sportUuidsToSlugs(uuids: string[]): string[] {
  return uuids
    .map(uuid => sportUuidToSlug(uuid))
    .filter((slug): slug is string => slug !== null);
}

/**
 * Validate that a sport slug exists in the mapping
 */
export function isValidSportSlug(slug: string): boolean {
  return slug in SPORT_UUID_MAPPING;
}

/**
 * Validate that a sport UUID exists in the mapping
 */
export function isValidSportUuid(uuid: string): boolean {
  return uuid in SPORT_SLUG_MAPPING;
}

/**
 * Get sport UUIDs from slugs with async interface for future API integration
 * Currently synchronous but provides async interface for caching and API calls
 */
export async function getSportUUIDs(slugs: string[]): Promise<string[]> {
  // For now this is synchronous, but we can add API calls or async caching here later
  return Promise.resolve(sportSlugsToUuids(slugs));
}

/**
 * Get sport slugs from UUIDs with async interface for future API integration
 */
export async function getSportSlugs(uuids: string[]): Promise<string[]> {
  return Promise.resolve(sportUuidsToSlugs(uuids));
}

/**
 * Get complete sport mapping by slug
 */
export function getSportMappingBySlug(slug: string): SportMapping | null {
  return SPORT_MAPPINGS.find(mapping => mapping.slug === slug) || null;
}

/**
 * Get complete sport mapping by UUID
 */
export function getSportMappingByUuid(uuid: string): SportMapping | null {
  return SPORT_MAPPINGS.find(mapping => mapping.uuid === uuid) || null;
}

/**
 * Get all available sport slugs
 */
export function getAllSportSlugs(): string[] {
  return Object.keys(SPORT_UUID_MAPPING);
}

/**
 * Get all available sport UUIDs
 */
export function getAllSportUuids(): string[] {
  return Object.values(SPORT_UUID_MAPPING);
}

/**
 * Get sports that have teams (excluding college basketball which has 0 teams)
 */
export function getSportsWithTeams(): SportMapping[] {
  return SPORT_MAPPINGS.filter(sport => sport.hasTeams && sport.teamCount > 0);
}

/**
 * Get sports without teams or with 0 teams
 */
export function getSportsWithoutTeams(): SportMapping[] {
  return SPORT_MAPPINGS.filter(sport => !sport.hasTeams || sport.teamCount === 0);
}

/**
 * Clear the mapping cache (useful for testing)
 */
export function clearMappingCache(): void {
  mappingCache.clear();
}

/**
 * Error handling for missing sports
 */
export class SportMappingError extends Error {
  constructor(
    message: string,
    public readonly invalidSlugs?: string[],
    public readonly invalidUuids?: string[]
  ) {
    super(message);
    this.name = 'SportMappingError';
  }
}

/**
 * Convert sport slugs to UUIDs with error handling
 * Throws error if any slugs are invalid
 */
export function sportSlugsToUuidsStrict(slugs: string[]): string[] {
  const invalidSlugs: string[] = [];
  const uuids: string[] = [];

  for (const slug of slugs) {
    const uuid = sportSlugToUuid(slug);
    if (uuid) {
      uuids.push(uuid);
    } else {
      invalidSlugs.push(slug);
    }
  }

  if (invalidSlugs.length > 0) {
    throw new SportMappingError(
      `Invalid sport slugs: ${invalidSlugs.join(', ')}`,
      invalidSlugs
    );
  }

  return uuids;
}

/**
 * Convert sport UUIDs to slugs with error handling
 * Throws error if any UUIDs are invalid
 */
export function sportUuidsToSlugsStrict(uuids: string[]): string[] {
  const invalidUuids: string[] = [];
  const slugs: string[] = [];

  for (const uuid of uuids) {
    const slug = sportUuidToSlug(uuid);
    if (slug) {
      slugs.push(slug);
    } else {
      invalidUuids.push(uuid);
    }
  }

  if (invalidUuids.length > 0) {
    throw new SportMappingError(
      `Invalid sport UUIDs: ${invalidUuids.join(', ')}`,
      undefined,
      invalidUuids
    );
  }

  return slugs;
}