/**
 * Tests for Sport ID Mapping utilities
 */

import {
  SPORT_UUID_MAPPING,
  SPORT_SLUG_MAPPING,
  sportSlugToUuid,
  sportUuidToSlug,
  sportSlugsToUuids,
  sportUuidsToSlugs,
  isValidSportSlug,
  isValidSportUuid,
  getSportUUIDs,
  getSportSlugs,
  getSportMappingBySlug,
  getSportMappingByUuid,
  SportMappingError,
  sportSlugsToUuidsStrict,
  clearMappingCache,
} from '@/lib/sport-id-mapper';

describe('Sport ID Mapping', () => {
  beforeEach(() => {
    clearMappingCache();
  });

  describe('Basic mapping functions', () => {
    it('should convert slug to UUID correctly', () => {
      expect(sportSlugToUuid('football')).toBe('2350948d-f6d4-4a85-9358-b76ed505aea2');
      expect(sportSlugToUuid('basketball')).toBe('498127a1-e061-4386-89ce-a5f00692004c');
      expect(sportSlugToUuid('invalid-sport')).toBe(null);
    });

    it('should convert UUID to slug correctly', () => {
      expect(sportUuidToSlug('2350948d-f6d4-4a85-9358-b76ed505aea2')).toBe('football');
      expect(sportUuidToSlug('498127a1-e061-4386-89ce-a5f00692004c')).toBe('basketball');
      expect(sportUuidToSlug('invalid-uuid')).toBe(null);
    });

    it('should convert multiple slugs to UUIDs', () => {
      const slugs = ['football', 'basketball', 'invalid-sport'];
      const uuids = sportSlugsToUuids(slugs);

      expect(uuids).toHaveLength(2);
      expect(uuids).toContain('2350948d-f6d4-4a85-9358-b76ed505aea2');
      expect(uuids).toContain('498127a1-e061-4386-89ce-a5f00692004c');
    });

    it('should convert multiple UUIDs to slugs', () => {
      const uuids = ['2350948d-f6d4-4a85-9358-b76ed505aea2', '498127a1-e061-4386-89ce-a5f00692004c', 'invalid-uuid'];
      const slugs = sportUuidsToSlugs(uuids);

      expect(slugs).toHaveLength(2);
      expect(slugs).toContain('football');
      expect(slugs).toContain('basketball');
    });
  });

  describe('Validation functions', () => {
    it('should validate sport slugs correctly', () => {
      expect(isValidSportSlug('football')).toBe(true);
      expect(isValidSportSlug('basketball')).toBe(true);
      expect(isValidSportSlug('invalid-sport')).toBe(false);
    });

    it('should validate sport UUIDs correctly', () => {
      expect(isValidSportUuid('2350948d-f6d4-4a85-9358-b76ed505aea2')).toBe(true);
      expect(isValidSportUuid('498127a1-e061-4386-89ce-a5f00692004c')).toBe(true);
      expect(isValidSportUuid('invalid-uuid')).toBe(false);
    });
  });

  describe('Async functions', () => {
    it('should get sport UUIDs asynchronously', async () => {
      const slugs = ['football', 'basketball'];
      const uuids = await getSportUUIDs(slugs);

      expect(uuids).toHaveLength(2);
      expect(uuids).toContain('2350948d-f6d4-4a85-9358-b76ed505aea2');
      expect(uuids).toContain('498127a1-e061-4386-89ce-a5f00692004c');
    });

    it('should get sport slugs asynchronously', async () => {
      const uuids = ['2350948d-f6d4-4a85-9358-b76ed505aea2', '498127a1-e061-4386-89ce-a5f00692004c'];
      const slugs = await getSportSlugs(uuids);

      expect(slugs).toHaveLength(2);
      expect(slugs).toContain('football');
      expect(slugs).toContain('basketball');
    });
  });

  describe('Sport mapping metadata', () => {
    it('should get sport mapping by slug', () => {
      const mapping = getSportMappingBySlug('football');
      expect(mapping).toEqual({
        slug: 'football',
        uuid: '2350948d-f6d4-4a85-9358-b76ed505aea2',
        name: 'Football',
        hasTeams: true,
        teamCount: 32,
      });
    });

    it('should get sport mapping by UUID', () => {
      const mapping = getSportMappingByUuid('2350948d-f6d4-4a85-9358-b76ed505aea2');
      expect(mapping).toEqual({
        slug: 'football',
        uuid: '2350948d-f6d4-4a85-9358-b76ed505aea2',
        name: 'Football',
        hasTeams: true,
        teamCount: 32,
      });
    });

    it('should return null for invalid mappings', () => {
      expect(getSportMappingBySlug('invalid-sport')).toBe(null);
      expect(getSportMappingByUuid('invalid-uuid')).toBe(null);
    });
  });

  describe('Strict conversion functions', () => {
    it('should convert slugs to UUIDs strictly', () => {
      const slugs = ['football', 'basketball'];
      const uuids = sportSlugsToUuidsStrict(slugs);

      expect(uuids).toHaveLength(2);
      expect(uuids).toContain('2350948d-f6d4-4a85-9358-b76ed505aea2');
      expect(uuids).toContain('498127a1-e061-4386-89ce-a5f00692004c');
    });

    it('should throw error for invalid slugs in strict mode', () => {
      const slugs = ['football', 'invalid-sport'];

      expect(() => sportSlugsToUuidsStrict(slugs)).toThrow(SportMappingError);
      expect(() => sportSlugsToUuidsStrict(slugs)).toThrow('Invalid sport slugs: invalid-sport');
    });
  });

  describe('Data consistency', () => {
    it('should have consistent mapping data', () => {
      // Check that all mappings are bidirectional
      Object.entries(SPORT_UUID_MAPPING).forEach(([slug, uuid]) => {
        expect(SPORT_SLUG_MAPPING[uuid]).toBe(slug);
      });

      Object.entries(SPORT_SLUG_MAPPING).forEach(([uuid, slug]) => {
        expect(SPORT_UUID_MAPPING[slug]).toBe(uuid);
      });
    });

    it('should handle college basketball edge case', () => {
      // College basketball has 0 teams according to the mapping
      const mapping = getSportMappingBySlug('college-basketball');
      expect(mapping?.hasTeams).toBe(false);
      expect(mapping?.teamCount).toBe(0);
    });
  });

  describe('API compatibility test scenarios', () => {
    it('should handle onboarding sports selection scenario', async () => {
      // Simulate frontend selecting sports with slugs
      const selectedSlugs = ['football', 'basketball'];

      // Convert to UUIDs for API call
      const uuids = await getSportUUIDs(selectedSlugs);

      expect(uuids).toHaveLength(2);
      expect(uuids.every(uuid => isValidSportUuid(uuid))).toBe(true);
    });

    it('should handle team selection scenario', () => {
      // Simulate receiving UUIDs from previous step
      const sportUuids = ['2350948d-f6d4-4a85-9358-b76ed505aea2', '498127a1-e061-4386-89ce-a5f00692004c'];

      // These should be valid for API calls
      expect(sportUuids.every(uuid => isValidSportUuid(uuid))).toBe(true);

      // Can convert back to slugs for display if needed
      const slugs = sportUuidsToSlugs(sportUuids);
      expect(slugs).toEqual(['football', 'basketball']);
    });
  });
});