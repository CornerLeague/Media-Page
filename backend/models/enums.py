"""
Enums for Corner League Media database models
"""

import enum


class ContentFrequency(str, enum.Enum):
    """User content frequency preferences"""
    MINIMAL = "minimal"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"


class NewsType(str, enum.Enum):
    """Types of news content"""
    INJURIES = "injuries"
    TRADES = "trades"
    ROSTER = "roster"
    GENERAL = "general"
    SCORES = "scores"
    ANALYSIS = "analysis"


class GameStatus(str, enum.Enum):
    """Game status options"""
    SCHEDULED = "SCHEDULED"
    LIVE = "LIVE"
    FINAL = "FINAL"
    POSTPONED = "POSTPONED"
    CANCELLED = "CANCELLED"


class GameResult(str, enum.Enum):
    """Game result options"""
    WIN = "W"
    LOSS = "L"
    TIE = "T"


class ExperienceType(str, enum.Enum):
    """Fan experience types"""
    WATCH_PARTY = "watch_party"
    TAILGATE = "tailgate"
    VIEWING = "viewing"
    MEETUP = "meetup"


class ContentCategory(str, enum.Enum):
    """Content category options"""
    INJURIES = "injuries"
    TRADES = "trades"
    ROSTER = "roster"
    GENERAL = "general"
    SCORES = "scores"
    ANALYSIS = "analysis"


class IngestionStatus(str, enum.Enum):
    """Feed ingestion status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DUPLICATE = "duplicate"


class InteractionType(str, enum.Enum):
    """User interaction types for analytics"""
    ARTICLE_VIEW = "article_view"
    ARTICLE_SHARE = "article_share"
    TEAM_FOLLOW = "team_follow"
    TEAM_UNFOLLOW = "team_unfollow"
    GAME_VIEW = "game_view"
    EXPERIENCE_REGISTER = "experience_register"
    TICKET_VIEW = "ticket_view"
    SEARCH = "search"
    FEED_SCROLL = "feed_scroll"


class EntityType(str, enum.Enum):
    """Entity types for analytics and references"""
    ARTICLE = "article"
    TEAM = "team"
    GAME = "game"
    PLAYER = "player"
    EXPERIENCE = "experience"
    TICKET_DEAL = "ticket_deal"
    AI_SUMMARY = "ai_summary"


# College Basketball Specific Enums

class DivisionLevel(str, enum.Enum):
    """NCAA Division levels for college sports"""
    D1 = "D1"
    D2 = "D2"
    D3 = "D3"
    NAIA = "NAIA"
    NJCAA = "NJCAA"


class ConferenceType(str, enum.Enum):
    """Types of college conferences"""
    POWER_FIVE = "power_five"
    MID_MAJOR = "mid_major"
    LOW_MAJOR = "low_major"
    INDEPENDENT = "independent"


class CollegeType(str, enum.Enum):
    """Types of colleges/universities"""
    PUBLIC = "public"
    PRIVATE = "private"
    RELIGIOUS = "religious"
    MILITARY = "military"
    COMMUNITY = "community"


class Region(str, enum.Enum):
    """Geographic regions for college sports"""
    NORTHEAST = "northeast"
    SOUTHEAST = "southeast"
    MIDWEST = "midwest"
    SOUTHWEST = "southwest"
    WEST = "west"
    NORTHWEST = "northwest"


class ConferenceStatus(str, enum.Enum):
    """Conference membership status"""
    ACTIVE = "active"
    DEPARTING = "departing"
    JOINING = "joining"
    FORMER = "former"


# Phase 2: Academic Framework Enums

class SeasonType(str, enum.Enum):
    """Types of seasons within an academic year"""
    REGULAR_SEASON = "regular_season"
    CONFERENCE_TOURNAMENT = "conference_tournament"
    POSTSEASON = "postseason"
    NCAA_TOURNAMENT = "ncaa_tournament"
    NIT = "nit"
    CBI = "cbi"
    CIT = "cit"
    EXHIBITION = "exhibition"
    PRESEASON = "preseason"


class SemesterType(str, enum.Enum):
    """Academic semester types"""
    FALL = "fall"
    SPRING = "spring"
    SUMMER = "summer"
    WINTER = "winter"


class AcademicYearStatus(str, enum.Enum):
    """Academic year status"""
    CURRENT = "current"
    FUTURE = "future"
    PAST = "past"
    ACTIVE = "active"


class ConferenceMembershipType(str, enum.Enum):
    """Types of conference membership"""
    FULL_MEMBER = "full_member"
    ASSOCIATE_MEMBER = "associate_member"
    AFFILIATE_MEMBER = "affiliate_member"
    PROVISIONAL_MEMBER = "provisional_member"


# Phase 3: Competition Structure Enums

# Phase 4: Statistics & Rankings Enums

class PlayerPosition(str, enum.Enum):
    """Basketball player positions"""
    POINT_GUARD = "point_guard"
    SHOOTING_GUARD = "shooting_guard"
    SMALL_FORWARD = "small_forward"
    POWER_FORWARD = "power_forward"
    CENTER = "center"
    GUARD = "guard"
    FORWARD = "forward"


class PlayerEligibilityStatus(str, enum.Enum):
    """Player eligibility status"""
    ELIGIBLE = "eligible"
    INELIGIBLE = "ineligible"
    REDSHIRT = "redshirt"
    MEDICAL_REDSHIRT = "medical_redshirt"
    TRANSFER_PORTAL = "transfer_portal"
    GRADUATE_TRANSFER = "graduate_transfer"
    SUSPENDED = "suspended"
    INJURED = "injured"


class PlayerClass(str, enum.Enum):
    """Academic class standing"""
    FRESHMAN = "freshman"
    SOPHOMORE = "sophomore"
    JUNIOR = "junior"
    SENIOR = "senior"
    GRADUATE = "graduate"
    REDSHIRT_FRESHMAN = "redshirt_freshman"
    REDSHIRT_SOPHOMORE = "redshirt_sophomore"
    REDSHIRT_JUNIOR = "redshirt_junior"
    REDSHIRT_SENIOR = "redshirt_senior"


class RankingSystem(str, enum.Enum):
    """Different ranking/rating systems"""
    AP_POLL = "ap_poll"
    COACHES_POLL = "coaches_poll"
    NET_RANKING = "net_ranking"
    KENPOM = "kenpom"
    RPI = "rpi"
    BPI = "bpi"
    SAGARIN = "sagarin"
    TORVIK = "torvik"
    HASLAMETRICS = "haslametrics"
    MASSEY = "massey"
    BARTTOVIK = "barttovik"


class StatisticType(str, enum.Enum):
    """Types of statistics"""
    SEASON_TOTAL = "season_total"
    SEASON_AVERAGE = "season_average"
    GAME_STATS = "game_stats"
    CAREER_TOTAL = "career_total"
    CAREER_AVERAGE = "career_average"
    CONFERENCE_ONLY = "conference_only"
    NON_CONFERENCE = "non_conference"


class StatisticCategory(str, enum.Enum):
    """Categories of basketball statistics"""
    SCORING = "scoring"
    REBOUNDING = "rebounding"
    ASSISTS = "assists"
    STEALS = "steals"
    BLOCKS = "blocks"
    SHOOTING = "shooting"
    FREE_THROWS = "free_throws"
    TURNOVERS = "turnovers"
    FOULS = "fouls"
    EFFICIENCY = "efficiency"
    ADVANCED = "advanced"


class RecordType(str, enum.Enum):
    """Types of win-loss records"""
    OVERALL = "overall"
    CONFERENCE = "conference"
    NON_CONFERENCE = "non_conference"
    HOME = "home"
    AWAY = "away"
    NEUTRAL = "neutral"
    RANKED_OPPONENTS = "ranked_opponents"
    QUAD_1 = "quad_1"
    QUAD_2 = "quad_2"
    QUAD_3 = "quad_3"
    QUAD_4 = "quad_4"
    ROAD_WINS = "road_wins"
    QUALITY_WINS = "quality_wins"
    BAD_LOSSES = "bad_losses"


class VenueType(str, enum.Enum):
    """Types of basketball venues"""
    ARENA = "arena"
    GYMNASIUM = "gymnasium"
    STADIUM = "stadium"
    FIELD_HOUSE = "field_house"
    PAVILION = "pavilion"
    CENTER = "center"
    DOME = "dome"
    NEUTRAL_SITE = "neutral_site"


class TournamentType(str, enum.Enum):
    """Types of basketball tournaments"""
    NCAA_TOURNAMENT = "ncaa_tournament"
    CONFERENCE_TOURNAMENT = "conference_tournament"
    NIT = "nit"
    CBI = "cbi"
    CIT = "cit"
    PRESEASON = "preseason"
    REGULAR_SEASON = "regular_season"
    INVITATIONAL = "invitational"
    HOLIDAY_TOURNAMENT = "holiday_tournament"
    EXEMPT_TOURNAMENT = "exempt_tournament"


class TournamentStatus(str, enum.Enum):
    """Tournament status options"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    POSTPONED = "postponed"


