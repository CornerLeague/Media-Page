import React from 'react';
import { motion } from 'framer-motion';
import { Trophy, Users, TrendingUp, Star } from 'lucide-react';

const WelcomeScreen: React.FC = () => {
  console.log('WelcomeScreen component rendering');

  const features = [
    {
      icon: Trophy,
      title: 'Personalized Content',
      description: 'Get news and updates tailored to your favorite teams and sports'
    },
    {
      icon: Users,
      title: 'Community Insights',
      description: 'Connect with fans and get exclusive insider perspectives'
    },
    {
      icon: TrendingUp,
      title: 'Real-time Updates',
      description: 'Stay on top of scores, trades, and breaking news'
    },
    {
      icon: Star,
      title: 'Premium Features',
      description: 'Access advanced analytics and exclusive content'
    }
  ];

  return (
    <div className="flex flex-col items-center justify-center text-center space-y-8">
      {/* Hero section */}
      <motion.div
        className="space-y-4"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <motion.div
          className="text-6xl mb-4"
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ duration: 0.5, delay: 0.2, type: "spring", stiffness: 200 }}
        >
          🏟️
        </motion.div>

        {/* Title is now provided by OnboardingLayout */}

        <motion.p
          className="text-xl text-muted-foreground max-w-2xl mb-2"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          Your personalized sports media platform
        </motion.p>

        <motion.p
          className="text-lg text-muted-foreground max-w-2xl"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.5 }}
        >
          Let's tailor your sports experience. Choose your favorite sports and teams to get started with content that matters to you.
        </motion.p>
      </motion.div>

      {/* Features grid */}
      <motion.div
        className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl w-full"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.6 }}
      >
        {features.map((feature, index) => (
          <motion.div
            key={feature.title}
            className="flex items-start space-x-4 p-4 rounded-lg bg-card/50 border border-border/50"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.4, delay: 0.8 + index * 0.1 }}
            whileHover={{ scale: 1.02, transition: { duration: 0.2 } }}
          >
            <div className="flex-shrink-0">
              <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                <feature.icon className="w-5 h-5 text-primary" />
              </div>
            </div>
            <div className="text-left">
              <h3 className="font-semibold text-sm mb-1">{feature.title}</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">
                {feature.description}
              </p>
            </div>
          </motion.div>
        ))}
      </motion.div>

      {/* Call to action */}
      <motion.div
        className="text-center space-y-2"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6, delay: 1.2 }}
      >
        <p className="text-sm text-muted-foreground">
          This setup will only take 2-3 minutes
        </p>
        <div className="flex items-center justify-center space-x-1 text-xs text-muted-foreground">
          <span>●</span>
          <span>Choose sports</span>
          <span>●</span>
          <span>Select teams</span>
          <span>●</span>
          <span>Set preferences</span>
        </div>
      </motion.div>
    </div>
  );
};

export default WelcomeScreen;