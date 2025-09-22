import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { toast } from "@/components/ui/use-toast";
import { AlertCircle } from "lucide-react";
import { OnboardingLayout } from "./OnboardingLayout";
import { apiClient } from "@/lib/api-client";
import { useFirebaseAuth } from "@/contexts/FirebaseAuthContext";
import { updateLocalOnboardingStep, getLocalOnboardingStatus } from "@/lib/onboarding-storage";

export function PreferencesStep() {
  const navigate = useNavigate();
  const { isAuthenticated } = useFirebaseAuth();

  const [notifications, setNotifications] = useState({
    push: true,
    email: false,
    gameReminders: true,
    newsAlerts: false,
    scoreUpdates: true,
  });
  const [contentFrequency, setContentFrequency] = useState<'minimal' | 'standard' | 'comprehensive'>('standard');
  const [newsTypes, setNewsTypes] = useState([
    { type: 'injuries', enabled: true, priority: 1 },
    { type: 'trades', enabled: true, priority: 2 },
    { type: 'roster', enabled: true, priority: 3 },
    { type: 'scores', enabled: true, priority: 4 },
    { type: 'analysis', enabled: false, priority: 5 },
  ]);
  const [isApiAvailable, setIsApiAvailable] = useState(true);

  // Load saved preferences from localStorage
  useEffect(() => {
    const localStatus = getLocalOnboardingStatus();
    if (localStatus?.preferences) {
      setNotifications(localStatus.preferences.notifications);
      setContentFrequency(localStatus.preferences.contentFrequency);
      setNewsTypes(localStatus.preferences.newsTypes);
    }
  }, []);

  const handleContinue = async () => {
    const preferences = {
      newsTypes,
      notifications,
      contentFrequency,
    };

    // Always save to localStorage first
    updateLocalOnboardingStep(4, { preferences });

    // Try to save to API if available
    if (isAuthenticated) {
      try {
        await apiClient.updateOnboardingStep({
          step: 4,
          data: { preferences }
        });
        console.log('Preferences saved to API');
      } catch (error) {
        console.warn('Failed to save preferences to API, continuing with localStorage:', error);
        setIsApiAvailable(false);
        toast({
          title: "Saved Offline",
          description: "Your preferences have been saved locally.",
          variant: "default",
        });
      }
    }

    navigate("/onboarding/step/5");
  };

  const handleNotificationChange = (key: keyof typeof notifications) => {
    setNotifications(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const handleNewsTypeChange = (type: string, enabled: boolean) => {
    setNewsTypes(prev =>
      prev.map(newsType =>
        newsType.type === type
          ? { ...newsType, enabled }
          : newsType
      )
    );
  };

  return (
    <OnboardingLayout
      step={4}
      totalSteps={5}
      title="Set Your Preferences"
      subtitle="Customize your Corner League experience"
      showProgress={true}
      completedSteps={3}
      onNext={handleContinue}
    >
      <div className="space-y-6">
        {/* Offline indicator */}
        {!isApiAvailable && (
          <div className="bg-orange-50 dark:bg-orange-950/30 border border-orange-200 dark:border-orange-800 rounded-lg p-4">
            <div className="flex items-center gap-3">
              <AlertCircle className="h-5 w-5 text-orange-600 dark:text-orange-400" />
              <div className="text-sm">
                <p className="font-medium text-orange-800 dark:text-orange-200">
                  Working Offline
                </p>
                <p className="text-orange-700 dark:text-orange-300">
                  Your preferences are being saved locally and will sync when connection is restored.
                </p>
              </div>
            </div>
          </div>
        )}

        <div className="text-center">
          <p className="text-lg font-body text-muted-foreground">
            Fine-tune your notifications and content preferences.
          </p>
        </div>

        <div className="grid gap-6">
          {/* News Types */}
          <Card>
            <CardHeader>
              <CardTitle className="font-display">Content Types</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground font-body">
                Choose which types of sports content you want to see in your feed.
              </p>
              {newsTypes.map((newsType) => (
                <div key={newsType.type} className="flex items-center justify-between">
                  <Label htmlFor={newsType.type} className="font-body capitalize">
                    {newsType.type}
                  </Label>
                  <Switch
                    id={newsType.type}
                    checked={newsType.enabled}
                    onCheckedChange={(enabled) => handleNewsTypeChange(newsType.type, enabled)}
                  />
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Notifications */}
          <Card>
            <CardHeader>
              <CardTitle className="font-display">Notifications</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground font-body">
                Control how and when you receive notifications.
              </p>
              {Object.entries(notifications).map(([key, value]) => (
                <div key={key} className="flex items-center justify-between">
                  <Label htmlFor={key} className="font-body">
                    {key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
                  </Label>
                  <Switch
                    id={key}
                    checked={value}
                    onCheckedChange={() => handleNotificationChange(key as keyof typeof notifications)}
                  />
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Content Frequency */}
          <Card>
            <CardHeader>
              <CardTitle className="font-display">Content Frequency</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground font-body mb-4">
                How much content would you like to see?
              </p>
              <RadioGroup value={contentFrequency} onValueChange={(value) => setContentFrequency(value as any)}>
                <div className="space-y-3">
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="minimal" id="minimal" />
                    <Label htmlFor="minimal" className="font-body">Minimal - Essential updates only</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="standard" id="standard" />
                    <Label htmlFor="standard" className="font-body">Standard - Balanced mix of content</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="comprehensive" id="comprehensive" />
                    <Label htmlFor="comprehensive" className="font-body">Comprehensive - All available content</Label>
                  </div>
                </div>
              </RadioGroup>
            </CardContent>
          </Card>
        </div>
      </div>
    </OnboardingLayout>
  );
}

export default PreferencesStep;