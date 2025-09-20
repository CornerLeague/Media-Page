// Simple script to bypass onboarding
// Run this in the browser console to mark onboarding as completed

// Set onboarding as completed
localStorage.setItem('corner-league-onboarding-completed', JSON.stringify({
  completed: true,
  completedAt: new Date().toISOString()
}));

// Set some basic user preferences
const preferences = {
  id: 'temp-user-' + Date.now(),
  sports: ['nfl', 'nba'],
  teams: ['Chiefs', 'Lakers'],
  preferences: {
    aiSummaryLevel: 3,
    notifications: {
      gameAlerts: true,
      newsDigest: true,
      tradingUpdates: false
    }
  },
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString()
};

localStorage.setItem('corner-league-user-preferences', JSON.stringify(preferences));

console.log('Onboarding bypassed! Refresh the page to see the main dashboard.');
console.log('Preferences set:', preferences);