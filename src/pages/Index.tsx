import { TopNavBar } from "@/components/TopNavBar";
import { AISummarySection } from "@/components/AISummarySection";
import { SportsFeedSection } from "@/components/SportsFeedSection";
import { BestSeatsSection } from "@/components/BestSeatsSection";
import { FanExperiencesSection } from "@/components/FanExperiencesSection";

const Index = () => {
  return (
    <div className="min-h-screen bg-background font-body relative">
      {/* Navigation */}
      <TopNavBar />
      
      {/* Main Content Area */}
      <div className="flex flex-col h-[calc(100vh-4rem)] relative z-10">
        {/* AI Summary - Takes most of the space */}
        <AISummarySection />
        
        {/* Sports Feed - Fixed at bottom */}
        <div className="mt-auto pb-8">
          <SportsFeedSection />
          <BestSeatsSection />
          <FanExperiencesSection />
        </div>
      </div>
      
      {/* Background Effect at Bottom */}
      <div className="fixed bottom-0 left-0 w-full h-[900px] z-0 pointer-events-none">
        <div 
          data-us-project="WU9amvznpgPeJhQ4RhJU" 
          style={{width: '1440px', height: '900px', margin: '0 auto'}}
        />
        <script 
          type="text/javascript"
          dangerouslySetInnerHTML={{
            __html: `!function(){if(!window.UnicornStudio){window.UnicornStudio={isInitialized:!1};var i=document.createElement("script");i.src="https://cdn.jsdelivr.net/gh/hiunicornstudio/unicornstudio.js@v1.4.30/dist/unicornStudio.umd.js",i.onload=function(){window.UnicornStudio.isInitialized||(UnicornStudio.init(),window.UnicornStudio.isInitialized=!0)},(document.head || document.body).appendChild(i)}}();`
          }}
        />
      </div>
    </div>
  );
};

export default Index;
