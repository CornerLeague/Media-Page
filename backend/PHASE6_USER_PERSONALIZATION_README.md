# Phase 6: User Personalization - College Basketball Platform

## Overview

Phase 6 implements the final user personalization layer for the college basketball platform, providing comprehensive features for team following, bracket predictions, group challenges, personalized content feeds, and detailed engagement tracking. This phase integrates seamlessly with the existing user authentication system and builds upon all previous phases (1-5).

## 🎯 Key Features

### 1. **College Team Following System**
- **UserCollegePreferences**: Follow teams with different engagement levels (Casual, Regular, Die-Hard)
- **Granular Notifications**: Team-specific notification preferences for games, injuries, recruiting, and coaching changes
- **Interaction Scoring**: Calculated engagement scores based on user behavior (0.0-1.0)
- **Activity Tracking**: Monitor when users last interacted with team content

### 2. **March Madness Bracket System**
- **BracketPrediction**: Complete NCAA tournament bracket predictions with JSON storage
- **Scoring System**: Real-time scoring with accuracy tracking and leaderboards
- **Status Management**: Draft → Submitted → Locked → Scoring → Final workflow
- **Multiple Tournaments**: Support for different tournament types (NCAA, NIT, CBI, CIT)

### 3. **Group Bracket Challenges**
- **BracketChallenge**: Create and manage group competitions
- **Privacy Controls**: Public, Friends-Only, Invite-Only, and Private challenges
- **Flexible Scoring**: Customizable point systems for different rounds
- **Entry Management**: Optional entry fees and participant limits
- **Leaderboards**: Real-time ranking and challenge statistics

### 4. **Enhanced Notification System**
- **UserCollegeNotificationSettings**: Granular notification preferences for college basketball
- **Frequency Controls**: Never, Immediate, Daily Digest, Weekly Digest, Game Day Only
- **Quiet Hours**: Respect user sleep schedules
- **Multi-Channel**: Push notifications and email delivery
- **Context-Aware**: Pre-game reminders, halftime updates, final scores

### 5. **Personalized Content Feeds**
- **PersonalizedFeed**: Customizable content feed with weighted preferences
- **Content Types**: Articles, game updates, injury reports, recruiting news, coaching changes, rankings, tournament news
- **Algorithm Factors**: Recency, engagement history, and team preferences
- **Refresh Controls**: Configurable refresh intervals and item limits

### 6. **Engagement Tracking & Analytics**
- **UserEngagementMetrics**: Comprehensive interaction tracking
- **Behavioral Analysis**: Article views, shares, team follows, bracket actions, searches
- **Session Tracking**: Group interactions by session for pattern analysis
- **Value Scoring**: Weighted engagement values for personalization algorithms

### 7. **Personalization Profiles**
- **UserPersonalizationProfile**: Aggregated user preference profiles
- **Content Affinity**: Calculated scores for different content types
- **Team Relationships**: Affinity scores for teams and conferences
- **Engagement Patterns**: Time-based behavior analysis
- **Smart Recalculation**: Automatic profile updates based on new interactions

## 📊 Database Schema

### Core Tables

#### User College Preferences
```sql
user_college_preferences (
    id, user_id, college_team_id, engagement_level,
    is_active, followed_at, game_reminders, injury_updates,
    recruiting_news, coaching_updates, interaction_score,
    last_interaction_at, created_at, updated_at
)
```

#### Bracket Predictions
```sql
bracket_predictions (
    id, user_id, tournament_id, bracket_name, status,
    predictions (JSONB), total_score, possible_score,
    correct_picks, total_picks, submitted_at, locked_at,
    last_scored_at, created_at, updated_at
)
```

#### Bracket Challenges
```sql
bracket_challenges (
    id, creator_id, tournament_id, name, description,
    status, privacy_setting, entry_fee, max_participants,
    registration_deadline, scoring_system (JSONB),
    prize_structure (JSONB), invite_code, participant_count,
    created_at, updated_at
)
```

