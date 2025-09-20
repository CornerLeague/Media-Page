/**
 * Password Reset Component
 *
 * Provides a standalone password reset form for users who have forgotten their password.
 */

import { useState } from 'react';
import { usePasswordReset } from '@/contexts/FirebaseAuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, Mail, ArrowLeft, CheckCircle, AlertCircle } from 'lucide-react';
import { isValidEmail } from '@/lib/firebase-errors';

interface PasswordResetProps {
  onBackToSignIn?: () => void;
  className?: string;
}

export function PasswordReset({ onBackToSignIn, className }: PasswordResetProps) {
  const { resetPassword, isLoading, error, success, clearState } = usePasswordReset();
  const [email, setEmail] = useState('');
  const [emailError, setEmailError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Clear previous errors
    setEmailError(null);
    clearState();

    // Validate email
    if (!email.trim()) {
      setEmailError('Email address is required');
      return;
    }

    if (!isValidEmail(email)) {
      setEmailError('Please enter a valid email address');
      return;
    }

    await resetPassword(email);
  };

  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEmail(e.target.value);
    setEmailError(null);
    clearState();
  };

  return (
    <Card className={className}>
      <CardHeader className="space-y-1">
        <div className="flex items-center gap-2">
          {onBackToSignIn && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onBackToSignIn}
              disabled={isLoading}
              className="p-1 h-auto"
            >
              <ArrowLeft className="h-4 w-4" />
            </Button>
          )}
          <div>
            <CardTitle className="text-2xl font-bold">Reset Password</CardTitle>
            <CardDescription>
              Enter your email address and we'll send you a link to reset your password
            </CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {success && (
          <Alert>
            <CheckCircle className="h-4 w-4" />
            <AlertDescription>
              Password reset email sent! Check your inbox and follow the instructions.
            </AlertDescription>
          </Alert>
        )}

        {!success && (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email Address</Label>
              <div className="relative">
                <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  id="email"
                  type="email"
                  placeholder="Enter your email address"
                  value={email}
                  onChange={handleEmailChange}
                  disabled={isLoading}
                  className="pl-10"
                  required
                />
              </div>
              {emailError && (
                <p className="text-xs text-destructive">{emailError}</p>
              )}
            </div>

            <Button
              type="submit"
              className="w-full"
              disabled={isLoading || !email.trim()}
            >
              {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Send Reset Email
            </Button>
          </form>
        )}

        {success && onBackToSignIn && (
          <Button
            variant="outline"
            onClick={onBackToSignIn}
            className="w-full"
          >
            Back to Sign In
          </Button>
        )}

        <div className="text-center text-sm text-muted-foreground">
          <p>
            Remember your password?{' '}
            {onBackToSignIn && (
              <Button
                variant="link"
                className="p-0 h-auto font-normal"
                onClick={onBackToSignIn}
                disabled={isLoading}
              >
                Sign in
              </Button>
            )}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

export default PasswordReset;