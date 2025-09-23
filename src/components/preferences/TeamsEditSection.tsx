/**
 * TeamsEditSection Component
 *
 * Reusable team selection component for preferences editing.
 * Based on the existing TeamSelectionStep from onboarding.
 */

import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Checkbox } from '@/components/ui/checkbox';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from '@/components/ui/use-toast';
import { Search, Save, Star, AlertCircle, Users } from 'lucide-react';
import { createApiQueryClient, type OnboardingTeam } from '@/lib/api-client';
import { useFirebaseAuth } from '@/contexts/FirebaseAuthContext';
import { type TeamPreference, type SportPreference } from '@/hooks/usePreferences';
import { cn } from '@/lib/utils';

interface TeamWithSelection extends OnboardingTeam {
  isSelected: boolean;
  affinityScore: number;
}

interface TeamsEditSectionProps {
  teams: TeamPreference[];
  onTeamsChange: (teams: TeamPreference[]) => void;
  onSave: () => Promise<void>;
  isSaving: boolean;
  error: Error | null;
  availableSports: SportPreference[];
}

export function TeamsEditSection({
  teams,
  onTeamsChange,
  onSave,
  isSaving,
  error,
  availableSports,
}: TeamsEditSectionProps) {
  const { isAuthenticated, getIdToken, user } = useFirebaseAuth();
  const [teamsState, setTeamsState] = useState<TeamWithSelection[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSport, setSelectedSport] = useState<string>('all');
  const [isApiAvailable, setIsApiAvailable] = useState(true);

  const sportIds = availableSports.map(sport => sport.sportId);

  // Set up API client
  const queryConfigs = createApiQueryClient(
    isAuthenticated ? { getIdToken, isAuthenticated: true, userId: user?.uid } : undefined
  );

  // Fetch available teams
  const {
    data: availableTeamsData,
    isLoading,
    error: apiError,
  } = useQuery({
    ...queryConfigs.getOnboardingTeams(sportIds),
    retry: 2,
    retryDelay: 1000,
    enabled: sportIds.length > 0,
  });

  // Track API availability
  useEffect(() => {
    if (apiError) {
      setIsApiAvailable(false);
      console.warn('Teams API unavailable, using fallback data:', apiError);
    }
  }, [apiError]);

  // Fallback team data
  const getFallbackTeams = (): OnboardingTeam[] => {
    const fallbackTeams: OnboardingTeam[] = [];

    availableSports.forEach(sport => {
      switch (sport.sportId) {
        case 'nfl':
          fallbackTeams.push(
            { id: 'chiefs', name: 'Kansas City Chiefs', market: 'Kansas City', sportId: 'nfl', league: 'NFL', logo: '🏈' },
            { id: 'cowboys', name: 'Dallas Cowboys', market: 'Dallas', sportId: 'nfl', league: 'NFL', logo: '🏈' },
            { id: 'patriots', name: 'New England Patriots', market: 'New England', sportId: 'nfl', league: 'NFL', logo: '🏈' },
          );
          break;
        case 'nba':
          fallbackTeams.push(
            { id: 'lakers', name: 'Los Angeles Lakers', market: 'Los Angeles', sportId: 'nba', league: 'NBA', logo: '🏀' },
            { id: 'warriors', name: 'Golden State Warriors', market: 'Golden State', sportId: 'nba', league: 'NBA', logo: '🏀' },
            { id: 'celtics', name: 'Boston Celtics', market: 'Boston', sportId: 'nba', league: 'NBA', logo: '🏀' },
          );
          break;
        case 'mlb':
          fallbackTeams.push(
            { id: 'yankees', name: 'New York Yankees', market: 'New York', sportId: 'mlb', league: 'MLB', logo: '⚾' },
            { id: 'dodgers', name: 'Los Angeles Dodgers', market: 'Los Angeles', sportId: 'mlb', league: 'MLB', logo: '⚾' },
            { id: 'red-sox', name: 'Boston Red Sox', market: 'Boston', sportId: 'mlb', league: 'MLB', logo: '⚾' },
          );
          break;
        case 'nhl':
          fallbackTeams.push(
            { id: 'rangers', name: 'New York Rangers', market: 'New York', sportId: 'nhl', league: 'NHL', logo: '🏒' },
            { id: 'bruins', name: 'Boston Bruins', market: 'Boston', sportId: 'nhl', league: 'NHL', logo: '🏒' },
            { id: 'blackhawks', name: 'Chicago Blackhawks', market: 'Chicago', sportId: 'nhl', league: 'NHL', logo: '🏒' },
          );
          break;
      }
    });

    return fallbackTeams;
  };

  const activeTeamsData = availableTeamsData || getFallbackTeams();

  // Initialize teams state
  useEffect(() => {
    if (activeTeamsData.length > 0) {
      const teamsWithSelection = activeTeamsData.map((team) => {
        const existingTeam = teams.find(t => t.teamId === team.id);
        return {
          ...team,
          isSelected: !!existingTeam,
          affinityScore: existingTeam?.affinityScore || 5,
        };
      });

      setTeamsState(teamsWithSelection);
    }
  }, [activeTeamsData, teams]);

  const handleToggleTeam = (teamId: string) => {
    setTeamsState(prevTeams => {
      const targetTeam = prevTeams.find(t => t.id === teamId);
      if (!targetTeam) return prevTeams;

      const currentSelectedCount = prevTeams.filter(t => t.isSelected).length;
      const isSelecting = !targetTeam.isSelected;

      if (isSelecting && currentSelectedCount >= 10) {
        toast({
          title: 'Maximum 10 Teams',
          description: 'You can select a maximum of 10 teams. Please deselect one first.',
          variant: 'destructive',
        });
        return prevTeams;
      }

      const updatedTeams = prevTeams.map(team =>
        team.id === teamId
          ? { ...team, isSelected: !team.isSelected }
          : team
      );

      // Update parent component
      const selectedTeams: TeamPreference[] = updatedTeams
        .filter(team => team.isSelected)
        .map(team => ({
          teamId: team.id,
          name: team.name,
          sportId: team.sportId,
          league: team.league,
          affinityScore: team.affinityScore,
        }));

      onTeamsChange(selectedTeams);
      return updatedTeams;
    });
  };

  const handleAffinityChange = (teamId: string, score: number) => {
    setTeamsState(prevTeams => {
      const updatedTeams = prevTeams.map(team =>
        team.id === teamId
          ? { ...team, affinityScore: score }
          : team
      );

      // Update parent component
      const selectedTeams: TeamPreference[] = updatedTeams
        .filter(team => team.isSelected)
        .map(team => ({
          teamId: team.id,
          name: team.name,
          sportId: team.sportId,
          league: team.league,
          affinityScore: team.affinityScore,
        }));

      onTeamsChange(selectedTeams);
      return updatedTeams;
    });
  };

  // Filter teams based on search and sport
  const filteredTeams = teamsState.filter(team => {
    const matchesSearch = team.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         team.market.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesSport = selectedSport === 'all' || team.sportId === selectedSport;
    return matchesSearch && matchesSport;
  });

  const selectedCount = teamsState.filter(team => team.isSelected).length;

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Team Preferences</CardTitle>
          <CardDescription>Loading available teams...</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (availableSports.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Team Preferences</CardTitle>
          <CardDescription>Select sports first to choose teams</CardDescription>
        </CardHeader>
        <CardContent>
          <Alert>
            <Users className="h-4 w-4" />
            <AlertDescription>
              Please select your sports preferences first, then return here to choose your favorite teams.
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              Team Preferences
              <Badge variant="outline">{selectedCount} selected</Badge>
            </CardTitle>
            <CardDescription>
              Select your favorite teams and set your affinity level (maximum 10)
            </CardDescription>
          </div>
          <Button
            onClick={onSave}
            disabled={isSaving}
            size="sm"
          >
            {isSaving ? (
              <>
                <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                Saving...
              </>
            ) : (
              <>
                <Save className="mr-2 h-4 w-4" />
                Save Teams
              </>
            )}
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {!isApiAvailable && (
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              Working offline. Your changes will be saved when connection is restored.
            </AlertDescription>
          </Alert>
        )}

        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error.message}</AlertDescription>
          </Alert>
        )}

        {/* Filters */}
        <div className="flex gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search teams..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
          <Select value={selectedSport} onValueChange={setSelectedSport}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Filter by sport" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Sports</SelectItem>
              {availableSports.map(sport => (
                <SelectItem key={sport.sportId} value={sport.sportId}>
                  {sport.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Teams Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {filteredTeams.map(team => (
            <Card
              key={team.id}
              className={cn(
                'transition-all duration-200 cursor-pointer hover:shadow-md',
                team.isSelected
                  ? 'ring-2 ring-primary bg-primary/5'
                  : 'hover:bg-muted/50'
              )}
              onClick={() => handleToggleTeam(team.id)}
            >
              <CardContent className="p-4">
                <div className="flex items-start gap-3">
                  <Checkbox
                    checked={team.isSelected}
                    onChange={() => {}} // Handled by card click
                    className="mt-1"
                  />

                  <div className="flex-1 space-y-2">
                    <div className="flex items-center gap-2">
                      <span className="text-lg">{team.logo}</span>
                      <div className="flex-1">
                        <h4 className="font-semibold text-sm leading-tight">
                          {team.name}
                        </h4>
                        <p className="text-xs text-muted-foreground">
                          {team.market} • {team.league}
                        </p>
                      </div>
                    </div>

                    {team.isSelected && (
                      <div className="space-y-2" onClick={(e) => e.stopPropagation()}>
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-medium">Affinity Level:</span>
                          <div className="flex gap-1">
                            {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(score => (
                              <button
                                key={score}
                                onClick={() => handleAffinityChange(team.id, score)}
                                className={cn(
                                  'w-5 h-5 rounded-full border transition-colors',
                                  score <= team.affinityScore
                                    ? 'bg-primary border-primary'
                                    : 'border-muted-foreground hover:border-primary'
                                )}
                                title={`Set affinity to ${score}`}
                              >
                                {score <= team.affinityScore && (
                                  <Star className="w-3 h-3 text-white fill-white mx-auto" />
                                )}
                              </button>
                            ))}
                          </div>
                        </div>
                        <p className="text-xs text-muted-foreground">
                          {team.affinityScore}/10 - Higher levels get more content priority
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {filteredTeams.length === 0 && (
          <div className="text-center py-8">
            <p className="text-muted-foreground">
              No teams found matching your search criteria.
            </p>
          </div>
        )}

        {selectedCount > 0 && (
          <Alert>
            <Star className="h-4 w-4" />
            <AlertDescription>
              <strong>Tip:</strong> Use affinity levels to prioritize teams. Higher levels (8-10) get more
              coverage in your feed, while lower levels (1-3) get occasional updates.
            </AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  );
}