#### Enhanced Notifications
```sql
user_college_notification_settings (
    id, user_id, enabled, [frequency_preferences],
    push_notifications, email_notifications,
    quiet_hours_enabled, quiet_hours_start, quiet_hours_end,
    [game_day_preferences], created_at, updated_at
)
```

#### Personalized Feeds
```sql
personalized_feeds (
    id, user_id, enabled, [content_weights],
    [algorithm_factors], max_items_per_refresh,
    refresh_interval_hours, last_refreshed_at,
    created_at, updated_at
)
```

#### Engagement Metrics
```sql
user_engagement_metrics (
    id, user_id, metric_type, entity_type, entity_id,
    occurred_at, metadata (JSONB), engagement_value,
    session_id, college_team_id, created_at, updated_at
)
```

#### Personalization Profiles
```sql
user_personalization_profiles (
    id, user_id, content_type_scores (JSONB),
    team_affinity_scores (JSONB), conference_affinity_scores (JSONB),
    engagement_patterns (JSONB), total_interactions,
    average_session_duration, last_active_at,
    last_calculated_at, calculation_version, created_at, updated_at
)
```

## 🚀 Installation & Migration

### 1. Apply Database Migration
```bash
cd backend/migrations
python phase6_user_personalization_migration.py
```

### 2. Generate Seed Data
```bash
python phase6_user_personalization_seed_data.py
```

### 3. Apply Performance Optimizations
```bash
python phase6_performance_optimization.py
```

### 4. Test Integration
```bash
python test_phase6_integration.py
```

## 🔧 Configuration

### Engagement Levels
- **Casual**: Basic following, minimal notifications
- **Regular**: Standard following, regular notifications
- **Die-Hard**: Heavy engagement, all notifications

### Notification Frequencies
- **Never**: No notifications
- **Immediate**: Real-time notifications
- **Daily Digest**: Once per day summary
- **Weekly Digest**: Weekly summary
- **Game Day Only**: Only on game days

### Content Types & Weights
- **Articles**: General news articles (default: 1.00)
- **Game Updates**: Live game information (default: 0.80)
- **Injury Reports**: Player injury news (default: 0.70)
- **Recruiting News**: Recruiting updates (default: 0.60)
- **Coaching News**: Coaching changes (default: 0.75)
- **Rankings**: Team rankings (default: 0.65)
- **Tournament News**: Tournament updates (default: 0.90)
- **Bracket Updates**: Bracket-related news (default: 0.85)

## 📈 Performance Optimizations

### Database Indexes
- **Composite Indexes**: Multi-column indexes for common query patterns
- **Partial Indexes**: Filtered indexes for active/enabled records only
- **Functional Indexes**: GIN indexes for JSON column queries
- **Materialized Views**: Pre-computed analytics for dashboards

### Key Performance Features
- **Concurrent Index Creation**: Non-blocking index creation
- **Query Optimization**: Optimized for common personalization patterns
- **Statistics Updates**: Regular ANALYZE for query planner optimization
- **Materialized View Refresh**: Scheduled refresh for analytics views

### Monitoring Queries
- Slow personalization queries analysis
- Index usage statistics
- Table size monitoring
- Materialized view freshness tracking
- Active user distribution metrics

## 🎮 Usage Examples

### Following a College Team
```python
from backend.models import UserCollegePreferences
from backend.models.enums import EngagementLevel

# Create a die-hard fan preference
preference = UserCollegePreferences(
    user_id=user.id,
    college_team_id=duke.id,
    engagement_level=EngagementLevel.DIE_HARD,
    game_reminders=True,
    injury_updates=True,
    recruiting_news=True,
    coaching_updates=True
)
```

### Creating a Bracket Prediction
```python
from backend.models import BracketPrediction

bracket = BracketPrediction(
    user_id=user.id,
    tournament_id=march_madness.id,
    bracket_name="My Championship Bracket",
    predictions={
        "rounds": {
            "round_1": {"east": [...], "west": [...], "south": [...], "midwest": [...]},
            "round_2": {...},
            "championship": "Duke"
        }
    }
)
```

