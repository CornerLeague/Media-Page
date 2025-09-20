// Re-export Firebase types for convenience
export type {
  UserPreferences,
  NotificationPreferences,
  UserProfile,
  Article,
  AuthState,
  FirebaseOperationResult,
  CreateDocument,
  UpdateDocument,
} from './lib/types/firebase-types';

// Sports and Teams Types (previously from onboarding-types)
export interface League {
  id: string;
  name: string;
  sportId: string;
  teams: string[];
}

export interface Sport {
  id: string;
  name: string;
  hasTeams: boolean;
  icon?: string;
  popularTeams?: string[];
  leagues?: League[];
}

export interface Team {
  id: string;
  name: string;
  market: string;
  sportId: string;
  league: string;
  logo?: string;
  primaryColor?: string;
  secondaryColor?: string;
  abbreviation?: string;
}

// Legacy type for backward compatibility
export interface LegacyUserPreferences {
  sports: string[]
  teams: string[]
  aiSummaryLevel: number
  notifications: {
    gameAlerts: boolean
    newsDigest: boolean
    tradingUpdates: boolean
  }
}