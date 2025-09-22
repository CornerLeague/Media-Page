#!/usr/bin/env python3
"""
Phase 2 Academic Framework Usage Examples
Demonstrates how to use the new academic year, season, and conference membership models
"""

from datetime import date
from models.college import (
    AcademicYear, Season, ConferenceMembership, SeasonConfiguration,
    College, CollegeConference
)
from models.enums import (
    SeasonType, AcademicYearStatus, ConferenceStatus, ConferenceMembershipType
)


def example_academic_year_management(session):
    """Example: Managing academic years"""
    print("📅 Academic Year Management Example")

    # Get current academic year
    current_year = session.query(AcademicYear).filter(
        AcademicYear.status == AcademicYearStatus.CURRENT
    ).first()

    print(f"Current academic year: {current_year.name}")
    print(f"Display format: {current_year.display_years}")
    print(f"Is current: {current_year.is_current}")
    print(f"Season count: {len(current_year.seasons)}")

    # Get all future academic years for planning
    future_years = session.query(AcademicYear).filter(
        AcademicYear.status == AcademicYearStatus.FUTURE
    ).order_by(AcademicYear.start_year).all()

    print(f"Future years planned: {[y.name for y in future_years]}")


def example_season_management(session):
    """Example: Working with seasons"""
    print("\n🏀 Season Management Example")

    # Get current active season
    current_season = session.query(Season).filter(
        Season.is_current == True
    ).first()

    print(f"Current season: {current_season.display_name}")
    print(f"Type: {current_season.season_type}")
    print(f"Dates: {current_season.start_date} to {current_season.end_date}")

    if current_season.max_regular_season_games:
        print(f"Max games allowed: {current_season.max_regular_season_games}")

    if current_season.selection_sunday:
        print(f"Selection Sunday: {current_season.selection_sunday}")

    # Get all seasons for current academic year
    academic_year = current_season.academic_year
    seasons_by_type = {}

    for season in academic_year.seasons:
        seasons_by_type[season.season_type] = season

    print(f"Available season types: {list(seasons_by_type.keys())}")


def example_conference_realignment(session):
    """Example: Tracking conference realignment"""
    print("\n🔄 Conference Realignment Example")

    # Find a college for this example (would be real data in production)
    college = session.query(College).first()
    if not college:
        print("No college data available for example")
        return

    print(f"College: {college.name}")

    # Get current conference membership
    current_membership = session.query(ConferenceMembership).filter(
        ConferenceMembership.college_id == college.id,
        ConferenceMembership.status == ConferenceStatus.ACTIVE,
        ConferenceMembership.end_date.is_(None)
    ).first()

    if current_membership:
        print(f"Current conference: {current_membership.conference.name}")
        print(f"Membership type: {current_membership.membership_type}")
        print(f"Member since: {current_membership.start_date}")
        print(f"Is active: {current_membership.is_active}")

        if current_membership.duration_days:
            print(f"Duration: {current_membership.duration_days} days")

    # Get conference history
    all_memberships = session.query(ConferenceMembership).filter(
        ConferenceMembership.college_id == college.id
    ).order_by(ConferenceMembership.start_date.desc()).all()

    print(f"Conference history ({len(all_memberships)} memberships):")
    for membership in all_memberships:
        status_text = f"({membership.status})"
        date_range = f"{membership.start_date}"
        if membership.end_date:
            date_range += f" to {membership.end_date}"
        else:
            date_range += " to present"

        print(f"  • {membership.conference.name} {status_text}: {date_range}")


def example_season_configuration(session):
    """Example: Managing season configurations"""
    print("\n⚙️ Season Configuration Example")

    # Get current season
    current_season = session.query(Season).filter(
        Season.is_current == True
    ).first()

    if not current_season:
        print("No current season available for example")
        return

    # Get all configurations for current season
    configs = session.query(SeasonConfiguration).filter(
        SeasonConfiguration.season_id == current_season.id,
        SeasonConfiguration.is_active == True
    ).all()

    print(f"Active configurations for {current_season.name}:")

    for config in configs:
        scope = "Global" if config.conference_id is None else f"Conference: {config.conference.name}"
        print(f"  • {config.setting_key} ({scope})")
        print(f"    Value: {config.setting_value} (type: {config.setting_type})")
        print(f"    Parsed: {config.parsed_value}")
        if config.description:
            print(f"    Description: {config.description}")
        print()


