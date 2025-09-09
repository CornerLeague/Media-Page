import { TopNavBar } from "@/components/TopNavBar";
import { AISummarySection } from "@/components/AISummarySection";
import { SportsFeedSection } from "@/components/SportsFeedSection";

const Index = () => {
  return (
    <div className="min-h-screen bg-background font-body">
      {/* Navigation */}
      <TopNavBar />
      
      {/* Main Content Area */}
      <div className="flex flex-col h-[calc(100vh-4rem)]">
        {/* AI Summary - Takes most of the space */}
        <AISummarySection />
        
        {/* Sports Feed - Fixed at bottom */}
        <div className="mt-auto pb-8">
          <SportsFeedSection />
        </div>
      </div>
    </div>
  );
};

export default Index;
