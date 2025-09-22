"""
SQLAlchemy Models for Corner League Media
"""

from .base import Base, TimestampMixin
from .sports import Sport, League, Team, TeamLeagueMembership, ProfessionalDivision, TeamDivisionMembership
from .users import (
    User,
    UserSportPreference,
    UserTeamPreference,
    UserNewsPreference,
    UserNotificationSettings,
)
from .games import Game, GameEvent
from .content import (
    FeedSource,
    FeedSourceMapping,
    FeedSnapshot,
    Article,
    ArticleSport,
    ArticleTeam,
    AISummary,
)
from .players import Player, DepthChartEntry
from .tickets import TicketProvider, TicketDeal
from .experiences import FanExperience, UserExperienceRegistration
from .analytics import UserInteraction, ContentPerformance
from .college import (
    Division, CollegeConference, College, CollegeTeam,
    AcademicYear, Season, ConferenceMembership, SeasonConfiguration
)
from .college_phase3 import Venue, Tournament, TournamentBracket, TournamentGame, TournamentVenue
from .college_games import CollegeGame
# Temporarily comment out to resolve Player class conflict
# from .college_phase4 import (
#     Player as CollegePlayer, TeamStatistics, PlayerStatistics,
#     Rankings, AdvancedMetrics, SeasonRecords
# )
from .college_phase5_content import (
    CollegeContent, InjuryReport, RecruitingNews, CoachingNews,
    ContentTeamAssociation, ContentClassification
)
from .college_phase6_personalization import (
    UserCollegePreferences, BracketPrediction, BracketChallenge,
    BracketChallengeParticipation, UserCollegeNotificationSettings,
    PersonalizedFeed, UserEngagementMetrics, UserPersonalizationProfile
)
from .college_football_phase1 import (
    FootballTeam, FootballPlayer, FootballGame, FootballRoster, FootballSeason
)
from .college_football_phase3 import (
    BowlGame, BowlTieIn, BowlSelection,
    CollegeFootballPlayoff, CFPTeam, CFPGame,
    ConferenceChampionship, RivalryGame, RivalryGameHistory,
    PostseasonTournament
)
from .college_football_phase4 import (
    FootballRecruitingClass, FootballRecruit, FootballRecruitingOffer, FootballRecruitingVisit,
    FootballTransferPortalEntry, FootballCoachingStaff, FootballNILDeal, FootballEligibilityTracking
)
from .college_football_phase5_content import (
    FootballContent, FootballInjuryReport, FootballRecruitingNews, FootballCoachingNews,
    FootballDepthChartUpdate, FootballGamePreview, FootballBowlNews
)

__all__ = [
    # Base
    "Base",
    "TimestampMixin",
    # Sports
    "Sport",
    "League",
    "Team",
    "TeamLeagueMembership",
    "ProfessionalDivision",
    "TeamDivisionMembership",
    # Users
    "User",
    "UserSportPreference",
    "UserTeamPreference",
    "UserNewsPreference",
    "UserNotificationSettings",
    # Games
    "Game",
    "GameEvent",
    # Content
    "FeedSource",
    "FeedSourceMapping",
    "FeedSnapshot",
    "Article",
    "ArticleSport",
    "ArticleTeam",
    "AISummary",
    # Players
    "Player",
    "DepthChartEntry",
    # Tickets
    "TicketProvider",
    "TicketDeal",
    # Experiences
    "FanExperience",
    "UserExperienceRegistration",
    # Analytics
    "UserInteraction",
    "ContentPerformance",
    # College - Phase 1 & 2
    "Division",
    "CollegeConference",
    "College",
    "CollegeTeam",
    "AcademicYear",
    "Season",
    "ConferenceMembership",
    "SeasonConfiguration",
    # College - Phase 3 Competition Structure
    "Venue",
    "Tournament",
    "TournamentBracket",
    "TournamentGame",
    "TournamentVenue",
    "CollegeGame",
    # College - Phase 4 Statistics & Rankings (temporarily commented out)
    # "CollegePlayer",
    # "TeamStatistics",
    # "PlayerStatistics",
    # "Rankings",
    # "AdvancedMetrics",
    # "SeasonRecords",
    # College - Phase 5 Content Integration
    "CollegeContent",
    "InjuryReport",
    "RecruitingNews",
    "CoachingNews",
    "ContentTeamAssociation",
    "ContentClassification",
    # College - Phase 6 User Personalization
    "UserCollegePreferences",
    "BracketPrediction",
    "BracketChallenge",
    "BracketChallengeParticipation",
    "UserCollegeNotificationSettings",
    "PersonalizedFeed",
    "UserEngagementMetrics",
    "UserPersonalizationProfile",
    # College Football - Phase 1 Foundation
    "FootballTeam",
    "FootballPlayer",
    "FootballGame",
    "FootballRoster",
    "FootballSeason",
    # College Football - Phase 3 Postseason Structure
    "BowlGame",
    "BowlTieIn",
    "BowlSelection",
    "CollegeFootballPlayoff",
    "CFPTeam",
    "CFPGame",
    "ConferenceChampionship",
    "RivalryGame",
    "RivalryGameHistory",
    "PostseasonTournament",
    # College Football - Phase 4 Recruiting & Transfer Portal
    "FootballRecruitingClass",
    "FootballRecruit",
    "FootballRecruitingOffer",
    "FootballRecruitingVisit",
    "FootballTransferPortalEntry",
    "FootballCoachingStaff",
    "FootballNILDeal",
    "FootballEligibilityTracking",
    # College Football - Phase 5 Content Integration
    "FootballContent",
    "FootballInjuryReport",
    "FootballRecruitingNews",
    "FootballCoachingNews",
    "FootballDepthChartUpdate",
    "FootballGamePreview",
    "FootballBowlNews",
]