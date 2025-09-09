import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

export const TopNavBar = () => {
  return (
    <nav className="w-full h-16 flex items-center justify-between px-6 md:px-8 lg:px-12">
      {/* Left side - League/Brand */}
      <div className="flex items-center">
        <h1 className="font-display font-bold text-xl md:text-2xl text-foreground">
          NFL
        </h1>
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