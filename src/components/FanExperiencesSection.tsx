import { Card } from "@/components/ui/card";
import { Star, Users, Calendar, Clock } from "lucide-react";

interface ExperienceData {
  id: number;
  title: string;
  venue: string;
  description: string;
  rating: number;
  capacity: string;
  date: string;
  duration: string;
  price: string;
}

export const FanExperiencesSection = () => {
  const experiences: ExperienceData[] = [
    {
      id: 1,
      title: "VIP Stadium Tour",
      venue: "Arrowhead Stadium",
      description: "Behind-the-scenes access to locker rooms, field, and press box",
      rating: 4.9,
      capacity: "Limited to 20 fans",
      date: "Jan 12",
      duration: "2 hours",
      price: "$85"
    },
    {
      id: 2,
      title: "Meet & Greet",
      venue: "Crypto.com Arena",
      description: "Exclusive player meet and greet with photo opportunities",
      rating: 4.8,
      capacity: "Limited to 15 fans", 
      date: "Jan 16",
      duration: "45 minutes",
      price: "$150"
    },
    {
      id: 3,
      title: "Pregame Warmups",
      venue: "SoFi Stadium",
      description: "Watch team warmups from exclusive field-level access",
      rating: 4.7,
      capacity: "Limited to 30 fans",
      date: "Jan 20",
      duration: "1 hour",
      price: "$65"
    },
    {
      id: 4,
      title: "Courtside Experience",
      venue: "Madison Square Garden",
      description: "Premium courtside viewing with complimentary refreshments",
      rating: 4.9,
      capacity: "Limited to 10 fans",
      date: "Jan 23",
      duration: "3 hours",
      price: "$250"
    }
  ];

  return (
    <section className="w-full mt-6 sm:mt-8">
      <div className="px-4 sm:px-6 md:px-8 lg:px-12">
        <h2 className="font-display font-semibold text-base text-foreground mb-4">
          Fan Experiences
        </h2>
      </div>
      
      <div className="overflow-x-auto scrollbar-hide">
        <div className="flex gap-3 sm:gap-4 px-4 sm:px-6 md:px-8 lg:px-12 pb-4">
          {experiences.map(experience => (
            <Card key={experience.id} className="w-72 sm:w-80 flex-shrink-0 overflow-hidden border-0 shadow-sm bg-white/10 backdrop-blur-md hover:bg-white/20 transition-all duration-normal cursor-pointer">
              <div className="relative h-32 overflow-hidden bg-gradient-to-br from-accent/20 to-accent/5">
                <div className="absolute inset-0 flex items-center justify-center">
                  <Star className="w-12 h-12 text-accent/40" />
                </div>
                <div className="absolute top-3 right-3">
                  <span className="px-2 py-1 text-xs font-medium font-body bg-accent text-accent-foreground rounded-md">
                    {experience.price}
                  </span>
                </div>
                <div className="absolute top-3 left-3">
                  <div className="flex items-center gap-1 px-2 py-1 bg-background/80 rounded-md">
                    <Star className="w-3 h-3 text-yellow-500 fill-current" />
                    <span className="text-xs font-medium text-foreground">{experience.rating}</span>
                  </div>
                </div>
              </div>
              
              <div className="p-4 space-y-3">
                <div>
                  <h3 className="font-display font-semibold text-sm text-foreground leading-tight">
                    {experience.title}
                  </h3>
                  <p className="text-muted-foreground font-body text-xs mt-1">
                    {experience.venue}
                  </p>
                </div>
                
                <p className="text-xs text-muted-foreground font-body leading-relaxed">
                  {experience.description}
                </p>
                
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <Calendar className="w-3 h-3" />
                  <span className="font-body">{experience.date}</span>
                </div>
                
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    <span className="font-body">{experience.duration}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Users className="w-3 h-3" />
                    <span className="font-body text-xs">{experience.capacity}</span>
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};