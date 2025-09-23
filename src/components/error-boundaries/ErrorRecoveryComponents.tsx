/**
 * Error Recovery Components
 *
 * Enhanced error message components with clear recovery guidance,
 * contextual help, and user-friendly error displays.
 */

import React from 'react';
import { AlertTriangle, RefreshCw, HelpCircle, ArrowLeft, Home, CheckCircle2, XCircle, Info } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { cn } from '@/lib/utils';

// Error severity levels
export type ErrorSeverity = 'info' | 'warning' | 'error' | 'critical';

// Error recovery action
export interface RecoveryAction {
  label: string;
  action: () => void;
  variant?: 'default' | 'outline' | 'destructive' | 'secondary';
  icon?: React.ComponentType<{ className?: string }>;
  disabled?: boolean;
  loading?: boolean;
}

// Error context information
export interface ErrorContext {
  step?: number;
  stepName?: string;
  field?: string;
  component?: string;
  timestamp?: Date;
  userAgent?: string;
  url?: string;
}

// Props for error display components
export interface ErrorDisplayProps {
  title: string;
  message: string;
  severity?: ErrorSeverity;
  context?: ErrorContext;
  recoveryActions?: RecoveryAction[];
  onDismiss?: () => void;
  canRetry?: boolean;
  retryCount?: number;
  maxRetries?: number;
  helpText?: string;
  technicalDetails?: string;
  showTechnicalDetails?: boolean;
  className?: string;
}

// Field-level error display
export interface FieldErrorProps {
  error: string;
  field: string;
  severity?: ErrorSeverity;
  onClear?: () => void;
  helpText?: string;
  className?: string;
}

/**
 * Get icon for error severity
 */
function getSeverityIcon(severity: ErrorSeverity) {
  switch (severity) {
    case 'info':
      return Info;
    case 'warning':
      return AlertTriangle;
    case 'error':
      return XCircle;
    case 'critical':
      return AlertTriangle;
    default:
      return AlertTriangle;
  }
}

/**
 * Get color classes for error severity
 */
function getSeverityClasses(severity: ErrorSeverity) {
  switch (severity) {
    case 'info':
      return {
        icon: 'text-blue-500',
        border: 'border-blue-200',
        bg: 'bg-blue-50 dark:bg-blue-950/30',
        text: 'text-blue-800 dark:text-blue-200',
      };
    case 'warning':
      return {
        icon: 'text-orange-500',
        border: 'border-orange-200',
        bg: 'bg-orange-50 dark:bg-orange-950/30',
        text: 'text-orange-800 dark:text-orange-200',
      };
    case 'error':
      return {
        icon: 'text-red-500',
        border: 'border-red-200',
        bg: 'bg-red-50 dark:bg-red-950/30',
        text: 'text-red-800 dark:text-red-200',
      };
    case 'critical':
      return {
        icon: 'text-red-600',
        border: 'border-red-300',
        bg: 'bg-red-100 dark:bg-red-950/50',
        text: 'text-red-900 dark:text-red-100',
      };
    default:
      return {
        icon: 'text-gray-500',
        border: 'border-gray-200',
        bg: 'bg-gray-50 dark:bg-gray-950/30',
        text: 'text-gray-800 dark:text-gray-200',
      };
  }
}

/**
 * Inline Field Error Display
 */
export function FieldError({
  error,
  field,
  severity = 'error',
  onClear,
  helpText,
  className,
}: FieldErrorProps) {
  const Icon = getSeverityIcon(severity);
  const classes = getSeverityClasses(severity);

  return (
    <div className={cn('space-y-1', className)}>
      <div className={cn('flex items-center gap-2 text-sm', classes.text)}>
        <Icon className={cn('h-4 w-4', classes.icon)} />
        <span>{error}</span>
        {onClear && (
          <Button
            variant="ghost"
            size="sm"
            onClick={onClear}
            className="h-4 w-4 p-0 hover:bg-transparent"
            aria-label={`Clear error for ${field}`}
          >
            <XCircle className="h-3 w-3" />
          </Button>
        )}
      </div>

      {helpText && (
        <div className="flex items-start gap-2">
          <HelpCircle className="h-3 w-3 text-muted-foreground mt-0.5 flex-shrink-0" />
          <p className="text-xs text-muted-foreground">{helpText}</p>
        </div>
      )}
    </div>
  );
}

/**
 * Enhanced Error Alert
 */
