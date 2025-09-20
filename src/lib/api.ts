import { UserPreferences } from '@/types'

// Mock API implementation for development
export const sportsApi = {
  async getPreferences(): Promise<UserPreferences | null> {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 500))

    // Return mock preferences
    return {
      sports: ['nfl', 'nba', 'mlb'],
      teams: ['Chiefs', 'Lakers', 'Yankees'],
      aiSummaryLevel: 3,
      notifications: {
        gameAlerts: true,
        newsDigest: true,
        tradingUpdates: false
      }
    }
  },

  async updatePreferences(preferences: UserPreferences): Promise<void> {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 500))
    console.log('Updated preferences:', preferences)
  }
}