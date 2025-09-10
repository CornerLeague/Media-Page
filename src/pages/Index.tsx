import { TopNavBar } from "@/components/TopNavBar";
import { AISummarySection } from "@/components/AISummarySection";
import { SportsFeedSection } from "@/components/SportsFeedSection";
import { BestSeatsSection } from "@/components/BestSeatsSection";
import { FanExperiencesSection } from "@/components/FanExperiencesSection";

const Index = () => {
  return (
    <div className="min-h-screen bg-background font-body">
      {/* Navigation */}
      <TopNavBar />
      
      {/* Main Content Area */}
      <div className="flex flex-col min-h-[calc(100vh-4rem)]">
        {/* AI Summary - Takes available space */}
        <AISummarySection />
        
        {/* Sports Feed - Bottom sections */}
        <div className="pb-4 sm:pb-8">
          <SportsFeedSection />
          <BestSeatsSection />
          <FanExperiencesSection />
        </div>
      </div>
    </div>
  );
};

export default Index;
