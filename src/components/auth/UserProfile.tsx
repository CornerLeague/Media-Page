import { useFirebaseAuth } from '@/contexts/FirebaseAuthContext'

export function UserProfile() {
  const { user, signOut } = useFirebaseAuth()

  if (!user) return null

  return (
    <div className="flex items-center gap-2">
      <img
        src={user.photoURL || '/default-avatar.png'}
        alt={user.displayName || 'User'}
        className="w-8 h-8 rounded-full"
      />
      <span className="text-sm font-medium">{user.displayName || user.email}</span>
      <button
        onClick={() => signOut()}
        className="text-sm text-muted-foreground hover:text-foreground"
      >
        Sign out
      </button>
    </div>
  )
}