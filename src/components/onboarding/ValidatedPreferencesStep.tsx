/**
 * Validated Preferences Step
 *
 * Enhanced preferences step component with comprehensive validation,
 * error handling, and recovery mechanisms.
 */

import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { toast } from "@/components/ui/use-toast";
import { AlertCircle, Loader2, Mail, Bell, Clock } from "lucide-react";

import { OnboardingLayout } from "@/pages/onboarding/OnboardingLayout";
import { apiClient } from "@/lib/api-client";
import { useFirebaseAuth } from "@/contexts/FirebaseAuthContext";
import { updateLocalOnboardingStep, getLocalOnboardingStatus } from "@/lib/onboarding-storage";

// Validation imports
import { useContentPreferencesValidation } from "@/hooks/useOnboardingValidation";
import { ErrorAlert, FieldError, RecoveryGuidance } from "@/components/error-boundaries/ErrorRecoveryComponents";
import { reportOnboardingError } from "@/lib/error-reporting";
import { retryableFetch } from "@/lib/api-retry";

// Types
interface NotificationSettings {
  push: boolean;
  email: boolean;
  gameReminders: boolean;
  newsAlerts: boolean;
  scoreUpdates: boolean;
}

interface NewsTypeSetting {
  type: string;
  enabled: boolean;
  priority: number;
}

interface ValidationState {
  isValidating: boolean;
  showValidationErrors: boolean;
  hasBeenSubmitted: boolean;
}

interface PreferencesFormData {
  contentFrequency: 'low' | 'medium' | 'high';
  emailNotifications: boolean;
  emailAddress: string;
  pushNotifications: boolean;
  newsTypes: string[];
  timeZone: string;
  notifications: NotificationSettings;
  newsTypesSettings: NewsTypeSetting[];
}

// Available news types
const AVAILABLE_NEWS_TYPES = [
  { id: 'breaking', label: 'Breaking News', description: 'Major announcements and urgent updates' },
  { id: 'analysis', label: 'Analysis & Opinion', description: 'Expert commentary and in-depth analysis' },
  { id: 'scores', label: 'Scores & Results', description: 'Game scores and final results' },
  { id: 'trades', label: 'Trades & Transactions', description: 'Player trades and roster moves' },
  { id: 'injuries', label: 'Injury Reports', description: 'Player injury updates and status' },
  { id: 'predictions', label: 'Predictions & Betting', description: 'Game predictions and betting insights' },
];

// Time zones
const TIME_ZONES = [
  { value: 'America/New_York', label: 'Eastern Time (ET)' },
  { value: 'America/Chicago', label: 'Central Time (CT)' },
  { value: 'America/Denver', label: 'Mountain Time (MT)' },
  { value: 'America/Los_Angeles', label: 'Pacific Time (PT)' },
  { value: 'America/Anchorage', label: 'Alaska Time (AKT)' },
  { value: 'Pacific/Honolulu', label: 'Hawaii Time (HST)' },
];

/**
 * Enhanced Preferences Step with Validation
 */
