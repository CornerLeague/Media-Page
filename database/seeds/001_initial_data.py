"""
Initial seed data for Corner League Media

Provides essential data for development and testing:
- Sports and leagues
- Sample teams
- Feed sources
- Test users with preferences
"""

import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import *
from backend.models.enums import *
from backend.database import get_async_session


async def seed_sports_and_leagues(session: AsyncSession):
    """Seed sports, leagues, and teams"""
    print("Seeding sports and leagues...")

    # Basketball
    basketball = Sport(
        name="Basketball",
        slug="basketball",
        has_teams=True,
        icon="basketball",
        is_active=True,
        display_order=1
    )
    session.add(basketball)
    await session.flush()

    nba = League(
        sport_id=basketball.id,
        name="National Basketball Association",
        slug="nba",
        abbreviation="NBA",
        is_active=True,
        season_start_month=10,
        season_end_month=6
    )
    session.add(nba)
    await session.flush()

    # NFL Football
    football = Sport(
        name="Football",
        slug="football",
        has_teams=True,
        icon="football",
        is_active=True,
        display_order=2
    )
    session.add(football)
    await session.flush()

    nfl = League(
        sport_id=football.id,
        name="National Football League",
        slug="nfl",
        abbreviation="NFL",
        is_active=True,
        season_start_month=9,
        season_end_month=2
    )
    session.add(nfl)
    await session.flush()

    # Baseball
    baseball = Sport(
        name="Baseball",
        slug="baseball",
        has_teams=True,
        icon="baseball",
        is_active=True,
        display_order=3
    )
    session.add(baseball)
    await session.flush()

    mlb = League(
        sport_id=baseball.id,
        name="Major League Baseball",
        slug="mlb",
        abbreviation="MLB",
        is_active=True,
        season_start_month=3,
        season_end_month=10
    )
    session.add(mlb)
    await session.flush()

    # Hockey
    hockey = Sport(
        name="Hockey",
        slug="hockey",
        has_teams=True,
        icon="hockey",
        is_active=True,
        display_order=4
    )
    session.add(hockey)
    await session.flush()

    nhl = League(
        sport_id=hockey.id,
        name="National Hockey League",
        slug="nhl",
        abbreviation="NHL",
        is_active=True,
        season_start_month=10,
        season_end_month=6
    )
    session.add(nhl)
    await session.flush()

    return {
        'basketball': basketball,
        'football': football,
        'baseball': baseball,
        'hockey': hockey,
        'nba': nba,
        'nfl': nfl,
        'mlb': mlb,
        'nhl': nhl
    }


async def seed_teams(session: AsyncSession, sports_data: dict):
    """Seed sample teams"""
    print("Seeding teams...")

    teams = []

    # NBA Teams
    nba_teams_data = [
        ("Los Angeles", "Lakers", "LAL", "#552583", "#FDB927"),
        ("Boston", "Celtics", "BOS", "#007A33", "#BA9653"),
        ("Golden State", "Warriors", "GSW", "#1D428A", "#FFC72C"),
        ("Miami", "Heat", "MIA", "#98002E", "#F9A01B"),
        ("Chicago", "Bulls", "CHI", "#CE1141", "#000000"),
        ("San Antonio", "Spurs", "SAS", "#C4CED4", "#000000"),
        ("Phoenix", "Suns", "PHX", "#1D1160", "#E56020"),
        ("Dallas", "Mavericks", "DAL", "#00538C", "#002B5E"),
    ]

    for market, name, abbrev, primary, secondary in nba_teams_data:
        team = Team(
            sport_id=sports_data['basketball'].id,
            league_id=sports_data['nba'].id,
            name=name,
            market=market,
            slug=f"{market.lower().replace(' ', '-')}-{name.lower()}",
            abbreviation=abbrev,
            primary_color=primary,
            secondary_color=secondary,
            is_active=True,
            external_id=f"nba-{abbrev.lower()}"
        )
        teams.append(team)
        session.add(team)

    # NFL Teams
    nfl_teams_data = [
        ("New England", "Patriots", "NE", "#002244", "#C60C30"),
        ("Kansas City", "Chiefs", "KC", "#E31837", "#FFB81C"),
        ("Green Bay", "Packers", "GB", "#203731", "#FFB612"),
        ("Pittsburgh", "Steelers", "PIT", "#FFB612", "#101820"),
        ("Dallas", "Cowboys", "DAL", "#003594", "#869397"),
        ("San Francisco", "49ers", "SF", "#AA0000", "#B3995D"),
        ("Seattle", "Seahawks", "SEA", "#002244", "#69BE28"),
        ("Buffalo", "Bills", "BUF", "#00338D", "#C60C30"),
    ]

    for market, name, abbrev, primary, secondary in nfl_teams_data:
        team = Team(
            sport_id=sports_data['football'].id,
            league_id=sports_data['nfl'].id,
            name=name,
            market=market,
            slug=f"{market.lower().replace(' ', '-')}-{name.lower()}",
            abbreviation=abbrev,
            primary_color=primary,
            secondary_color=secondary,
            is_active=True,
            external_id=f"nfl-{abbrev.lower()}"
        )
        teams.append(team)
        session.add(team)

    # MLB Teams
    mlb_teams_data = [
        ("New York", "Yankees", "NYY", "#132448", "#C4CED4"),
        ("Los Angeles", "Dodgers", "LAD", "#005A9C", "#EF3E42"),
        ("Boston", "Red Sox", "BOS", "#BD3039", "#0C2340"),
        ("Atlanta", "Braves", "ATL", "#CE1141", "#13274F"),
        ("Houston", "Astros", "HOU", "#002D62", "#EB6E1F"),
        ("Tampa Bay", "Rays", "TB", "#092C5C", "#8FBCE6"),
        ("Chicago", "Cubs", "CHC", "#0E3386", "#CC3433"),
        ("San Diego", "Padres", "SD", "#2F241D", "#FFC425"),
    ]

    for market, name, abbrev, primary, secondary in mlb_teams_data:
        team = Team(
            sport_id=sports_data['baseball'].id,
            league_id=sports_data['mlb'].id,
            name=name,
            market=market,
            slug=f"{market.lower().replace(' ', '-')}-{name.lower()}",
            abbreviation=abbrev,
            primary_color=primary,
            secondary_color=secondary,
            is_active=True,
            external_id=f"mlb-{abbrev.lower()}"
        )
        teams.append(team)
        session.add(team)

    await session.flush()
    return teams


