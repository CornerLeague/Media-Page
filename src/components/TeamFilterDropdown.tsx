import React, { useState, useCallback, useMemo } from 'react';
import { Filter, X, Check } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { Command, CommandEmpty, CommandGroup, CommandItem, CommandList } from '@/components/ui/command';

export interface FilterOption {
  id: string;
  name: string;
  count?: number;
}

export interface FilterCategory {
  id: string;
  name: string;
  options: FilterOption[];
  multiSelect?: boolean;
}

export interface FilterValues {
  [categoryId: string]: string | string[];
}

interface TeamFilterDropdownProps {
  categories: FilterCategory[];
  values: FilterValues;
  onChange: (values: FilterValues) => void;
  disabled?: boolean;
  className?: string;
  placeholder?: string;
  showClearAll?: boolean;
}

export function TeamFilterDropdown({
  categories,
  values,
  onChange,
  disabled = false,
  className,
  placeholder = "Filter teams...",
  showClearAll = true,
}: TeamFilterDropdownProps) {
  const [isOpen, setIsOpen] = useState(false);

  // Calculate total active filters
  const activeFiltersCount = useMemo(() => {
    return Object.values(values).reduce((count, value) => {
      if (Array.isArray(value)) {
        return count + value.length;
      }
      return value ? count + 1 : count;
    }, 0);
  }, [values]);

  // Handle filter changes
  const handleFilterChange = useCallback((categoryId: string, optionId: string, multiSelect = false) => {
    const currentValue = values[categoryId];

    if (multiSelect) {
      const currentArray = Array.isArray(currentValue) ? currentValue : [];
      const newArray = currentArray.includes(optionId)
        ? currentArray.filter(id => id !== optionId)
        : [...currentArray, optionId];

      onChange({
        ...values,
        [categoryId]: newArray,
      });
    } else {
      onChange({
        ...values,
        [categoryId]: currentValue === optionId ? '' : optionId,
      });
    }
  }, [values, onChange]);

  // Handle clear all filters
  const handleClearAll = useCallback(() => {
    const clearedValues: FilterValues = {};
    categories.forEach(category => {
      clearedValues[category.id] = category.multiSelect ? [] : '';
    });
    onChange(clearedValues);
  }, [categories, onChange]);

  // Check if an option is selected
  const isOptionSelected = useCallback((categoryId: string, optionId: string) => {
    const value = values[categoryId];
    if (Array.isArray(value)) {
      return value.includes(optionId);
    }
    return value === optionId;
  }, [values]);

  // Get display text for active filters
  const getActiveFiltersText = useCallback(() => {
    const activeFilters: string[] = [];

    categories.forEach(category => {
      const value = values[category.id];
      if (Array.isArray(value) && value.length > 0) {
        const selectedOptions = category.options.filter(opt => value.includes(opt.id));
        activeFilters.push(...selectedOptions.map(opt => opt.name));
      } else if (value) {
        const selectedOption = category.options.find(opt => opt.id === value);
        if (selectedOption) {
          activeFilters.push(selectedOption.name);
        }
      }
    });

    return activeFilters;
  }, [categories, values]);

  const activeFiltersText = getActiveFiltersText();

  return (
    <div className={cn("relative", className)}>
      <Popover open={isOpen} onOpenChange={setIsOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            role="combobox"
            aria-expanded={isOpen}
            disabled={disabled}
            className={cn(
              "w-full justify-between",
              activeFiltersCount > 0 && "border-primary"
            )}
          >
            <div className="flex items-center gap-2">
              <Filter className="h-4 w-4" />
              <span className="truncate">
                {activeFiltersCount > 0
                  ? `${activeFiltersCount} filter${activeFiltersCount === 1 ? '' : 's'} applied`
                  : placeholder
                }
              </span>
            </div>
            {activeFiltersCount > 0 && (
              <Badge variant="secondary" className="ml-2 h-5 px-1.5 text-xs">
                {activeFiltersCount}
              </Badge>
            )}
          </Button>
        </PopoverTrigger>

        <PopoverContent className="w-full p-4" align="start">
          <div className="space-y-4">
            {/* Header with Clear All */}
            <div className="flex items-center justify-between">
              <h4 className="font-medium text-sm">Filter Teams</h4>
              {showClearAll && activeFiltersCount > 0 && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleClearAll}
                  className="h-auto p-1 text-xs text-muted-foreground hover:text-foreground"
                >
                  Clear all
                </Button>
              )}
            </div>

            {/* Active Filters Display */}
            {activeFiltersText.length > 0 && (
              <div className="space-y-2">
                <div className="text-xs font-medium text-muted-foreground">Active filters:</div>
                <div className="flex flex-wrap gap-1">
                  {activeFiltersText.map((filter, index) => (
                    <Badge key={index} variant="secondary" className="text-xs">
                      {filter}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Filter Categories */}
            {categories.map((category) => (
              <div key={category.id} className="space-y-2">
                <div className="text-sm font-medium">{category.name}</div>

                {category.multiSelect ? (
                  // Multi-select with checkboxes
                  <div className="space-y-1">
                    {category.options.map((option) => (
                      <div
                        key={option.id}
                        className="flex items-center space-x-2 cursor-pointer"
                        onClick={() => handleFilterChange(category.id, option.id, true)}
                      >
                        <div className={cn(
                          "flex h-4 w-4 items-center justify-center rounded border",
                          isOptionSelected(category.id, option.id)
                            ? "bg-primary border-primary text-primary-foreground"
                            : "border-muted-foreground"
                        )}>
                          {isOptionSelected(category.id, option.id) && (
                            <Check className="h-3 w-3" />
                          )}
                        </div>
                        <div className="flex-1 text-sm">
                          {option.name}
                          {option.count && (
                            <span className="ml-1 text-muted-foreground">({option.count})</span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  // Single select dropdown
                  <Select
                    value={values[category.id] as string || ''}
                    onValueChange={(value) => handleFilterChange(category.id, value, false)}
                  >
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder={`Select ${category.name.toLowerCase()}...`} />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">All {category.name}</SelectItem>
                      {category.options.map((option) => (
                        <SelectItem key={option.id} value={option.id}>
                          {option.name}
                          {option.count && (
                            <span className="ml-1 text-muted-foreground">({option.count})</span>
                          )}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                )}
              </div>
            ))}

            {/* No categories message */}
            {categories.length === 0 && (
              <div className="text-center text-sm text-muted-foreground py-4">
                No filter options available
              </div>
            )}
          </div>
        </PopoverContent>
      </Popover>
    </div>
  );
}

// Utility function to create filter categories from team data
export function createFilterCategoriesFromTeams(teams: Array<{
  sport_id?: string;
  sport_name?: string;
  league_id?: string;
  league_name?: string;
}>): FilterCategory[] {
  const categories: FilterCategory[] = [];

  // Extract unique sports
  const sportsMap = new Map<string, { name: string; count: number }>();
  teams.forEach(team => {
    if (team.sport_id && team.sport_name) {
      const existing = sportsMap.get(team.sport_id);
      if (existing) {
        existing.count++;
      } else {
        sportsMap.set(team.sport_id, { name: team.sport_name, count: 1 });
      }
    }
  });

  if (sportsMap.size > 1) {
    categories.push({
      id: 'sport',
      name: 'Sport',
      options: Array.from(sportsMap.entries()).map(([id, { name, count }]) => ({
        id,
        name,
        count,
      })),
      multiSelect: true,
    });
  }

  // Extract unique leagues
  const leaguesMap = new Map<string, { name: string; count: number }>();
  teams.forEach(team => {
    if (team.league_id && team.league_name) {
      const existing = leaguesMap.get(team.league_id);
      if (existing) {
        existing.count++;
      } else {
        leaguesMap.set(team.league_id, { name: team.league_name, count: 1 });
      }
    }
  });

  if (leaguesMap.size > 1) {
    categories.push({
      id: 'league',
      name: 'League',
      options: Array.from(leaguesMap.entries()).map(([id, { name, count }]) => ({
        id,
        name,
        count,
      })),
      multiSelect: true,
    });
  }

  return categories;
}

export default TeamFilterDropdown;