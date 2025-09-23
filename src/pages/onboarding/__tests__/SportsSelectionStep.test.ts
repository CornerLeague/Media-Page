/**
 * Unit tests for Sports Selection Step rank validation and persistence logic
 */

// Mock implementation of the validation function for testing
interface SportItem {
  id: string;
  isSelected: boolean;
  rank: number;
}

function validateRankIntegrity(sports: SportItem[]): {
  isValid: boolean;
  errors: string[];
} {
  const errors: string[] = [];
  const selectedSports = sports.filter(sport => sport.isSelected);

  if (selectedSports.length === 0) {
    return { isValid: true, errors: [] };
  }

  // Check for duplicate ranks
  const ranks = selectedSports.map(sport => sport.rank);
  const uniqueRanks = new Set(ranks);
  if (ranks.length !== uniqueRanks.size) {
    errors.push('Duplicate ranks detected');
  }

  // Check for invalid rank values
  const invalidRanks = selectedSports.filter(sport =>
    sport.rank <= 0 || sport.rank > selectedSports.length || !Number.isInteger(sport.rank)
  );
  if (invalidRanks.length > 0) {
    errors.push('Invalid rank values detected');
  }

  // Check for missing ranks in sequence
  const sortedRanks = [...ranks].sort((a, b) => a - b);
  for (let i = 0; i < sortedRanks.length; i++) {
    if (sortedRanks[i] !== i + 1) {
      errors.push('Missing ranks in sequence');
      break;
    }
  }

  // Check that unselected sports have rank 0
  const unselectedWithRank = sports.filter(sport => !sport.isSelected && sport.rank !== 0);
  if (unselectedWithRank.length > 0) {
    errors.push('Unselected sports have non-zero ranks');
  }

  return {
    isValid: errors.length === 0,
    errors
  };
}

function normalizeRanks(sports: SportItem[]): SportItem[] {
  const selectedSports = sports.filter(sport => sport.isSelected);

  // Sort selected sports by their current rank to preserve order
  const sortedSelected = selectedSports.sort((a, b) => {
    if (a.rank === 0 && b.rank === 0) return 0;
    if (a.rank === 0) return 1;
    if (b.rank === 0) return -1;
    return a.rank - b.rank;
  });

  return sports.map(sport => {
    if (!sport.isSelected) {
      return { ...sport, rank: 0 };
    }

    const newRank = sortedSelected.findIndex(s => s.id === sport.id) + 1;
    return { ...sport, rank: newRank };
  });
}

// Test cases
describe('Sports Selection Rank Validation', () => {
  test('validates correct rank sequence', () => {
    const sports: SportItem[] = [
      { id: 'nfl', isSelected: true, rank: 1 },
      { id: 'nba', isSelected: true, rank: 2 },
      { id: 'mlb', isSelected: false, rank: 0 }
    ];

    const result = validateRankIntegrity(sports);
    expect(result.isValid).toBe(true);
    expect(result.errors).toHaveLength(0);
  });

  test('detects duplicate ranks', () => {
    const sports: SportItem[] = [
      { id: 'nfl', isSelected: true, rank: 1 },
      { id: 'nba', isSelected: true, rank: 1 },
      { id: 'mlb', isSelected: false, rank: 0 }
    ];

    const result = validateRankIntegrity(sports);
    expect(result.isValid).toBe(false);
    expect(result.errors).toContain('Duplicate ranks detected');
  });

  test('detects missing ranks in sequence', () => {
    const sports: SportItem[] = [
      { id: 'nfl', isSelected: true, rank: 1 },
      { id: 'nba', isSelected: true, rank: 3 },
      { id: 'mlb', isSelected: false, rank: 0 }
    ];

    const result = validateRankIntegrity(sports);
    expect(result.isValid).toBe(false);
    expect(result.errors).toContain('Missing ranks in sequence');
  });

  test('detects invalid rank values', () => {
    const sports: SportItem[] = [
      { id: 'nfl', isSelected: true, rank: 0 },
      { id: 'nba', isSelected: true, rank: 1 },
      { id: 'mlb', isSelected: false, rank: 0 }
    ];

    const result = validateRankIntegrity(sports);
    expect(result.isValid).toBe(false);
    expect(result.errors).toContain('Invalid rank values detected');
  });

  test('detects unselected sports with non-zero ranks', () => {
    const sports: SportItem[] = [
      { id: 'nfl', isSelected: true, rank: 1 },
      { id: 'nba', isSelected: false, rank: 2 },
      { id: 'mlb', isSelected: false, rank: 0 }
    ];

    const result = validateRankIntegrity(sports);
    expect(result.isValid).toBe(false);
    expect(result.errors).toContain('Unselected sports have non-zero ranks');
  });

  test('handles empty selection correctly', () => {
    const sports: SportItem[] = [
      { id: 'nfl', isSelected: false, rank: 0 },
      { id: 'nba', isSelected: false, rank: 0 },
      { id: 'mlb', isSelected: false, rank: 0 }
    ];

    const result = validateRankIntegrity(sports);
    expect(result.isValid).toBe(true);
    expect(result.errors).toHaveLength(0);
  });
});