export function ValidatedPreferencesStep() {
  const navigate = useNavigate();
  const { isAuthenticated, user } = useFirebaseAuth();

  // Component state
  const [formData, setFormData] = useState<PreferencesFormData>({
    contentFrequency: 'medium',
    emailNotifications: false,
    emailAddress: user?.email || '',
    pushNotifications: true,
    newsTypes: ['breaking', 'scores', 'trades'],
    timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'America/New_York',
    notifications: {
      push: true,
      email: false,
      gameReminders: true,
      newsAlerts: false,
      scoreUpdates: true,
    },
    newsTypesSettings: AVAILABLE_NEWS_TYPES.map((type, index) => ({
      type: type.id,
      enabled: ['breaking', 'scores', 'trades'].includes(type.id),
      priority: index + 1,
    })),
  });

  const [isApiAvailable, setIsApiAvailable] = useState(true);
  const [validationState, setValidationState] = useState<ValidationState>({
    isValidating: false,
    showValidationErrors: false,
    hasBeenSubmitted: false,
  });

  // Validation hook
  const validation = useContentPreferencesValidation();

  // Load saved preferences from localStorage
  useEffect(() => {
    const localStatus = getLocalOnboardingStatus();
    if (localStatus?.preferences) {
      const saved = localStatus.preferences;
      setFormData(prev => ({
        ...prev,
        contentFrequency: saved.contentFrequency || prev.contentFrequency,
        emailNotifications: saved.emailNotifications || prev.emailNotifications,
        emailAddress: saved.emailAddress || prev.emailAddress,
        pushNotifications: saved.pushNotifications !== undefined ? saved.pushNotifications : prev.pushNotifications,
        newsTypes: saved.newsTypes || prev.newsTypes,
        timeZone: saved.timeZone || prev.timeZone,
        notifications: { ...prev.notifications, ...saved.notifications },
        newsTypesSettings: saved.newsTypesSettings || prev.newsTypesSettings,
      }));
    }
  }, [user?.email]);

  // Real-time validation
  useEffect(() => {
    if (validationState.hasBeenSubmitted || validationState.showValidationErrors) {
      // Validate email requirement
      validation.validateEmailRequirement(formData.emailNotifications, formData.emailAddress);

      // Validate news types selection
      validation.validateNewsTypesSelection(formData.newsTypes);
    }
  }, [
    formData.emailNotifications,
    formData.emailAddress,
    formData.newsTypes,
    validationState.hasBeenSubmitted,
    validationState.showValidationErrors,
    validation
  ]);

  // Form field handlers with validation
  const handleContentFrequencyChange = useCallback((value: 'low' | 'medium' | 'high') => {
    setFormData(prev => ({ ...prev, contentFrequency: value }));
    validation.touch();
  }, [validation]);

  const handleEmailNotificationsChange = useCallback((enabled: boolean) => {
    setFormData(prev => ({ ...prev, emailNotifications: enabled }));

    // Clear email address validation error when disabling email notifications
    if (!enabled) {
      validation.clearFieldError('emailAddress');
    }

    validation.touch();
  }, [validation]);

  const handleEmailAddressChange = useCallback((email: string) => {
    setFormData(prev => ({ ...prev, emailAddress: email }));

    // Validate email field in real-time
    if (formData.emailNotifications) {
      validation.validateField('emailAddress', email);
    }

    validation.touch();
  }, [formData.emailNotifications, validation]);

  const handlePushNotificationsChange = useCallback((enabled: boolean) => {
    setFormData(prev => ({ ...prev, pushNotifications: enabled }));
    validation.touch();
  }, [validation]);

  const handleNewsTypeChange = useCallback((newsTypeId: string, enabled: boolean) => {
    setFormData(prev => {
      const updatedNewsTypes = enabled
        ? [...prev.newsTypes, newsTypeId]
        : prev.newsTypes.filter(id => id !== newsTypeId);

      const updatedSettings = prev.newsTypesSettings.map(setting =>
        setting.type === newsTypeId
          ? { ...setting, enabled }
          : setting
      );

      return {
        ...prev,
        newsTypes: updatedNewsTypes,
        newsTypesSettings: updatedSettings,
      };
    });

    validation.touch();
  }, [validation]);

  const handleNotificationChange = useCallback((key: keyof NotificationSettings) => {
    setFormData(prev => ({
      ...prev,
      notifications: { ...prev.notifications, [key]: !prev.notifications[key] }
    }));
    validation.touch();
  }, [validation]);

  const handleTimeZoneChange = useCallback((timeZone: string) => {
    setFormData(prev => ({ ...prev, timeZone }));
    validation.touch();
  }, [validation]);

  // Enhanced submission with validation
  const handleContinue = useCallback(async () => {
    setValidationState(prev => ({
      ...prev,
      isValidating: true,
      hasBeenSubmitted: true,
      showValidationErrors: true,
    }));

    try {
      // Prepare data for validation
      const validationData = {
        contentFrequency: formData.contentFrequency,
        emailNotifications: formData.emailNotifications,
        emailAddress: formData.emailAddress,
        pushNotifications: formData.pushNotifications,
        newsTypes: formData.newsTypes,
        timeZone: formData.timeZone,
      };

      // Validate current preferences
      const isValid = await validation.validate(validationData);

      if (!isValid) {
        setValidationState(prev => ({ ...prev, isValidating: false }));
        toast({
          title: "Validation Error",
          description: "Please fix the errors below and try again.",
          variant: "destructive",
        });
        return;
      }

      // Prepare preferences data
      const preferences = {
        contentFrequency: formData.contentFrequency,
        emailNotifications: formData.emailNotifications,
        emailAddress: formData.emailAddress,
        pushNotifications: formData.pushNotifications,
        newsTypes: formData.newsTypes,
        timeZone: formData.timeZone,
        notifications: formData.notifications,
        newsTypesSettings: formData.newsTypesSettings,
      };

      // Always save to localStorage first
      updateLocalOnboardingStep(4, { preferences });

      // Try to save to API if available
      if (isAuthenticated) {
        try {
          await retryableFetch.post('/api/onboarding/step', {
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

      // Navigation success
      setValidationState(prev => ({ ...prev, isValidating: false }));
      navigate("/onboarding/step/5");

    } catch (error) {
      setValidationState(prev => ({ ...prev, isValidating: false }));

      reportOnboardingError(
        4,
        'Failed to submit content preferences',
        error instanceof Error ? error : new Error(String(error)),
        { formData, userId: user?.uid }
      );

      toast({
        title: "Submission Failed",
        description: "Failed to save your preferences. Please try again.",
        variant: "destructive",
      });
    }
  }, [
    validation,
    formData,
    isAuthenticated,
    user?.uid,
    navigate
  ]);

  return (
    <OnboardingLayout
      step={4}
      totalSteps={5}
      title="Set Your Preferences"
      subtitle="Customize your Corner League experience"
      showProgress={true}
      completedSteps={3}
      onNext={handleContinue}
      isNextDisabled={validationState.isValidating}
    >
      <div className="space-y-6">
        {/* Offline indicator */}
        {!isApiAvailable && (
          <ErrorAlert
            title="Working Offline"
            message="Your preferences are being saved locally and will sync when connection is restored."
            severity="warning"
          />
        )}

        {/* Validation errors */}
        {validationState.showValidationErrors && validation.hasErrors && (
          <ErrorAlert
            title="Please Fix These Issues"
            message="There are some issues with your preferences that need to be fixed."
            severity="error"
          />
        )}

        <div className="text-center">
          <p className="text-lg font-body text-muted-foreground">
            Fine-tune your notifications and content preferences.
          </p>
        </div>

        <div className="grid gap-6">
          {/* Content Frequency */}
          <Card>
            <CardHeader>
              <CardTitle className="font-display flex items-center gap-2">
                <Clock className="h-5 w-5" />
                Content Frequency
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground font-body mb-4">
                How much content would you like to see?
              </p>

              {validation.fieldErrors.contentFrequency && (
                <div className="mb-4">
                  <FieldError
                    error={validation.fieldErrors.contentFrequency}
                    field="contentFrequency"
                    severity="error"
                    onClear={() => validation.clearFieldError('contentFrequency')}
                  />
                </div>
              )}

              <RadioGroup
                value={formData.contentFrequency}
                onValueChange={handleContentFrequencyChange}
                className="space-y-3"
              >
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="low" id="low" />
                  <Label htmlFor="low" className="font-body cursor-pointer">
                    <div>
                      <div className="font-medium">Low - Essential updates only</div>
                      <div className="text-sm text-muted-foreground">Breaking news and scores</div>
                    </div>
                  </Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="medium" id="medium" />
                  <Label htmlFor="medium" className="font-body cursor-pointer">
                    <div>
                      <div className="font-medium">Medium - Balanced mix of content</div>
                      <div className="text-sm text-muted-foreground">News, scores, and analysis</div>
                    </div>
                  </Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="high" id="high" />
                  <Label htmlFor="high" className="font-body cursor-pointer">
                    <div>
                      <div className="font-medium">High - All available content</div>
                      <div className="text-sm text-muted-foreground">Everything including rumors and predictions</div>
                    </div>
                  </Label>
                </div>
              </RadioGroup>
            </CardContent>
          </Card>

          {/* News Types */}
          <Card>
            <CardHeader>
              <CardTitle className="font-display">Content Types</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground font-body">
                Choose which types of sports content you want to see in your feed.
              </p>

              {validation.fieldErrors.newsTypes && (
                <FieldError
                  error={validation.fieldErrors.newsTypes}
                  field="newsTypes"
                  severity="error"
                  onClear={() => validation.clearFieldError('newsTypes')}
                  helpText="Select at least one news type to customize your feed."
                />
              )}

              <div className="space-y-3">
                {AVAILABLE_NEWS_TYPES.map((newsType) => (
                  <div key={newsType.id} className="flex items-start space-x-3">
                    <Checkbox
                      id={newsType.id}
                      checked={formData.newsTypes.includes(newsType.id)}
                      onCheckedChange={(enabled) => handleNewsTypeChange(newsType.id, !!enabled)}
                      className="mt-1"
                    />
                    <div className="flex-1">
                      <Label htmlFor={newsType.id} className="font-body cursor-pointer">
                        <div className="font-medium">{newsType.label}</div>
                        <div className="text-sm text-muted-foreground">{newsType.description}</div>
                      </Label>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Notifications */}
          <Card>
            <CardHeader>
              <CardTitle className="font-display flex items-center gap-2">
                <Bell className="h-5 w-5" />
                Notifications
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground font-body">
                Control how and when you receive notifications.
              </p>

              {/* Push Notifications */}
              <div className="flex items-center justify-between">
                <div>
                  <Label htmlFor="push-notifications" className="font-body font-medium">
                    Push Notifications
                  </Label>
                  <p className="text-sm text-muted-foreground">
                    Receive notifications directly to your device
                  </p>
                </div>
                <Switch
                  id="push-notifications"
                  checked={formData.pushNotifications}
                  onCheckedChange={handlePushNotificationsChange}
                />
              </div>

              {/* Email Notifications */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="email-notifications" className="font-body font-medium flex items-center gap-2">
                      <Mail className="h-4 w-4" />
                      Email Notifications
                    </Label>
                    <p className="text-sm text-muted-foreground">
                      Receive notifications via email
                    </p>
                  </div>
                  <Switch
                    id="email-notifications"
                    checked={formData.emailNotifications}
                    onCheckedChange={handleEmailNotificationsChange}
                  />
                </div>

                {/* Email Address Input */}
                {formData.emailNotifications && (
                  <div className="space-y-2">
                    <Label htmlFor="email-address" className="text-sm font-medium">
                      Email Address
                    </Label>
                    <Input
                      id="email-address"
                      type="email"
                      placeholder="Enter your email address"
                      value={formData.emailAddress}
                      onChange={(e) => handleEmailAddressChange(e.target.value)}
                      className={cn(
                        validation.fieldErrors.emailAddress && "border-red-300 focus:border-red-500"
                      )}
                    />
                    {validation.fieldErrors.emailAddress && (
                      <FieldError
                        error={validation.fieldErrors.emailAddress}
                        field="emailAddress"
                        severity="error"
                        onClear={() => validation.clearFieldError('emailAddress')}
                      />
                    )}
                  </div>
                )}
              </div>

              {/* Specific notification types */}
              <div className="space-y-3 pt-2 border-t">
                {Object.entries(formData.notifications).map(([key, value]) => (
                  <div key={key} className="flex items-center justify-between">
                    <Label htmlFor={key} className="font-body text-sm">
                      {key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
                    </Label>
                    <Switch
                      id={key}
                      checked={value}
                      onCheckedChange={() => handleNotificationChange(key as keyof NotificationSettings)}
                    />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Time Zone */}
          <Card>
            <CardHeader>
              <CardTitle className="font-display">Time Zone</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground font-body mb-4">
                Set your time zone for accurate scheduling of content and notifications.
              </p>

              {validation.fieldErrors.timeZone && (
                <div className="mb-4">
                  <FieldError
                    error={validation.fieldErrors.timeZone}
                    field="timeZone"
                    severity="error"
                    onClear={() => validation.clearFieldError('timeZone')}
                  />
                </div>
              )}

              <Select value={formData.timeZone} onValueChange={handleTimeZoneChange}>
                <SelectTrigger>
                  <SelectValue placeholder="Select your time zone" />
                </SelectTrigger>
                <SelectContent>
                  {TIME_ZONES.map((tz) => (
                    <SelectItem key={tz.value} value={tz.value}>
                      {tz.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </CardContent>
          </Card>
        </div>

        {/* Continue button state */}
        {validationState.isValidating && (
          <div className="flex justify-center">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Validating your preferences...</span>
            </div>
          </div>
        )}

        {/* Help tip */}
        <div className="bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
          <p className="text-sm text-blue-800 dark:text-blue-200 font-body">
            <strong>Tip:</strong> You can always change these preferences later in your account settings.
          </p>
        </div>
      </div>
    </OnboardingLayout>
  );
}

export default ValidatedPreferencesStep;