async def seed_feed_sources(session: AsyncSession, sports_data: dict, teams: list):
    """Seed RSS feed sources"""
    print("Seeding feed sources...")

    feed_sources = []

    # General sports feeds
    general_feeds = [
        {
            "name": "ESPN",
            "url": "https://www.espn.com/espn/rss/news",
            "website": "https://www.espn.com",
            "description": "ESPN sports news feed"
        },
        {
            "name": "Sports Illustrated",
            "url": "https://www.si.com/rss/si_topstories.rss",
            "website": "https://www.si.com",
            "description": "Sports Illustrated top stories"
        },
        {
            "name": "The Athletic",
            "url": "https://theathletic.com/rss/",
            "website": "https://theathletic.com",
            "description": "The Athletic sports journalism"
        }
    ]

    for feed_data in general_feeds:
        feed_source = FeedSource(
            name=feed_data["name"],
            url=feed_data["url"],
            website=feed_data["website"],
            description=feed_data["description"],
            is_active=True,
            fetch_interval_minutes=30
        )
        feed_sources.append(feed_source)
        session.add(feed_source)

    # Sport-specific feeds
    sport_feeds = [
        {
            "name": "NBA.com",
            "url": "https://www.nba.com/news/rss.xml",
            "website": "https://www.nba.com",
            "description": "Official NBA news",
            "sport": sports_data["basketball"]
        },
        {
            "name": "NFL.com",
            "url": "https://www.nfl.com/news/rss.xml",
            "website": "https://www.nfl.com",
            "description": "Official NFL news",
            "sport": sports_data["football"]
        },
        {
            "name": "MLB.com",
            "url": "https://www.mlb.com/news/rss.xml",
            "website": "https://www.mlb.com",
            "description": "Official MLB news",
            "sport": sports_data["baseball"]
        }
    ]

    for feed_data in sport_feeds:
        feed_source = FeedSource(
            name=feed_data["name"],
            url=feed_data["url"],
            website=feed_data["website"],
            description=feed_data["description"],
            is_active=True,
            fetch_interval_minutes=20
        )
        feed_sources.append(feed_source)
        session.add(feed_source)

    await session.flush()

    # Create feed source mappings
    for i, feed_source in enumerate(feed_sources):
        if i < len(general_feeds):
            # General feeds map to all sports
            for sport in [sports_data["basketball"], sports_data["football"], sports_data["baseball"]]:
                mapping = FeedSourceMapping(
                    feed_source_id=feed_source.id,
                    sport_id=sport.id,
                    priority=1
                )
                session.add(mapping)
        else:
            # Sport-specific feeds
            sport_index = i - len(general_feeds)
            if sport_index < len(sport_feeds):
                sport = sport_feeds[sport_index]["sport"]
                mapping = FeedSourceMapping(
                    feed_source_id=feed_source.id,
                    sport_id=sport.id,
                    priority=2
                )
                session.add(mapping)

    return feed_sources