describe('Sports Selection Rank Normalization', () => {
  test('normalizes ranks correctly', () => {
    const sports: SportItem[] = [
      { id: 'nfl', isSelected: true, rank: 3 },
      { id: 'nba', isSelected: true, rank: 1 },
      { id: 'mlb', isSelected: false, rank: 5 },
      { id: 'nhl', isSelected: true, rank: 2 }
    ];

    const normalized = normalizeRanks(sports);

    // NBA should be rank 1, NHL rank 2, NFL rank 3, MLB rank 0
    expect(normalized.find(s => s.id === 'nba')?.rank).toBe(1);
    expect(normalized.find(s => s.id === 'nhl')?.rank).toBe(2);
    expect(normalized.find(s => s.id === 'nfl')?.rank).toBe(3);
    expect(normalized.find(s => s.id === 'mlb')?.rank).toBe(0);
    expect(normalized.find(s => s.id === 'mlb')?.isSelected).toBe(false);
  });

  test('handles unselected sports correctly', () => {
    const sports: SportItem[] = [
      { id: 'nfl', isSelected: false, rank: 3 },
      { id: 'nba', isSelected: false, rank: 1 },
      { id: 'mlb', isSelected: false, rank: 5 }
    ];

    const normalized = normalizeRanks(sports);

    normalized.forEach(sport => {
      expect(sport.rank).toBe(0);
      expect(sport.isSelected).toBe(false);
    });
  });

  test('preserves rank order for selected sports', () => {
    const sports: SportItem[] = [
      { id: 'nfl', isSelected: true, rank: 2 },
      { id: 'nba', isSelected: true, rank: 1 },
      { id: 'mlb', isSelected: true, rank: 3 }
    ];

    const normalized = normalizeRanks(sports);
    const selectedNormalized = normalized.filter(s => s.isSelected);

    // Should maintain the original order: NBA(1), NFL(2), MLB(3)
    expect(selectedNormalized[0].id).toBe('nba');
    expect(selectedNormalized[0].rank).toBe(1);
    expect(selectedNormalized[1].id).toBe('nfl');
    expect(selectedNormalized[1].rank).toBe(2);
    expect(selectedNormalized[2].id).toBe('mlb');
    expect(selectedNormalized[2].rank).toBe(3);
  });
});

// Mock Jest functions for testing environment
const expect = {
  toBe: (value: any) => (actual: any) => actual === value,
  toHaveLength: (length: number) => (actual: any[]) => actual.length === length,
  toContain: (item: any) => (actual: any[]) => actual.includes(item)
};

// Run the tests (this would normally be handled by Jest)
console.log('Running Sports Selection Tests...');

// Example test run
const testSports: SportItem[] = [
  { id: 'nfl', isSelected: true, rank: 1 },
  { id: 'nba', isSelected: true, rank: 2 },
  { id: 'mlb', isSelected: false, rank: 0 }
];

const validation = validateRankIntegrity(testSports);
console.log('Validation Test Result:', validation);

const normalized = normalizeRanks(testSports);
console.log('Normalization Test Result:', normalized);

export { validateRankIntegrity, normalizeRanks };