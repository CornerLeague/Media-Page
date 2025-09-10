import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { ChevronDown } from "lucide-react";

export const TopNavBar = () => {
  return (
    <nav className="w-full h-16 flex items-center justify-between px-6 md:px-8 lg:px-12">
      {/* Left side - League/Brand */}
      <div className="flex items-center gap-2">
        <h1 className="font-display font-bold text-2xl md:text-3xl lg:text-4xl text-foreground">
          NFL
        </h1>
        <ChevronDown className="h-6 w-6 text-foreground" />
      </div>

      {/* Right side - Profile */}
      <div className="flex items-center">
        <Avatar className="h-10 w-10 border-2 border-border/20">
          <AvatarImage src="" alt="Profile" />
          <AvatarFallback className="bg-muted text-muted-foreground font-body font-medium">
            U
          </AvatarFallback>
        </Avatar>
      </div>
    </nav>
  );
};