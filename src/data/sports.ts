import { Sport } from '@/types';
import { SPORT_UUID_MAPPING } from '@/lib/sport-id-mapper';

export const AVAILABLE_SPORTS: Sport[] = [
  {
    id: SPORT_UUID_MAPPING['football'], // Use UUID for backend compatibility
    name: 'NFL',
    hasTeams: true,
    icon: '🏈',
    popularTeams: ['chiefs', 'cowboys', 'patriots', 'packers', '49ers'],
    leagues: [
      {
        id: 'nfl',
        name: 'National Football League',
        sportId: SPORT_UUID_MAPPING['football'],
        teams: [], // Will be populated from teams data
      }
    ]
  },
  {
    id: SPORT_UUID_MAPPING['basketball'], // Use UUID for backend compatibility
    name: 'NBA',
    hasTeams: true,
    icon: '🏀',
    popularTeams: ['lakers', 'warriors', 'celtics', 'heat', 'bulls'],
    leagues: [
      {
        id: 'nba',
        name: 'National Basketball Association',
        sportId: SPORT_UUID_MAPPING['basketball'],
        teams: [],
      }
    ]
  },
  {
    id: SPORT_UUID_MAPPING['baseball'], // Use UUID for backend compatibility
    name: 'MLB',
    hasTeams: true,
    icon: '⚾',
    popularTeams: ['yankees', 'dodgers', 'red-sox', 'giants', 'cubs'],
    leagues: [
      {
        id: 'mlb',
        name: 'Major League Baseball',
        sportId: SPORT_UUID_MAPPING['baseball'],
        teams: [],
      }
    ]
  },
  {
    id: SPORT_UUID_MAPPING['hockey'], // Use UUID for backend compatibility
    name: 'NHL',
    hasTeams: true,
    icon: '🏒',
    popularTeams: ['rangers', 'bruins', 'blackhawks', 'penguins', 'maple-leafs'],
    leagues: [
      {
        id: 'nhl',
        name: 'National Hockey League',
        sportId: SPORT_UUID_MAPPING['hockey'],
        teams: [],
      }
    ]
  },
  {
    id: SPORT_UUID_MAPPING['soccer'], // Use UUID for backend compatibility
    name: 'MLS',
    hasTeams: true,
    icon: '⚽',
    popularTeams: ['lafc', 'inter-miami', 'atlanta-united', 'seattle-sounders', 'nycfc'],
    leagues: [
      {
        id: 'mls',
        name: 'Major League Soccer',
        sportId: SPORT_UUID_MAPPING['soccer'],
        teams: [],
      }
    ]
  },
  {
    id: SPORT_UUID_MAPPING['college-football'], // Use UUID for backend compatibility
    name: 'College Football',
    hasTeams: true,
    icon: '🏈',
    popularTeams: ['alabama', 'michigan', 'georgia', 'ohio-state', 'clemson'],
    leagues: [
      {
        id: 'sec',
        name: 'SEC',
        sportId: SPORT_UUID_MAPPING['college-football'],
        teams: [],
      },
      {
        id: 'big-ten',
        name: 'Big Ten',
        sportId: SPORT_UUID_MAPPING['college-football'],
        teams: [],
      },
      {
        id: 'acc',
        name: 'ACC',
        sportId: SPORT_UUID_MAPPING['college-football'],
        teams: [],
      },
      {
        id: 'big-12',
        name: 'Big 12',
        sportId: SPORT_UUID_MAPPING['college-football'],
        teams: [],
      },
      {
        id: 'pac-12',
        name: 'Pac-12',
        sportId: SPORT_UUID_MAPPING['college-football'],
        teams: [],
      }
    ]
  },
  {
    id: SPORT_UUID_MAPPING['college-basketball'], // Use UUID for backend compatibility
    name: 'College Basketball',
    hasTeams: false, // According to the mapping, college basketball has 0 teams
    icon: '🏀',
    popularTeams: ['duke', 'north-carolina', 'kansas', 'kentucky', 'gonzaga'],
    leagues: [
      {
        id: 'acc-basketball',
        name: 'ACC',
        sportId: SPORT_UUID_MAPPING['college-basketball'],
        teams: [],
      },
      {
        id: 'big-east',
        name: 'Big East',
        sportId: SPORT_UUID_MAPPING['college-basketball'],
        teams: [],
      },
      {
        id: 'sec-basketball',
        name: 'SEC',
        sportId: SPORT_UUID_MAPPING['college-basketball'],
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