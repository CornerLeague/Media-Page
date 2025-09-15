import React from 'react';

const WelcomeScreen: React.FC = () => {
  console.log('WelcomeScreen component rendering');

  // TEMPORARY: Simplified version for debugging
  return (
    <div className="flex flex-col items-center justify-center min-h-96 p-8 text-center">
      <h1 className="text-3xl font-bold mb-4">Welcome to Corner League Media</h1>
      <p className="text-lg text-muted-foreground mb-6">
        Your personalized sports media platform
      </p>
      <div className="bg-card p-4 rounded-lg">
        <p className="text-sm text-muted-foreground">
          This is the welcome screen - working properly!
        </p>
      </div>
    </div>
  );
};

export default WelcomeScreen;