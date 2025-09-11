import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { ChevronDown } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ThemeToggle } from "@/components/ThemeToggle";

export const TopNavBar = () => {
  return (
    <nav className="w-full h-16 flex items-center justify-between px-6 md:px-8 lg:px-12">
      {/* Left side - League/Brand */}
      <div className="flex items-center gap-2">
        <h1 className="font-display font-bold text-2xl md:text-3xl lg:text-4xl text-foreground">
          NFL
        </h1>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <ChevronDown className="h-6 w-6 text-foreground cursor-pointer" />
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start">
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {/* Right side - Theme Toggle & Profile */}
      <div className="flex items-center gap-2">
        <ThemeToggle />
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