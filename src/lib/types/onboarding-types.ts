export interface UserPreferences {
  id: string;
  sports: SportPreference[];
  teams: TeamPreference[];
  preferences: UserSettings;
  completedAt?: string;
  createdAt: string;
  updatedAt: string;
}

export interface SportPreference {
  sportId: string;
  name: string;
  rank: number;
  hasTeams: boolean;
}

export interface TeamPreference {
  teamId: string;
  name: string;
  sportId: string;
  league: string;
  affinityScore: number;
}

export interface UserSettings {
  newsTypes: NewsTypePreference[];
  notifications: NotificationSettings;
  contentFrequency: ContentFrequency;
}

export interface NewsTypePreference {
  type: 'injuries' | 'trades' | 'roster' | 'general' | 'scores' | 'analysis';
  enabled: boolean;
  priority: number;
}

export interface NotificationSettings {
  push: boolean;
  email: boolean;
  gameReminders: boolean;
  newsAlerts: boolean;
  scoreUpdates: boolean;
}

export type ContentFrequency = 'minimal' | 'standard' | 'comprehensive';

export interface Sport {
  id: string;
  name: string;
  hasTeams: boolean;
  icon: string;
  popularTeams?: string[];
  leagues?: League[];
}

export interface League {
  id: string;
  name: string;
  sportId: string;
  teams: Team[];
}

export interface Team {
  id: string;
  name: string;
  market: string;
  sportId: string;
  league: string;
  logo: string;
  primaryColor: string;
  secondaryColor: string;
  abbreviation: string;
}

export interface OnboardingStep {
  id: string;
  title: string;
  description: string;
  isCompleted: boolean;
  isRequired: boolean;
}

export interface OnboardingState {
  currentStep: number;
  steps: OnboardingStep[];
  userPreferences: Partial<UserPreferences>;
  isComplete: boolean;
  errors: Record<string, string>;
}

export type OnboardingAction =
  | { type: 'SET_CURRENT_STEP'; payload: number }
  | { type: 'UPDATE_SPORTS'; payload: SportPreference[] }
  | { type: 'UPDATE_TEAMS'; payload: TeamPreference[] }
  | { type: 'UPDATE_PREFERENCES'; payload: UserSettings }
  | { type: 'SET_STEP_COMPLETED'; payload: { stepId: string; completed: boolean } }
  | { type: 'SET_ERROR'; payload: { field: string; error: string } }
  | { type: 'CLEAR_ERRORS' }
  | { type: 'COMPLETE_ONBOARDING' }
  | { type: 'RESET_ONBOARDING' };

export const ONBOARDING_STEPS: OnboardingStep[] = [
  {
    id: 'welcome',
    title: 'Welcome',
    description: 'Get started with Corner League Media',
    isCompleted: false,
    isRequired: true,
  },
  {
    id: 'sports',
    title: 'Select Sports',
    description: 'Choose your favorite sports',
    isCompleted: false,
    isRequired: true,
  },
  {
    id: 'teams',
    title: 'Choose Teams',
    description: 'Pick your favorite teams',
    isCompleted: false,
    isRequired: true,
  },
  {
    id: 'preferences',
    title: 'Preferences',
    description: 'Customize your experience',
    isCompleted: false,
    isRequired: false,
  },
  {
    id: 'complete',
    title: 'Complete',
    description: 'Your setup is ready!',
    isCompleted: false,
    isRequired: true,
  },
];

export const DEFAULT_USER_SETTINGS: UserSettings = {
  newsTypes: [
    { type: 'injuries', enabled: true, priority: 1 },
    { type: 'trades', enabled: true, priority: 2 },
    { type: 'roster', enabled: true, priority: 3 },
    { type: 'scores', enabled: true, priority: 4 },
    { type: 'general', enabled: false, priority: 5 },
    { type: 'analysis', enabled: false, priority: 6 },
  ],
  notifications: {
    push: false,
    email: false,
    gameReminders: false,
    newsAlerts: false,
    scoreUpdates: false,
  },
  contentFrequency: 'standard',
};