async def seed_test_users(session: AsyncSession, sports_data: dict, teams: list):
    """Seed test users with preferences"""
    print("Seeding test users...")

    # Test user 1: Basketball fan
    user1 = User(
        clerk_user_id="user_test_basketball_fan_123",
        email="basketball.fan@test.com",
        display_name="Basketball Fan",
        content_frequency=ContentFrequency.STANDARD,
        is_active=True,
        onboarding_completed_at=datetime.now(),
        last_active_at=datetime.now()
    )
    session.add(user1)
    await session.flush()

    # User 1 preferences
    sport_pref1 = UserSportPreference(
        user_id=user1.id,
        sport_id=sports_data["basketball"].id,
        rank=1,
        is_active=True
    )
    session.add(sport_pref1)

    # Find Lakers and Celtics teams for user 1
    lakers = next((t for t in teams if t.name == "Lakers"), None)
    celtics = next((t for t in teams if t.name == "Celtics"), None)

    if lakers:
        team_pref1 = UserTeamPreference(
            user_id=user1.id,
            team_id=lakers.id,
            affinity_score=Decimal("0.9"),
            is_active=True
        )
        session.add(team_pref1)

    if celtics:
        team_pref2 = UserTeamPreference(
            user_id=user1.id,
            team_id=celtics.id,
            affinity_score=Decimal("0.7"),
            is_active=True
        )
        session.add(team_pref2)

    # News preferences for user 1
    news_types = [
        (NewsType.GENERAL, True, 1),
        (NewsType.SCORES, True, 2),
        (NewsType.TRADES, True, 3),
        (NewsType.INJURIES, True, 4),
        (NewsType.ROSTER, False, 5),
        (NewsType.ANALYSIS, False, 6),
    ]

    for news_type, enabled, priority in news_types:
        news_pref = UserNewsPreference(
            user_id=user1.id,
            news_type=news_type,
            enabled=enabled,
            priority=priority
        )
        session.add(news_pref)

    # Notification settings for user 1
    notification_settings1 = UserNotificationSettings(
        user_id=user1.id,
        push_enabled=True,
        email_enabled=False,
        game_reminders=True,
        news_alerts=True,
        score_updates=True
    )
    session.add(notification_settings1)

    # Test user 2: Multi-sport fan
    user2 = User(
        clerk_user_id="user_test_multisport_fan_456",
        email="multisport.fan@test.com",
        display_name="Multi-Sport Fan",
        content_frequency=ContentFrequency.COMPREHENSIVE,
        is_active=True,
        onboarding_completed_at=datetime.now(),
        last_active_at=datetime.now()
    )
    session.add(user2)
    await session.flush()

    # User 2 sport preferences
    sport_prefs2 = [
        (sports_data["football"], 1),
        (sports_data["basketball"], 2),
        (sports_data["baseball"], 3)
    ]

    for sport, rank in sport_prefs2:
        sport_pref = UserSportPreference(
            user_id=user2.id,
            sport_id=sport.id,
            rank=rank,
            is_active=True
        )
        session.add(sport_pref)

    # User 2 team preferences
    patriots = next((t for t in teams if t.name == "Patriots"), None)
    warriors = next((t for t in teams if t.name == "Warriors"), None)
    yankees = next((t for t in teams if t.name == "Yankees"), None)

    team_prefs2 = [
        (patriots, Decimal("0.95")),
        (warriors, Decimal("0.8")),
        (yankees, Decimal("0.75"))
    ]

    for team, affinity in team_prefs2:
        if team:
            team_pref = UserTeamPreference(
                user_id=user2.id,
                team_id=team.id,
                affinity_score=affinity,
                is_active=True
            )
            session.add(team_pref)

    return [user1, user2]


