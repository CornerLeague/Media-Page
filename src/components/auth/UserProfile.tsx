import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useFirebaseAuth, useProfileManagement, useEmailVerification, usePasswordManagement } from '@/contexts/FirebaseAuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu';
import { Loader2, User, Mail, Shield, Settings, LogOut, CheckCircle, AlertCircle, Edit3 } from 'lucide-react';

export function UserProfile() {
  const { user, signOut } = useFirebaseAuth();
  const navigate = useNavigate();

  if (!user) return null;

  const handleEditPreferences = () => {
    navigate('/profile/preferences');
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" className="flex items-center gap-2 h-auto p-2" data-testid="user-profile-trigger">
          <Avatar className="w-8 h-8" data-testid="user-avatar">
            <AvatarImage src={user.photoURL || ''} alt={user.displayName || 'User'} />
            <AvatarFallback>
              {(user.displayName?.[0] || user.email?.[0] || 'U').toUpperCase()}
            </AvatarFallback>
          </Avatar>
          <span className="text-sm font-medium hidden sm:inline">
            {user.displayName || user.email}
          </span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56">
        <div className="px-2 py-1.5">
          <p className="text-sm font-medium">{user.displayName || 'User'}</p>
          <p className="text-xs text-muted-foreground">{user.email}</p>
        </div>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={handleEditPreferences}>
          <Edit3 className="mr-2 h-4 w-4" />
          Edit Preferences
        </DropdownMenuItem>
        <UserProfileDialog user={user}>
          <DropdownMenuItem onSelect={(e) => e.preventDefault()}>
            <User className="mr-2 h-4 w-4" />
            Profile Settings
          </DropdownMenuItem>
        </UserProfileDialog>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={() => signOut()}>
          <LogOut className="mr-2 h-4 w-4" />
          Sign out
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

interface UserProfileDialogProps {
  user: any;
  children: React.ReactNode;
}

function UserProfileDialog({ user, children }: UserProfileDialogProps) {
  const [open, setOpen] = useState(false);

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {children}
      </DialogTrigger>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Profile Settings</DialogTitle>
          <DialogDescription>
            Manage your account settings and preferences.
          </DialogDescription>
        </DialogHeader>

        <Tabs defaultValue="profile" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="profile">Profile</TabsTrigger>
            <TabsTrigger value="security">Security</TabsTrigger>
            <TabsTrigger value="account">Account</TabsTrigger>
          </TabsList>

          <TabsContent value="profile" className="space-y-4">
            <ProfileTab user={user} />
          </TabsContent>

          <TabsContent value="security" className="space-y-4">
            <SecurityTab user={user} />
          </TabsContent>

          <TabsContent value="account" className="space-y-4">
            <AccountTab user={user} />
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}

function ProfileTab({ user }: { user: any }) {
  const { updateProfile, isLoading, error, success, clearState } = useProfileManagement();
  const [displayName, setDisplayName] = useState(user?.displayName || '');

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    await updateProfile({ displayName });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <User className="h-5 w-5" />
          Profile Information
        </CardTitle>
        <CardDescription>
          Update your profile details and preferences.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center gap-4">
          <Avatar className="w-16 h-16">
            <AvatarImage src={user?.photoURL || ''} alt={user?.displayName || 'User'} />
            <AvatarFallback className="text-lg">
              {(user?.displayName?.[0] || user?.email?.[0] || 'U').toUpperCase()}
            </AvatarFallback>
          </Avatar>
          <div>
            <p className="text-sm font-medium">{user?.displayName || 'No display name'}</p>
            <p className="text-xs text-muted-foreground">{user?.email}</p>
          </div>
        </div>

        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {success && (
          <Alert>
            <CheckCircle className="h-4 w-4" />
            <AlertDescription>Profile updated successfully!</AlertDescription>
          </Alert>
        )}

        <form onSubmit={handleUpdateProfile} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="displayName">Display Name</Label>
            <Input
              id="displayName"
              value={displayName}
              onChange={(e) => {
                setDisplayName(e.target.value);
                clearState();
              }}
              placeholder="Enter your display name"
              disabled={isLoading}
            />
          </div>

          <div className="space-y-2">
            <Label>Email Address</Label>
            <Input value={user?.email || ''} disabled />
            <p className="text-xs text-muted-foreground">
              Email address cannot be changed directly. Contact support if needed.
            </p>
          </div>

          <Button type="submit" disabled={isLoading || !displayName.trim()}>
            {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Update Profile
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}

function SecurityTab({ user }: { user: any }) {
  const emailVerification = useEmailVerification();
  const passwordManagement = usePasswordManagement();
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      return;
    }
    await passwordManagement.changePassword(currentPassword, newPassword);
    if (passwordManagement.success) {
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    }
  };

  const isPasswordFormValid =
    currentPassword.length >= 6 &&
    newPassword.length >= 6 &&
    confirmPassword === newPassword;

  return (
    <div className="space-y-4">
      {/* Email Verification */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Mail className="h-5 w-5" />
            Email Verification
          </CardTitle>
          <CardDescription>
            Verify your email address to secure your account.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-sm">Email Status:</span>
              <Badge variant={emailVerification.isEmailVerified ? "default" : "secondary"}>
                {emailVerification.isEmailVerified ? 'Verified' : 'Unverified'}
              </Badge>
            </div>
            {!emailVerification.isEmailVerified && (
              <Button
                variant="outline"
                size="sm"
                onClick={emailVerification.sendVerification}
                disabled={emailVerification.isLoading}
              >
                {emailVerification.isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Send Verification
              </Button>
            )}
          </div>

          {emailVerification.error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{emailVerification.error}</AlertDescription>
            </Alert>
          )}

          {emailVerification.success && (
            <Alert>
              <CheckCircle className="h-4 w-4" />
              <AlertDescription>Verification email sent! Check your inbox.</AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Password Change */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Change Password
          </CardTitle>
          <CardDescription>
            Update your password to keep your account secure.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {passwordManagement.error && (
            <Alert variant="destructive" className="mb-4">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{passwordManagement.error}</AlertDescription>
            </Alert>
          )}

          {passwordManagement.success && (
            <Alert className="mb-4">
              <CheckCircle className="h-4 w-4" />
              <AlertDescription>Password updated successfully!</AlertDescription>
            </Alert>
          )}

          <form onSubmit={handlePasswordChange} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="currentPassword">Current Password</Label>
              <Input
                id="currentPassword"
                type="password"
                value={currentPassword}
                onChange={(e) => {
                  setCurrentPassword(e.target.value);
                  passwordManagement.clearState();
                }}
                disabled={passwordManagement.isLoading}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="newPassword">New Password</Label>
              <Input
                id="newPassword"
                type="password"
                value={newPassword}
                onChange={(e) => {
                  setNewPassword(e.target.value);
                  passwordManagement.clearState();
                }}
                disabled={passwordManagement.isLoading}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="confirmPassword">Confirm New Password</Label>
              <Input
                id="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={(e) => {
                  setConfirmPassword(e.target.value);
                  passwordManagement.clearState();
                }}
                disabled={passwordManagement.isLoading}
                required
              />
              {newPassword && confirmPassword && newPassword !== confirmPassword && (
                <p className="text-xs text-destructive">Passwords do not match</p>
              )}
            </div>

            <Button
              type="submit"
              disabled={passwordManagement.isLoading || !isPasswordFormValid}
            >
              {passwordManagement.isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Update Password
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}

function AccountTab({ user }: { user: any }) {
  const { getUserMetadata } = useFirebaseAuth();
  const metadata = getUserMetadata();

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Settings className="h-5 w-5" />
          Account Information
        </CardTitle>
        <CardDescription>
          View your account details and metadata.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label className="text-sm font-medium">User ID</Label>
            <p className="text-sm text-muted-foreground font-mono break-all">{user?.uid}</p>
          </div>

          <div>
            <Label className="text-sm font-medium">Email Verified</Label>
            <p className="text-sm">
              <Badge variant={user?.emailVerified ? "default" : "secondary"}>
                {user?.emailVerified ? 'Yes' : 'No'}
              </Badge>
            </p>
          </div>

          {metadata?.creationTime && (
            <div>
              <Label className="text-sm font-medium">Account Created</Label>
              <p className="text-sm text-muted-foreground">
                {new Date(metadata.creationTime).toLocaleDateString()}
              </p>
            </div>
          )}

          {metadata?.lastSignInTime && (
            <div>
              <Label className="text-sm font-medium">Last Sign In</Label>
              <p className="text-sm text-muted-foreground">
                {new Date(metadata.lastSignInTime).toLocaleDateString()}
              </p>
            </div>
          )}
        </div>

        <Separator />

        <div>
          <Label className="text-sm font-medium">Sign-in Providers</Label>
          <div className="flex flex-wrap gap-2 mt-2">
            {user?.providerData?.map((provider: any, index: number) => (
              <Badge key={index} variant="outline">
                {provider.providerId === 'password' ? 'Email/Password' : provider.providerId}
              </Badge>
            )) || <Badge variant="outline">Email/Password</Badge>}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}