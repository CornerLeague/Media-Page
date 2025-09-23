/**
 * ResetOnboardingDialog Component
 *
 * Confirmation dialog for resetting user onboarding. Provides clear warning
 * about data loss and confirmation flow to prevent accidental resets.
 */

import { useState } from 'react';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';
import { Button } from '@/components/ui/button';
import { AlertTriangle, RotateCcw } from 'lucide-react';
import { useResetOnboarding } from '@/hooks/useResetOnboarding';

export interface ResetOnboardingDialogProps {
  children: React.ReactNode;
}

export function ResetOnboardingDialog({ children }: ResetOnboardingDialogProps) {
  const [isOpen, setIsOpen] = useState(false);
  const { resetOnboarding, isResetting } = useResetOnboarding();

  const handleReset = async () => {
    try {
      await resetOnboarding();
      setIsOpen(false);
    } catch (error) {
      // Error is handled by the hook
      console.error('Reset failed:', error);
    }
  };

  return (
    <AlertDialog open={isOpen} onOpenChange={setIsOpen}>
      <AlertDialogTrigger asChild>
        {children}
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-destructive/10">
              <AlertTriangle className="h-5 w-5 text-destructive" />
            </div>
            <div>
              <AlertDialogTitle className="text-left">
                Reset Onboarding?
              </AlertDialogTitle>
            </div>
          </div>
          <AlertDialogDescription className="text-left space-y-3">
            <p>This action will permanently delete all your current preferences, including:</p>
            <ul className="list-disc pl-6 space-y-1">
              <li>Selected sports and their rankings</li>
              <li>Favorite teams and affinity scores</li>
              <li>Content preferences and notification settings</li>
            </ul>
            <strong className="block text-foreground">
              You will be redirected to the onboarding flow to set up your preferences again.
            </strong>
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter className="flex-col-reverse sm:flex-row gap-2">
          <AlertDialogCancel disabled={isResetting}>
            Cancel
          </AlertDialogCancel>
          <AlertDialogAction
            onClick={handleReset}
            disabled={isResetting}
            className="bg-destructive hover:bg-destructive/90 text-destructive-foreground"
          >
            {isResetting ? (
              <>
                <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                Resetting...
              </>
            ) : (
              <>
                <RotateCcw className="mr-2 h-4 w-4" />
                Reset Onboarding
              </>
            )}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}