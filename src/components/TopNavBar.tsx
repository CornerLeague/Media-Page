import { ChevronDown } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ThemeToggle } from "@/components/ThemeToggle";
import { UserButton, useAuth, useUser } from "@clerk/clerk-react";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";

export const TopNavBar = () => {
  const { isSignedIn, isLoaded } = useAuth();
  const { user } = useUser();
  const navigate = useNavigate();

  const handleSignIn = () => {
    navigate("/auth/sign-in");
  };

  return (
    <nav className="w-full h-16 flex items-center justify-between px-6 md:px-8 lg:px-12">
      {/* Left side - League/Brand */}
      <div className="flex items-center gap-2">
        <h1 className="font-display font-bold text-2xl md:text-3xl lg:text-4xl text-foreground">
          Corner League Media
        </h1>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <ChevronDown className="h-6 w-6 text-foreground cursor-pointer" />
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start">
            <DropdownMenuItem>NFL</DropdownMenuItem>
            <DropdownMenuItem>NBA</DropdownMenuItem>
            <DropdownMenuItem>MLB</DropdownMenuItem>
            <DropdownMenuItem>NHL</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {/* Right side - Theme Toggle & Profile */}
      <div className="flex items-center gap-3">
        <ThemeToggle />

        {isLoaded ? (
          isSignedIn ? (
            <div className="flex items-center gap-2">
              {user?.firstName && (
                <span className="text-sm font-medium text-foreground hidden sm:inline">
                  Welcome, {user.firstName}
                </span>
              )}
              <UserButton
                appearance={{
                  elements: {
                    avatarBox: "w-10 h-10 border-2 border-border/20",
                    userButtonPopoverCard: "shadow-lg border border-border/20",
                    userButtonPopoverActionButton: "hover:bg-muted/50",
                  }
                }}
                afterSignOutUrl="/auth/sign-in"
              />
            </div>
          ) : (
            <Button
              onClick={handleSignIn}
              variant="outline"
              size="sm"
              className="border-border/20 hover:bg-muted/50"
            >
              Sign In
            </Button>
          )
        ) : (
          <div className="w-10 h-10 animate-pulse bg-muted rounded-full" />
        )}
      </div>
    </nav>
  );
};