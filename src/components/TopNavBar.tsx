import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { ChevronDown } from "lucide-react";
import { useEffect, useRef } from "react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

// TypeScript declaration for UnicornStudio
declare global {
  interface Window {
    UnicornStudio?: {
      init: () => void;
      isInitialized?: boolean;
    };
  }
}

export const TopNavBar = () => {
  const unicornRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Initialize UnicornStudio when component mounts
    const initUnicorn = () => {
      if (window.UnicornStudio && !window.UnicornStudio.isInitialized) {
        window.UnicornStudio.init();
        window.UnicornStudio.isInitialized = true;
      }
    };

    // If UnicornStudio is already loaded, initialize
    if (window.UnicornStudio) {
      initUnicorn();
    } else {
      // Wait for script to load
      const checkForUnicorn = setInterval(() => {
        if (window.UnicornStudio) {
          initUnicorn();
          clearInterval(checkForUnicorn);
        }
      }, 100);

      // Clean up interval after 5 seconds
      setTimeout(() => clearInterval(checkForUnicorn), 5000);
    }
  }, []);

  return (
    <nav className="w-full h-16 flex items-center justify-between px-6 md:px-8 lg:px-12">
      {/* Left side - League/Brand */}
      <div className="flex items-center gap-2">
        <div className="relative">
          <div 
            ref={unicornRef}
            data-us-project="KHxxB8NGQDs95HP5DSf8" 
            style={{width: '120px', height: '40px'}}
            className="overflow-hidden"
          />
          {/* Fallback text */}
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <span className="font-display font-bold text-2xl md:text-3xl lg:text-4xl text-foreground">
              NFL
            </span>
          </div>
        </div>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <ChevronDown className="h-6 w-6 text-foreground cursor-pointer" />
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start">
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {/* Right side - Profile */}
      <div className="flex items-center">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Avatar className="h-10 w-10 border-2 border-border/20 cursor-pointer">
              <AvatarImage src="" alt="Profile" />
              <AvatarFallback className="bg-muted text-muted-foreground font-body font-medium">
                U
              </AvatarFallback>
            </Avatar>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem>
              Account Settings
            </DropdownMenuItem>
            <DropdownMenuItem>
              Log Out
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </nav>
  );
};