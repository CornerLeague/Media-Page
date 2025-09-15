import { SignIn as ClerkSignIn } from "@clerk/clerk-react";
import { Card, CardContent } from "@/components/ui/card";

export default function SignIn() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="font-display font-bold text-4xl text-foreground mb-2">
            Corner League Media
          </h1>
          <p className="text-muted-foreground">
            Sign in to your sports media platform
          </p>
        </div>

        <Card className="border border-border/20 shadow-lg">
          <CardContent className="p-0">
            <ClerkSignIn
              appearance={{
                elements: {
                  rootBox: "w-full",
                  card: "border-0 shadow-none",
                  headerTitle: "text-2xl font-display font-semibold",
                  headerSubtitle: "text-muted-foreground",
                  socialButtonsBlockButton: "border border-border hover:bg-muted/50",
                  socialButtonsBlockButtonText: "font-medium",
                  formButtonPrimary: "bg-primary hover:bg-primary/90 text-primary-foreground",
                  formFieldInput: "border-border focus:border-primary",
                  footerActionLink: "text-primary hover:text-primary/80",
                }
              }}
              redirectUrl="/onboarding"
              signUpUrl="/auth/sign-up"
            />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}