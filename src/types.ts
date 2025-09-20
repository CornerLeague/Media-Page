export interface UserPreferences {
  sports: string[]
  teams: string[]
  aiSummaryLevel: number
  notifications: {
    gameAlerts: boolean
    newsDigest: boolean
    tradingUpdates: boolean
  }
}