import React, { useState, useRef, useEffect } from 'react';
import { Check, ChevronDown, Search, X, AlertCircle, Filter } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Command, CommandEmpty, CommandGroup, CommandItem, CommandList } from '@/components/ui/command';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { useTeamSelection, type UseTeamSelectionReturn } from '@/hooks/useTeamSelection';
import { type Team, type EnhancedTeam } from '@/lib/api-client';
import { TeamSearchInput } from '@/components/TeamSearchInput';
import { TeamFilterDropdown, createFilterCategoriesFromTeams, type FilterValues } from '@/components/TeamFilterDropdown';
import { toast } from '@/components/ui/sonner';

interface TeamSelectorProps {
  selectedTeams: Team[];
  onTeamSelect: (teams: Team[]) => void;
  sportIds?: string[];
  leagueIds?: string[];
  multiSelect?: boolean;
  placeholder?: string;
  searchPlaceholder?: string;
  maxSelections?: number;
  disabled?: boolean;
  error?: string;
  className?: string;
  showFilters?: boolean;
  showSearchSuggestions?: boolean;
  useEnhancedSearch?: boolean;
}

interface TeamOptionProps {
  team: Team | EnhancedTeam;
  isSelected: boolean;
  onSelect: () => void;
  multiSelect?: boolean;
  showHighlighting?: boolean;
}

function TeamOption({ team, isSelected, onSelect, multiSelect = true, showHighlighting = false }: TeamOptionProps) {
  const enhancedTeam = showHighlighting ? (team as EnhancedTeam) : null;
  const hasSearchMatches = enhancedTeam?.search_matches && enhancedTeam.search_matches.length > 0;
  return (
    <CommandItem
      key={team.id}
      onSelect={onSelect}
      className="flex items-center gap-3 p-3 cursor-pointer"
    >
      {/* Team logo */}
      <div className="flex-shrink-0">
        {team.logo_url ? (
          <img
            src={team.logo_url}
            alt={`${team.display_name} logo`}
            className="h-8 w-8 rounded-full object-cover"
          />
        ) : (
          <div className="h-8 w-8 rounded-full bg-muted flex items-center justify-center text-xs font-bold">
            {team.abbreviation || team.name.charAt(0)}
          </div>
        )}
      </div>

      {/* Team info */}
      <div className="flex-1 min-w-0">
        <div className="font-medium text-sm truncate">
          {hasSearchMatches && enhancedTeam?.search_matches.find(m => m.field === 'display_name') ? (
            <span
              dangerouslySetInnerHTML={{
                __html: enhancedTeam.search_matches.find(m => m.field === 'display_name')?.highlighted || team.display_name
              }}
            />
          ) : (
            team.display_name
          )}
        </div>
        <div className="text-xs text-muted-foreground flex items-center gap-2">
          {team.league_name && (
            <>
              <span>{team.league_name}</span>
              <span>•</span>
            </>
          )}
          <span>{team.sport_name || 'Sport'}</span>
          {enhancedTeam?.relevance_score && (
            <>
              <span>•</span>
              <span className="text-primary font-medium">
                {Math.round(enhancedTeam.relevance_score)}% match
              </span>
            </>
          )}
        </div>
      </div>

      {/* Team colors */}
      {(team.primary_color || team.secondary_color) && (
        <div className="flex gap-1">
          {team.primary_color && (
            <div
              className="h-3 w-3 rounded-full border border-border"
              style={{ backgroundColor: team.primary_color }}
              title={`Primary: ${team.primary_color}`}
            />
          )}
          {team.secondary_color && (
            <div
              className="h-3 w-3 rounded-full border border-border"
              style={{ backgroundColor: team.secondary_color }}
              title={`Secondary: ${team.secondary_color}`}
            />
          )}
        </div>
      )}

      {/* Selection indicator */}
      {isSelected && (
        <Check className="h-4 w-4 text-primary" />
      )}
    </CommandItem>
  );
}

interface SelectedTeamChipProps {
  team: Team;
  onRemove: () => void;
  disabled?: boolean;
}

function SelectedTeamChip({ team, onRemove, disabled }: SelectedTeamChipProps) {
  return (
    <Badge
      variant="secondary"
      className="flex items-center gap-2 pl-2 pr-1 py-1 max-w-full"
    >
      {/* Team logo */}
      <div className="flex-shrink-0">
        {team.logo_url ? (
          <img
            src={team.logo_url}
            alt={`${team.display_name} logo`}
            className="h-4 w-4 rounded-full object-cover"
          />
        ) : (
          <div className="h-4 w-4 rounded-full bg-muted flex items-center justify-center text-xs font-bold">
            {team.abbreviation || team.name.charAt(0)}
          </div>
        )}
      </div>

      {/* Team name */}
      <span className="text-xs truncate flex-1 min-w-0">
        {team.display_name}
      </span>

      {/* Remove button */}
      {!disabled && (
        <button
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            onRemove();
          }}
          className="flex-shrink-0 rounded-full p-0.5 hover:bg-muted-foreground/20 transition-colors"
          aria-label={`Remove ${team.display_name}`}
        >
          <X className="h-3 w-3" />
        </button>
      )}
    </Badge>
  );
}

