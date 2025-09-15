import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Checkbox } from '@/components/ui/checkbox';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import {
  Settings,
  Bell,
  Newspaper,
  Heart,
  TrendingUp,
  Users,
  Trophy,
  AlertCircle,
  BarChart3,
  ChevronRight,
} from 'lucide-react';
import { useOnboarding } from '@/hooks/useOnboarding';
import {
  UserSettings,
  NewsTypePreference,
  ContentFrequency,
  DEFAULT_USER_SETTINGS,
} from '@/lib/types/onboarding-types';

// Form schema
const preferencesSchema = z.object({
  newsTypes: z.array(z.object({
    type: z.enum(['injuries', 'trades', 'roster', 'general', 'scores', 'analysis']),
    enabled: z.boolean(),
    priority: z.number(),
  })).min(1, 'Please enable at least one news type'),
  notifications: z.object({
    push: z.boolean(),
    email: z.boolean(),
    gameReminders: z.boolean(),
    newsAlerts: z.boolean(),
    scoreUpdates: z.boolean(),
  }),
  contentFrequency: z.enum(['minimal', 'standard', 'comprehensive']),
});

type PreferencesFormData = z.infer<typeof preferencesSchema>;

const newsTypeConfig = [
  {
    type: 'injuries' as const,
    label: 'Injury Reports',
    description: 'Player injuries, recoveries, and impact analysis',
    icon: AlertCircle,
    color: 'text-red-500',
  },
  {
    type: 'trades' as const,
    label: 'Trades & Transactions',
    description: 'Player trades, signings, and roster moves',
    icon: Users,
    color: 'text-blue-500',
  },
  {
    type: 'roster' as const,
    label: 'Roster Changes',
    description: 'Lineup changes, call-ups, and depth chart updates',
    icon: Users,
    color: 'text-green-500',
  },
  {
    type: 'scores' as const,
    label: 'Scores & Results',
    description: 'Game results, highlights, and quick recaps',
    icon: Trophy,
    color: 'text-yellow-500',
  },
  {
    type: 'analysis' as const,
    label: 'Analysis & Opinion',
    description: 'Expert analysis, predictions, and commentary',
    icon: BarChart3,
    color: 'text-purple-500',
  },
  {
    type: 'general' as const,
    label: 'General News',
    description: 'Other team news, league updates, and stories',
    icon: Newspaper,
    color: 'text-gray-500',
  },
];

const contentFrequencyOptions = [
  {
    value: 'minimal' as ContentFrequency,
    label: 'Minimal',
    description: 'Essential updates only',
    badge: 'Light',
  },
  {
    value: 'standard' as ContentFrequency,
    label: 'Standard',
    description: 'Balanced mix of news and updates',
    badge: 'Recommended',
  },
  {
    value: 'comprehensive' as ContentFrequency,
    label: 'Comprehensive',
    description: 'All available content and deep coverage',
    badge: 'Complete',
  },
];

