import { SportsFeedCard } from "./SportsFeedCard";
import nflHero from "@/assets/nfl-hero.jpg";
import nbaAction from "@/assets/nba-action.jpg";
import soccerAction from "@/assets/soccer-action.jpg";

export const SportsFeedSection = () => {
  const feedItems = [
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
  ];

  return (
    <section className="w-full">
      <div className="px-6 md:px-8 lg:px-12">
        {/* AI Summary Section */}
        <div className="mb-6">
          <h2 className="font-display font-semibold text-base text-foreground mb-3">
            AI Summary
          </h2>
          <p className="font-body text-muted-foreground text-sm leading-relaxed">
            Today's key highlights: Chiefs advance with dominant performance, Lakers exploring trade options ahead of deadline, and World Cup qualifiers deliver dramatic finishes across Europe.
          </p>
        </div>
        
        <h2 className="font-display font-semibold text-base text-foreground mb-4">
          Latest Updates
        </h2>
      </div>
      
      <div className="overflow-x-auto scrollbar-hide">
        <div className="flex gap-4 px-6 md:px-8 lg:px-12 pb-4">
          {feedItems.map((item) => (
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