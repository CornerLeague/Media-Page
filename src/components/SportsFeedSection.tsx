import { useState } from "react";
import { SportsFeedCard } from "./SportsFeedCard";
import { ChevronDown } from "lucide-react";
import nflHero from "@/assets/nfl-hero.jpg";
import nbaAction from "@/assets/nba-action.jpg";
import soccerAction from "@/assets/soccer-action.jpg";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useToast } from "@/hooks/use-toast";

export const SportsFeedSection = () => {
  const [selectedCategory, setSelectedCategory] = useState("Latest Stories");
  const { toast } = useToast();

  const feedData = {
    "Latest Stories": [
      {
        id: 1,
        title: "Chiefs Dominate AFC Championship",
        description: "Patrick Mahomes leads Kansas City to a commanding victory with 3 touchdowns and 340 passing yards.",
        image: nflHero,
        time: "2 hours ago",
        category: "NFL"
      },
      {
        id: 2,
        title: "Lakers Trade Rumors Intensify",
        description: "Multiple sources report active discussions around potential roster moves before the deadline.",
        image: nbaAction,
        time: "4 hours ago",
        category: "NBA"
      },
      {
        id: 3,
        title: "World Cup Qualifier Results",
        description: "Dramatic late goals decide crucial matches in European qualifying rounds.",
        image: soccerAction,
        time: "6 hours ago",
        category: "Soccer"
      },
      {
        id: 4,
        title: "Draft Prospects Rising",
        description: "College standouts making impressive cases for early selection in upcoming draft.",
        image: nflHero,
        time: "8 hours ago",
        category: "College"
      }
    ],
    "Injuries": [
      {
        id: 1,
        title: "Star QB Out 4-6 Weeks",
        description: "Team confirms ACL injury will sideline franchise quarterback for remainder of regular season.",
        image: nflHero,
        time: "1 hour ago",
        category: "Injury Report"
      },
      {
        id: 2,
        title: "All-Pro Defender Returns",
        description: "Defensive captain cleared for contact after recovering from shoulder surgery.",
        image: nbaAction,
        time: "3 hours ago",
        category: "Recovery Update"
      },
      {
        id: 3,
        title: "Rookie Placed on IR",
        description: "First-year player will miss 8 weeks with hamstring injury sustained in practice.",
        image: soccerAction,
        time: "5 hours ago",
        category: "Injury Report"
      }
    ],
    "Roster Moves": [
      {
        id: 1,
        title: "Veteran Linebacker Signed",
        description: "Team adds experienced pass rusher to strengthen defensive rotation.",
        image: nflHero,
        time: "30 minutes ago",
        category: "Signing"
      },
      {
        id: 2,
        title: "Practice Squad Elevation",
        description: "Wide receiver promoted to active roster ahead of crucial division matchup.",
        image: nbaAction,
        time: "2 hours ago",
        category: "Promotion"
      },
      {
        id: 3,
        title: "Veteran Released",
        description: "Team parts ways with longtime contributor to create salary cap space.",
        image: soccerAction,
        time: "4 hours ago",
        category: "Release"
      }
    ],
    "Trade Rumors": [
      {
        id: 1,
        title: "Superstar on Trading Block",
        description: "Multiple teams reportedly interested in acquiring Pro Bowl receiver before deadline.",
        image: nflHero,
        time: "45 minutes ago",
        category: "Trade Talk"
      },
      {
        id: 2,
        title: "Draft Pick Package Discussed",
        description: "Front office exploring options to move up in upcoming draft for elite prospect.",
        image: nbaAction,
        time: "2 hours ago",
        category: "Draft Trade"
      },
      {
        id: 3,
        title: "Contender Pursuing Edge Rusher",
        description: "Playoff-bound team looking to add pass rush help for postseason run.",
        image: soccerAction,
        time: "3 hours ago",
        category: "Trade Interest"
      }
    ],
    "Depth Chart": [
      {
        id: 1,
        title: "Rookie Climbs Depth Chart",
        description: "First-year player now listed as second-string after impressive preseason performance.",
        image: nflHero,
        time: "1 hour ago",
        category: "Position Battle"
      },
      {
        id: 2,
        title: "Starting Lineup Changes",
        description: "Coach announces new starting five following bye week evaluations.",
        image: nbaAction,
        time: "3 hours ago",
        category: "Lineup Update"
      },
      {
        id: 3,
        title: "Special Teams Captain Named",
        description: "Veteran player assigned leadership role on special teams units.",
        image: soccerAction,
        time: "5 hours ago",
        category: "Special Teams"
      }
    ]
  };

  const handleCategorySelect = (category: string) => {
    setSelectedCategory(category);
    toast({
      title: "Category Updated",
      description: `Now showing ${category.toLowerCase()} content`,
    });
  };

  const currentFeedItems = feedData[selectedCategory as keyof typeof feedData] || feedData["Latest Stories"];

  return (
    <section className="w-full">
      <div className="px-4 sm:px-6 md:px-8 lg:px-12">
        {/* AI Summary Section */}
        <div className="mb-6 mt-12">
          <h2 className="font-display font-semibold text-base text-foreground mb-3">
            AI Summary
          </h2>
          <p className="font-body text-muted-foreground text-sm leading-relaxed">
            Today's key highlights: Chiefs advance with dominant performance, Lakers exploring trade options ahead of deadline, and World Cup qualifiers deliver dramatic finishes across Europe.
          </p>
        </div>
        
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <h2 className="font-display font-semibold text-base text-foreground mb-4 mt-20 flex items-center gap-2 cursor-pointer hover:text-primary transition-colors">
              {selectedCategory}
              <ChevronDown className="w-4 h-4" />
            </h2>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start">
            <DropdownMenuItem onClick={() => handleCategorySelect("Latest Stories")}>
              Latest Stories
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => handleCategorySelect("Injuries")}>
              Injuries
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => handleCategorySelect("Roster Moves")}>
              Roster Moves
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => handleCategorySelect("Trade Rumors")}>
              Trade Rumors
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => handleCategorySelect("Depth Chart")}>
              Depth Chart
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
      
      <div className="overflow-x-auto scrollbar-hide">
        <div className="flex gap-3 sm:gap-4 px-4 sm:px-6 md:px-8 lg:px-12 pb-4">
          {currentFeedItems.map(item => (
            <SportsFeedCard 
              key={item.id} 
              title={item.title} 
              description={item.description} 
              image={item.image} 
              time={item.time} 
              category={item.category} 
            />
          ))}
        </div>
      </div>
    </section>
  );
};