import { Card } from "@/components/ui/card";
import { MapPin, Calendar, DollarSign } from "lucide-react";

interface SeatData {
  id: number;
  venue: string;
  game: string;
  section: string;
  price: string;
  date: string;
  time: string;
  image: string;
}

export const BestSeatsSection = () => {
  const bestSeats: SeatData[] = [
    {
      id: 1,
      venue: "Arrowhead Stadium",
      game: "Chiefs vs Patriots",
      section: "Section 137, Row 15",
      price: "$285",
      date: "Jan 15",
      time: "1:00 PM",
      image: "/api/placeholder/300/180"
    },
    {
      id: 2,
      venue: "Crypto.com Arena",
      game: "Lakers vs Warriors",
      section: "Section 111, Row 8",
      price: "$420",
      date: "Jan 18",
      time: "7:30 PM",
      image: "/api/placeholder/300/180"
    },
    {
      id: 3,
      venue: "SoFi Stadium",
      game: "Rams vs Seahawks",
      section: "Section 225, Row 12",
      price: "$195",
      date: "Jan 22",
      time: "4:25 PM",
      image: "/api/placeholder/300/180"
    },
    {
      id: 4,
      venue: "Madison Square Garden",
      game: "Knicks vs Celtics",
      section: "Section 108, Row 6",
      price: "$350",
      date: "Jan 25",
      time: "8:00 PM",
      image: "/api/placeholder/300/180"
    }
  ];

  return (
    <section className="w-full mt-6 sm:mt-8">
      <div className="px-4 sm:px-6 md:px-8 lg:px-12">
        <h2 className="font-display font-semibold text-base text-foreground mb-4">
          Best Seats
        </h2>
      </div>
      
      <div className="overflow-x-auto scrollbar-hide">
        <div className="flex gap-3 sm:gap-4 px-4 sm:px-6 md:px-8 lg:px-12 pb-4">
          {bestSeats.map(seat => (
            <Card key={seat.id} className="w-72 sm:w-80 flex-shrink-0 overflow-hidden border-0 shadow-sm bg-white/10 backdrop-blur-md hover:bg-white/20 transition-all duration-normal cursor-pointer">
              <div className="relative h-32 overflow-hidden bg-gradient-to-br from-primary/20 to-primary/5">
                <div className="absolute inset-0 flex items-center justify-center">
                  <MapPin className="w-12 h-12 text-primary/40" />
                </div>
                <div className="absolute top-3 right-3">
                  <span className="px-2 py-1 text-xs font-medium font-body bg-primary text-primary-foreground rounded-md">
                    {seat.price}
                  </span>
                </div>
              </div>
              
              <div className="p-4 space-y-3">
                <div>
                  <h3 className="font-display font-semibold text-sm text-foreground leading-tight">
                    {seat.game}
                  </h3>
                  <p className="text-muted-foreground font-body text-xs mt-1">
                    {seat.venue}
                  </p>
                </div>
                
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <Calendar className="w-3 h-3" />
                  <span className="font-body">{seat.date} at {seat.time}</span>
                </div>
                
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <MapPin className="w-3 h-3" />
                  <span className="font-body">{seat.section}</span>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};