async def seed_sample_content(session: AsyncSession, sports_data: dict, teams: list):
    """Seed sample articles and content"""
    print("Seeding sample content...")

    # Sample articles
    articles_data = [
        {
            "title": "Lakers Win Big in Season Opener",
            "summary": "The Los Angeles Lakers dominated their season opener with a decisive victory.",
            "content": "In a thrilling season opener, the Los Angeles Lakers showcased their championship caliber with a dominant 125-100 victory over their division rivals. The team's star players delivered exceptional performances, setting high expectations for the upcoming season.",
            "author": "Sports Reporter",
            "source": "ESPN",
            "category": ContentCategory.GENERAL,
            "published_at": datetime.now() - timedelta(hours=2),
            "sport": sports_data["basketball"],
            "team_name": "Lakers"
        },
        {
            "title": "NFL Trade Deadline Shakeup",
            "summary": "Several major trades have reshaped the NFL landscape ahead of the playoffs.",
            "content": "The NFL trade deadline brought significant changes across the league, with multiple contenders making strategic moves to bolster their playoff chances. The most notable trade involved a star quarterback moving to a championship-contending team.",
            "author": "Trade Insider",
            "source": "NFL.com",
            "category": ContentCategory.TRADES,
            "published_at": datetime.now() - timedelta(hours=6),
            "sport": sports_data["football"],
            "team_name": "Patriots"
        },
        {
            "title": "Baseball Season Awards Announced",
            "summary": "The MVP and Cy Young awards have been announced for the completed baseball season.",
            "content": "Major League Baseball announced the winners of this year's most prestigious individual awards. The MVP race was particularly competitive, with the winner edging out strong competition from players across both leagues.",
            "author": "Awards Reporter",
            "source": "MLB.com",
            "category": ContentCategory.GENERAL,
            "published_at": datetime.now() - timedelta(days=1),
            "sport": sports_data["baseball"],
            "team_name": "Yankees"
        }
    ]

    for article_data in articles_data:
        # Find the team
        team = next((t for t in teams if t.name == article_data["team_name"]), None)

        article = Article(
            title=article_data["title"],
            summary=article_data["summary"],
            content=article_data["content"],
            author=article_data["author"],
            source=article_data["source"],
            category=article_data["category"],
            published_at=article_data["published_at"],
            word_count=len(article_data["content"].split()),
            reading_time_minutes=max(1, len(article_data["content"].split()) // 200),
            is_active=True
        )
        session.add(article)
        await session.flush()

        # Create sport relationship
        article_sport = ArticleSport(
            article_id=article.id,
            sport_id=article_data["sport"].id,
            relevance_score=Decimal("0.9")
        )
        session.add(article_sport)

        # Create team relationship if team found
        if team:
            article_team = ArticleTeam(
                article_id=article.id,
                team_id=team.id,
                relevance_score=Decimal("0.8"),
                mentioned_players=[]
            )
            session.add(article_team)


async def seed_sample_games(session: AsyncSession, sports_data: dict, teams: list):
    """Seed sample games and scores"""
    print("Seeding sample games...")

    # Find some teams for games
    lakers = next((t for t in teams if t.name == "Lakers"), None)
    celtics = next((t for t in teams if t.name == "Celtics"), None)
    patriots = next((t for t in teams if t.name == "Patriots"), None)
    chiefs = next((t for t in teams if t.name == "Chiefs"), None)

    games_data = []

    # NBA game
    if lakers and celtics:
        games_data.append({
            "sport": sports_data["basketball"],
            "league": sports_data["nba"],
            "home_team": lakers,
            "away_team": celtics,
            "scheduled_at": datetime.now() + timedelta(days=1),
            "status": GameStatus.SCHEDULED,
            "home_score": 0,
            "away_score": 0,
            "season": 2025,
            "venue": "Crypto.com Arena"
        })

    # NFL game
    if patriots and chiefs:
        games_data.append({
            "sport": sports_data["football"],
            "league": sports_data["nfl"],
            "home_team": patriots,
            "away_team": chiefs,
            "scheduled_at": datetime.now() + timedelta(days=7),
            "status": GameStatus.SCHEDULED,
            "home_score": 0,
            "away_score": 0,
            "season": 2024,
            "week": 15,
            "venue": "Gillette Stadium"
        })

    # Completed game
    if lakers and celtics:
        games_data.append({
            "sport": sports_data["basketball"],
            "league": sports_data["nba"],
            "home_team": celtics,
            "away_team": lakers,
            "scheduled_at": datetime.now() - timedelta(days=2),
            "status": GameStatus.FINAL,
            "home_score": 108,
            "away_score": 125,
            "season": 2025,
            "venue": "TD Garden"
        })

    for game_data in games_data:
        game = Game(
            sport_id=game_data["sport"].id,
            league_id=game_data["league"].id,
            home_team_id=game_data["home_team"].id,
            away_team_id=game_data["away_team"].id,
            scheduled_at=game_data["scheduled_at"],
            status=game_data["status"],
            home_score=game_data["home_score"],
            away_score=game_data["away_score"],
            season=game_data.get("season"),
            week=game_data.get("week"),
            venue=game_data.get("venue")
        )
        session.add(game)


async def seed_ticket_providers_and_deals(session: AsyncSession, teams: list):
    """Seed ticket providers and sample deals"""
    print("Seeding ticket providers and deals...")

    # Ticket providers
    providers_data = [
        {
            "name": "StubHub",
            "website": "https://www.stubhub.com",
            "description": "StubHub ticket marketplace"
        },
        {
            "name": "Ticketmaster",
            "website": "https://www.ticketmaster.com",
            "description": "Official Ticketmaster tickets"
        },
        {
            "name": "SeatGeek",
            "website": "https://seatgeek.com",
            "description": "SeatGeek ticket platform"
        }
    ]

    providers = []
    for provider_data in providers_data:
        provider = TicketProvider(
            name=provider_data["name"],
            website=provider_data["website"],
            is_active=True
        )
        providers.append(provider)
        session.add(provider)

    await session.flush()

    # Sample ticket deals
    lakers = next((t for t in teams if t.name == "Lakers"), None)
    if lakers and providers:
        deals_data = [
            {
                "provider": providers[0],
                "team": lakers,
                "section": "Section 100",
                "price": Decimal("150.00"),
                "quantity": 2,
                "deal_score": Decimal("0.85")
            },
            {
                "provider": providers[1],
                "team": lakers,
                "section": "Section 200",
                "price": Decimal("89.00"),
                "quantity": 4,
                "deal_score": Decimal("0.92")
            }
        ]

        for deal_data in deals_data:
            deal = TicketDeal(
                provider_id=deal_data["provider"].id,
                team_id=deal_data["team"].id,
                section=deal_data["section"],
                price=deal_data["price"],
                quantity=deal_data["quantity"],
                deal_score=deal_data["deal_score"],
                valid_until=datetime.now() + timedelta(days=30),
                is_active=True
            )
            session.add(deal)


async def seed_fan_experiences(session: AsyncSession, teams: list):
    """Seed sample fan experiences"""
    print("Seeding fan experiences...")

    lakers = next((t for t in teams if t.name == "Lakers"), None)
    patriots = next((t for t in teams if t.name == "Patriots"), None)

    experiences_data = []

    if lakers:
        experiences_data.extend([
            {
                "team": lakers,
                "title": "Lakers Watch Party",
                "description": "Join fellow Lakers fans for the big game!",
                "experience_type": ExperienceType.WATCH_PARTY,
                "start_time": datetime.now() + timedelta(days=3, hours=19),
                "location": "Downtown Sports Bar",
                "organizer": "Lakers Fan Club",
                "max_attendees": 50,
                "current_attendees": 12
            }
        ])

    if patriots:
        experiences_data.extend([
            {
                "team": patriots,
                "title": "Patriots Tailgate",
                "description": "Pre-game tailgate party in the parking lot",
                "experience_type": ExperienceType.TAILGATE,
                "start_time": datetime.now() + timedelta(days=7, hours=11),
                "location": "Gillette Stadium Lot 1",
                "organizer": "Pats Nation",
                "max_attendees": 100,
                "current_attendees": 35
            }
        ])

    for exp_data in experiences_data:
        experience = FanExperience(
            team_id=exp_data["team"].id,
            title=exp_data["title"],
            description=exp_data["description"],
            experience_type=exp_data["experience_type"],
            start_time=exp_data["start_time"],
            location=exp_data["location"],
            organizer=exp_data["organizer"],
            max_attendees=exp_data["max_attendees"],
            current_attendees=exp_data["current_attendees"],
            is_active=True
        )
        session.add(experience)


async def main():
    """Run all seed operations"""
    print("Starting database seeding...")

    async with get_async_session() as session:
        try:
            # Seed in dependency order
            sports_data = await seed_sports_and_leagues(session)
            teams = await seed_teams(session, sports_data)
            await seed_feed_sources(session, sports_data, teams)
            await seed_test_users(session, sports_data, teams)
            await seed_sample_content(session, sports_data, teams)
            await seed_sample_games(session, sports_data, teams)
            await seed_ticket_providers_and_deals(session, teams)
            await seed_fan_experiences(session, teams)

            await session.commit()
            print("✅ Database seeding completed successfully!")

        except Exception as e:
            await session.rollback()
            print(f"❌ Error during seeding: {str(e)}")
            raise


if __name__ == "__main__":
    asyncio.run(main())