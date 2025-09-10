import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { ChevronDown } from "lucide-react";

export const TopNavBar = () => {
  return (
    <nav className="w-full h-16 flex items-center justify-between px-6 md:px-8 lg:px-12">
      {/* Left side - League/Brand */}
      <div className="flex items-center gap-2">
        <div 
          data-us-project="KHxxB8NGQDs95HP5DSf8" 
          style={{width: '200px', height: '80px'}}
        />
        <script 
          type="text/javascript"
          dangerouslySetInnerHTML={{
            __html: `!function(){if(!window.UnicornStudio){window.UnicornStudio={isInitialized:!1};var i=document.createElement("script");i.src="https://cdn.jsdelivr.net/gh/hiunicornstudio/unicornstudio.js@v1.4.30/dist/unicornStudio.umd.js",i.onload=function(){window.UnicornStudio.isInitialized||(UnicornStudio.init(),window.UnicornStudio.isInitialized=!0)},(document.head || document.body).appendChild(i)}}();`
          }}
        />
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