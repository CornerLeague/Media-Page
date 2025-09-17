import React, { useState, useEffect, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Search,
  Users,
  Heart,
  Star,
  Filter,
  Trophy,
  ChevronRight,
} from 'lucide-react';
import { useOnboarding } from '@/hooks/useOnboarding';
import { TEAMS, getTeamsBySport, searchTeams } from '@/data/teams';
import { AVAILABLE_SPORTS } from '@/data/sports';
import { TeamPreference, Team } from '@/lib/types/onboarding-types';

interface TeamCardProps {
  team: Team;
  isSelected: boolean;
  onToggle: (team: Team) => void;
  affinityScore?: number;
}

const TeamCard: React.FC<TeamCardProps> = ({
  team,
  isSelected,
  onToggle,
  affinityScore = 50,
}) => {
  return (
    <Card
      className={`cursor-pointer transition-all hover:shadow-md ${
        isSelected ? 'border-primary bg-primary/5' : 'hover:border-muted-foreground/50'
      }`}
      onClick={() => onToggle(team)}
    >
      <CardContent className="p-4">
        <div className="flex items-center space-x-3">
          {/* Team logo/icon */}
          <div
            className="h-10 w-10 rounded-full flex items-center justify-center text-lg"
            style={{ backgroundColor: team.primaryColor + '20' }}
          >
            {team.logo}
          </div>

          {/* Team info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-2">
              <h3 className="font-semibold truncate">
                {team.market} {team.name}
              </h3>
              <Badge variant="outline" className="text-xs">
                {team.abbreviation}
              </Badge>
            </div>
            <p className="text-sm text-muted-foreground">
              {team.league}
            </p>
          </div>

          {/* Selection indicator */}
          <div className="flex items-center space-x-2">
            {isSelected && (
              <div className="flex items-center space-x-1 text-primary">
                <Heart className="h-4 w-4 fill-current" />
                <span className="text-xs font-medium">{affinityScore}%</span>
              </div>
            )}
            <Checkbox
              checked={isSelected}
              onCheckedChange={() => onToggle(team)}
              onClick={(e) => e.stopPropagation()}
              aria-label={`${isSelected ? 'Deselect' : 'Select'} ${team.market} ${team.name}`}
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

const TeamSelection: React.FC = () => {
  const { userPreferences, updateTeams, setError, clearErrors } = useOnboarding();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTeams, setSelectedTeams] = useState<Map<string, TeamPreference>>(new Map());
  const [activeSport, setActiveSport] = useState<string>('');

  // Get selected sports from user preferences
  const selectedSports = userPreferences.sports || [];
  const sportsWithTeams = selectedSports.filter(sport => sport.hasTeams);

  // Initialize active sport
  useEffect(() => {
    if (sportsWithTeams.length > 0 && !activeSport) {
      setActiveSport(sportsWithTeams[0].sportId);
    }
  }, [sportsWithTeams, activeSport]);

  // Initialize selected teams from user preferences
  useEffect(() => {
    if (userPreferences.teams) {
      const teamsMap = new Map();
      userPreferences.teams.forEach(team => {
        teamsMap.set(team.teamId, team);
      });
      setSelectedTeams(teamsMap);
    }
  }, [userPreferences.teams]);

  // Update user preferences when team selection changes
  useEffect(() => {
    const teamsList = Array.from(selectedTeams.values());
    updateTeams(teamsList);

    // Clear errors when teams are selected
    if (teamsList.length > 0) {
      clearErrors();
    }
  }, [selectedTeams, updateTeams, clearErrors]);

  // Filter and search teams
  const filteredTeams = useMemo(() => {
    let teams: Team[] = [];

    if (activeSport) {
      teams = getTeamsBySport(activeSport);
    }

    if (searchQuery.trim()) {
      teams = searchTeams(searchQuery, activeSport);
    }

    return teams;
  }, [activeSport, searchQuery]);

  // Group teams by league
  const teamsByLeague = useMemo(() => {
    const groups: Record<string, Team[]> = {};
    filteredTeams.forEach(team => {
      if (!groups[team.league]) {
        groups[team.league] = [];
      }
      groups[team.league].push(team);
    });
    return groups;
  }, [filteredTeams]);

  const handleToggleTeam = (team: Team) => {
    setSelectedTeams(prev => {
      const newMap = new Map(prev);

      if (newMap.has(team.id)) {
        newMap.delete(team.id);
      } else {
        const teamPreference: TeamPreference = {
          teamId: team.id,
          name: `${team.market} ${team.name}`,
          sportId: team.sportId,
          league: team.league,
          affinityScore: 75, // Default affinity score
        };
        newMap.set(team.id, teamPreference);
      }

      return newMap;
    });
  };

  const handleSelectPopularForSport = (sportId: string) => {
    const sport = AVAILABLE_SPORTS.find(s => s.id === sportId);
    if (sport?.popularTeams) {
      const popularTeams = TEAMS.filter(team =>
        sport.popularTeams?.includes(team.id) && team.sportId === sportId
      );

      setSelectedTeams(prev => {
        const newMap = new Map(prev);

        popularTeams.forEach(team => {
          if (!newMap.has(team.id)) {
            const teamPreference: TeamPreference = {
              teamId: team.id,
              name: `${team.market} ${team.name}`,
              sportId: team.sportId,
              league: team.league,
              affinityScore: 80, // Higher affinity for popular teams
            };
            newMap.set(team.id, teamPreference);
          }
        });

        return newMap;
      });
    }
  };

  const handleClearSport = (sportId: string) => {
    setSelectedTeams(prev => {
      const newMap = new Map(prev);

      // Remove all teams for this sport
      for (const [teamId, team] of newMap.entries()) {
        if (team.sportId === sportId) {
          newMap.delete(teamId);
        }
      }

      return newMap;
    });
  };

  const selectedCount = selectedTeams.size;
  const teamsForCurrentSport = Array.from(selectedTeams.values()).filter(
    team => team.sportId === activeSport
  );

  // Check if we need teams for any of the selected sports
  const needsTeams = sportsWithTeams.length > 0;
  const hasMinimumSelection = !needsTeams || selectedCount > 0;

  if (sportsWithTeams.length === 0) {
    return (
      <div className="text-center space-y-4">
        <div className="flex justify-center mb-4">
          <Trophy className="h-8 w-8 text-muted-foreground" />
        </div>
        <h2 className="text-xl font-semibold">No Team Selection Needed</h2>
        <p className="text-muted-foreground max-w-md mx-auto">
          None of your selected sports have teams to choose from.
          You can continue to the next step.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center space-y-2">
        <div className="flex justify-center mb-4">
          <Users className="h-8 w-8 text-primary" />
        </div>
        <p className="text-muted-foreground">
          Choose your favorite teams from the sports you selected.
        </p>
      </div>

      {/* Selection status */}
      <div className="text-center">
        <p className="text-sm text-muted-foreground">
          {selectedCount === 0 ? (
            <span className="text-destructive">Please select at least one team</span>
          ) : (
            <span>
              {selectedCount} team{selectedCount !== 1 ? 's' : ''} selected across{' '}
              {new Set(Array.from(selectedTeams.values()).map(t => t.sportId)).size} sport{new Set(Array.from(selectedTeams.values()).map(t => t.sportId)).size !== 1 ? 's' : ''}
            </span>
          )}
        </p>
      </div>

      {/* Sports tabs */}
      <Tabs value={activeSport} onValueChange={setActiveSport} className="w-full">
        <TabsList className="grid w-full grid-cols-2 lg:grid-cols-4">
          {sportsWithTeams.slice(0, 4).map(sport => (
            <TabsTrigger key={sport.sportId} value={sport.sportId} className="text-xs">
              {sport.name}
              {teamsForCurrentSport.length > 0 && sport.sportId === activeSport && (
                <Badge variant="secondary" className="ml-1 text-xs">
                  {Array.from(selectedTeams.values()).filter(t => t.sportId === sport.sportId).length}
                </Badge>
              )}
            </TabsTrigger>
          ))}
        </TabsList>

        {sportsWithTeams.map(sport => (
          <TabsContent key={sport.sportId} value={sport.sportId} className="space-y-4">
            {/* Search and actions for current sport */}
            <div className="flex flex-col sm:flex-row gap-2">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder={`Search ${sport.name} teams...`}
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleSelectPopularForSport(sport.sportId)}
                  className="whitespace-nowrap"
                >
                  <Star className="h-4 w-4 mr-1" />
                  Popular
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleClearSport(sport.sportId)}
                  className="whitespace-nowrap"
                >
                  Clear
                </Button>
              </div>
            </div>

            {/* Teams list */}
            <ScrollArea className="h-96">
              <div className="space-y-4">
                {Object.entries(teamsByLeague).map(([league, teams]) => (
                  <div key={league}>
                    <h4 className="font-semibold text-sm mb-3 flex items-center">
                      <Filter className="h-4 w-4 mr-2" />
                      {league}
                      <Badge variant="outline" className="ml-2 text-xs">
                        {teams.length} teams
                      </Badge>
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {teams.map(team => (
                        <TeamCard
                          key={team.id}
                          team={team}
                          isSelected={selectedTeams.has(team.id)}
                          onToggle={handleToggleTeam}
                          affinityScore={selectedTeams.get(team.id)?.affinityScore}
                        />
                      ))}
                    </div>
                  </div>
                ))}

                {filteredTeams.length === 0 && (
                  <div className="text-center py-8">
                    <p className="text-muted-foreground">
                      {searchQuery ? 'No teams found matching your search.' : 'No teams available.'}
                    </p>
                  </div>
                )}
              </div>
            </ScrollArea>
          </TabsContent>
        ))}
      </Tabs>

      {/* Instructions */}
      <div className="text-center max-w-md mx-auto">
        <Card className="bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800">
          <CardContent className="p-4">
            <div className="flex items-start space-x-2">
              <ChevronRight className="h-4 w-4 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
              <p className="text-sm text-blue-800 dark:text-blue-200">
                <strong>Tip:</strong> You can select multiple teams from each sport.
                Your choices will personalize your news feed and recommendations.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Validation message */}
      {!hasMinimumSelection && (
        <div className="text-center">
          <p className="text-sm text-destructive">
            Select at least one team to continue
          </p>
        </div>
      )}
    </div>
  );
};

export default TeamSelection;