### Setting Up Personalized Feed
```python
from backend.models import PersonalizedFeed

feed = PersonalizedFeed(
    user_id=user.id,
    articles_weight=1.0,
    tournament_news_weight=0.9,
    game_updates_weight=0.8,
    recency_factor=0.3,
    engagement_factor=0.4,
    team_preference_factor=0.5
)
```

### Tracking Engagement
```python
from backend.models import UserEngagementMetrics
from backend.models.enums import EngagementMetricType

metric = UserEngagementMetrics(
    user_id=user.id,
    metric_type=EngagementMetricType.ARTICLE_VIEW,
    entity_type="article",
    entity_id=article.id,
    engagement_value=0.3,
    college_team_id=team.id
)
```

## 🔗 Integration Points

### Existing User System
- **Seamless Integration**: Works with existing User model and Firebase authentication
- **Preference Extension**: Extends existing UserTeamPreference and UserNotificationSettings
- **Onboarding Compatible**: Integrates with existing onboarding flow

### Content Pipeline Integration
- **Article Classification**: Links with Phase 5 content classification system
- **Team Associations**: Leverages existing team-content relationships
- **Real-time Updates**: Integrates with live scoring and game updates

### Analytics Integration
- **Engagement Tracking**: Comprehensive user interaction analytics
- **Performance Metrics**: Team popularity and content engagement analysis
- **Behavioral Patterns**: Time-based usage pattern analysis

## 🎯 Personalization Algorithm

### Content Scoring Formula
```
content_score = (
    content_type_weight * 0.4 +
    team_affinity_score * team_preference_factor +
    recency_score * recency_factor +
    user_engagement_history * engagement_factor
) * interaction_multiplier
```

### Factors
- **Content Type Weight**: User's preference for content type (0.0-1.0)
- **Team Affinity**: User's affinity for teams involved (0.0-1.0)
- **Recency Score**: How recent the content is (0.0-1.0)
- **Engagement History**: User's past interaction with similar content (0.0-1.0)
- **Interaction Multiplier**: Boost for high-engagement content types

## 🔄 Maintenance

### Regular Tasks
1. **Refresh Materialized Views**: Daily refresh for analytics
2. **Update User Profiles**: Recalculate personalization profiles for active users
3. **Clean Old Metrics**: Archive engagement metrics older than 1 year
4. **Update Statistics**: Weekly ANALYZE for query optimization

### Monitoring
- Track slow queries using pg_stat_statements
- Monitor index usage and table sizes
- Analyze user engagement patterns
- Review bracket challenge participation rates

## 🚨 Security & Privacy

### Data Protection
- **User Consent**: All tracking requires user opt-in
- **Data Minimization**: Only collect necessary engagement data
- **Retention Policies**: Automatic cleanup of old engagement data
- **Privacy Controls**: Users can disable personalization features

### Access Controls
- **Row Level Security**: User data is isolated by user_id
- **API Permissions**: Proper authorization for all personalization endpoints
- **Audit Logging**: Track access to user preference data

## 📋 Future Enhancements

### Planned Features
1. **Social Features**: Friend connections and social bracket sharing
2. **Machine Learning**: Advanced content recommendation algorithms
3. **Push Notification Service**: Real-time push notification delivery
4. **Mobile App Integration**: Native mobile app personalization support
5. **Advanced Analytics**: More sophisticated user behavior analysis

### Optimization Opportunities
1. **Caching Layer**: Redis caching for personalized feeds
2. **Background Processing**: Async profile recalculation
3. **CDN Integration**: Content delivery optimization
4. **A/B Testing**: Personalization algorithm testing framework

## 📞 Support

For questions about Phase 6 implementation:
- Review the comprehensive model documentation in `college_phase6_personalization.py`
- Check integration tests in `test_phase6_integration.py`
- Monitor performance using queries in `phase6_performance_optimization.py`
- Review seed data examples in `phase6_user_personalization_seed_data.py`

Phase 6 completes the college basketball platform with a robust, scalable user personalization system that provides tailored experiences while maintaining high performance and data privacy standards.