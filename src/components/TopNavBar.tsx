import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { ChevronDown } from "lucide-react";

export const TopNavBar = () => {
  return (
    <nav className="w-full h-16 flex items-center justify-between px-6 md:px-8 lg:px-12">
      {/* Left side - League/Brand */}
      <div className="flex items-center gap-2">
        <div className="relative group cursor-pointer">
          <div className="font-display font-bold text-2xl md:text-3xl lg:text-4xl text-foreground 
                          relative z-10 transition-all duration-300 
                          hover:text-transparent hover:bg-gradient-to-r hover:from-primary hover:to-accent hover:bg-clip-text
                          [text-shadow:2px_2px_0px_hsl(var(--primary)/0.3),-2px_-2px_0px_hsl(var(--accent)/0.3)]
                          group-hover:[filter:blur(0.5px)_contrast(1.2)]">
            NFL
          </div>
          <div className="absolute inset-0 font-display font-bold text-2xl md:text-3xl lg:text-4xl 
                          text-primary/20 
                          transform translate-x-0.5 translate-y-0.5 
                          group-hover:translate-x-1 group-hover:translate-y-1 
                          transition-all duration-300 z-0">
            NFL
          </div>
          <div className="absolute inset-0 font-display font-bold text-2xl md:text-3xl lg:text-4xl 
                          text-accent/20 
                          transform -translate-x-0.5 -translate-y-0.5 
                          group-hover:-translate-x-1 group-hover:-translate-y-1 
                          transition-all duration-300 z-0">
            NFL
          </div>
        </div>
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