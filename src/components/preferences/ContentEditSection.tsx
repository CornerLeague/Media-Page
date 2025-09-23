/**
 * ContentEditSection Component
 *
 * Content preferences editing component for news types, notifications, and frequency settings.
 * Based on the existing PreferencesStep from onboarding.
 */

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Save, Bell, Newspaper, AlertCircle, Settings2 } from 'lucide-react';
import { type ContentPreferences } from '@/hooks/usePreferences';
import { cn } from '@/lib/utils';

interface ContentEditSectionProps {
  preferences: ContentPreferences | null;
  onPreferencesChange: (preferences: ContentPreferences) => void;
  onSave: () => Promise<void>;
  isSaving: boolean;
  error: Error | null;
}

const NEWS_TYPES = [
  { id: 'injuries', label: 'Injuries & Health', description: 'Player injuries, recovery updates, and health reports' },
  { id: 'trades', label: 'Trades & Transfers', description: 'Player trades, free agency, and roster moves' },
  { id: 'roster', label: 'Roster Changes', description: 'Lineup changes, starting rotations, and depth chart updates' },
  { id: 'scores', label: 'Scores & Results', description: 'Game results, standings, and statistics' },
  { id: 'analysis', label: 'Analysis & Opinion', description: 'Expert analysis, predictions, and commentary' },
  { id: 'news', label: 'General News', description: 'Breaking news, announcements, and league updates' },
];

const FREQUENCY_OPTIONS = [
  { value: 'minimal', label: 'Minimal', description: 'Only the most important updates' },
  { value: 'standard', label: 'Standard', description: 'Regular updates and news' },
  { value: 'comprehensive', label: 'Comprehensive', description: 'All available content and updates' },
];

