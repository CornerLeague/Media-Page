import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import {
  CheckCircle,
  Trophy,
  Users,
  Settings,
  Sparkles,
  ArrowRight,
  Heart,
  Star,
  Zap,
} from 'lucide-react';
import { useOnboarding } from '@/hooks/useOnboarding';
import { AVAILABLE_SPORTS } from '@/data/sports';
import { TEAMS } from '@/data/teams';

const OnboardingComplete: React.FC = () => {
  const { userPreferences } = useOnboarding();
  const [showCelebration, setShowCelebration] = useState(false);

  // Trigger celebration animation
  useEffect(() => {
    const timer = setTimeout(() => {
      setShowCelebration(true);
    }, 300);

    return () => clearTimeout(timer);
  }, []);

  // Get user's selections for display
  const selectedSports = userPreferences.sports || [];
  const selectedTeams = userPreferences.teams || [];
  const preferences = userPreferences.preferences;

  const enabledNewsTypes = preferences?.newsTypes?.filter(nt => nt.enabled) || [];
  const notificationCount = preferences?.notifications
    ? Object.values(preferences.notifications).filter(Boolean).length
    : 0;

  // Get sport and team details for display
  const sportsDetails = selectedSports.map(sport =>
    AVAILABLE_SPORTS.find(s => s.id === sport.sportId)
  ).filter(Boolean);

  const teamsDetails = selectedTeams.map(team =>
    TEAMS.find(t => t.id === team.teamId)
  ).filter(Boolean);

  const achievements = [
    {
      icon: Trophy,
      title: 'Sports Selected',
      count: selectedSports.length,
      description: 'Your favorite sports',
    },
    {
      icon: Users,
      title: 'Teams Chosen',
      count: selectedTeams.length,
      description: 'Teams you follow',
    },
    {
      icon: Settings,
      title: 'Preferences Set',
      count: enabledNewsTypes.length,
      description: 'Content types enabled',
    },
  ];

  return (
    <div className="space-y-8">
      {/* Success Header with Animation */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-center space-y-4"
      >
        <div className="flex justify-center mb-6">
          <div className="relative">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
              className="h-20 w-20 bg-green-500 rounded-full flex items-center justify-center"
            >
              <CheckCircle className="h-10 w-10 text-white" />
            </motion.div>

            {/* Celebration particles */}
            {showCelebration && (
              <>
                {[...Array(6)].map((_, i) => (
                  <motion.div
                    key={i}
                    initial={{ scale: 0, rotate: 0 }}
                    animate={{
                      scale: [0, 1, 0],
                      rotate: [0, 180, 360],
                      x: [0, Math.cos(i * 60 * Math.PI / 180) * 40],
                      y: [0, Math.sin(i * 60 * Math.PI / 180) * 40],
                    }}
                    transition={{
                      delay: 0.5 + i * 0.1,
                      duration: 1.5,
                      repeat: 2,
                    }}
                    className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2"
                  >
                    <Zap className="h-4 w-4 text-yellow-500" />
                  </motion.div>
                ))}
              </>
            )}

            <motion.div
              initial={{ scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ delay: 0.4, type: "spring" }}
              className="absolute -top-1 -right-1"
            >
              <Sparkles className="h-6 w-6 text-yellow-500" />
            </motion.div>
          </div>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.5 }}
          className="text-4xl font-bold tracking-tight"
        >
          🎉
        </motion.div>

        <motion.p
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.5 }}
          className="text-xl text-muted-foreground max-w-2xl mx-auto"
        >
          Your personalized sports experience is ready. We've tailored everything
          based on your preferences to bring you the content you care about most.
        </motion.p>
      </motion.div>

      {/* Achievements */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6, duration: 0.5 }}
        className="grid grid-cols-1 md:grid-cols-3 gap-4"
      >
        {achievements.map((achievement, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{
              delay: 0.7 + index * 0.1,
              duration: 0.4,
              type: "spring",
              stiffness: 100,
            }}
          >
            <Card className="text-center border-2 border-green-200 bg-green-50 dark:bg-green-950 dark:border-green-800 hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                <div className="flex flex-col items-center space-y-2">
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ delay: 0.8 + index * 0.1, type: "spring" }}
                  >
                    <achievement.icon className="h-8 w-8 text-green-600 dark:text-green-400" />
                  </motion.div>
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.9 + index * 0.1 }}
                    className="text-3xl font-bold text-green-700 dark:text-green-300"
                  >
                    {achievement.count}
                  </motion.div>
                  <div className="font-semibold">{achievement.title}</div>
                  <p className="text-sm text-muted-foreground">
                    {achievement.description}
                  </p>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </motion.div>

      {/* Summary of Selections */}
      <Card>
        <CardContent className="p-6 space-y-6">
          <h2 className="text-lg font-semibold flex items-center">
            <Star className="h-5 w-5 mr-2 text-yellow-500" />
            Your Personalized Setup
          </h2>

          {/* Sports Summary */}
          {sportsDetails.length > 0 && (
            <div>
              <h4 className="font-medium mb-3 flex items-center text-sm">
                <Trophy className="h-4 w-4 mr-2" />
                Favorite Sports ({sportsDetails.length})
              </h4>
              <div className="flex flex-wrap gap-2">
                {sportsDetails.map((sport, index) => {
                  const userSport = selectedSports.find(s => s.sportId === sport?.id);
                  return sport ? (
                    <Badge key={sport.id} variant="secondary" className="text-sm">
                      {sport.icon} {sport.name}
                      {userSport && (
                        <span className="ml-1 text-xs opacity-75">
                          #{userSport.rank}
                        </span>
                      )}
                    </Badge>
                  ) : null;
                })}
              </div>
            </div>
          )}

          {/* Teams Summary */}
          {teamsDetails.length > 0 && (
            <div>
              <h4 className="font-medium mb-3 flex items-center text-sm">
                <Users className="h-4 w-4 mr-2" />
                Favorite Teams ({teamsDetails.length})
              </h4>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
                {teamsDetails.map((team) => {
                  const userTeam = selectedTeams.find(t => t.teamId === team?.id);
                  return team ? (
                    <div
                      key={team.id}
                      className="flex items-center space-x-2 p-2 bg-muted/50 rounded-md"
                    >
                      <div className="text-sm">{team.logo}</div>
                      <div className="min-w-0 flex-1">
                        <div className="text-sm font-medium truncate">
                          {team.market} {team.name}
                        </div>
                        <div className="text-xs text-muted-foreground">
                          {team.league}
                          {userTeam && (
                            <span className="ml-1">
                              • {userTeam.affinityScore}% match
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  ) : null;
                })}
              </div>
            </div>
          )}

          <Separator />

          {/* Content Preferences Summary */}
          <div>
            <h4 className="font-medium mb-3 flex items-center text-sm">
              <Settings className="h-4 w-4 mr-2" />
              Content Preferences
            </h4>
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span>Content Frequency:</span>
                <Badge variant="outline">
                  {preferences?.contentFrequency || 'Standard'}
                </Badge>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span>News Types Enabled:</span>
                <Badge variant="outline">
                  {enabledNewsTypes.length} of {preferences?.newsTypes?.length || 6}
                </Badge>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span>Notifications Enabled:</span>
                <Badge variant="outline">
                  {notificationCount} of 5
                </Badge>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* What's Next */}
      <Card className="bg-primary/5 border-primary/20">
        <CardContent className="p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center">
            <Heart className="h-5 w-5 mr-2 text-primary" />
            What's Next?
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div className="flex items-start space-x-2">
              <ArrowRight className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
              <div>
                <div className="font-medium">Personalized Feed</div>
                <div className="text-muted-foreground">
                  Start seeing content tailored to your favorite teams and sports
                </div>
              </div>
            </div>
            <div className="flex items-start space-x-2">
              <ArrowRight className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
              <div>
                <div className="font-medium">Smart Recommendations</div>
                <div className="text-muted-foreground">
                  Discover relevant content and trending discussions
                </div>
              </div>
            </div>
            <div className="flex items-start space-x-2">
              <ArrowRight className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
              <div>
                <div className="font-medium">Live Updates</div>
                <div className="text-muted-foreground">
                  Get real-time scores and breaking news for your teams
                </div>
              </div>
            </div>
            <div className="flex items-start space-x-2">
              <ArrowRight className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
              <div>
                <div className="font-medium">Exclusive Content</div>
                <div className="text-muted-foreground">
                  Access premium analysis and insider information
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Privacy Note */}
      <div className="text-center max-w-md mx-auto">
        <p className="text-xs text-muted-foreground">
          Your preferences have been saved locally and can be updated anytime in your settings.
          We respect your privacy and will never share your personal information.
        </p>
      </div>
    </div>
  );
};

export default OnboardingComplete;