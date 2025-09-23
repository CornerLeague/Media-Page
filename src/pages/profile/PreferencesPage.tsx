/**
 * PreferencesPage Component
 *
 * Full CRUD interface for user preferences including sports, teams, and content settings.
 * Reuses existing onboarding components in edit mode as required by section 2.1.
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { toast } from '@/components/ui/use-toast';
import { ArrowLeft, Save, RotateCcw, AlertCircle, CheckCircle, Settings, Target, Users, Trash2, AlertTriangle } from 'lucide-react';
import { usePreferences, type SportPreference, type TeamPreference, type ContentPreferences } from '@/hooks/usePreferences';
import { SportsEditSection } from '@/components/preferences/SportsEditSection';
import { TeamsEditSection } from '@/components/preferences/TeamsEditSection';
import { ContentEditSection } from '@/components/preferences/ContentEditSection';
import { ResetOnboardingDialog } from '@/components/preferences/ResetOnboardingDialog';
import { cn } from '@/lib/utils';

export function PreferencesPage() {
  const navigate = useNavigate();
  const {
    preferencesData,
    isLoading,
    error,
    updateSportsPreferences,
    updateTeamsPreferences,
    updateContentPreferences,
    isUpdatingSports,
    isUpdatingTeams,
    isUpdatingContent,
    sportsError,
    teamsError,
    contentError,
    refreshPreferences,
    clearErrors,
  } = usePreferences();

  // Local state for editing
  const [editedSports, setEditedSports] = useState<SportPreference[]>([]);
  const [editedTeams, setEditedTeams] = useState<TeamPreference[]>([]);
  const [editedContent, setEditedContent] = useState<ContentPreferences | null>(null);
  const [hasChanges, setHasChanges] = useState(false);
  const [activeTab, setActiveTab] = useState<'sports' | 'teams' | 'content'>('sports');

  // Initialize local state when data loads
  useEffect(() => {
    if (preferencesData) {
      setEditedSports(preferencesData.sports);
      setEditedTeams(preferencesData.teams);
      setEditedContent(preferencesData.preferences);
    }
  }, [preferencesData]);

  // Track changes
  useEffect(() => {
    if (!preferencesData) return;

    const sportsChanged = JSON.stringify(editedSports) !== JSON.stringify(preferencesData.sports);
    const teamsChanged = JSON.stringify(editedTeams) !== JSON.stringify(preferencesData.teams);
    const contentChanged = JSON.stringify(editedContent) !== JSON.stringify(preferencesData.preferences);

    setHasChanges(sportsChanged || teamsChanged || contentChanged);
  }, [editedSports, editedTeams, editedContent, preferencesData]);

  const handleGoBack = () => {
    if (hasChanges) {
      const confirmLeave = confirm('You have unsaved changes. Are you sure you want to leave?');
      if (!confirmLeave) return;
    }
    navigate('/');
  };

  const handleSaveSports = async () => {
    try {
      await updateSportsPreferences(editedSports);
    } catch (error) {
      console.error('Failed to save sports preferences:', error);
    }
  };

  const handleSaveTeams = async () => {
    try {
      await updateTeamsPreferences(editedTeams);
    } catch (error) {
      console.error('Failed to save team preferences:', error);
    }
  };

  const handleSaveContent = async () => {
    if (!editedContent) return;
    try {
      await updateContentPreferences(editedContent);
    } catch (error) {
      console.error('Failed to save content preferences:', error);
    }
  };

  const handleSaveAll = async () => {
    try {
      if (!editedContent) return;

      // Save all sections in parallel
      await Promise.all([
        updateSportsPreferences(editedSports),
        updateTeamsPreferences(editedTeams),
        updateContentPreferences(editedContent),
      ]);

      toast({
        title: 'All Preferences Saved',
        description: 'Your preferences have been updated successfully.',
      });
    } catch (error) {
      toast({
        title: 'Save Failed',
        description: 'Some preferences could not be saved. Please try again.',
        variant: 'destructive',
      });
    }
  };

  const handleResetAll = () => {
    if (!preferencesData) return;

    const confirmReset = confirm('Are you sure you want to reset all changes?');
    if (!confirmReset) return;

    setEditedSports(preferencesData.sports);
    setEditedTeams(preferencesData.teams);
    setEditedContent(preferencesData.preferences);
    clearErrors();

    toast({
      title: 'Changes Reset',
      description: 'All changes have been reset to saved values.',
    });
  };

  const isAnySaving = isUpdatingSports || isUpdatingTeams || isUpdatingContent;
  const hasAnyError = sportsError || teamsError || contentError;

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container mx-auto px-4 py-8">
          <div className="flex justify-center items-center min-h-[400px]">
            <div className="text-center space-y-4">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
              <p className="text-muted-foreground">Loading preferences...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container mx-auto px-4 py-8">
          <div className="max-w-2xl mx-auto">
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                Failed to load preferences. Please try again or contact support.
              </AlertDescription>
            </Alert>
            <div className="flex gap-4 mt-4">
              <Button onClick={() => refreshPreferences()} variant="outline">
                <RotateCcw className="mr-2 h-4 w-4" />
                Try Again
              </Button>
              <Button onClick={handleGoBack} variant="ghost">
                <ArrowLeft className="mr-2 h-4 w-4" />
                Go Back
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <div className="flex items-center gap-3">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleGoBack}
                  className="hover:bg-muted/50"
                >
                  <ArrowLeft className="h-4 w-4" />
                </Button>
                <h1 className="text-3xl font-display font-bold text-foreground">
                  Edit Preferences
                </h1>
              </div>
              <p className="text-muted-foreground">
                Customize your sports, teams, and content preferences
              </p>
            </div>

            {hasChanges && (
              <div className="flex items-center gap-2">
                <Badge variant="secondary" className="animate-pulse">
                  Unsaved Changes
                </Badge>
              </div>
            )}
          </div>

          {/* Error Alert */}
          {hasAnyError && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                {sportsError?.message || teamsError?.message || contentError?.message}
              </AlertDescription>
            </Alert>
          )}

          {/* Action Buttons */}
          {hasChanges && (
            <Card className="border-primary/20 bg-primary/5">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div className="space-y-1">
                    <h3 className="font-semibold text-foreground">Unsaved Changes</h3>
                    <p className="text-sm text-muted-foreground">
                      You have unsaved changes. Save them or reset to continue.
                    </p>
                  </div>
                  <div className="flex gap-3">
                    <Button
                      variant="outline"
                      onClick={handleResetAll}
                      disabled={isAnySaving}
                    >
                      <RotateCcw className="mr-2 h-4 w-4" />
                      Reset
                    </Button>
                    <Button
                      onClick={handleSaveAll}
                      disabled={isAnySaving}
                      className="bg-primary hover:bg-primary/90"
                    >
                      {isAnySaving ? (
                        <>
                          <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                          Saving...
                        </>
                      ) : (
                        <>
                          <Save className="mr-2 h-4 w-4" />
                          Save All
                        </>
                      )}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Preferences Tabs */}
          <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as any)}>
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="sports" className="flex items-center gap-2">
                <Target className="h-4 w-4" />
                Sports
              </TabsTrigger>
              <TabsTrigger value="teams" className="flex items-center gap-2">
                <Users className="h-4 w-4" />
                Teams
              </TabsTrigger>
              <TabsTrigger value="content" className="flex items-center gap-2">
                <Settings className="h-4 w-4" />
                Content
              </TabsTrigger>
            </TabsList>

            <TabsContent value="sports" className="space-y-6">
              <SportsEditSection
                sports={editedSports}
                onSportsChange={setEditedSports}
                onSave={handleSaveSports}
                isSaving={isUpdatingSports}
                error={sportsError}
              />
            </TabsContent>

            <TabsContent value="teams" className="space-y-6">
              <TeamsEditSection
                teams={editedTeams}
                onTeamsChange={setEditedTeams}
                onSave={handleSaveTeams}
                isSaving={isUpdatingTeams}
                error={teamsError}
                availableSports={editedSports}
              />
            </TabsContent>

            <TabsContent value="content" className="space-y-6">
              <ContentEditSection
                preferences={editedContent}
                onPreferencesChange={setEditedContent}
                onSave={handleSaveContent}
                isSaving={isUpdatingContent}
                error={contentError}
              />
            </TabsContent>
          </Tabs>

          {/* Danger Zone */}
          <div className="space-y-6">
            <Separator />
            <Card className="border-destructive/20 bg-destructive/5">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-destructive/10">
                    <AlertTriangle className="h-4 w-4 text-destructive" />
                  </div>
                  <div>
                    <CardTitle className="text-destructive">Danger Zone</CardTitle>
                    <CardDescription>
                      Irreversible actions that will affect your account
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between p-4 border border-destructive/20 rounded-lg bg-background/50">
                  <div className="space-y-1">
                    <h4 className="font-medium text-foreground">Reset Onboarding</h4>
                    <p className="text-sm text-muted-foreground">
                      Delete all preferences and restart the onboarding process
                    </p>
                  </div>
                  <ResetOnboardingDialog>
                    <Button
                      variant="destructive"
                      size="sm"
                      className="bg-destructive hover:bg-destructive/90"
                    >
                      <Trash2 className="mr-2 h-4 w-4" />
                      Reset Onboarding
                    </Button>
                  </ResetOnboardingDialog>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}