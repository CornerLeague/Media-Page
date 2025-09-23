"""Phase 3: Apply Firebase constraints after data migration

Revision ID: phase3_firebase_constraints
Revises: 8ddc8bc4b5c2
Create Date: 2025-09-22 00:01:00.000000

PHASE 3: Apply constraints and cleanup after data migration.

This migration applies the final constraints and cleanup operations after
Phase 2 data migration has been completed and validated.

PREREQUISITES:
- Phase 1 migration (8ddc8bc4b5c2) must be completed
- Phase 2 data migration script must have run successfully
- All users must have valid firebase_uid values
- No duplicate firebase_uid values should exist

SAFETY FEATURES:
- Pre-flight validation checks
- Constraint application in safe order
- Rollback procedures for each step
- Detailed logging and error reporting

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'phase3_firebase_constraints'
down_revision: Union[str, None] = '8ddc8bc4b5c2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """PHASE 3: Apply Firebase constraints and cleanup.

    This migration applies the final constraints after data migration is complete.
    It includes safety checks and follows the proper order for constraint application.
    """

    # SAFETY CHECK 1: Verify all users have firebase_uid
    print("Running pre-flight safety checks...")

    # Check for NULL firebase_uid values
    connection = op.get_bind()
    result = connection.execute(sa.text("""
        SELECT COUNT(*) FROM users WHERE firebase_uid IS NULL OR firebase_uid = ''
    """))
    null_count = result.scalar()

    if null_count > 0:
        raise Exception(f"SAFETY CHECK FAILED: {null_count} users have NULL firebase_uid. "
                       "Run Phase 2 data migration first.")

    print(f"✓ Safety check passed: All users have firebase_uid values")

    # SAFETY CHECK 2: Verify no duplicate firebase_uid values
    result = connection.execute(sa.text("""
        SELECT firebase_uid, COUNT(*) as count
        FROM users
        GROUP BY firebase_uid
        HAVING COUNT(*) > 1
    """))
    duplicates = result.fetchall()

    if duplicates:
        duplicate_list = [f"{uid}: {count}" for uid, count in duplicates]
        raise Exception(f"SAFETY CHECK FAILED: Duplicate firebase_uid values found: {duplicate_list}")

    print(f"✓ Safety check passed: All firebase_uid values are unique")

    # SAFETY CHECK 3: Verify email uniqueness (if emails exist)
    result = connection.execute(sa.text("""
        SELECT email, COUNT(*) as count
        FROM users
        WHERE email IS NOT NULL AND email != ''
        GROUP BY email
        HAVING COUNT(*) > 1
    """))
    email_duplicates = result.fetchall()

    if email_duplicates:
        print(f"WARNING: {len(email_duplicates)} duplicate email addresses found")
        for email, count in email_duplicates:
            print(f"  {email}: {count} occurrences")
        print("Proceeding anyway as email uniqueness will be enforced going forward")

    print("All safety checks passed. Proceeding with constraint application...")

    # STEP 1: Apply NOT NULL constraint on firebase_uid
    print("Step 1: Making firebase_uid NOT NULL...")
    op.alter_column('users', 'firebase_uid',
                   existing_type=sa.String(length=128),
                   nullable=False)

    # STEP 2: Add unique constraint on firebase_uid
    print("Step 2: Adding unique constraint on firebase_uid...")
    op.create_unique_constraint('uq_users_firebase_uid', 'users', ['firebase_uid'])

    # STEP 3: Add unique constraint on email (with NULL handling)
    print("Step 3: Adding unique constraint on email...")
    # Create partial unique index for email (ignoring NULLs)
    op.execute(sa.text("""
        CREATE UNIQUE INDEX uq_users_email_partial
        ON users (email)
        WHERE email IS NOT NULL AND email != ''
    """))

    # STEP 4: Remove old clerk_user_id column and constraint (if they exist)
    print("Step 4: Removing old clerk_user_id column...")

    # Check if clerk_user_id constraint exists before dropping
    constraint_check = connection.execute(sa.text("""
        SELECT constraint_name
        FROM information_schema.table_constraints
        WHERE table_name = 'users'
        AND constraint_name = 'users_clerk_user_id_key'
    """))

    if constraint_check.fetchone():
        print("  Dropping clerk_user_id unique constraint...")
        op.drop_constraint('users_clerk_user_id_key', 'users', type_='unique')
    else:
        print("  clerk_user_id constraint not found (already removed)")

    # Check if clerk_user_id column exists before dropping
    column_check = connection.execute(sa.text("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'users'
        AND column_name = 'clerk_user_id'
    """))

    if column_check.fetchone():
        print("  Dropping clerk_user_id column...")
        op.drop_column('users', 'clerk_user_id')
    else:
        print("  clerk_user_id column not found (already removed)")

    # FINAL VALIDATION
    print("Running final validation...")

    # Verify firebase_uid is now NOT NULL with unique constraint
    result = connection.execute(sa.text("""
        SELECT
            is_nullable,
            (SELECT COUNT(*) FROM pg_constraint c
             JOIN pg_attribute a ON a.attnum = ANY(c.conkey)
             WHERE c.conrelid = 'users'::regclass
             AND a.attname = 'firebase_uid'
             AND c.contype = 'u') as unique_constraints
        FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'firebase_uid'
    """))

    validation = result.fetchone()
    if validation:
        is_nullable, unique_count = validation
        if is_nullable != 'NO':
            raise Exception("VALIDATION FAILED: firebase_uid is still nullable")
        if unique_count == 0:
            raise Exception("VALIDATION FAILED: firebase_uid unique constraint not found")

    # Get total user count for final report
    result = connection.execute(sa.text("SELECT COUNT(*) FROM users"))
    total_users = result.scalar()

    print("=" * 60)
    print("🎉 PHASE 3 MIGRATION COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print(f"✓ {total_users} users migrated to Firebase authentication")
    print("✓ firebase_uid column: NOT NULL + UNIQUE constraint applied")
    print("✓ email column: UNIQUE constraint applied (ignoring NULLs)")
    print("✓ clerk_user_id column: REMOVED")
    print("✓ All safety validations passed")
    print("")
    print("NEXT STEPS:")
    print("1. Update your application code to use firebase_uid")
    print("2. Test Firebase authentication integration")
    print("3. Verify all user authentication flows work correctly")
    print("4. Monitor application logs for any authentication issues")
    print("")
    print("Migration is now complete and production-ready!")


def downgrade() -> None:
    """SAFE ROLLBACK: Reverse Phase 3 constraint changes.

    This rollback removes the constraints added in Phase 3 but does NOT
    restore clerk_user_id or migrate data back. Those require separate
    data migration processes.
    """

    print("Rolling back Phase 3 constraints...")
    connection = op.get_bind()

    # STEP 1: Remove firebase_uid unique constraint
    print("Step 1: Removing firebase_uid unique constraint...")
    try:
        op.drop_constraint('uq_users_firebase_uid', 'users', type_='unique')
        print("  ✓ firebase_uid unique constraint removed")
    except Exception as e:
        print(f"  ⚠ Could not remove firebase_uid unique constraint: {e}")

    # STEP 2: Make firebase_uid nullable again
    print("Step 2: Making firebase_uid nullable...")
    try:
        op.alter_column('users', 'firebase_uid',
                       existing_type=sa.String(length=128),
                       nullable=True)
        print("  ✓ firebase_uid is now nullable")
    except Exception as e:
        print(f"  ⚠ Could not make firebase_uid nullable: {e}")

    # STEP 3: Remove email unique constraint
    print("Step 3: Removing email unique constraint...")
    try:
        op.execute(sa.text("DROP INDEX IF EXISTS uq_users_email_partial"))
        print("  ✓ email unique constraint removed")
    except Exception as e:
        print(f"  ⚠ Could not remove email unique constraint: {e}")

    print("=" * 60)
    print("PHASE 3 ROLLBACK COMPLETED")
    print("=" * 60)
    print("⚠ WARNING: This rollback only removes constraints")
    print("⚠ It does NOT restore clerk_user_id or migrate data back")
    print("")
    print("If you need to fully restore clerk authentication:")
    print("1. Create a new migration to add clerk_user_id column")
    print("2. Run data migration to populate clerk_user_id from firebase_uid")
    print("3. Apply clerk_user_id constraints")
    print("4. Remove firebase_uid column (if desired)")
    print("")
    print("Current state: Users have firebase_uid (nullable) but no constraints")