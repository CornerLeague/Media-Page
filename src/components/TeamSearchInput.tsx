import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Search, X, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Command, CommandEmpty, CommandGroup, CommandItem, CommandList } from '@/components/ui/command';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { useQuery } from '@tanstack/react-query';
import { apiClient, type SearchSuggestion } from '@/lib/api-client';

interface TeamSearchInputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  className?: string;
  showSuggestions?: boolean;
  debounceMs?: number;
  onKeyDown?: (e: React.KeyboardEvent<HTMLInputElement>) => void;
}

export function TeamSearchInput({
  value,
  onChange,
  placeholder = "Search for teams...",
  disabled = false,
  className,
  showSuggestions = true,
  debounceMs = 300,
  onKeyDown,
}: TeamSearchInputProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [debouncedValue, setDebouncedValue] = useState(value);
  const inputRef = useRef<HTMLInputElement>(null);
  const [isFocused, setIsFocused] = useState(false);

  // Debounce the search value
  useEffect(() => {
    const timeout = setTimeout(() => {
      setDebouncedValue(value);
    }, debounceMs);

    return () => clearTimeout(timeout);
  }, [value, debounceMs]);

  // Fetch search suggestions
  const {
    data: suggestionsData,
    isLoading: isLoadingSuggestions,
    error: suggestionsError,
  } = useQuery({
    queryKey: ['teams', 'search-suggestions', debouncedValue],
    queryFn: () => apiClient.getSearchSuggestions(debouncedValue),
    enabled: showSuggestions && debouncedValue.length >= 2 && isFocused,
    staleTime: 10 * 60 * 1000, // 10 minutes
  });

  const suggestions = suggestionsData?.suggestions || [];
  const shouldShowSuggestions = showSuggestions && isFocused && value.length >= 2 && suggestions.length > 0;

  // Handle input changes
  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    onChange(newValue);

    // Show suggestions dropdown if we have input and suggestions are enabled
    if (showSuggestions && newValue.length >= 2) {
      setIsOpen(true);
    } else {
      setIsOpen(false);
    }
  }, [onChange, showSuggestions]);

  // Handle clear button
  const handleClear = useCallback(() => {
    onChange('');
    setIsOpen(false);
    inputRef.current?.focus();
  }, [onChange]);

  // Handle suggestion selection
  const handleSuggestionSelect = useCallback((suggestion: SearchSuggestion) => {
    onChange(suggestion.suggestion);
    setIsOpen(false);
    inputRef.current?.focus();
  }, [onChange]);

  // Handle keyboard events
  const handleKeyDown = useCallback((e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Escape') {
      if (value) {
        handleClear();
      } else {
        inputRef.current?.blur();
      }
      e.preventDefault();
    } else if (e.key === 'Enter' && !isOpen) {
      // Trigger search on Enter if suggestions aren't open
      e.preventDefault();
    }

    // Call parent onKeyDown handler if provided
    onKeyDown?.(e);
  }, [value, handleClear, isOpen, onKeyDown]);

  // Handle focus events
  const handleFocus = useCallback(() => {
    setIsFocused(true);
    if (showSuggestions && value.length >= 2) {
      setIsOpen(true);
    }
  }, [showSuggestions, value.length]);

  const handleBlur = useCallback(() => {
    setIsFocused(false);
    // Delay closing to allow for suggestion clicks
    setTimeout(() => setIsOpen(false), 150);
  }, []);

  return (
    <div className={cn("relative", className)}>
      <Popover open={isOpen && shouldShowSuggestions} onOpenChange={setIsOpen}>
        <PopoverTrigger asChild>
          <div className="relative">
            {/* Search Icon */}
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />

            {/* Input Field */}
            <Input
              ref={inputRef}
              type="text"
              placeholder={placeholder}
              value={value}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              onFocus={handleFocus}
              onBlur={handleBlur}
              disabled={disabled}
              className={cn(
                "pl-9 pr-9",
                value && "pr-9" // Make room for clear button
              )}
            />

            {/* Loading Indicator */}
            {isLoadingSuggestions && value.length >= 2 && (
              <Loader2 className="absolute right-8 top-1/2 h-4 w-4 -translate-y-1/2 animate-spin text-muted-foreground" />
            )}

            {/* Clear Button */}
            {value && !disabled && (
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={handleClear}
                className="absolute right-1 top-1/2 h-6 w-6 -translate-y-1/2 p-0 hover:bg-transparent"
                tabIndex={-1}
              >
                <X className="h-3 w-3" />
                <span className="sr-only">Clear search</span>
              </Button>
            )}
          </div>
        </PopoverTrigger>

        {/* Suggestions Dropdown */}
        <PopoverContent
          className="w-full p-0"
          align="start"
          side="bottom"
          sideOffset={4}
        >
          <Command>
            <CommandList className="max-h-[200px]">
              {suggestions.length === 0 && !isLoadingSuggestions && (
                <CommandEmpty>No suggestions found.</CommandEmpty>
              )}

              {suggestions.length > 0 && (
                <CommandGroup>
                  {suggestions.map((suggestion, index) => (
                    <CommandItem
                      key={`${suggestion.suggestion}-${index}`}
                      onSelect={() => handleSuggestionSelect(suggestion)}
                      className="flex items-center justify-between p-3 cursor-pointer"
                    >
                      <div className="flex items-center gap-2">
                        <Search className="h-4 w-4 text-muted-foreground" />
                        <div>
                          <div className="font-medium text-sm">{suggestion.suggestion}</div>
                          <div className="text-xs text-muted-foreground">
                            {suggestion.team_count} team{suggestion.team_count !== 1 ? 's' : ''}
                            {suggestion.preview_teams.length > 0 && (
                              <span> • {suggestion.preview_teams.slice(0, 2).join(', ')}</span>
                            )}
                            {suggestion.preview_teams.length > 2 && (
                              <span> +{suggestion.preview_teams.length - 2} more</span>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="text-xs text-muted-foreground capitalize">
                        {suggestion.type.replace('_', ' ')}
                      </div>
                    </CommandItem>
                  ))}
                </CommandGroup>
              )}
            </CommandList>
          </Command>
        </PopoverContent>
      </Popover>
    </div>
  );
}

export default TeamSearchInput;