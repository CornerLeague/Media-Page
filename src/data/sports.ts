import { Sport } from '@/lib/types/onboarding-types';

export const AVAILABLE_SPORTS: Sport[] = [
  {
    id: 'nfl',
    name: 'NFL',
    hasTeams: true,
    icon: '🏈',
    popularTeams: ['chiefs', 'cowboys', 'patriots', 'packers', '49ers'],
    leagues: [
      {
        id: 'nfl',
        name: 'National Football League',
        sportId: 'nfl',
        teams: [], // Will be populated from teams data
      }
    ]
  },
  {
    id: 'nba',
    name: 'NBA',
    hasTeams: true,
    icon: '🏀',
    popularTeams: ['lakers', 'warriors', 'celtics', 'heat', 'bulls'],
    leagues: [
      {
        id: 'nba',
        name: 'National Basketball Association',
        sportId: 'nba',
        teams: [],
      }
    ]
  },
  {
    id: 'mlb',
    name: 'MLB',
    hasTeams: true,
    icon: '⚾',
    popularTeams: ['yankees', 'dodgers', 'red-sox', 'giants', 'cubs'],
    leagues: [
      {
        id: 'mlb',
        name: 'Major League Baseball',
        sportId: 'mlb',
        teams: [],
      }
    ]
  },
  {
    id: 'nhl',
    name: 'NHL',
    hasTeams: true,
    icon: '🏒',
    popularTeams: ['rangers', 'bruins', 'blackhawks', 'penguins', 'maple-leafs'],
    leagues: [
      {
        id: 'nhl',
        name: 'National Hockey League',
        sportId: 'nhl',
        teams: [],
      }
    ]
  },
  {
    id: 'mls',
    name: 'MLS',
    hasTeams: true,
    icon: '⚽',
    popularTeams: ['lafc', 'inter-miami', 'atlanta-united', 'seattle-sounders', 'nycfc'],
    leagues: [
      {
        id: 'mls',
        name: 'Major League Soccer',
        sportId: 'mls',
        teams: [],
      }
    ]
  },
  {
    id: 'college-football',
    name: 'College Football',
    hasTeams: true,
    icon: '🏈',
    popularTeams: ['alabama', 'michigan', 'georgia', 'ohio-state', 'clemson'],
    leagues: [
      {
        id: 'sec',
        name: 'SEC',
        sportId: 'college-football',
        teams: [],
      },
      {
        id: 'big-ten',
        name: 'Big Ten',
        sportId: 'college-football',
        teams: [],
      },
      {
        id: 'acc',
        name: 'ACC',
        sportId: 'college-football',
        teams: [],
      },
      {
        id: 'big-12',
        name: 'Big 12',
        sportId: 'college-football',
        teams: [],
      },
      {
        id: 'pac-12',
        name: 'Pac-12',
        sportId: 'college-football',
        teams: [],
      }
    ]
  },
  {
    id: 'college-basketball',
    name: 'College Basketball',
    hasTeams: true,
    icon: '🏀',
    popularTeams: ['duke', 'north-carolina', 'kansas', 'kentucky', 'gonzaga'],
    leagues: [
      {
        id: 'acc-basketball',
        name: 'ACC',
        sportId: 'college-basketball',
        teams: [],
      },
      {
        id: 'big-east',
        name: 'Big East',
        sportId: 'college-basketball',
        teams: [],
      },
      {
        id: 'sec-basketball',
        name: 'SEC',
        sportId: 'college-basketball',
        teams: [],
      }
    ]
  },
  {
    id: 'formula1',
    name: 'Formula 1',
    hasTeams: false,
    icon: '🏎️',
  },
  {
    id: 'golf',
    name: 'Golf',
    hasTeams: false,
    icon: '⛳',
  },
  {
    id: 'tennis',
    name: 'Tennis',
    hasTeams: false,
    icon: '🎾',
  },
];

export const getSportById = (sportId: string): Sport | undefined => {
  return AVAILABLE_SPORTS.find(sport => sport.id === sportId);
};

export const getSportsWithTeams = (): Sport[] => {
  return AVAILABLE_SPORTS.filter(sport => sport.hasTeams);
};

export const getSportsWithoutTeams = (): Sport[] => {
  return AVAILABLE_SPORTS.filter(sport => !sport.hasTeams);
};

export const getPopularSports = (): Sport[] => {
  // Return the most popular sports (first 4)
  return AVAILABLE_SPORTS.slice(0, 4);
};