export function ErrorAlert({
  title,
  message,
  severity = 'error',
  context,
  recoveryActions = [],
  onDismiss,
  canRetry = false,
  retryCount = 0,
  maxRetries = 3,
  helpText,
  technicalDetails,
  showTechnicalDetails = false,
  className,
}: ErrorDisplayProps) {
  const [showDetails, setShowDetails] = React.useState(showTechnicalDetails);
  const Icon = getSeverityIcon(severity);
  const classes = getSeverityClasses(severity);

  return (
    <Alert className={cn(classes.border, classes.bg, className)}>
      <Icon className={cn('h-4 w-4', classes.icon)} />
      <AlertTitle className={cn('flex items-center justify-between', classes.text)}>
        <span>{title}</span>
        {onDismiss && (
          <Button
            variant="ghost"
            size="sm"
            onClick={onDismiss}
            className="h-4 w-4 p-0 hover:bg-transparent"
            aria-label="Dismiss error"
          >
            <XCircle className="h-3 w-3" />
          </Button>
        )}
      </AlertTitle>

      <AlertDescription className="space-y-4">
        <div className={classes.text}>
          <p>{message}</p>

          {context && (
            <div className="mt-2 text-xs opacity-75">
              {context.step && context.stepName && (
                <p>Step {context.step}: {context.stepName}</p>
              )}
              {context.field && (
                <p>Field: {context.field}</p>
              )}
              {context.timestamp && (
                <p>Time: {context.timestamp.toLocaleTimeString()}</p>
              )}
            </div>
          )}
        </div>

        {helpText && (
          <div className="flex items-start gap-2">
            <HelpCircle className="h-4 w-4 text-muted-foreground mt-0.5 flex-shrink-0" />
            <p className="text-sm text-muted-foreground">{helpText}</p>
          </div>
        )}

        {canRetry && retryCount > 0 && (
          <div className="flex justify-center">
            <Badge variant="outline">
              Attempt {retryCount} of {maxRetries}
            </Badge>
          </div>
        )}

        {recoveryActions.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {recoveryActions.map((action, index) => (
              <Button
                key={index}
                variant={action.variant || 'default'}
                size="sm"
                onClick={action.action}
                disabled={action.disabled}
                className="flex items-center gap-2"
              >
                {action.loading ? (
                  <RefreshCw className="h-4 w-4 animate-spin" />
                ) : (
                  action.icon && <action.icon className="h-4 w-4" />
                )}
                {action.label}
              </Button>
            ))}
          </div>
        )}

        {technicalDetails && (
          <Collapsible open={showDetails} onOpenChange={setShowDetails}>
            <CollapsibleTrigger asChild>
              <Button variant="ghost" size="sm" className="text-xs">
                {showDetails ? 'Hide' : 'Show'} technical details
              </Button>
            </CollapsibleTrigger>
            <CollapsibleContent className="mt-2">
              <div className="bg-muted/50 rounded p-3 font-mono text-xs overflow-auto max-h-32">
                <pre>{technicalDetails}</pre>
              </div>
            </CollapsibleContent>
          </Collapsible>
        )}
      </AlertDescription>
    </Alert>
  );
}

/**
 * Full-Screen Error Display
 */
