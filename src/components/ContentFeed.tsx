/**
 * ContentFeed Component
 *
 * Enhanced sports content feed with personalization based on user preferences.
 * Filters content by sport preferences, content frequency, and news type preferences.
 */

import { useState } from "react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { NewsCard } from "./NewsCard";
import { SportsFeedCard } from "./SportsFeedCard";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import {
  ChevronDown,
  Filter,
  Clock,
  Star,
  TrendingUp,
  ExternalLink,
} from "lucide-react";
import { type PersonalizedFeedData } from "@/hooks/usePersonalizedFeed";
import { type UserPreferences } from "@/hooks/useAuth";

interface ContentFeedProps {
  personalizedData: PersonalizedFeedData;
  userPreferences: UserPreferences;
  onNewsClick?: (article: any) => void;
  onSportsItemClick?: (item: any) => void;
}

type ContentFilter = 'all' | 'teams' | 'sports' | 'trending';
type ContentSort = 'recent' | 'priority' | 'relevance';

export function ContentFeed({
  personalizedData,
  userPreferences,
  onNewsClick,
  onSportsItemClick
}: ContentFeedProps) {
  const [selectedFilter, setSelectedFilter] = useState<ContentFilter>('all');
  const [selectedSort, setSelectedSort] = useState<ContentSort>('priority');
  const [selectedNewsType, setSelectedNewsType] = useState<string>('all');

  const { sportsFeed, aggregatedNews, isLoading, error } = personalizedData;

  // Get enabled news types for filtering
  const enabledNewsTypes = userPreferences.preferences.newsTypes
    .filter(nt => nt.enabled)
    .sort((a, b) => a.priority - b.priority);

  // Filter content based on selections
  const filteredContent = getFilteredContent({
    sportsFeed,
    aggregatedNews,
    filter: selectedFilter,
    sort: selectedSort,
    newsType: selectedNewsType,
    userPreferences,
  });

  const handleNewsClick = (article: any) => {
    onNewsClick?.(article);
    if (article.url) {
      window.open(article.url, '_blank', 'noopener,noreferrer');
    }
  };

  const handleSportsItemClick = (item: any) => {
    onSportsItemClick?.(item);
    if (item.externalUrl) {
      window.open(item.externalUrl, '_blank', 'noopener,noreferrer');
    }
  };

  return (
    <section className="w-full">
      <div className="px-4 sm:px-6 md:px-8 lg:px-12">
        {/* Header with Filters */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div className="flex items-center gap-4">
            <h2 className="font-display font-semibold text-xl text-foreground">
              Personalized Feed
            </h2>
            <Badge variant="secondary" className="font-body text-xs">
              {userPreferences.preferences.contentFrequency} mode
            </Badge>
          </div>

          <div className="flex items-center gap-2">
            {/* Content Filter */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm" className="font-body">
                  <Filter className="w-4 h-4 mr-2" />
                  {getFilterLabel(selectedFilter)}
                  <ChevronDown className="w-4 h-4 ml-2" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => setSelectedFilter('all')}>
                  All Content
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setSelectedFilter('teams')}>
                  Your Teams
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setSelectedFilter('sports')}>
                  Your Sports
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setSelectedFilter('trending')}>
                  Trending
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>

            {/* Sort Options */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm" className="font-body">
                  <Clock className="w-4 h-4 mr-2" />
                  {getSortLabel(selectedSort)}
                  <ChevronDown className="w-4 h-4 ml-2" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => setSelectedSort('priority')}>
                  By Priority
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setSelectedSort('recent')}>
                  Most Recent
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setSelectedSort('relevance')}>
                  Most Relevant
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>

            {/* News Type Filter */}
            {enabledNewsTypes.length > 1 && (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" size="sm" className="font-body">
                    {getNewsTypeLabel(selectedNewsType)}
                    <ChevronDown className="w-4 h-4 ml-2" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem onClick={() => setSelectedNewsType('all')}>
                    All News Types
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  {enabledNewsTypes.map((newsType) => (
                    <DropdownMenuItem
                      key={newsType.type}
                      onClick={() => setSelectedNewsType(newsType.type)}
                    >
                      {capitalizeFirst(newsType.type)}
                    </DropdownMenuItem>
                  ))}
                </DropdownMenuContent>
              </DropdownMenu>
            )}
          </div>
        </div>

        {/* Content Frequency Info */}
        <ContentFrequencyInfo frequency={userPreferences.preferences.contentFrequency} />

        {/* Loading State */}
        {isLoading && (
          <div className="space-y-6">
            <ContentLoadingSkeleton />
          </div>
        )}

        {/* Error State */}
        {error && (
          <Card className="border-red-200 dark:border-red-800">
            <CardContent className="p-6">
              <div className="text-red-600 dark:text-red-400">
                <p className="font-medium mb-2">Unable to load personalized content</p>
                <p className="text-sm text-red-700 dark:text-red-500">{error.message}</p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Content Feed */}
        {!isLoading && !error && (
          <div className="space-y-8">
            {/* Featured Team News */}
            {filteredContent.teamNews.length > 0 && (
              <div>
                <h3 className="font-display font-semibold text-lg text-foreground mb-4 flex items-center gap-2">
                  <Star className="w-5 h-5 text-yellow-500" />
                  Team Updates
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {filteredContent.teamNews.slice(0, 6).map((article) => (
                    <NewsCard
                      key={`team-${article.id}`}
                      article={article}
                      onClick={() => handleNewsClick(article)}
                      showTeamBadge={true}
                      teamName={article.teamName}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Sports Feed */}
            {filteredContent.sportsContent.length > 0 && (
              <div>
                <h3 className="font-display font-semibold text-lg text-foreground mb-4 flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-blue-500" />
                  Sports Headlines
                </h3>
                <div className="overflow-x-auto scrollbar-hide">
                  <div className="flex gap-4 pb-4">
                    {filteredContent.sportsContent.slice(0, 8).map((item) => (
                      <SportsFeedCard
                        key={`sports-${item.id}`}
                        item={item}
                        onClick={() => handleSportsItemClick(item)}
                      />
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Combined Feed */}
            {filteredContent.combinedFeed.length > 0 && (
              <div>
                <h3 className="font-display font-semibold text-lg text-foreground mb-4">
                  All Updates
                </h3>
                <div className="space-y-4">
                  {filteredContent.combinedFeed.slice(0, 12).map((item, index) => (
                    <ContentFeedItem
                      key={`combined-${item.id}-${index}`}
                      item={item}
                      onClick={() => item.type === 'news' ? handleNewsClick(item) : handleSportsItemClick(item)}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* No Content State */}
            {filteredContent.teamNews.length === 0 &&
             filteredContent.sportsContent.length === 0 &&
             filteredContent.combinedFeed.length === 0 && (
              <Card>
                <CardContent className="p-8 text-center">
                  <p className="text-muted-foreground font-body mb-4">
                    No content available for your current filters
                  </p>
                  <Button
                    variant="outline"
                    onClick={() => {
                      setSelectedFilter('all');
                      setSelectedNewsType('all');
                    }}
                  >
                    Clear Filters
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </div>
    </section>
  );
}

// Helper Components

function ContentFrequencyInfo({ frequency }: { frequency: string }) {
  const getFrequencyDescription = (freq: string) => {
    switch (freq) {
      case 'minimal':
        return 'Showing essential updates only';
      case 'standard':
        return 'Showing regular updates and highlights';
      case 'comprehensive':
        return 'Showing all available content';
      default:
        return 'Personalized content feed';
    }
  };

  return (
    <div className="bg-muted/30 rounded-lg p-4 mb-6">
      <p className="text-sm text-muted-foreground font-body">
        {getFrequencyDescription(frequency)}
      </p>
    </div>
  );
}

function ContentLoadingSkeleton() {
  return (
    <div className="space-y-6">
      {Array.from({ length: 3 }).map((_, sectionIndex) => (
        <div key={sectionIndex} className="space-y-4">
          <Skeleton className="h-6 w-40" />
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Array.from({ length: 3 }).map((_, itemIndex) => (
              <Card key={itemIndex}>
                <CardContent className="p-4">
                  <Skeleton className="h-32 w-full mb-3" />
                  <Skeleton className="h-4 w-3/4 mb-2" />
                  <Skeleton className="h-3 w-1/2" />
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

function ContentFeedItem({ item, onClick }: { item: any; onClick: () => void }) {
  return (
    <Card className="cursor-pointer hover:shadow-md transition-shadow" onClick={onClick}>
      <CardContent className="p-4">
        <div className="flex items-start gap-4">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <Badge variant={item.type === 'news' ? 'default' : 'secondary'} className="text-xs">
                {item.type === 'news' ? item.category : 'Sports'}
              </Badge>
              {item.teamName && (
                <Badge variant="outline" className="text-xs">
                  {item.teamName}
                </Badge>
              )}
            </div>
            <h4 className="font-medium text-sm mb-2 line-clamp-2">{item.title}</h4>
            {item.summary && (
              <p className="text-xs text-muted-foreground line-clamp-2 mb-2">{item.summary}</p>
            )}
            <div className="flex items-center justify-between">
              <span className="text-xs text-muted-foreground">
                {new Date(item.published_at || item.publishedAt).toLocaleDateString()}
              </span>
              <ExternalLink className="w-3 h-3 text-muted-foreground" />
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// Helper Functions

function getFilterLabel(filter: ContentFilter): string {
  switch (filter) {
    case 'all': return 'All Content';
    case 'teams': return 'Your Teams';
    case 'sports': return 'Your Sports';
    case 'trending': return 'Trending';
    default: return 'Filter';
  }
}

function getSortLabel(sort: ContentSort): string {
  switch (sort) {
    case 'recent': return 'Recent';
    case 'priority': return 'Priority';
    case 'relevance': return 'Relevant';
    default: return 'Sort';
  }
}

function getNewsTypeLabel(newsType: string): string {
  return newsType === 'all' ? 'All Types' : capitalizeFirst(newsType);
}

function capitalizeFirst(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

function getFilteredContent({
  sportsFeed,
  aggregatedNews,
  filter,
  sort,
  newsType,
  userPreferences,
}: {
  sportsFeed: any[];
  aggregatedNews: any[];
  filter: ContentFilter;
  sort: ContentSort;
  newsType: string;
  userPreferences: UserPreferences;
}) {
  // Filter team news
  let teamNews = [...aggregatedNews];
  if (newsType !== 'all') {
    teamNews = teamNews.filter(news => news.category === newsType);
  }

  // Filter sports content
  let sportsContent = [...sportsFeed];
  if (filter === 'teams') {
    const userTeamIds = userPreferences.teams.map(t => t.teamId);
    sportsContent = sportsContent.filter(item =>
      item.teams?.some((teamId: string) => userTeamIds.includes(teamId))
    );
  } else if (filter === 'sports') {
    const userSportIds = userPreferences.sports.map(s => s.sportId);
    sportsContent = sportsContent.filter(item =>
      item.sports?.some((sportId: string) => userSportIds.includes(sportId))
    );
  }

  // Create combined feed
  const combinedFeed = [
    ...teamNews.map(news => ({ ...news, type: 'news' })),
    ...sportsContent.map(sports => ({ ...sports, type: 'sports' }))
  ];

  // Sort content
  const sortContent = (content: any[]) => {
    switch (sort) {
      case 'recent':
        return content.sort((a, b) =>
          new Date(b.published_at || b.publishedAt).getTime() -
          new Date(a.published_at || a.publishedAt).getTime()
        );
      case 'priority':
        return content.sort((a, b) => (b.priority || 0) - (a.priority || 0));
      case 'relevance':
        return content.sort((a, b) => {
          const aRelevance = calculateRelevance(a, userPreferences);
          const bRelevance = calculateRelevance(b, userPreferences);
          return bRelevance - aRelevance;
        });
      default:
        return content;
    }
  };

  return {
    teamNews: sortContent(teamNews),
    sportsContent: sortContent(sportsContent),
    combinedFeed: sortContent(combinedFeed),
  };
}

function calculateRelevance(item: any, userPreferences: UserPreferences): number {
  let relevance = 0;

  // Team relevance
  const userTeamIds = userPreferences.teams.map(t => t.teamId);
  if (item.teamId && userTeamIds.includes(item.teamId)) {
    const team = userPreferences.teams.find(t => t.teamId === item.teamId);
    relevance += (team?.affinityScore || 0) * 10;
  }

  // Sport relevance
  const userSportIds = userPreferences.sports.map(s => s.sportId);
  if (item.sports?.some((sportId: string) => userSportIds.includes(sportId))) {
    relevance += 5;
  }

  // News type preference
  const newsTypePref = userPreferences.preferences.newsTypes.find(nt => nt.type === item.category);
  if (newsTypePref?.enabled) {
    relevance += (6 - newsTypePref.priority);
  }

  return relevance;
}

export default ContentFeed;