"""College Football Phase 4: Recruiting and Transfer Portal Seed Data

Revision ID: college_football_phase4_seed
Revises: college_football_phase4
Create Date: 2025-09-21 21:05:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text
import uuid
from datetime import date, datetime

# revision identifiers, used by Alembic.
revision = 'college_football_phase4_seed'
down_revision = 'college_football_phase4'
branch_labels = None
depends_on = None


def upgrade():
    # Get database connection
    connection = op.get_bind()

    # Sample recruiting classes for major programs
    recruiting_classes_data = [
        # Alabama 2024 Recruiting Class
        {
            'id': str(uuid.uuid4()),
            'team_name': 'Alabama',
            'class_year': 2024,
            'name': 'Alabama Crimson Tide Class of 2024',
            'early_signing_period_commits': 18,
            'regular_signing_period_commits': 5,
            'late_period_commits': 2,
            'full_scholarships_used': 22,
            'partial_scholarships_used': 2.5,
            'total_scholarship_count': 24.5,
            'offensive_line_commits': 3,
            'quarterback_commits': 1,
            'running_back_commits': 2,
            'wide_receiver_commits': 4,
            'tight_end_commits': 1,
            'defensive_line_commits': 4,
            'linebacker_commits': 3,
            'defensive_back_commits': 5,
            'special_teams_commits': 1,
            'in_state_commits': 8,
            'out_of_state_commits': 17,
            'international_commits': 0,
            'transfer_additions': 3,
            'graduate_transfer_additions': 1,
            'national_ranking': 1,
            'conference_ranking': 1,
            'class_rating': 325.87,
            'average_star_rating': 4.24,
            'five_star_commits': 6,
            'four_star_commits': 15,
            'three_star_commits': 4,
            'two_star_commits': 0,
            'unrated_commits': 0,
            'top_100_commits': 12,
            'top_300_commits': 20,
            'is_complete': True,
            'early_enrollees': 8,
            'decommitments': 2,
            'signings_not_qualified': 0,
            'class_notes': 'Elite recruiting class featuring multiple 5-star prospects across all position groups.'
        },
        # Georgia 2024 Recruiting Class
        {
            'id': str(uuid.uuid4()),
            'team_name': 'Georgia',
            'class_year': 2024,
            'name': 'Georgia Bulldogs Class of 2024',
            'early_signing_period_commits': 17,
            'regular_signing_period_commits': 6,
            'late_period_commits': 1,
            'full_scholarships_used': 21,
            'partial_scholarships_used': 2.0,
            'total_scholarship_count': 23.0,
            'offensive_line_commits': 4,
            'quarterback_commits': 1,
            'running_back_commits': 1,
            'wide_receiver_commits': 3,
            'tight_end_commits': 2,
            'defensive_line_commits': 3,
            'linebacker_commits': 2,
            'defensive_back_commits': 6,
            'special_teams_commits': 1,
            'in_state_commits': 12,
            'out_of_state_commits': 12,
            'international_commits': 0,
            'transfer_additions': 2,
            'graduate_transfer_additions': 0,
            'national_ranking': 2,
            'conference_ranking': 2,
            'class_rating': 318.45,
            'average_star_rating': 4.17,
            'five_star_commits': 4,
            'four_star_commits': 16,
            'three_star_commits': 4,
            'two_star_commits': 0,
            'unrated_commits': 0,
            'top_100_commits': 10,
            'top_300_commits': 18,
            'is_complete': True,
            'early_enrollees': 6,
            'decommitments': 1,
            'signings_not_qualified': 0,
            'class_notes': 'Strong in-state recruiting with excellent defensive back haul.'
        },
        # Ohio State 2024 Recruiting Class
        {
            'id': str(uuid.uuid4()),
            'team_name': 'Ohio State',
            'class_year': 2024,
            'name': 'Ohio State Buckeyes Class of 2024',
            'early_signing_period_commits': 16,
            'regular_signing_period_commits': 5,
            'late_period_commits': 1,
            'full_scholarships_used': 20,
            'partial_scholarships_used': 1.5,
            'total_scholarship_count': 21.5,
            'offensive_line_commits': 3,
            'quarterback_commits': 1,
            'running_back_commits': 2,
            'wide_receiver_commits': 4,
            'tight_end_commits': 1,
            'defensive_line_commits': 3,
            'linebacker_commits': 2,
            'defensive_back_commits': 4,
            'special_teams_commits': 1,
            'in_state_commits': 6,
            'out_of_state_commits': 16,
            'international_commits': 0,
            'transfer_additions': 4,
            'graduate_transfer_additions': 1,
            'national_ranking': 3,
            'conference_ranking': 1,
            'class_rating': 305.22,
            'average_star_rating': 4.09,
            'five_star_commits': 3,
            'four_star_commits': 14,
            'three_star_commits': 5,
            'two_star_commits': 0,
            'unrated_commits': 0,
            'top_100_commits': 8,
            'top_300_commits': 16,
            'is_complete': True,
            'early_enrollees': 7,
            'decommitments': 3,
            'signings_not_qualified': 0,
            'class_notes': 'National recruiting class with strong offensive line and receiver groups.'
        }
    ]

    # Sample individual recruits
    recruits_data = [
        # Alabama recruits
        {
            'id': str(uuid.uuid4()),
            'team_name': 'Alabama',
            'first_name': 'Caleb',
            'last_name': 'Downs',
            'full_name': 'Caleb Downs',
            'high_school': 'Mill Creek High School',
            'high_school_city': 'Hoschton',
            'high_school_state': 'Georgia',
            'graduation_year': 2024,
            'primary_position': 'S',
            'position_group': 'DEFENSIVE_BACK',
            'height_inches': 72,
            'weight_pounds': 185,
            'star_rating': '5_star',
            'national_ranking': 4,
            'position_ranking': 1,
            'state_ranking': 1,
            'commitment_status': 'signed',
            'commitment_date': date(2023, 12, 20),
            'signing_date': date(2023, 12, 20),
            'is_early_enrollee': True,
            'early_enrollment_date': date(2024, 1, 8),
            'scholarship_offered': True,
            'scholarship_type': 'FULL_SCHOLARSHIP',
            'total_offers': 25,
            'recruiting_notes': 'Elite safety prospect with exceptional coverage skills and football IQ.'
        },
        {
            'id': str(uuid.uuid4()),
            'team_name': 'Alabama',
            'first_name': 'Ryan',
            'last_name': 'Williams',
            'full_name': 'Ryan Williams',
            'high_school': 'Saraland High School',
            'high_school_city': 'Saraland',
            'high_school_state': 'Alabama',
            'graduation_year': 2024,
            'primary_position': 'WR',
            'position_group': 'RECEIVER',
            'height_inches': 70,
            'weight_pounds': 175,
            'star_rating': '5_star',
            'national_ranking': 2,
            'position_ranking': 1,
            'state_ranking': 1,
            'commitment_status': 'signed',
            'commitment_date': date(2023, 6, 15),
            'signing_date': date(2023, 12, 20),
            'is_early_enrollee': True,
            'early_enrollment_date': date(2024, 1, 8),
            'scholarship_offered': True,
            'scholarship_type': 'FULL_SCHOLARSHIP',
            'total_offers': 30,
            'recruiting_notes': 'Dynamic receiver with exceptional speed and route-running ability.'
        },
        # Georgia recruits
        {
            'id': str(uuid.uuid4()),
            'team_name': 'Georgia',
            'first_name': 'Dylan',
            'last_name': 'Raiola',
            'full_name': 'Dylan Raiola',
            'high_school': 'Buford High School',
            'high_school_city': 'Buford',
            'high_school_state': 'Georgia',
            'graduation_year': 2024,
            'primary_position': 'QB',
            'position_group': 'QUARTERBACK',
            'height_inches': 75,
            'weight_pounds': 220,
            'star_rating': '5_star',
            'national_ranking': 1,
            'position_ranking': 1,
            'state_ranking': 1,
            'commitment_status': 'decommitted',
            'commitment_date': date(2022, 5, 20),
            'last_decommitment_date': date(2023, 12, 10),
            'decommitment_count': 1,
            'is_early_enrollee': False,
            'scholarship_offered': True,
            'scholarship_type': 'FULL_SCHOLARSHIP',
            'total_offers': 35,
            'recruiting_notes': 'Elite quarterback prospect who decommitted late in process.'
        },
        # Ohio State recruits
        {
            'id': str(uuid.uuid4()),
            'team_name': 'Ohio State',
            'first_name': 'Jeremiah',
            'last_name': 'Smith',
            'full_name': 'Jeremiah Smith',
            'high_school': 'Chaminade-Madonna College Prep',
            'high_school_city': 'Hollywood',
            'high_school_state': 'Florida',
            'graduation_year': 2024,
            'primary_position': 'WR',
            'position_group': 'RECEIVER',
            'height_inches': 74,
            'weight_pounds': 185,
            'star_rating': '5_star',
            'national_ranking': 3,
            'position_ranking': 2,
            'state_ranking': 1,
            'commitment_status': 'signed',
            'commitment_date': date(2023, 7, 1),
            'signing_date': date(2023, 12, 20),
            'is_early_enrollee': True,
            'early_enrollment_date': date(2024, 1, 8),
            'scholarship_offered': True,
            'scholarship_type': 'FULL_SCHOLARSHIP',
            'total_offers': 28,
            'recruiting_notes': 'Elite receiver with great size and athletic ability.'
        }
    ]

    # Sample transfer portal entries
    transfer_portal_data = [
        {
            'id': str(uuid.uuid4()),
            'previous_team_name': 'USC',
            'first_name': 'Caleb',
            'last_name': 'Williams',
            'full_name': 'Caleb Williams',
            'previous_college_name': 'University of Southern California',
            'portal_entry_date': date(2024, 1, 15),
            'portal_entry_reason': 'coaching_staff_change',
            'is_graduate_transfer': False,
            'primary_position': 'QB',
            'position_group': 'QUARTERBACK',
            'current_class': 'JUNIOR',
            'years_of_eligibility_remaining': 2,
            'height_inches': 73,
            'weight_pounds': 215,
            'years_at_previous_school': 2,
            'transfer_status': 'enrolled',
            'immediate_eligibility': True,
            'sit_out_required': False,
            'coaching_change_factor': True,
            'playing_time_factor': False,
            'academic_factor': False,
            'family_factor': False,
            'transfer_notes': 'Entered portal following coaching change at USC.'
        },
        {
            'id': str(uuid.uuid4()),
            'previous_team_name': 'Alabama',
            'first_name': 'Jalen',
            'last_name': 'Hurts',
            'full_name': 'Jalen Hurts',
            'previous_college_name': 'University of Alabama',
            'portal_entry_date': date(2019, 1, 20),
            'portal_entry_reason': 'lack_of_playing_time',
            'is_graduate_transfer': True,
            'primary_position': 'QB',
            'position_group': 'QUARTERBACK',
            'current_class': 'GRADUATE',
            'years_of_eligibility_remaining': 1,
            'height_inches': 73,
            'weight_pounds': 218,
            'years_at_previous_school': 3,
            'new_team_name': 'Oklahoma',
            'commitment_date': date(2019, 1, 25),
            'enrollment_date': date(2019, 8, 20),
            'transfer_status': 'enrolled',
            'immediate_eligibility': True,
            'sit_out_required': False,
            'playing_time_factor': True,
            'coaching_change_factor': False,
            'academic_factor': False,
            'family_factor': False,
            'transfer_notes': 'Graduate transfer seeking starting opportunity.'
        }
    ]

    # Sample coaching staff
    coaching_staff_data = [
        # Alabama coaching staff
        {
            'id': str(uuid.uuid4()),
            'team_name': 'Alabama',
            'first_name': 'Nick',
            'last_name': 'Saban',
            'full_name': 'Nick Saban',
            'coaching_position': 'head_coach',
            'coaching_level': 'head_coach',
            'hire_date': date(2007, 1, 3),
            'start_date': date(2007, 1, 3),
            'contract_status': 'retired',
            'annual_salary': 11700000.00,
            'contract_length_years': 8,
            'college_coaching_years': 28,
            'nfl_coaching_years': 5,
            'alma_mater': 'Kent State University',
            'degree': 'Business',
            'primary_recruiting_region': 'Southeast',
            'recruiting_rating': 10,
            'coaching_rating': 10,
            'is_active': False,
            'termination_date': date(2024, 1, 10),
            'termination_reason': 'Retirement',
            'coaching_notes': 'Legendary coach with 7 national championships.'
        },
        {
            'id': str(uuid.uuid4()),
            'team_name': 'Alabama',
            'first_name': 'Kalen',
            'last_name': 'DeBoer',
            'full_name': 'Kalen DeBoer',
            'coaching_position': 'head_coach',
            'coaching_level': 'head_coach',
            'hire_date': date(2024, 1, 12),
            'start_date': date(2024, 1, 12),
            'contract_status': 'active',
            'annual_salary': 10250000.00,
            'contract_length_years': 6,
            'college_coaching_years': 15,
            'nfl_coaching_years': 0,
            'alma_mater': 'University of Sioux Falls',
            'degree': 'Physical Education',
            'primary_recruiting_region': 'National',
            'recruiting_rating': 8,
            'coaching_rating': 9,
            'is_active': True,
            'coaching_notes': 'Former Washington head coach, known for offensive innovation.'
        },
        # Georgia coaching staff
        {
            'id': str(uuid.uuid4()),
            'team_name': 'Georgia',
            'first_name': 'Kirby',
            'last_name': 'Smart',
            'full_name': 'Kirby Smart',
            'coaching_position': 'head_coach',
            'coaching_level': 'head_coach',
            'hire_date': date(2015, 12, 6),
            'start_date': date(2016, 1, 1),
            'contract_status': 'active',
            'annual_salary': 11250000.00,
            'contract_length_years': 10,
            'college_coaching_years': 20,
            'nfl_coaching_years': 0,
            'alma_mater': 'University of Georgia',
            'degree': 'Finance',
            'primary_recruiting_region': 'Southeast',
            'recruiting_rating': 10,
            'coaching_rating': 9,
            'is_active': True,
            'coaching_notes': 'Former Alabama DC, won national championship in 2021.'
        }
    ]

    # Sample NIL deals
    nil_deals_data = [
        {
            'id': str(uuid.uuid4()),
            'player_name': 'Caleb Williams',
            'deal_name': 'Gatorade Partnership',
            'deal_type': 'endorsement',
            'nil_category': 'traditional_advertising',
            'partner_name': 'Gatorade',
            'partner_type': 'Corporation',
            'partner_location': 'Chicago, IL',
            'deal_value': 500000.00,
            'payment_structure': 'Annual',
            'payment_amount': 500000.00,
            'payment_frequency': 'annual',
            'deal_date': date(2023, 8, 15),
            'effective_date': date(2023, 8, 15),
            'expiration_date': date(2024, 8, 15),
            'deal_duration_months': 12,
            'compliance_status': 'approved',
            'school_approval_required': True,
            'school_approval_date': date(2023, 8, 10),
            'ncaa_reporting_required': True,
            'reporting_date': date(2023, 8, 16),
            'nil_collective_involved': False,
            'booster_involvement': False,
            'deal_status': 'active',
            'public_announcement': True,
            'announcement_date': date(2023, 8, 20),
            'deal_notes': 'Multi-year endorsement deal with performance bonuses.'
        },
        {
            'id': str(uuid.uuid4()),
            'player_name': 'Ryan Williams',
            'deal_name': 'Local Car Dealership',
            'deal_type': 'appearance',
            'nil_category': 'personal_appearances',
            'partner_name': 'Tuscaloosa Toyota',
            'partner_type': 'Local Business',
            'partner_location': 'Tuscaloosa, AL',
            'deal_value': 25000.00,
            'payment_structure': 'Per appearance',
            'payment_amount': 5000.00,
            'payment_frequency': 'per_event',
            'deal_date': date(2024, 2, 1),
            'effective_date': date(2024, 2, 1),
            'expiration_date': date(2024, 12, 31),
            'deal_duration_months': 11,
            'compliance_status': 'approved',
            'school_approval_required': True,
            'school_approval_date': date(2024, 1, 28),
            'ncaa_reporting_required': True,
            'reporting_date': date(2024, 2, 2),
            'nil_collective_involved': False,
            'booster_involvement': False,
            'deal_status': 'active',
            'public_announcement': False,
            'deal_notes': 'Local dealership appearances and social media posts.'
        }
    ]

    # Insert recruiting classes
    for class_data in recruiting_classes_data:
        # Get team_id and academic_year_id
        team_result = connection.execute(text("""
            SELECT ft.id as team_id, ay.id as academic_year_id
            FROM football_teams ft
            JOIN college_teams ct ON ft.college_team_id = ct.id
            JOIN colleges c ON ct.college_id = c.id
            JOIN academic_years ay ON ay.name = '2023-24'
            WHERE c.name LIKE :team_name
            LIMIT 1
        """), {'team_name': f"%{class_data['team_name']}%"}).fetchone()

        if team_result:
            connection.execute(text("""
                INSERT INTO football_recruiting_classes (
                    id, created_at, updated_at, team_id, academic_year_id,
                    class_year, name, early_signing_period_commits, regular_signing_period_commits,
                    late_period_commits, full_scholarships_used, partial_scholarships_used,
                    total_scholarship_count, offensive_line_commits, quarterback_commits,
                    running_back_commits, wide_receiver_commits, tight_end_commits,
                    defensive_line_commits, linebacker_commits, defensive_back_commits,
                    special_teams_commits, in_state_commits, out_of_state_commits,
                    international_commits, transfer_additions, graduate_transfer_additions,
                    national_ranking, conference_ranking, class_rating, average_star_rating,
                    five_star_commits, four_star_commits, three_star_commits, two_star_commits,
                    unrated_commits, top_100_commits, top_300_commits, is_complete,
                    early_enrollees, decommitments, signings_not_qualified, class_notes
                ) VALUES (
                    :id, :created_at, :updated_at, :team_id, :academic_year_id,
                    :class_year, :name, :early_signing_period_commits, :regular_signing_period_commits,
                    :late_period_commits, :full_scholarships_used, :partial_scholarships_used,
                    :total_scholarship_count, :offensive_line_commits, :quarterback_commits,
                    :running_back_commits, :wide_receiver_commits, :tight_end_commits,
                    :defensive_line_commits, :linebacker_commits, :defensive_back_commits,
                    :special_teams_commits, :in_state_commits, :out_of_state_commits,
                    :international_commits, :transfer_additions, :graduate_transfer_additions,
                    :national_ranking, :conference_ranking, :class_rating, :average_star_rating,
                    :five_star_commits, :four_star_commits, :three_star_commits, :two_star_commits,
                    :unrated_commits, :top_100_commits, :top_300_commits, :is_complete,
                    :early_enrollees, :decommitments, :signings_not_qualified, :class_notes
                )
            """), {
                **class_data,
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'team_id': team_result.team_id,
                'academic_year_id': team_result.academic_year_id
            })

    # Insert individual recruits
    for recruit_data in recruits_data:
        # Get recruiting_class_id and committed_to_team_id
        class_result = connection.execute(text("""
            SELECT frc.id as recruiting_class_id, ft.id as team_id
            FROM football_recruiting_classes frc
            JOIN football_teams ft ON frc.team_id = ft.id
            JOIN college_teams ct ON ft.college_team_id = ct.id
            JOIN colleges c ON ct.college_id = c.id
            WHERE c.name LIKE :team_name AND frc.class_year = :graduation_year
            LIMIT 1
        """), {
            'team_name': f"%{recruit_data['team_name']}%",
            'graduation_year': recruit_data['graduation_year']
        }).fetchone()

        if class_result:
            connection.execute(text("""
                INSERT INTO football_recruits (
                    id, created_at, updated_at, recruiting_class_id, first_name, last_name,
                    full_name, high_school, high_school_city, high_school_state,
                    graduation_year, primary_position, position_group, height_inches,
                    weight_pounds, star_rating, national_ranking, position_ranking,
                    state_ranking, commitment_status, committed_to_team_id, commitment_date,
                    signing_date, is_early_enrollee, early_enrollment_date, decommitment_count,
                    last_decommitment_date, scholarship_offered, scholarship_type, total_offers,
                    recruiting_notes
                ) VALUES (
                    :id, :created_at, :updated_at, :recruiting_class_id, :first_name, :last_name,
                    :full_name, :high_school, :high_school_city, :high_school_state,
                    :graduation_year, :primary_position, :position_group, :height_inches,
                    :weight_pounds, :star_rating, :national_ranking, :position_ranking,
                    :state_ranking, :commitment_status, :committed_to_team_id, :commitment_date,
                    :signing_date, :is_early_enrollee, :early_enrollment_date, :decommitment_count,
                    :last_decommitment_date, :scholarship_offered, :scholarship_type, :total_offers,
                    :recruiting_notes
                )
            """), {
                **{k: v for k, v in recruit_data.items() if k != 'team_name'},
                'id': recruit_data['id'],
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'recruiting_class_id': class_result.recruiting_class_id,
                'committed_to_team_id': class_result.team_id if recruit_data['commitment_status'] in ['committed', 'signed'] else None,
                'decommitment_count': recruit_data.get('decommitment_count', 0),
                'last_decommitment_date': recruit_data.get('last_decommitment_date'),
                'early_enrollment_date': recruit_data.get('early_enrollment_date')
            })

    # Insert transfer portal entries
    for transfer_data in transfer_portal_data:
        # Get previous_team_id and new_team_id
        previous_team_result = connection.execute(text("""
            SELECT ft.id as team_id
            FROM football_teams ft
            JOIN college_teams ct ON ft.college_team_id = ct.id
            JOIN colleges c ON ct.college_id = c.id
            WHERE c.name LIKE :team_name
            LIMIT 1
        """), {'team_name': f"%{transfer_data['previous_team_name']}%"}).fetchone()

        new_team_id = None
        if 'new_team_name' in transfer_data:
            new_team_result = connection.execute(text("""
                SELECT ft.id as team_id
                FROM football_teams ft
                JOIN college_teams ct ON ft.college_team_id = ct.id
                JOIN colleges c ON ct.college_id = c.id
                WHERE c.name LIKE :team_name
                LIMIT 1
            """), {'team_name': f"%{transfer_data['new_team_name']}%"}).fetchone()
            if new_team_result:
                new_team_id = new_team_result.team_id

        if previous_team_result:
            connection.execute(text("""
                INSERT INTO football_transfer_portal_entries (
                    id, created_at, updated_at, first_name, last_name, full_name,
                    previous_team_id, previous_college_name, portal_entry_date,
                    portal_entry_reason, is_graduate_transfer, primary_position,
                    position_group, current_class, years_of_eligibility_remaining,
                    height_inches, weight_pounds, years_at_previous_school,
                    new_team_id, commitment_date, enrollment_date, transfer_status,
                    immediate_eligibility, sit_out_required, coaching_change_factor,
                    playing_time_factor, academic_factor, family_factor, transfer_notes
                ) VALUES (
                    :id, :created_at, :updated_at, :first_name, :last_name, :full_name,
                    :previous_team_id, :previous_college_name, :portal_entry_date,
                    :portal_entry_reason, :is_graduate_transfer, :primary_position,
                    :position_group, :current_class, :years_of_eligibility_remaining,
                    :height_inches, :weight_pounds, :years_at_previous_school,
                    :new_team_id, :commitment_date, :enrollment_date, :transfer_status,
                    :immediate_eligibility, :sit_out_required, :coaching_change_factor,
                    :playing_time_factor, :academic_factor, :family_factor, :transfer_notes
                )
            """), {
                **{k: v for k, v in transfer_data.items() if k not in ['previous_team_name', 'new_team_name']},
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'previous_team_id': previous_team_result.team_id,
                'new_team_id': new_team_id,
                'commitment_date': transfer_data.get('commitment_date'),
                'enrollment_date': transfer_data.get('enrollment_date')
            })

    # Insert coaching staff
    for coach_data in coaching_staff_data:
        # Get team_id and academic_year_id
        team_result = connection.execute(text("""
            SELECT ft.id as team_id, ay.id as academic_year_id
            FROM football_teams ft
            JOIN college_teams ct ON ft.college_team_id = ct.id
            JOIN colleges c ON ct.college_id = c.id
            JOIN academic_years ay ON ay.name = '2023-24'
            WHERE c.name LIKE :team_name
            LIMIT 1
        """), {'team_name': f"%{coach_data['team_name']}%"}).fetchone()

        if team_result:
            connection.execute(text("""
                INSERT INTO football_coaching_staff (
                    id, created_at, updated_at, team_id, academic_year_id,
                    first_name, last_name, full_name, coaching_position, coaching_level,
                    hire_date, start_date, contract_status, annual_salary, contract_length_years,
                    college_coaching_years, nfl_coaching_years, alma_mater, degree,
                    primary_recruiting_region, recruiting_rating, coaching_rating,
                    is_active, termination_date, termination_reason, coaching_notes
                ) VALUES (
                    :id, :created_at, :updated_at, :team_id, :academic_year_id,
                    :first_name, :last_name, :full_name, :coaching_position, :coaching_level,
                    :hire_date, :start_date, :contract_status, :annual_salary, :contract_length_years,
                    :college_coaching_years, :nfl_coaching_years, :alma_mater, :degree,
                    :primary_recruiting_region, :recruiting_rating, :coaching_rating,
                    :is_active, :termination_date, :termination_reason, :coaching_notes
                )
            """), {
                **{k: v for k, v in coach_data.items() if k != 'team_name'},
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'team_id': team_result.team_id,
                'academic_year_id': team_result.academic_year_id,
                'termination_date': coach_data.get('termination_date'),
                'termination_reason': coach_data.get('termination_reason')
            })

    # Insert NIL deals
    for nil_data in nil_deals_data:
        # Get player_id from football_players based on name
        player_result = connection.execute(text("""
            SELECT id FROM football_players
            WHERE full_name = :player_name
            LIMIT 1
        """), {'player_name': nil_data['player_name']}).fetchone()

        if player_result:
            connection.execute(text("""
                INSERT INTO football_nil_deals (
                    id, created_at, updated_at, player_id, deal_name, deal_type,
                    nil_category, partner_name, partner_type, partner_location,
                    deal_value, payment_structure, payment_amount, payment_frequency,
                    deal_date, effective_date, expiration_date, deal_duration_months,
                    compliance_status, school_approval_required, school_approval_date,
                    ncaa_reporting_required, reporting_date, nil_collective_involved,
                    booster_involvement, deal_status, public_announcement,
                    announcement_date, deal_notes
                ) VALUES (
                    :id, :created_at, :updated_at, :player_id, :deal_name, :deal_type,
                    :nil_category, :partner_name, :partner_type, :partner_location,
                    :deal_value, :payment_structure, :payment_amount, :payment_frequency,
                    :deal_date, :effective_date, :expiration_date, :deal_duration_months,
                    :compliance_status, :school_approval_required, :school_approval_date,
                    :ncaa_reporting_required, :reporting_date, :nil_collective_involved,
                    :booster_involvement, :deal_status, :public_announcement,
                    :announcement_date, :deal_notes
                )
            """), {
                **{k: v for k, v in nil_data.items() if k != 'player_name'},
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'player_id': player_result.id,
                'school_approval_date': nil_data.get('school_approval_date'),
                'reporting_date': nil_data.get('reporting_date'),
                'announcement_date': nil_data.get('announcement_date')
            })


def downgrade():
    # Remove seed data in reverse order
    connection = op.get_bind()

    # Remove NIL deals
    connection.execute(text("DELETE FROM football_nil_deals"))

    # Remove coaching staff
    connection.execute(text("DELETE FROM football_coaching_staff"))

    # Remove transfer portal entries
    connection.execute(text("DELETE FROM football_transfer_portal_entries"))

    # Remove recruiting visits
    connection.execute(text("DELETE FROM football_recruiting_visits"))

    # Remove recruiting offers
    connection.execute(text("DELETE FROM football_recruiting_offers"))

    # Remove recruits
    connection.execute(text("DELETE FROM football_recruits"))

    # Remove recruiting classes
    connection.execute(text("DELETE FROM football_recruiting_classes"))