export function FullScreenError({
  title,
  message,
  severity = 'error',
  context,
  recoveryActions = [],
  onDismiss,
  canRetry = false,
  retryCount = 0,
  maxRetries = 3,
  helpText,
  technicalDetails,
  className,
}: ErrorDisplayProps) {
  const Icon = getSeverityIcon(severity);

  const defaultActions: RecoveryAction[] = [
    {
      label: 'Go Back',
      action: () => window.history.back(),
      variant: 'outline',
      icon: ArrowLeft,
    },
    {
      label: 'Go Home',
      action: () => window.location.href = '/',
      variant: 'outline',
      icon: Home,
    },
  ];

  const allActions = [...recoveryActions, ...defaultActions];

  return (
    <div className={cn('min-h-screen bg-background flex items-center justify-center p-4', className)}>
      <Card className="w-full max-w-lg">
        <CardHeader className="text-center">
          <div className="flex justify-center mb-4">
            <Icon className="h-12 w-12 text-red-500" />
          </div>
          <CardTitle className="text-xl">{title}</CardTitle>
        </CardHeader>

        <CardContent className="space-y-6">
          <div className="text-center space-y-2">
            <p className="text-muted-foreground">{message}</p>

            {context && (
              <div className="text-sm text-muted-foreground">
                {context.step && context.stepName && (
                  <p>Error occurred on step {context.step}: {context.stepName}</p>
                )}
                {context.timestamp && (
                  <p>Time: {context.timestamp.toLocaleString()}</p>
                )}
              </div>
            )}
          </div>

          {helpText && (
            <Alert>
              <HelpCircle className="h-4 w-4" />
              <AlertDescription>{helpText}</AlertDescription>
            </Alert>
          )}

          {canRetry && retryCount > 0 && (
            <div className="flex justify-center">
              <Badge variant="outline">
                Attempt {retryCount} of {maxRetries}
              </Badge>
            </div>
          )}

          {allActions.length > 0 && (
            <div className="space-y-3">
              {allActions.slice(0, 2).map((action, index) => (
                <Button
                  key={index}
                  variant={action.variant || 'default'}
                  size="lg"
                  onClick={action.action}
                  disabled={action.disabled}
                  className="w-full flex items-center justify-center gap-2"
                >
                  {action.loading ? (
                    <RefreshCw className="h-4 w-4 animate-spin" />
                  ) : (
                    action.icon && <action.icon className="h-4 w-4" />
                  )}
                  {action.label}
                </Button>
              ))}

              {allActions.length > 2 && (
                <div className="flex gap-2">
                  {allActions.slice(2).map((action, index) => (
                    <Button
                      key={index + 2}
                      variant={action.variant || 'outline'}
                      size="sm"
                      onClick={action.action}
                      disabled={action.disabled}
                      className="flex-1 flex items-center justify-center gap-2"
                    >
                      {action.loading ? (
                        <RefreshCw className="h-3 w-3 animate-spin" />
                      ) : (
                        action.icon && <action.icon className="h-3 w-3" />
                      )}
                      {action.label}
                    </Button>
                  ))}
                </div>
              )}
            </div>
          )}

          {technicalDetails && (
            <Collapsible>
              <CollapsibleTrigger asChild>
                <Button variant="ghost" size="sm" className="text-xs w-full">
                  Show technical details
                </Button>
              </CollapsibleTrigger>
              <CollapsibleContent className="mt-2">
                <div className="bg-muted/50 rounded p-3 font-mono text-xs overflow-auto max-h-32">
                  <pre>{technicalDetails}</pre>
                </div>
              </CollapsibleContent>
            </Collapsible>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

/**
 * Success Message Component
 */
export function SuccessMessage({
  title,
  message,
  onDismiss,
  actions = [],
  className,
}: {
  title: string;
  message: string;
  onDismiss?: () => void;
  actions?: RecoveryAction[];
  className?: string;
}) {
  return (
    <Alert className={cn('border-green-200 bg-green-50 dark:bg-green-950/30', className)}>
      <CheckCircle2 className="h-4 w-4 text-green-500" />
      <AlertTitle className="text-green-800 dark:text-green-200 flex items-center justify-between">
        <span>{title}</span>
        {onDismiss && (
          <Button
            variant="ghost"
            size="sm"
            onClick={onDismiss}
            className="h-4 w-4 p-0 hover:bg-transparent"
            aria-label="Dismiss success message"
          >
            <XCircle className="h-3 w-3" />
          </Button>
        )}
      </AlertTitle>
      <AlertDescription className="space-y-4">
        <p className="text-green-700 dark:text-green-300">{message}</p>

        {actions.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {actions.map((action, index) => (
              <Button
                key={index}
                variant={action.variant || 'default'}
                size="sm"
                onClick={action.action}
                disabled={action.disabled}
                className="flex items-center gap-2"
              >
                {action.loading ? (
                  <RefreshCw className="h-4 w-4 animate-spin" />
                ) : (
                  action.icon && <action.icon className="h-4 w-4" />
                )}
                {action.label}
              </Button>
            ))}
          </div>
        )}
      </AlertDescription>
    </Alert>
  );
}

/**
 * Recovery Guidance Component
 */
export function RecoveryGuidance({
  steps,
  title = 'How to fix this',
  className,
}: {
  steps: string[];
  title?: string;
  className?: string;
}) {
  return (
    <div className={cn('space-y-3', className)}>
      <h4 className="font-medium text-sm flex items-center gap-2">
        <HelpCircle className="h-4 w-4" />
        {title}
      </h4>
      <ol className="space-y-2 text-sm text-muted-foreground">
        {steps.map((step, index) => (
          <li key={index} className="flex gap-3">
            <span className="flex-shrink-0 w-5 h-5 bg-primary/10 text-primary rounded-full flex items-center justify-center text-xs font-medium">
              {index + 1}
            </span>
            <span className="flex-1">{step}</span>
          </li>
        ))}
      </ol>
    </div>
  );
}

export default {
  FieldError,
  ErrorAlert,
  FullScreenError,
  SuccessMessage,
  RecoveryGuidance,
};