export function ContentEditSection({
  preferences,
  onPreferencesChange,
  onSave,
  isSaving,
  error,
}: ContentEditSectionProps) {
  const [localPreferences, setLocalPreferences] = useState<ContentPreferences | null>(null);

  // Initialize local state
  useEffect(() => {
    if (preferences) {
      setLocalPreferences(preferences);
    }
  }, [preferences]);

  if (!localPreferences) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Content Preferences</CardTitle>
          <CardDescription>Loading preferences...</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  const handleNewsTypeToggle = (typeId: string, enabled: boolean) => {
    const updatedNewsTypes = localPreferences.newsTypes.map(newsType =>
      newsType.type === typeId ? { ...newsType, enabled } : newsType
    );

    const updatedPreferences = {
      ...localPreferences,
      newsTypes: updatedNewsTypes,
    };

    setLocalPreferences(updatedPreferences);
    onPreferencesChange(updatedPreferences);
  };

  const handleNewsTypePriority = (typeId: string, priority: number) => {
    const updatedNewsTypes = localPreferences.newsTypes.map(newsType =>
      newsType.type === typeId ? { ...newsType, priority } : newsType
    );

    const updatedPreferences = {
      ...localPreferences,
      newsTypes: updatedNewsTypes,
    };

    setLocalPreferences(updatedPreferences);
    onPreferencesChange(updatedPreferences);
  };

  const handleNotificationToggle = (key: keyof ContentPreferences['notifications'], enabled: boolean) => {
    const updatedPreferences = {
      ...localPreferences,
      notifications: {
        ...localPreferences.notifications,
        [key]: enabled,
      },
    };

    setLocalPreferences(updatedPreferences);
    onPreferencesChange(updatedPreferences);
  };

  const handleFrequencyChange = (frequency: ContentPreferences['contentFrequency']) => {
    const updatedPreferences = {
      ...localPreferences,
      contentFrequency: frequency,
    };

    setLocalPreferences(updatedPreferences);
    onPreferencesChange(updatedPreferences);
  };

  const enabledNewsTypesCount = localPreferences.newsTypes.filter(nt => nt.enabled).length;
  const enabledNotificationsCount = Object.values(localPreferences.notifications).filter(Boolean).length;

  return (
    <div className="space-y-6">
      {/* Content Frequency */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Settings2 className="h-5 w-5" />
                Content Frequency
              </CardTitle>
              <CardDescription>
                How much content would you like to receive?
              </CardDescription>
            </div>
            <Badge variant="outline">{localPreferences.contentFrequency}</Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {FREQUENCY_OPTIONS.map(option => (
              <div
                key={option.value}
                className={cn(
                  'border rounded-lg p-4 cursor-pointer transition-all',
                  localPreferences.contentFrequency === option.value
                    ? 'border-primary bg-primary/5'
                    : 'border-border hover:border-primary/50'
                )}
                onClick={() => handleFrequencyChange(option.value as ContentPreferences['contentFrequency'])}
              >
                <div className="flex items-center space-x-3">
                  <div className={cn(
                    'w-4 h-4 rounded-full border-2 flex items-center justify-center',
                    localPreferences.contentFrequency === option.value
                      ? 'border-primary bg-primary'
                      : 'border-muted-foreground'
                  )}>
                    {localPreferences.contentFrequency === option.value && (
                      <div className="w-2 h-2 rounded-full bg-white" />
                    )}
                  </div>
                  <div className="flex-1">
                    <h4 className="font-semibold">{option.label}</h4>
                    <p className="text-sm text-muted-foreground">{option.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* News Types */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Newspaper className="h-5 w-5" />
                News Types
                <Badge variant="outline">{enabledNewsTypesCount} enabled</Badge>
              </CardTitle>
              <CardDescription>
                Choose which types of content you want to see
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
                  Save Content
                </>
              )}
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {error && (
            <Alert variant="destructive" className="mb-4">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error.message}</AlertDescription>
            </Alert>
          )}

          <div className="space-y-4">
            {NEWS_TYPES.map(newsType => {
              const preference = localPreferences.newsTypes.find(nt => nt.type === newsType.id);
              const isEnabled = preference?.enabled || false;
              const priority = preference?.priority || 5;

              return (
                <div key={newsType.id} className="border rounded-lg p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <h4 className="font-semibold">{newsType.label}</h4>
                        {isEnabled && (
                          <Badge variant="secondary" className="text-xs">
                            Priority {priority}
                          </Badge>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground">
                        {newsType.description}
                      </p>
                    </div>
                    <Switch
                      checked={isEnabled}
                      onCheckedChange={(checked) => handleNewsTypeToggle(newsType.id, checked)}
                    />
                  </div>

                  {isEnabled && (
                    <div className="pt-2 border-t">
                      <div className="flex items-center justify-between">
                        <Label className="text-sm">Priority Level:</Label>
                        <Select
                          value={priority.toString()}
                          onValueChange={(value) => handleNewsTypePriority(newsType.id, parseInt(value))}
                        >
                          <SelectTrigger className="w-[120px]">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="1">1 - Lowest</SelectItem>
                            <SelectItem value="2">2 - Low</SelectItem>
                            <SelectItem value="3">3 - Medium</SelectItem>
                            <SelectItem value="4">4 - High</SelectItem>
                            <SelectItem value="5">5 - Highest</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Notifications */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="h-5 w-5" />
            Notifications
            <Badge variant="outline">{enabledNotificationsCount} enabled</Badge>
          </CardTitle>
          <CardDescription>
            Configure how you want to be notified about updates
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <Label className="font-semibold">Push Notifications</Label>
                <p className="text-sm text-muted-foreground">
                  Receive push notifications on your device
                </p>
              </div>
              <Switch
                checked={localPreferences.notifications.push}
                onCheckedChange={(checked) => handleNotificationToggle('push', checked)}
              />
            </div>

            <Separator />

            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <Label className="font-semibold">Email Notifications</Label>
                <p className="text-sm text-muted-foreground">
                  Receive updates via email
                </p>
              </div>
              <Switch
                checked={localPreferences.notifications.email}
                onCheckedChange={(checked) => handleNotificationToggle('email', checked)}
              />
            </div>

            <Separator />

            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <Label className="font-semibold">Game Reminders</Label>
                <p className="text-sm text-muted-foreground">
                  Get reminded before your teams' games
                </p>
              </div>
              <Switch
                checked={localPreferences.notifications.gameReminders}
                onCheckedChange={(checked) => handleNotificationToggle('gameReminders', checked)}
              />
            </div>

            <Separator />

            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <Label className="font-semibold">News Alerts</Label>
                <p className="text-sm text-muted-foreground">
                  Breaking news and important updates
                </p>
              </div>
              <Switch
                checked={localPreferences.notifications.newsAlerts}
                onCheckedChange={(checked) => handleNotificationToggle('newsAlerts', checked)}
              />
            </div>

            <Separator />

            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <Label className="font-semibold">Score Updates</Label>
                <p className="text-sm text-muted-foreground">
                  Live scores and game results
                </p>
              </div>
              <Switch
                checked={localPreferences.notifications.scoreUpdates}
                onCheckedChange={(checked) => handleNotificationToggle('scoreUpdates', checked)}
              />
            </div>
          </div>

          {enabledNotificationsCount === 0 && (
            <Alert className="mt-4">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                You have all notifications disabled. You may miss important updates about your teams.
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>
    </div>
  );
}