def example_queries_and_analytics(session):
    """Example: Common queries and analytics"""
    print("\n📊 Queries and Analytics Examples")

    # Count seasons by type across all academic years
    from sqlalchemy import func

    season_counts = session.query(
        Season.season_type,
        func.count(Season.id).label('count')
    ).group_by(Season.season_type).all()

    print("Season types across all academic years:")
    for season_type, count in season_counts:
        print(f"  • {season_type}: {count} seasons")

    # Find colleges with conference changes
    colleges_with_changes = session.query(College).join(
        ConferenceMembership
    ).group_by(College.id).having(
        func.count(ConferenceMembership.id) > 1
    ).all()

    print(f"\nColleges with conference changes: {len(colleges_with_changes)}")

    # Academic years with the most seasons
    ay_season_counts = session.query(
        AcademicYear.name,
        func.count(Season.id).label('season_count')
    ).join(Season).group_by(
        AcademicYear.id, AcademicYear.name
    ).order_by(
        func.count(Season.id).desc()
    ).all()

    print("\nAcademic years by season count:")
    for ay_name, count in ay_season_counts:
        print(f"  • {ay_name}: {count} seasons")


def example_conference_membership_workflow(session):
    """Example: Complete conference membership workflow"""
    print("\n🔄 Conference Membership Workflow Example")

    # This would be used when a college announces a conference change
    # Example: Moving from Conference A to Conference B

    college = session.query(College).first()
    if not college:
        print("No college data available for workflow example")
        return

    print(f"Workflow for: {college.name}")

    # Step 1: Announcement phase
    # (College announces they're leaving current conference)

    # Step 2: Update current membership status
    current_membership = session.query(ConferenceMembership).filter(
        ConferenceMembership.college_id == college.id,
        ConferenceMembership.status == ConferenceStatus.ACTIVE
    ).first()

    if current_membership:
        print(f"Current membership: {current_membership.conference.name}")

        # Mark as departing (would happen when announced)
        # current_membership.status = ConferenceStatus.DEPARTING
        # current_membership.end_date = date(2025, 6, 30)  # End of academic year

        print("Status would be updated to 'departing'")

    # Step 3: Create new membership record
    # (When new conference is announced)

    print("New membership record would be created:")
    print("  • Status: 'joining'")
    print("  • Start date: Beginning of next academic year")
    print("  • Announced date: Today")

    # Example of what the new record would look like:
    """
    new_conference = session.query(CollegeConference).filter(
        CollegeConference.id != current_membership.conference_id
    ).first()

    next_academic_year = session.query(AcademicYear).filter(
        AcademicYear.status == AcademicYearStatus.FUTURE
    ).order_by(AcademicYear.start_year).first()

    new_membership = ConferenceMembership(
        college_id=college.id,
        conference_id=new_conference.id,
        academic_year_id=next_academic_year.id,
        membership_type=ConferenceMembershipType.FULL_MEMBER,
        status=ConferenceStatus.JOINING,
        start_date=next_academic_year.start_date,
        announced_date=date.today(),
        is_primary_sport=True,
        notes="Conference realignment move announced"
    )
    """


def main():
    """Main example runner"""
    print("🚀 Phase 2 Academic Framework Usage Examples")
    print("=" * 60)

    # Note: In a real application, you would have a proper database session
    # This is just showing the structure and methods available

    print("These examples show how to use the Phase 2 models:")
    print("• Academic year management and queries")
    print("• Season tracking and current season detection")
    print("• Conference realignment tracking")
    print("• Season configuration management")
    print("• Common analytics queries")
    print("• Conference membership workflows")

    print("\n⚠️  Note: These examples require an active database session")
    print("with Phase 2 data populated. Run the migration first:")
    print("   alembic upgrade head")


if __name__ == "__main__":
    main()