export function TeamSelector({
  selectedTeams,
  onTeamSelect,
  sportIds = [],
  leagueIds = [],
  multiSelect = true,
  placeholder = "Select teams...",
  searchPlaceholder = "Search for teams...",
  maxSelections = 10,
  disabled = false,
  error,
  className,
  showFilters = true,
  showSearchSuggestions = true,
  useEnhancedSearch = true,
}: TeamSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [filterValues, setFilterValues] = useState<FilterValues>({});
  const searchInputRef = useRef<HTMLInputElement>(null);

  // Extract filter IDs from filter values
  const selectedSportIds = Array.isArray(filterValues.sport) ? filterValues.sport : (filterValues.sport ? [filterValues.sport] : []);
  const selectedLeagueIds = Array.isArray(filterValues.league) ? filterValues.league : (filterValues.league ? [filterValues.league] : []);

  // Merge prop sportIds/leagueIds with filter values
  const allSportIds = [...sportIds, ...selectedSportIds];
  const allLeagueIds = [...leagueIds, ...selectedLeagueIds];

  const {
    searchQuery,
    setSearchQuery,
    isSearching,
    searchError,
    teams,
    enhancedTeams,
    totalTeams,
    searchMetadata,
    toggleTeamSelection: internalToggleTeamSelection,
    isTeamSelected,
    selectedTeams: internalSelectedTeams,
    setSelectedTeams: setInternalSelectedTeams,
  } = useTeamSelection({
    sportIds: allSportIds,
    leagueIds: allLeagueIds,
    initialSelectedTeams: selectedTeams,
    debounceMs: 300,
    pageSize: 50,
    useEnhancedSearch,
  });

  // Sync external selectedTeams with internal state when they change externally
  useEffect(() => {
    setInternalSelectedTeams(selectedTeams);
  }, [selectedTeams]); // Removed setInternalSelectedTeams to prevent infinite loop

  // Handle team selection with enhanced feedback
  const handleTeamSelect = (team: Team) => {
    if (disabled) return;

    if (multiSelect) {
      // Check max selections limit
      if (maxSelections && !isTeamSelected(team.id) && selectedTeams.length >= maxSelections) {
        toast.warning(`Maximum of ${maxSelections} teams allowed`, {
          description: "Please remove a team before adding another.",
          duration: 3000,
        });
        return;
      }

      const isCurrentlySelected = isTeamSelected(team.id);
      const newSelection = isCurrentlySelected
        ? selectedTeams.filter(t => t.id !== team.id)
        : [...selectedTeams, team];

      onTeamSelect(newSelection);

      // Show toast feedback for selections
      if (!isCurrentlySelected) {
        toast.success(`Added ${team.display_name}`, {
          description: `${newSelection.length}/${maxSelections || "∞"} teams selected`,
          duration: 2000,
        });

        // Warning when approaching limit
        if (maxSelections && newSelection.length >= maxSelections - 2) {
          toast.warning(`Approaching limit (${newSelection.length}/${maxSelections})`, {
            description: "You can select a few more teams.",
            duration: 3000,
          });
        }
      }
    } else {
      // Single select - close dropdown and select team
      onTeamSelect([team]);
      setIsOpen(false);
      toast.success(`Selected ${team.display_name}`);
    }
  };

  // Handle removing selected team
  const handleRemoveTeam = (teamId: string) => {
    if (disabled) return;
    const newSelection = selectedTeams.filter(t => t.id !== teamId);
    onTeamSelect(newSelection);
  };

  // Focus search input when dropdown opens
  useEffect(() => {
    if (isOpen && searchInputRef.current) {
      searchInputRef.current.focus();
    }
  }, [isOpen]);

  // Filter out already selected teams from search results
  const availableTeams = teams.filter(team => !isTeamSelected(team.id));
  const availableEnhancedTeams = enhancedTeams.filter(team => !isTeamSelected(team.id));

  // Create filter categories from available teams
  const filterCategories = showFilters ? createFilterCategoriesFromTeams(teams) : [];

  const hasMaxSelections = maxSelections && selectedTeams.length >= maxSelections;

  return (
    <div className={cn("space-y-3", className)}>
      {/* Selected teams display */}
      {selectedTeams.length > 0 && (
        <div className="space-y-2">
          <div className="text-sm font-medium text-foreground">
            Selected Teams ({selectedTeams.length}
            {maxSelections && ` / ${maxSelections}`})
          </div>
          <div className="flex flex-wrap gap-2">
            {selectedTeams.map((team) => (
              <SelectedTeamChip
                key={team.id}
                team={team}
                onRemove={() => handleRemoveTeam(team.id)}
                disabled={disabled}
              />
            ))}
          </div>
        </div>
      )}

      {/* Search and Filter Controls */}
      <div className="space-y-2">
        <div className="flex gap-2">
          {/* Search Input */}
          <div className="flex-1">
            <TeamSearchInput
              value={searchQuery}
              onChange={setSearchQuery}
              placeholder={searchPlaceholder}
              disabled={disabled}
              showSuggestions={showSearchSuggestions}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !isOpen) {
                  setIsOpen(true);
                }
              }}
            />
          </div>

          {/* Filter Dropdown */}
          {showFilters && filterCategories.length > 0 && (
            <div className="w-48">
              <TeamFilterDropdown
                categories={filterCategories}
                values={filterValues}
                onChange={setFilterValues}
                disabled={disabled}
                placeholder="Filter teams..."
              />
            </div>
          )}
        </div>

        {/* Search metadata display */}
        {searchMetadata && searchQuery && (
          <div className="text-xs text-muted-foreground">
            Found {searchMetadata.total_matches} results in {Math.round(searchMetadata.response_time_ms)}ms
          </div>
        )}
      </div>

      {/* Team selector dropdown */}
      <Popover open={isOpen} onOpenChange={setIsOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            role="combobox"
            aria-expanded={isOpen}
            aria-label="Select teams"
            disabled={disabled || (hasMaxSelections && multiSelect)}
            className={cn(
              "w-full justify-between",
              error && "border-destructive",
              hasMaxSelections && "opacity-60"
            )}
          >
            <span className="truncate">
              {hasMaxSelections
                ? "Maximum teams selected"
                : selectedTeams.length > 0
                ? `${selectedTeams.length} team${selectedTeams.length === 1 ? '' : 's'} selected`
                : placeholder
              }
            </span>
            <ChevronDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
          </Button>
        </PopoverTrigger>

        <PopoverContent className="w-full p-0" align="start">
          <Command>

            <CommandList className="max-h-[300px]">
              {/* Loading state */}
              {isSearching && (
                <div className="py-6 text-center">
                  <div className="inline-flex items-center gap-2 text-sm text-muted-foreground">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary" />
                    Searching teams...
                  </div>
                </div>
              )}

              {/* Error state */}
              {searchError && (
                <div className="py-6 px-3">
                  <div className="flex items-center gap-2 text-sm text-destructive">
                    <AlertCircle className="h-4 w-4" />
                    <span>Failed to search teams. Please try again.</span>
                  </div>
                </div>
              )}

              {/* No results */}
              {!isSearching && !searchError && availableTeams.length === 0 && searchQuery.length >= 2 && (
                <CommandEmpty>
                  No teams found for "{searchQuery}".
                </CommandEmpty>
              )}

              {/* Empty state when no search */}
              {!isSearching && !searchError && searchQuery.length < 2 && sportIds.length === 0 && (
                <div className="py-6 text-center text-sm text-muted-foreground">
                  Type to search for teams...
                </div>
              )}

              {/* No sports selected */}
              {!isSearching && !searchError && searchQuery.length < 2 && sportIds.length === 0 && (
                <div className="py-6 text-center text-sm text-muted-foreground">
                  Select sports first to see teams.
                </div>
              )}

              {/* Teams list */}
              {!isSearching && !searchError && availableTeams.length > 0 && (
                <CommandGroup>
                  {(useEnhancedSearch ? availableEnhancedTeams : availableTeams).map((team) => (
                    <TeamOption
                      key={team.id}
                      team={team}
                      isSelected={isTeamSelected(team.id)}
                      onSelect={() => handleTeamSelect(team)}
                      multiSelect={multiSelect}
                      showHighlighting={useEnhancedSearch && !!searchQuery}
                    />
                  ))}
                </CommandGroup>
              )}

              {/* Results info */}
              {!isSearching && !searchError && totalTeams > 0 && (
                <div className="border-t px-3 py-2 text-xs text-muted-foreground">
                  Showing {availableTeams.length} of {totalTeams} teams
                </div>
              )}
            </CommandList>
          </Command>
        </PopoverContent>
      </Popover>

      {/* Error message */}
      {error && (
        <div className="flex items-center gap-2 text-sm text-destructive">
          <AlertCircle className="h-4 w-4" />
          <span>{error}</span>
        </div>
      )}

      {/* Helper text */}
      {!error && (
        <div className="text-xs text-muted-foreground">
          {multiSelect ? (
            <>
              {hasMaxSelections
                ? `Maximum of ${maxSelections} teams selected.`
                : maxSelections
                ? `Select up to ${maxSelections} teams.`
                : 'Select multiple teams to personalize your content.'
              }
            </>
          ) : (
            'Select a team to continue.'
          )}
        </div>
      )}
    </div>
  );
}

export default TeamSelector;