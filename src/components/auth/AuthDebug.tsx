import { useFirebaseAuth } from "@/contexts/FirebaseAuthContext";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export function AuthDebug() {
  const { isAuthenticated, isLoading, user } = useFirebaseAuth();

  if (isLoading) {
    return (
      <Card className="m-4">
        <CardHeader>
          <CardTitle>Auth Debug</CardTitle>
        </CardHeader>
        <CardContent>
          <Badge variant="secondary">Loading...</Badge>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="m-4">
      <CardHeader>
        <CardTitle>Auth Debug</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        <div className="flex items-center gap-2">
          <span className="font-medium">Signed In:</span>
          <Badge variant={isAuthenticated ? "default" : "destructive"}>
            {isAuthenticated ? "Yes" : "No"}
          </Badge>
        </div>

        {isAuthenticated && user && (
          <>
            <div className="flex items-center gap-2">
              <span className="font-medium">User ID:</span>
              <code className="text-sm bg-muted px-2 py-1 rounded">
                {user.uid}
              </code>
            </div>

            <div className="flex items-center gap-2">
              <span className="font-medium">Email:</span>
              <span className="text-sm">
                {user.email || "No email"}
              </span>
            </div>

            <div className="flex items-center gap-2">
              <span className="font-medium">Name:</span>
              <span className="text-sm">
                {user.displayName || "No display name"}
              </span>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}