class TournamentFormat(str, enum.Enum):
    """Tournament bracket formats"""
    SINGLE_ELIMINATION = "single_elimination"
    DOUBLE_ELIMINATION = "double_elimination"
    ROUND_ROBIN = "round_robin"
    SWISS = "swiss"
    POOL_PLAY = "pool_play"
    STEPPED_BRACKET = "stepped_bracket"


class GameType(str, enum.Enum):
    """Types of basketball games"""
    REGULAR_SEASON = "regular_season"
    CONFERENCE_TOURNAMENT = "conference_tournament"
    NCAA_TOURNAMENT = "ncaa_tournament"
    NIT = "nit"
    CBI = "cbi"
    CIT = "cit"
    EXHIBITION = "exhibition"
    SCRIMMAGE = "scrimmage"
    INVITATIONAL = "invitational"
    HOLIDAY_TOURNAMENT = "holiday_tournament"
    POSTSEASON = "postseason"


class BracketRegion(str, enum.Enum):
    """NCAA Tournament bracket regions"""
    EAST = "east"
    WEST = "west"
    SOUTH = "south"
    MIDWEST = "midwest"


class GameImportance(str, enum.Enum):
    """Game importance levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    CHAMPIONSHIP = "championship"


class HomeCourtAdvantage(str, enum.Enum):
    """Home court advantage types"""
    HOME = "home"
    AWAY = "away"
    NEUTRAL = "neutral"


# =============================================================================
# Phase 5: Content Integration Enums
# =============================================================================

class CollegeContentType(str, enum.Enum):
    """Enhanced content types specific to college basketball"""
    GAME_PREVIEW = "game_preview"
    GAME_RECAP = "game_recap"
    INJURY_REPORT = "injury_report"
    RECRUITING_NEWS = "recruiting_news"
    TRANSFER_PORTAL = "transfer_portal"
    COACHING_NEWS = "coaching_news"
    CONFERENCE_NEWS = "conference_news"
    TOURNAMENT_NEWS = "tournament_news"
    RANKING_NEWS = "ranking_news"
    ACADEMIC_NEWS = "academic_news"
    SUSPENSION_NEWS = "suspension_news"
    ELIGIBILITY_NEWS = "eligibility_news"
    DEPTH_CHART = "depth_chart"
    SEASON_OUTLOOK = "season_outlook"
    BRACKET_ANALYSIS = "bracket_analysis"
    RECRUITING_COMMIT = "recruiting_commit"
    RECRUITING_DECOMMIT = "recruiting_decommit"
    RECRUITING_VISIT = "recruiting_visit"
    COACH_HIRE = "coach_hire"
    COACH_FIRE = "coach_fire"
    COACH_EXTENSION = "coach_extension"
    FACILITY_NEWS = "facility_news"
    ALUMNI_NEWS = "alumni_news"


class InjuryType(str, enum.Enum):
    """Types of player injuries"""
    ANKLE = "ankle"
    KNEE = "knee"
    FOOT = "foot"
    BACK = "back"
    SHOULDER = "shoulder"
    HAND = "hand"
    WRIST = "wrist"
    HIP = "hip"
    CONCUSSION = "concussion"
    ILLNESS = "illness"
    PERSONAL = "personal"
    OTHER = "other"


class InjurySeverity(str, enum.Enum):
    """Severity levels for injuries"""
    MINOR = "minor"              # Day-to-day
    MODERATE = "moderate"        # Week-to-week
    MAJOR = "major"              # Month+ recovery
    SEASON_ENDING = "season_ending"
    CAREER_ENDING = "career_ending"


class RecruitingEventType(str, enum.Enum):
    """Types of recruiting events"""
    COMMIT = "commit"
    DECOMMIT = "decommit"
    VISIT = "visit"
    OFFER = "offer"
    CONTACT = "contact"
    EVALUATION = "evaluation"
    TRANSFER_ENTRY = "transfer_entry"
    TRANSFER_COMMITMENT = "transfer_commitment"
    TRANSFER_WITHDRAWAL = "transfer_withdrawal"


class CoachingChangeType(str, enum.Enum):
    """Types of coaching changes"""
    HIRE = "hire"
    FIRE = "fire"
    RESIGNATION = "resignation"
    RETIREMENT = "retirement"
    EXTENSION = "extension"
    PROMOTION = "promotion"
    DEMOTION = "demotion"
    SUSPENSION = "suspension"
    REINSTATEMENT = "reinstatement"


# =============================================================================
# Phase 6: User Personalization Enums
# =============================================================================

class EngagementLevel(str, enum.Enum):
    """User engagement levels with teams"""
    CASUAL = "casual"           # Basic following, minimal notifications
    REGULAR = "regular"         # Standard following, regular notifications
    DIE_HARD = "die_hard"      # Heavy engagement, all notifications


class BracketPredictionStatus(str, enum.Enum):
    """Status of bracket predictions"""
    DRAFT = "draft"             # User is still editing
    SUBMITTED = "submitted"     # Final submission, no more changes
    LOCKED = "locked"          # Tournament started, predictions locked
    SCORING = "scoring"        # Tournament in progress, calculating scores
    FINAL = "final"           # Tournament complete, final scores


class BracketChallengeStatus(str, enum.Enum):
    """Status of bracket challenges"""
    OPEN = "open"              # Accepting new participants
    CLOSED = "closed"          # No new participants, predictions allowed
    LOCKED = "locked"          # Tournament started, no more changes
    IN_PROGRESS = "in_progress" # Tournament ongoing
    COMPLETED = "completed"    # Tournament finished


class ChallengePrivacy(str, enum.Enum):
    """Privacy settings for bracket challenges"""
    PUBLIC = "public"          # Anyone can find and join
    FRIENDS_ONLY = "friends_only" # Only friends can join
    INVITE_ONLY = "invite_only"   # Only invited users can join
    PRIVATE = "private"        # Creator only


class NotificationFrequency(str, enum.Enum):
    """Frequency settings for notifications"""
    NEVER = "never"
    IMMEDIATE = "immediate"
    DAILY_DIGEST = "daily_digest"
    WEEKLY_DIGEST = "weekly_digest"
    GAME_DAY_ONLY = "game_day_only"


class CollegeNotificationType(str, enum.Enum):
    """Specific notification types for college basketball"""
    GAME_REMINDERS = "game_reminders"
    SCORE_UPDATES = "score_updates"
    INJURY_UPDATES = "injury_updates"
    RECRUITING_NEWS = "recruiting_news"
    COACHING_CHANGES = "coaching_changes"
    RANKING_CHANGES = "ranking_changes"
    TOURNAMENT_UPDATES = "tournament_updates"
    BRACKET_CHALLENGE = "bracket_challenge"
    TRANSFER_PORTAL = "transfer_portal"
    SUSPENSION_NEWS = "suspension_news"


class FeedContentType(str, enum.Enum):
    """Types of content that can appear in personalized feeds"""
    ARTICLES = "articles"
    GAME_UPDATES = "game_updates"
    INJURY_REPORTS = "injury_reports"
    RECRUITING_NEWS = "recruiting_news"
    COACHING_NEWS = "coaching_news"
    RANKINGS = "rankings"
    TOURNAMENT_NEWS = "tournament_news"
    BRACKET_UPDATES = "bracket_updates"
    SOCIAL_UPDATES = "social_updates"


class EngagementMetricType(str, enum.Enum):
    """Types of user engagement metrics to track"""
    ARTICLE_VIEW = "article_view"
    ARTICLE_SHARE = "article_share"
    ARTICLE_LIKE = "article_like"
    TEAM_PAGE_VIEW = "team_page_view"
    GAME_DETAIL_VIEW = "game_detail_view"
    BRACKET_CREATED = "bracket_created"
    BRACKET_UPDATED = "bracket_updated"
    CHALLENGE_JOINED = "challenge_joined"
    COMMENT_POSTED = "comment_posted"
    SEARCH_PERFORMED = "search_performed"
    NOTIFICATION_CLICKED = "notification_clicked"
    FEED_SCROLL = "feed_scroll"
    TEAM_FOLLOWED = "team_followed"
    TEAM_UNFOLLOWED = "team_unfollowed"
    SETTINGS_UPDATED = "settings_updated"


class PersonalizationScore(str, enum.Enum):
    """Content relevance scoring for personalization"""
    VERY_LOW = "very_low"      # 0.0 - 0.2
    LOW = "low"                # 0.2 - 0.4
    MEDIUM = "medium"          # 0.4 - 0.6
    HIGH = "high"              # 0.6 - 0.8
    VERY_HIGH = "very_high"    # 0.8 - 1.0


# =============================================================================
# College Football Specific Enums
# =============================================================================

class FootballPosition(str, enum.Enum):
    """Football player positions"""
    # Offense
    QUARTERBACK = "quarterback"
    RUNNING_BACK = "running_back"
    FULLBACK = "fullback"
    WIDE_RECEIVER = "wide_receiver"
    TIGHT_END = "tight_end"
    LEFT_TACKLE = "left_tackle"
    LEFT_GUARD = "left_guard"
    CENTER = "center"
    RIGHT_GUARD = "right_guard"
    RIGHT_TACKLE = "right_tackle"

    # Defense
    DEFENSIVE_END = "defensive_end"
    DEFENSIVE_TACKLE = "defensive_tackle"
    NOSE_TACKLE = "nose_tackle"
    OUTSIDE_LINEBACKER = "outside_linebacker"
    MIDDLE_LINEBACKER = "middle_linebacker"
    INSIDE_LINEBACKER = "inside_linebacker"
    CORNERBACK = "cornerback"
    SAFETY = "safety"
    FREE_SAFETY = "free_safety"
    STRONG_SAFETY = "strong_safety"

    # Special Teams
    KICKER = "kicker"
    PUNTER = "punter"
    LONG_SNAPPER = "long_snapper"
    RETURN_SPECIALIST = "return_specialist"

    # Position Groups
    OFFENSIVE_LINE = "offensive_line"
    DEFENSIVE_LINE = "defensive_line"
    LINEBACKER = "linebacker"
    DEFENSIVE_BACK = "defensive_back"


class FootballPositionGroup(str, enum.Enum):
    """Football position groups for depth chart organization"""
    QUARTERBACK = "quarterback"
    RUNNING_BACK = "running_back"
    WIDE_RECEIVER = "wide_receiver"
    TIGHT_END = "tight_end"
    OFFENSIVE_LINE = "offensive_line"
    DEFENSIVE_LINE = "defensive_line"
    LINEBACKER = "linebacker"
    DEFENSIVE_BACK = "defensive_back"
    SPECIAL_TEAMS = "special_teams"


class FootballPlayType(str, enum.Enum):
    """Types of football plays"""
    # Offensive plays
    RUSH = "rush"
    PASS = "pass"
    OPTION = "option"
    PLAY_ACTION = "play_action"
    SCREEN = "screen"
    DRAW = "draw"
    WILDCAT = "wildcat"

    # Special teams plays
    PUNT = "punt"
    FIELD_GOAL = "field_goal"
    EXTRA_POINT = "extra_point"
    KICKOFF = "kickoff"
    PUNT_RETURN = "punt_return"
    KICKOFF_RETURN = "kickoff_return"
    FAKE_PUNT = "fake_punt"
    FAKE_FIELD_GOAL = "fake_field_goal"
    ONSIDE_KICK = "onside_kick"

    # Defensive plays
    BLITZ = "blitz"
    COVERAGE = "coverage"
    RUN_DEFENSE = "run_defense"

    # Miscellaneous
    PENALTY = "penalty"
    TIMEOUT = "timeout"
    KNEEL_DOWN = "kneel_down"
    SPIKE = "spike"
    TWO_POINT_CONVERSION = "two_point_conversion"


class FootballGameContext(str, enum.Enum):
    """Context or situation during football games"""
    FIRST_DOWN = "first_down"
    SECOND_DOWN = "second_down"
    THIRD_DOWN = "third_down"
    FOURTH_DOWN = "fourth_down"
    RED_ZONE = "red_zone"
    GOAL_LINE = "goal_line"
    TWO_MINUTE_WARNING = "two_minute_warning"
    OVERTIME = "overtime"
    GARBAGE_TIME = "garbage_time"
    CLUTCH_TIME = "clutch_time"
    GOAL_TO_GO = "goal_to_go"
    SHORT_YARDAGE = "short_yardage"
    LONG_YARDAGE = "long_yardage"


class FootballWeatherCondition(str, enum.Enum):
    """Weather conditions for football games"""
    CLEAR = "clear"
    PARTLY_CLOUDY = "partly_cloudy"
    CLOUDY = "cloudy"
    LIGHT_RAIN = "light_rain"
    HEAVY_RAIN = "heavy_rain"
    LIGHT_SNOW = "light_snow"
    HEAVY_SNOW = "heavy_snow"
    WIND = "wind"
    FOG = "fog"
    COLD = "cold"
    HOT = "hot"
    HUMID = "humid"
    DOME = "dome"
    UNKNOWN = "unknown"


class FootballFormation(str, enum.Enum):
    """Football formations"""
    # Offensive formations
    I_FORMATION = "i_formation"
    SHOTGUN = "shotgun"
    PISTOL = "pistol"
    WILDCAT = "wildcat"
    SPREAD = "spread"
    PRO_SET = "pro_set"
    SINGLE_BACK = "single_back"
    EMPTY_BACKFIELD = "empty_backfield"
    JUMBO = "jumbo"

    # Defensive formations
    FOUR_THREE = "4_3"
    THREE_FOUR = "3_4"
    FOUR_TWO_FIVE = "4_2_5"
    THREE_THREE_FIVE = "3_3_5"
    SIX_ONE = "6_1"
    FIVE_TWO = "5_2"
    GOAL_LINE_DEFENSE = "goal_line_defense"
    PREVENT = "prevent"
    DIME = "dime"
    QUARTER = "quarter"


class BowlGameType(str, enum.Enum):
    """Types of bowl games"""
    COLLEGE_FOOTBALL_PLAYOFF = "college_football_playoff"
    NEW_YEARS_SIX = "new_years_six"
    MAJOR_BOWL = "major_bowl"
    MINOR_BOWL = "minor_bowl"
    CONFERENCE_CHAMPIONSHIP = "conference_championship"
    NATIONAL_CHAMPIONSHIP = "national_championship"


class FootballSeasonType(str, enum.Enum):
    """Types of football seasons"""
    REGULAR_SEASON = "regular_season"
    CONFERENCE_CHAMPIONSHIP = "conference_championship"
    BOWL_SEASON = "bowl_season"
    PLAYOFF = "playoff"
    SPRING_PRACTICE = "spring_practice"
    FALL_PRACTICE = "fall_practice"
    RECRUITING = "recruiting"
    TRANSFER_PORTAL = "transfer_portal"


class RecruitingClass(str, enum.Enum):
    """Recruiting class years"""
    FRESHMAN = "freshman"
    REDSHIRT_FRESHMAN = "redshirt_freshman"
    TRANSFER = "transfer"
    GRADUATE_TRANSFER = "graduate_transfer"
    JUCO_TRANSFER = "juco_transfer"


class ScholarshipType(str, enum.Enum):
    """Types of football scholarships"""
    FULL_SCHOLARSHIP = "full_scholarship"
    PARTIAL_SCHOLARSHIP = "partial_scholarship"
    WALK_ON = "walk_on"
    PREFERRED_WALK_ON = "preferred_walk_on"
    GREY_SHIRT = "grey_shirt"
    BLUE_SHIRT = "blue_shirt"


class FootballRankingSystem(str, enum.Enum):
    """Football-specific ranking systems"""
    AP_POLL = "ap_poll"
    COACHES_POLL = "coaches_poll"
    CFP_RANKING = "cfp_ranking"
    BCS = "bcs"
    SAGARIN = "sagarin"
    MASSEY = "massey"
    FPI = "fpi"
    SP_PLUS = "sp_plus"
    PFF = "pff"
    RECRUITING_RANKING = "recruiting_ranking"


# =============================================================================
# College Football Phase 2: Play-by-Play and Advanced Analytics Enums
# =============================================================================

class PlayResult(str, enum.Enum):
    """Result of a football play"""
    GAIN = "gain"
    LOSS = "loss"
    NO_GAIN = "no_gain"
    TOUCHDOWN = "touchdown"
    FUMBLE = "fumble"
    INTERCEPTION = "interception"
    INCOMPLETE = "incomplete"
    SACK = "sack"
    SAFETY = "safety"
    TURNOVER_ON_DOWNS = "turnover_on_downs"
    PENALTY = "penalty"
    FIELD_GOAL_GOOD = "field_goal_good"
    FIELD_GOAL_MISSED = "field_goal_missed"
    EXTRA_POINT_GOOD = "extra_point_good"
    EXTRA_POINT_MISSED = "extra_point_missed"
    BLOCKED_KICK = "blocked_kick"
    PUNT = "punt"
    PUNT_BLOCKED = "punt_blocked"
    PUNT_DOWNED = "punt_downed"
    PUNT_FAIR_CATCH = "punt_fair_catch"
    PUNT_TOUCHBACK = "punt_touchback"
    PUNT_OUT_OF_BOUNDS = "punt_out_of_bounds"
    KICKOFF = "kickoff"
    KICKOFF_TOUCHBACK = "kickoff_touchback"
    KICKOFF_OUT_OF_BOUNDS = "kickoff_out_of_bounds"
    ONSIDE_KICK_RECOVERED = "onside_kick_recovered"
    ONSIDE_KICK_FAILED = "onside_kick_failed"


class DriveResult(str, enum.Enum):
    """Result of a drive"""
    TOUCHDOWN = "touchdown"
    FIELD_GOAL = "field_goal"
    MISSED_FIELD_GOAL = "missed_field_goal"
    PUNT = "punt"
    FUMBLE_LOST = "fumble_lost"
    INTERCEPTION = "interception"
    TURNOVER_ON_DOWNS = "turnover_on_downs"
    SAFETY = "safety"
    END_OF_HALF = "end_of_half"
    END_OF_GAME = "end_of_game"
    DOWNS = "downs"
    BLOCKED_PUNT = "blocked_punt"
    BLOCKED_FIELD_GOAL = "blocked_field_goal"


class FieldPosition(str, enum.Enum):
    """Field position zones for analytics"""
    OWN_ENDZONE = "own_endzone"           # 0-10 yard line (own territory)
    OWN_TERRITORY = "own_territory"       # 11-50 yard line (own territory)
    MIDFIELD = "midfield"                 # Around 50 yard line
    OPPONENT_TERRITORY = "opponent_territory"  # 49-21 yard line (opponent territory)
    RED_ZONE = "red_zone"                 # 20-1 yard line (opponent territory)
    GOAL_LINE = "goal_line"               # 1-5 yard line (opponent territory)


class DownType(str, enum.Enum):
    """Down and distance context"""
    FIRST_DOWN = "first_down"
    SECOND_SHORT = "second_short"         # 2nd and 1-3
    SECOND_MEDIUM = "second_medium"       # 2nd and 4-7
    SECOND_LONG = "second_long"           # 2nd and 8+
    THIRD_SHORT = "third_short"           # 3rd and 1-3
    THIRD_MEDIUM = "third_medium"         # 3rd and 4-7
    THIRD_LONG = "third_long"             # 3rd and 8+
    FOURTH_DOWN = "fourth_down"


class PlayDirection(str, enum.Enum):
    """Direction of play relative to line of scrimmage"""
    LEFT = "left"
    RIGHT = "right"
    CENTER = "center"
    OUTSIDE_LEFT = "outside_left"
    OUTSIDE_RIGHT = "outside_right"
    UP_THE_MIDDLE = "up_the_middle"
    DEEP_LEFT = "deep_left"
    DEEP_RIGHT = "deep_right"
    DEEP_MIDDLE = "deep_middle"
    SHORT_LEFT = "short_left"
    SHORT_RIGHT = "short_right"
    SHORT_MIDDLE = "short_middle"


class PassLength(str, enum.Enum):
    """Length categories for pass plays"""
    SCREEN = "screen"                     # Behind line of scrimmage
    SHORT = "short"                       # 1-9 yards
    MEDIUM = "medium"                     # 10-19 yards
    DEEP = "deep"                         # 20+ yards
    BOMB = "bomb"                         # 40+ yards


class RushType(str, enum.Enum):
    """Types of rushing plays"""
    INSIDE_RUN = "inside_run"
    OUTSIDE_RUN = "outside_run"
    DRAW = "draw"
    POWER_RUN = "power_run"
    SWEEP = "sweep"
    REVERSE = "reverse"
    OPTION = "option"
    QB_SNEAK = "qb_sneak"
    QB_SCRAMBLE = "qb_scramble"
    DESIGNED_QB_RUN = "designed_qb_run"
    WILDCAT = "wildcat"


class DefensivePlayType(str, enum.Enum):
    """Types of defensive plays/alignments"""
    BASE_DEFENSE = "base_defense"
    BLITZ = "blitz"
    COVERAGE = "coverage"
    PREVENT = "prevent"
    GOAL_LINE = "goal_line"
    PUNT_BLOCK = "punt_block"
    FIELD_GOAL_BLOCK = "field_goal_block"
    RETURN_FORMATION = "return_formation"


class PenaltyType(str, enum.Enum):
    """Types of penalties"""
    # Offensive penalties
    FALSE_START = "false_start"
    HOLDING_OFFENSE = "holding_offense"
    ILLEGAL_FORMATION = "illegal_formation"
    ILLEGAL_MOTION = "illegal_motion"
    DELAY_OF_GAME = "delay_of_game"
    INTENTIONAL_GROUNDING = "intentional_grounding"
    ILLEGAL_FORWARD_PASS = "illegal_forward_pass"
    OFFENSIVE_PASS_INTERFERENCE = "offensive_pass_interference"
    UNSPORTSMANLIKE_CONDUCT_OFFENSE = "unsportsmanlike_conduct_offense"

    # Defensive penalties
    OFFSIDE = "offside"
    ENCROACHMENT = "encroachment"
    NEUTRAL_ZONE_INFRACTION = "neutral_zone_infraction"
    HOLDING_DEFENSE = "holding_defense"
    ILLEGAL_CONTACT = "illegal_contact"
    PASS_INTERFERENCE = "pass_interference"
    ROUGHING_THE_PASSER = "roughing_the_passer"
    ROUGHING_THE_KICKER = "roughing_the_kicker"
    TARGETING = "targeting"
    UNSPORTSMANLIKE_CONDUCT_DEFENSE = "unsportsmanlike_conduct_defense"

    # Special teams penalties
    ILLEGAL_BLOCK_ABOVE_WAIST = "illegal_block_above_waist"
    ILLEGAL_BLOCK_BELOW_WAIST = "illegal_block_below_waist"
    CLIPPING = "clipping"
    BLOCK_IN_BACK = "block_in_back"
    KICKOFF_OUT_OF_BOUNDS = "kickoff_out_of_bounds"

    # General penalties
    PERSONAL_FOUL = "personal_foul"
    UNNECESSARY_ROUGHNESS = "unnecessary_roughness"
    FACEMASK = "facemask"
    HORSE_COLLAR = "horse_collar"
    ILLEGAL_SUBSTITUTION = "illegal_substitution"
    TOO_MANY_MEN = "too_many_men"


class StatisticCategory(str, enum.Enum):
    """Categories of football statistics"""
    # Offensive statistics
    PASSING = "passing"
    RUSHING = "rushing"
    RECEIVING = "receiving"
    OFFENSIVE_LINE = "offensive_line"

    # Defensive statistics
    TACKLING = "tackling"
    PASS_DEFENSE = "pass_defense"
    RUN_DEFENSE = "run_defense"
    PRESSURE = "pressure"
    TURNOVERS = "turnovers"

    # Special teams statistics
    KICKING = "kicking"
    PUNTING = "punting"
    RETURNS = "returns"
    COVERAGE = "coverage"

    # Team statistics
    TEAM_OFFENSE = "team_offense"
    TEAM_DEFENSE = "team_defense"
    TEAM_SPECIAL_TEAMS = "team_special_teams"

    # Advanced metrics
    EFFICIENCY = "efficiency"
    SITUATIONAL = "situational"
    FIELD_POSITION = "field_position"


class AdvancedMetricType(str, enum.Enum):
    """Types of advanced football metrics"""
    # Expected points and win probability
    EPA = "epa"                           # Expected Points Added
    WPA = "wpa"                           # Win Probability Added

    # Success rates
    SUCCESS_RATE = "success_rate"         # Play success rate
    EXPLOSIVE_PLAY_RATE = "explosive_play_rate"
    STUFF_RATE = "stuff_rate"             # Negative plays rate

    # Efficiency metrics
    YARDS_PER_PLAY = "yards_per_play"
    POINTS_PER_DRIVE = "points_per_drive"
    PLAYS_PER_DRIVE = "plays_per_drive"
    TIME_PER_DRIVE = "time_per_drive"

    # Situational metrics
    THIRD_DOWN_CONVERSION = "third_down_conversion"
    RED_ZONE_EFFICIENCY = "red_zone_efficiency"
    GOAL_LINE_EFFICIENCY = "goal_line_efficiency"
    TWO_MINUTE_EFFICIENCY = "two_minute_efficiency"

    # Field position metrics
    AVERAGE_FIELD_POSITION = "average_field_position"
    FIELD_POSITION_ADVANTAGE = "field_position_advantage"

    # Defensive metrics
    DEFENSIVE_DVOA = "defensive_dvoa"     # Defense-adjusted Value Over Average
    HAVOC_RATE = "havoc_rate"            # Tackles for loss + forced fumbles + PBUs + INTs
    PRESSURE_RATE = "pressure_rate"

    # Special teams metrics
    FIELD_GOAL_EFFICIENCY = "field_goal_efficiency"
    PUNT_EFFICIENCY = "punt_efficiency"
    RETURN_EFFICIENCY = "return_efficiency"


class GameSituation(str, enum.Enum):
    """Game situation contexts for situational analysis"""
    EARLY_GAME = "early_game"             # 1st quarter


# =============================================================================
# College Football Phase 3: Postseason and Bowl Game Enums
# =============================================================================

class BowlTier(str, enum.Enum):
    """Tiers of bowl games"""
    CFP = "cfp"                           # College Football Playoff
    NEW_YEARS_SIX = "new_years_six"       # New Year's Six bowls
    MAJOR = "major"                       # Major bowl games
    REGIONAL = "regional"                 # Regional bowl games
    MINOR = "minor"                       # Minor/lower-tier bowl games


class BowlSelectionCriteria(str, enum.Enum):
    """Bowl selection criteria types"""
    CFP_SEMIFINAL = "cfp_semifinal"       # CFP semifinal rotation
    CFP_QUARTERFINAL = "cfp_quarterfinal" # CFP quarterfinal games
    CONFERENCE_TIE_IN = "conference_tie_in" # Conference champion tie-in
    AT_LARGE_POOL = "at_large_pool"       # At-large selection pool
    GROUP_OF_FIVE_ACCESS = "group_of_five_access" # Group of Five access bowl
    REGIONAL_TIE_IN = "regional_tie_in"   # Regional conference tie-ins
    OPEN_SELECTION = "open_selection"     # Open to all eligible teams


class PlayoffRound(str, enum.Enum):
    """College Football Playoff rounds"""
    FIRST_ROUND = "first_round"           # First round (on campus)
    QUARTERFINALS = "quarterfinals"       # Quarterfinals (bowl sites)
    SEMIFINALS = "semifinals"             # Semifinals (rotating bowls)
    CHAMPIONSHIP = "championship"         # National Championship


class CFPSeedType(str, enum.Enum):
    """CFP seed types"""
    AUTO_QUALIFIER = "auto_qualifier"     # Automatic qualifier (conference champion)
    AT_LARGE = "at_large"                # At-large selection


class ConferenceChampionshipFormat(str, enum.Enum):
    """Conference championship determination formats"""
    CHAMPIONSHIP_GAME = "championship_game"     # Conference championship game
    ROUND_ROBIN = "round_robin"                 # Round-robin regular season
    DIVISION_WINNERS = "division_winners"       # Division winners meet
    BEST_RECORD = "best_record"                 # Best conference record
    TIEBREAKER = "tiebreaker"                   # Determined by tiebreaker


class RivalryType(str, enum.Enum):
    """Types of football rivalries"""
    CONFERENCE = "conference"             # Conference rivalries
    REGIONAL = "regional"                 # Regional/border rivalries
    NATIONAL = "national"                 # National/historic rivalries
    TROPHY = "trophy"                     # Trophy game rivalries
    CROSS_DIVISION = "cross_division"     # Cross-division rivalries
    TRADITIONAL = "traditional"          # Traditional annual games


class TrophyStatus(str, enum.Enum):
    """Status of rivalry trophies"""
    ACTIVE = "active"                     # Trophy is active
    RETIRED = "retired"                   # Trophy has been retired
    DISCONTINUED = "discontinued"         # Rivalry discontinued
    DISPUTED = "disputed"                 # Trophy status in dispute
    MISSING = "missing"                   # Trophy is missing/lost


class PostseasonFormat(str, enum.Enum):
    """Postseason tournament formats"""
    SINGLE_ELIMINATION = "single_elimination"   # Single elimination bracket
    DOUBLE_ELIMINATION = "double_elimination"   # Double elimination bracket
    ROUND_ROBIN = "round_robin"                 # Round-robin format
    POOL_PLAY = "pool_play"                     # Pool play with brackets
    SWISS_SYSTEM = "swiss_system"               # Swiss system tournament
    LADDER = "ladder"                           # Ladder tournament


class SelectionMethod(str, enum.Enum):
    """Tournament selection methods"""
    COMMITTEE = "committee"               # Selection committee
    AUTOMATIC = "automatic"               # Automatic qualifiers only
    RANKING_BASED = "ranking_based"       # Based on rankings/polls
    CONFERENCE_RECORD = "conference_record" # Conference record based
    OVERALL_RECORD = "overall_record"     # Overall record based
    HYBRID = "hybrid"                     # Combination of methods


class BracketPosition(str, enum.Enum):
    """Bracket positioning for tournament games"""
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"
    CENTER = "center"
    CHAMPIONSHIP = "championship"


# =============================================================================
# College Football Phase 4: Recruiting and Transfer Portal Enums
# =============================================================================

class RecruitingStarRating(str, enum.Enum):
    """Star ratings for football recruits"""
    TWO_STAR = "2_star"
    THREE_STAR = "3_star"
    FOUR_STAR = "4_star"
    FIVE_STAR = "5_star"


class RecruitingStatus(str, enum.Enum):
    """Status of recruiting process"""
    INITIAL_CONTACT = "initial_contact"
    SHOWING_INTEREST = "showing_interest"
    OFFERED = "offered"
    VISITING = "visiting"
    COMMITTED = "committed"
    SIGNED = "signed"
    ENROLLED = "enrolled"
    DECOMMITTED = "decommitted"
    LOST_TO_COMPETITOR = "lost_to_competitor"


class CommitmentStatus(str, enum.Enum):
    """Commitment status of recruits"""
    UNCOMMITTED = "uncommitted"
    SOFT_COMMIT = "soft_commit"
    COMMITTED = "committed"
    SIGNED = "signed"
    DECOMMITTED = "decommitted"
    ENROLLED = "enrolled"


class VisitType(str, enum.Enum):
    """Types of recruiting visits"""
    UNOFFICIAL = "unofficial"
    OFFICIAL = "official"
    JUNIOR_DAY = "junior_day"
    CAMP_VISIT = "camp_visit"
    GAME_DAY = "game_day"


class TransferReason(str, enum.Enum):
    """Reasons for entering transfer portal"""
    PLAYING_TIME = "playing_time"
    COACHING_CHANGE = "coaching_change"
    ACADEMIC_REASONS = "academic_reasons"
    FAMILY_REASONS = "family_reasons"
    SCHEME_FIT = "scheme_fit"
    DEVELOPMENT_OPPORTUNITIES = "development_opportunities"
    DISCIPLINARY = "disciplinary"
    MEDICAL = "medical"
    PERSONAL = "personal"
    GRADUATE_TRANSFER = "graduate_transfer"
    OTHER = "other"


class TransferStatus(str, enum.Enum):
    """Status in transfer portal"""
    IN_PORTAL = "in_portal"
    COMMITTED = "committed"
    SIGNED = "signed"
    ENROLLED = "enrolled"
    RETURNED_TO_ORIGINAL = "returned_to_original"
    WITHDRAWN = "withdrawn"
    DISMISSED = "dismissed"


class EligibilityType(str, enum.Enum):
    """Types of eligibility tracking"""
    ACADEMIC = "academic"
    ATHLETIC = "athletic"
    TRANSFER = "transfer"
    NCAA_CLEARINGHOUSE = "ncaa_clearinghouse"
    MEDICAL = "medical"
    DISCIPLINARY = "disciplinary"


class CoachingPosition(str, enum.Enum):
    """Specific coaching positions"""
    HEAD_COACH = "head_coach"
    OFFENSIVE_COORDINATOR = "offensive_coordinator"
    DEFENSIVE_COORDINATOR = "defensive_coordinator"
    SPECIAL_TEAMS_COORDINATOR = "special_teams_coordinator"
    QUARTERBACKS_COACH = "quarterbacks_coach"
    RUNNING_BACKS_COACH = "running_backs_coach"
    WIDE_RECEIVERS_COACH = "wide_receivers_coach"
    TIGHT_ENDS_COACH = "tight_ends_coach"
    OFFENSIVE_LINE_COACH = "offensive_line_coach"
    DEFENSIVE_LINE_COACH = "defensive_line_coach"
    LINEBACKERS_COACH = "linebackers_coach"
    DEFENSIVE_BACKS_COACH = "defensive_backs_coach"
    SAFETIES_COACH = "safeties_coach"
    CORNERBACKS_COACH = "cornerbacks_coach"
    RECRUITING_COORDINATOR = "recruiting_coordinator"
    STRENGTH_CONDITIONING = "strength_conditioning"
    QUALITY_CONTROL = "quality_control"
    GRADUATE_ASSISTANT = "graduate_assistant"
    ANALYST = "analyst"


class CoachingLevel(str, enum.Enum):
    """Level of coaching position"""
    HEAD_COACH = "head_coach"
    COORDINATOR = "coordinator"
    POSITION_COACH = "position_coach"
    ASSISTANT_COACH = "assistant_coach"
    GRADUATE_ASSISTANT = "graduate_assistant"
    QUALITY_CONTROL = "quality_control"
    ANALYST = "analyst"
    SUPPORT_STAFF = "support_staff"


class ContractStatus(str, enum.Enum):
    """Employment contract status"""
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    RESIGNED = "resigned"
    RETIRED = "retired"
    SUSPENDED = "suspended"
    ON_LEAVE = "on_leave"


class NILDealType(str, enum.Enum):
    """Types of NIL deals"""
    ENDORSEMENT = "endorsement"
    SOCIAL_MEDIA = "social_media"
    APPEARANCE = "appearance"
    AUTOGRAPH_SESSION = "autograph_session"
    CAMP_INSTRUCTION = "camp_instruction"
    MERCHANDISE = "merchandise"
    LICENSING = "licensing"
    CONTENT_CREATION = "content_creation"
    PROMOTIONAL = "promotional"
    COLLECTIVE = "collective"
    OTHER = "other"


class NILCategory(str, enum.Enum):
    """Categories of NIL activities"""
    TRADITIONAL_ADVERTISING = "traditional_advertising"
    SOCIAL_MEDIA_PROMOTION = "social_media_promotion"
    PERSONAL_APPEARANCES = "personal_appearances"
    CAMPS_AND_LESSONS = "camps_and_lessons"
    AUTOGRAPHS_MEMORABILIA = "autographs_memorabilia"
    MERCHANDISE_SALES = "merchandise_sales"
    CONTENT_CREATION = "content_creation"
    CHARITY_WORK = "charity_work"
    BUSINESS_VENTURES = "business_ventures"
    COLLECTIVE_PAYMENTS = "collective_payments"


class ComplianceStatus(str, enum.Enum):
    """NCAA compliance status"""
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    CONDITIONALLY_APPROVED = "conditionally_approved"
    DENIED = "denied"
    UNDER_REVIEW = "under_review"
    REQUIRES_MODIFICATION = "requires_modification"
    VIOLATION_SUSPECTED = "violation_suspected"


class PortalEntryReason(str, enum.Enum):
    """Detailed reasons for portal entry"""
    LACK_OF_PLAYING_TIME = "lack_of_playing_time"
    COACHING_STAFF_CHANGE = "coaching_staff_change"
    SCHEME_CHANGE = "scheme_change"
    CLOSER_TO_HOME = "closer_to_home"
    ACADEMIC_PROGRAM = "academic_program"
    GRADUATE_SCHOOL = "graduate_school"
    INJURY_CONCERNS = "injury_concerns"
    TEAM_CULTURE = "team_culture"
    DEVELOPMENT_OPPORTUNITY = "development_opportunity"
    DISCIPLINARY_ISSUES = "disciplinary_issues"
    FAMILY_EMERGENCY = "family_emergency"
    BETTER_FIT = "better_fit"
    CONFERENCE_MOVE = "conference_move"
    NFL_PREPARATION = "nfl_preparation"


class RecruitingPeriod(str, enum.Enum):
    """NCAA recruiting periods"""
    CONTACT_PERIOD = "contact_period"
    EVALUATION_PERIOD = "evaluation_period"
    QUIET_PERIOD = "quiet_period"
    DEAD_PERIOD = "dead_period"


class SigningPeriod(str, enum.Enum):
    """National Letter of Intent signing periods"""
    EARLY_SIGNING_PERIOD = "early_signing_period"
    REGULAR_SIGNING_PERIOD = "regular_signing_period"
    LATE_SIGNING_PERIOD = "late_signing_period"


# =============================================================================
# College Football Phase 5: Content Integration Enums
# =============================================================================

class FootballContentType(str, enum.Enum):
    """Enhanced content types specific to college football"""
    # Game content
    GAME_PREVIEW = "game_preview"
    GAME_RECAP = "game_recap"
    GAME_HIGHLIGHTS = "game_highlights"
    PREGAME_ANALYSIS = "pregame_analysis"
    POSTGAME_ANALYSIS = "postgame_analysis"

    # Injury and health content
    INJURY_REPORT = "injury_report"
    INJURY_UPDATE = "injury_update"
    RETURN_FROM_INJURY = "return_from_injury"
    MEDICAL_CLEARANCE = "medical_clearance"
    SURGERY_NEWS = "surgery_news"

    # Recruiting content
    RECRUITING_NEWS = "recruiting_news"
    RECRUITING_COMMIT = "recruiting_commit"
    RECRUITING_DECOMMIT = "recruiting_decommit"
    RECRUITING_VISIT = "recruiting_visit"
    RECRUITING_RANKING = "recruiting_ranking"
    RECRUITING_CLASS_UPDATE = "recruiting_class_update"
    SIGNING_DAY_NEWS = "signing_day_news"

    # Transfer portal content
    TRANSFER_PORTAL_ENTRY = "transfer_portal_entry"
    TRANSFER_COMMITMENT = "transfer_commitment"
    TRANSFER_PORTAL_NEWS = "transfer_portal_news"
    TRANSFER_PORTAL_UPDATE = "transfer_portal_update"

    # Coaching content
    COACHING_NEWS = "coaching_news"
    COACH_HIRE = "coach_hire"
    COACH_FIRE = "coach_fire"
    COACH_RESIGNATION = "coach_resignation"
    COACH_CONTRACT = "coach_contract"
    COACHING_STAFF_UPDATE = "coaching_staff_update"

    # Depth chart and roster content
    DEPTH_CHART_UPDATE = "depth_chart_update"
    DEPTH_CHART_RELEASE = "depth_chart_release"
    POSITION_BATTLE = "position_battle"
    ROSTER_MOVE = "roster_move"
    STARTING_LINEUP_CHANGE = "starting_lineup_change"

    # Bowl and playoff content
    BOWL_SELECTION = "bowl_selection"
    BOWL_NEWS = "bowl_news"
    BOWL_PREVIEW = "bowl_preview"
    BOWL_RECAP = "bowl_recap"
    PLAYOFF_NEWS = "playoff_news"
    PLAYOFF_SELECTION = "playoff_selection"
    PLAYOFF_RANKING = "playoff_ranking"

    # Conference and season content
    CONFERENCE_NEWS = "conference_news"
    CONFERENCE_REALIGNMENT = "conference_realignment"
    SEASON_OUTLOOK = "season_outlook"
    SEASON_PREVIEW = "season_preview"
    SEASON_RECAP = "season_recap"

    # Rankings and awards content
    RANKING_NEWS = "ranking_news"
    POLL_UPDATE = "poll_update"
    AWARD_NEWS = "award_news"
    HONORS_ANNOUNCEMENT = "honors_announcement"

    # Academic and disciplinary content
    ACADEMIC_NEWS = "academic_news"
    SUSPENSION_NEWS = "suspension_news"
    ELIGIBILITY_NEWS = "eligibility_news"
    DISMISSAL_NEWS = "dismissal_news"

    # NIL and compliance content
    NIL_NEWS = "nil_news"
    NIL_DEAL_ANNOUNCEMENT = "nil_deal_announcement"
    COMPLIANCE_NEWS = "compliance_news"
    VIOLATION_NEWS = "violation_news"

    # Facilities and program content
    FACILITY_NEWS = "facility_news"
    FACILITY_UPGRADE = "facility_upgrade"
    PROGRAM_ANNOUNCEMENT = "program_announcement"

    # Media and coverage content
    PRESS_CONFERENCE = "press_conference"
    INTERVIEW = "interview"
    FEATURE_STORY = "feature_story"
    BREAKING_NEWS = "breaking_news"


class FootballInjuryType(str, enum.Enum):
    """Football-specific injury types"""
    # Head and neck injuries
    CONCUSSION = "concussion"
    NECK_INJURY = "neck_injury"
    HEAD_INJURY = "head_injury"

    # Upper body injuries
    SHOULDER_INJURY = "shoulder_injury"
    ARM_INJURY = "arm_injury"
    ELBOW_INJURY = "elbow_injury"
    WRIST_INJURY = "wrist_injury"
    HAND_INJURY = "hand_injury"
    FINGER_INJURY = "finger_injury"
    RIB_INJURY = "rib_injury"
    CHEST_INJURY = "chest_injury"

    # Core and back injuries
    BACK_INJURY = "back_injury"
    ABDOMINAL_INJURY = "abdominal_injury"
    CORE_INJURY = "core_injury"
    SPINE_INJURY = "spine_injury"

    # Lower body injuries
    HIP_INJURY = "hip_injury"
    GROIN_INJURY = "groin_injury"
    THIGH_INJURY = "thigh_injury"
    HAMSTRING_INJURY = "hamstring_injury"
    QUADRICEPS_INJURY = "quadriceps_injury"
    KNEE_INJURY = "knee_injury"
    SHIN_INJURY = "shin_injury"
    CALF_INJURY = "calf_injury"
    ANKLE_INJURY = "ankle_injury"
    FOOT_INJURY = "foot_injury"
    TOE_INJURY = "toe_injury"

    # Specific conditions
    ACL_TEAR = "acl_tear"
    MCL_TEAR = "mcl_tear"
    MENISCUS_TEAR = "meniscus_tear"
    ACHILLES_INJURY = "achilles_injury"
    TURF_TOE = "turf_toe"

    # Other
    ILLNESS = "illness"
    UNDISCLOSED = "undisclosed"
    OTHER = "other"


class FootballInjurySeverity(str, enum.Enum):
    """Football-specific injury severity levels"""
    MINOR = "minor"                    # 1-2 weeks
    MODERATE = "moderate"              # 3-6 weeks
    MAJOR = "major"                   # 7-12 weeks
    SEVERE = "severe"                 # 13+ weeks
    SEASON_ENDING = "season_ending"   # Out for season
    CAREER_ENDING = "career_ending"   # Career threatening


class FootballDepthChartStatus(str, enum.Enum):
    """Status on football depth chart"""
    STARTER = "starter"               # First team starter
    BACKUP = "backup"                # Second team
    THIRD_STRING = "third_string"     # Third team
    FOURTH_STRING = "fourth_string"   # Fourth team or lower
    SPECIAL_TEAMS = "special_teams"   # Special teams only
    REDSHIRT = "redshirt"            # Redshirting
    INJURED_RESERVE = "injured_reserve" # On injured reserve
    SUSPENDED = "suspended"           # Suspended from team
    DISMISSED = "dismissed"           # Dismissed from team
    TRANSFER_PORTAL = "transfer_portal" # In transfer portal


class FootballCoachingChangeType(str, enum.Enum):
    """Types of football coaching changes"""
    # Hirings
    HIRE = "hire"
    PROMOTION = "promotion"
    LATERAL_MOVE = "lateral_move"

    # Departures
    FIRE = "fire"
    RESIGNATION = "resignation"
    RETIREMENT = "retirement"
    MUTUAL_SEPARATION = "mutual_separation"

    # Contract changes
    CONTRACT_EXTENSION = "contract_extension"
    CONTRACT_RENEWAL = "contract_renewal"
    SALARY_INCREASE = "salary_increase"

    # Other changes
    ROLE_CHANGE = "role_change"
    ADDITIONAL_DUTIES = "additional_duties"
    LEAVE_OF_ABSENCE = "leave_of_absence"
    SUSPENSION = "suspension"


class FootballRecruitingEventType(str, enum.Enum):
    """Types of football recruiting events"""
    # Commitment events
    COMMIT = "commit"
    DECOMMIT = "decommit"
    RECOMMIT = "recommit"
    FLIP = "flip"

    # Transfer portal events
    TRANSFER_ENTRY = "transfer_entry"
    TRANSFER_COMMITMENT = "transfer_commitment"
    TRANSFER_WITHDRAWAL = "transfer_withdrawal"

    # Visit events
    OFFICIAL_VISIT = "official_visit"
    UNOFFICIAL_VISIT = "unofficial_visit"
    JUNIOR_DAY_VISIT = "junior_day_visit"
    CAMP_VISIT = "camp_visit"

    # Offer events
    OFFER_EXTENDED = "offer_extended"
    OFFER_ACCEPTED = "offer_accepted"
    OFFER_DECLINED = "offer_declined"
    OFFER_RESCINDED = "offer_rescinded"

    # Signing events
    SIGNED_LOI = "signed_loi"
    ENROLLED = "enrolled"

    # Ranking events
    RANKING_UPDATE = "ranking_update"
    STAR_RATING_CHANGE = "star_rating_change"


class FootballBowlNewsType(str, enum.Enum):
    """Types of football bowl-related news"""
    BOWL_SELECTION = "bowl_selection"
    BOWL_ANNOUNCEMENT = "bowl_announcement"
    BOWL_PREVIEW = "bowl_preview"
    BOWL_PREDICTION = "bowl_prediction"
    BOWL_MATCHUP_ANALYSIS = "bowl_matchup_analysis"
    BOWL_TICKET_INFO = "bowl_ticket_info"
    BOWL_TRAVEL_INFO = "bowl_travel_info"
    BOWL_HISTORY = "bowl_history"
    BOWL_TRADITION = "bowl_tradition"
    PLAYOFF_SELECTION = "playoff_selection"
    PLAYOFF_RANKING = "playoff_ranking"
    PLAYOFF_SEEDING = "playoff_seeding"
    PLAYOFF_SCHEDULE = "playoff_schedule"
    CHAMPIONSHIP_NEWS = "championship_news"