const PreferencesSetup: React.FC = () => {
  const { userPreferences, updatePreferences } = useOnboarding();
  const [newsTypePriorities, setNewsTypePriorities] = useState<Record<string, number>>({});

  // Initialize form with user preferences or defaults
  const form = useForm<PreferencesFormData>({
    resolver: zodResolver(preferencesSchema),
    defaultValues: userPreferences.preferences || DEFAULT_USER_SETTINGS,
  });

  // Initialize news type priorities
  useEffect(() => {
    const preferences = userPreferences.preferences || DEFAULT_USER_SETTINGS;
    const priorities: Record<string, number> = {};
    preferences.newsTypes.forEach(nt => {
      priorities[nt.type] = nt.priority;
    });
    setNewsTypePriorities(priorities);
  }, [userPreferences.preferences]);

  // Handle form submission
  const onSubmit = (data: PreferencesFormData) => {
    updatePreferences(data);
  };

  // Handle news type toggle
  const handleNewsTypeToggle = (type: string, enabled: boolean) => {
    const currentNewsTypes = form.getValues('newsTypes');
    const updatedNewsTypes = currentNewsTypes.map(nt =>
      nt.type === type ? { ...nt, enabled } : nt
    );
    form.setValue('newsTypes', updatedNewsTypes);
  };

  // Handle priority change
  const handlePriorityChange = (type: string, priority: number) => {
    setNewsTypePriorities(prev => ({
      ...prev,
      [type]: priority,
    }));

    const currentNewsTypes = form.getValues('newsTypes');
    const updatedNewsTypes = currentNewsTypes.map(nt =>
      nt.type === type ? { ...nt, priority } : nt
    );
    form.setValue('newsTypes', updatedNewsTypes);
  };

  // Watch form values to auto-save
  const watchedValues = form.watch();
  useEffect(() => {
    // Auto-save preferences as user makes changes
    const timer = setTimeout(() => {
      if (form.formState.isValid) {
        updatePreferences(watchedValues);
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [watchedValues, form.formState.isValid, updatePreferences]);

  const enabledNewsTypes = form.watch('newsTypes').filter(nt => nt.enabled);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center space-y-2">
        <div className="flex justify-center mb-4">
          <Settings className="h-8 w-8 text-primary" />
        </div>
        <p className="text-muted-foreground">
          Customize your experience to get the content you care about most.
        </p>
      </div>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          {/* News Types Section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Newspaper className="h-5 w-5" />
                <span>Content Preferences</span>
              </CardTitle>
              <p className="text-sm text-muted-foreground">
                Choose what types of news and updates you want to see.
              </p>
            </CardHeader>
            <CardContent className="space-y-4">
              <FormField
                control={form.control}
                name="newsTypes"
                render={() => (
                  <FormItem>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {newsTypeConfig.map((config) => {
                        const newsType = form.watch('newsTypes').find(nt => nt.type === config.type);
                        const isEnabled = newsType?.enabled || false;
                        const priority = newsTypePriorities[config.type] || 1;

                        return (
                          <Card
                            key={config.type}
                            className={`border-2 transition-all ${
                              isEnabled ? 'border-primary bg-primary/5' : 'border-muted'
                            }`}
                          >
                            <CardContent className="p-4">
                              <div className="flex items-start space-x-3">
                                <config.icon className={`h-5 w-5 mt-0.5 ${config.color}`} />
                                <div className="flex-1 space-y-2">
                                  <div className="flex items-center justify-between">
                                    <Label className="font-medium cursor-pointer">
                                      {config.label}
                                    </Label>
                                    <Switch
                                      checked={isEnabled}
                                      onCheckedChange={(checked) =>
                                        handleNewsTypeToggle(config.type, checked)
                                      }
                                    />
                                  </div>
                                  <p className="text-xs text-muted-foreground">
                                    {config.description}
                                  </p>

                                  {/* Priority selector */}
                                  {isEnabled && (
                                    <div className="flex items-center space-x-2 pt-2">
                                      <Label className="text-xs">Priority:</Label>
                                      <div className="flex space-x-1">
                                        {[1, 2, 3, 4, 5].map((p) => (
                                          <Button
                                            key={p}
                                            type="button"
                                            variant={priority >= p ? "default" : "outline"}
                                            size="sm"
                                            className="h-6 w-6 p-0 text-xs"
                                            onClick={() => handlePriorityChange(config.type, p)}
                                          >
                                            {p}
                                          </Button>
                                        ))}
                                      </div>
                                    </div>
                                  )}
                                </div>
                              </div>
                            </CardContent>
                          </Card>
                        );
                      })}
                    </div>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {enabledNewsTypes.length > 0 && (
                <div className="mt-4 p-3 bg-green-50 dark:bg-green-950 rounded-md">
                  <p className="text-sm text-green-800 dark:text-green-200">
                    ✓ {enabledNewsTypes.length} content type{enabledNewsTypes.length !== 1 ? 's' : ''} selected
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Content Frequency Section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <TrendingUp className="h-5 w-5" />
                <span>Content Frequency</span>
              </CardTitle>
              <p className="text-sm text-muted-foreground">
                How much content would you like to receive?
              </p>
            </CardHeader>
            <CardContent>
              <FormField
                control={form.control}
                name="contentFrequency"
                render={({ field }) => (
                  <FormItem className="space-y-3">
                    <FormControl>
                      <RadioGroup
                        onValueChange={field.onChange}
                        defaultValue={field.value}
                        className="grid grid-cols-1 md:grid-cols-3 gap-4"
                      >
                        {contentFrequencyOptions.map((option) => (
                          <div key={option.value}>
                            <RadioGroupItem
                              value={option.value}
                              id={option.value}
                              className="sr-only"
                            />
                            <Label
                              htmlFor={option.value}
                              className={`flex flex-col items-center justify-center p-4 border-2 rounded-lg cursor-pointer transition-all ${
                                field.value === option.value
                                  ? 'border-primary bg-primary/5'
                                  : 'border-muted hover:border-muted-foreground/50'
                              }`}
                            >
                              <div className="text-center space-y-2">
                                <div className="font-medium">{option.label}</div>
                                <Badge
                                  variant={option.value === 'standard' ? 'default' : 'secondary'}
                                  className="text-xs"
                                >
                                  {option.badge}
                                </Badge>
                                <p className="text-xs text-muted-foreground">
                                  {option.description}
                                </p>
                              </div>
                            </Label>
                          </div>
                        ))}
                      </RadioGroup>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </CardContent>
          </Card>

          {/* Notifications Section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Bell className="h-5 w-5" />
                <span>Notification Settings</span>
              </CardTitle>
              <p className="text-sm text-muted-foreground">
                Configure how you'd like to be notified about updates.
              </p>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="notifications.push"
                  render={({ field }) => (
                    <FormItem className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="space-y-0.5">
                        <FormLabel>Push Notifications</FormLabel>
                        <FormDescription className="text-xs">
                          Browser notifications for breaking news
                        </FormDescription>
                      </div>
                      <FormControl>
                        <Switch checked={field.value} onCheckedChange={field.onChange} />
                      </FormControl>
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="notifications.email"
                  render={({ field }) => (
                    <FormItem className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="space-y-0.5">
                        <FormLabel>Email Updates</FormLabel>
                        <FormDescription className="text-xs">
                          Daily/weekly digest emails
                        </FormDescription>
                      </div>
                      <FormControl>
                        <Switch checked={field.value} onCheckedChange={field.onChange} />
                      </FormControl>
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="notifications.gameReminders"
                  render={({ field }) => (
                    <FormItem className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="space-y-0.5">
                        <FormLabel>Game Reminders</FormLabel>
                        <FormDescription className="text-xs">
                          Reminders before your teams play
                        </FormDescription>
                      </div>
                      <FormControl>
                        <Switch checked={field.value} onCheckedChange={field.onChange} />
                      </FormControl>
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="notifications.scoreUpdates"
                  render={({ field }) => (
                    <FormItem className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="space-y-0.5">
                        <FormLabel>Score Updates</FormLabel>
                        <FormDescription className="text-xs">
                          Live score notifications during games
                        </FormDescription>
                      </div>
                      <FormControl>
                        <Switch checked={field.value} onCheckedChange={field.onChange} />
                      </FormControl>
                    </FormItem>
                  )}
                />
              </div>
            </CardContent>
          </Card>

          {/* Instructions */}
          <div className="text-center max-w-md mx-auto">
            <Card className="bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800">
              <CardContent className="p-4">
                <div className="flex items-start space-x-2">
                  <ChevronRight className="h-4 w-4 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
                  <p className="text-sm text-blue-800 dark:text-blue-200">
                    <strong>Note:</strong> These settings can be changed anytime from your account preferences.
                    Your choices are saved automatically as you make changes.
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </form>
      </Form>
    </div>
  );
};

export default PreferencesSetup;