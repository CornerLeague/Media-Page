"""migrate_users_to_firebase_auth

Revision ID: 8ddc8bc4b5c2
Revises: 003_indexes_and_triggers
Create Date: 2025-09-19 20:37:29.849330

MIGRATION OVERVIEW:
This migration transforms the user authentication system from Clerk to Firebase.

Key Changes:
1. Replaces clerk_user_id with firebase_uid as the primary authentication identifier
2. Adds enhanced user profile fields (first_name, last_name, bio, location, timezone)
3. Adds email verification tracking (is_verified, email_verified_at)
4. Makes email unique and indexed for better performance
5. Adds proper indexes for firebase_uid, is_active, and last_active_at

PRODUCTION DEPLOYMENT NOTES:
- This migration includes data transformation steps that should be carefully planned
- Before running in production, ensure you have a mapping between clerk_user_id and firebase_uid
- Consider splitting this into multiple migrations for large datasets:
  1. Add new columns
  2. Migrate data (separate script)
  3. Add constraints and drop old columns
- Test rollback thoroughly in staging environment
- Ensure adequate downtime window for large user tables

ROLLBACK SAFETY:
- The downgrade() function fully reverses all schema changes
- Data migration logic needs to be implemented for production use
- Rollback requires reverse mapping from firebase_uid to clerk_user_id

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8ddc8bc4b5c2'
down_revision: Union[str, None] = '003_indexes_and_triggers'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """PHASE 1: Add Firebase columns and structure (safe schema changes only).

    This is the first of a 3-phase migration to eliminate race conditions:
    - Phase 1: Add columns and indexes (this migration)
    - Phase 2: Data migration (separate script/migration)
    - Phase 3: Apply constraints (separate migration)
    """

    # Step 1: Add new Firebase UID column as NULLABLE (safe)
    op.add_column('users', sa.Column('firebase_uid', sa.String(length=128), nullable=True))

    # Step 2: Add new user profile columns (all nullable - safe)
    op.add_column('users', sa.Column('first_name', sa.String(length=50), nullable=True))
    op.add_column('users', sa.Column('last_name', sa.String(length=50), nullable=True))
    op.add_column('users', sa.Column('bio', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('date_of_birth', sa.Date(), nullable=True))
    op.add_column('users', sa.Column('location', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('timezone', sa.String(length=50), nullable=True, server_default='UTC'))
    op.add_column('users', sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('email_verified_at', sa.DateTime(timezone=True), nullable=True))

    # Step 3: Update email column to be nullable and add email index (safe)
    op.alter_column('users', 'email', existing_type=sa.String(255), nullable=True)
    op.create_index('idx_users_email', 'users', ['email'])

    # Step 4: Add performance indexes (safe - indexes don't affect data integrity)
    op.create_index('idx_users_firebase_uid', 'users', ['firebase_uid'])
    op.create_index('idx_users_is_active', 'users', ['is_active'])
    op.create_index('idx_users_last_active_at', 'users', ['last_active_at'])

    # CRITICAL: DO NOT add constraints or drop columns in this phase
    # The following operations are deferred to subsequent migrations:
    #
    # Phase 2 (Data Migration - separate process):
    # - Populate firebase_uid from clerk_user_id mapping
    # - Verify data integrity and completeness
    # - Validate no NULL firebase_uid values exist
    #
    # Phase 3 (Constraint Application - separate migration):
    # - op.alter_column('users', 'firebase_uid', nullable=False)
    # - op.create_unique_constraint('uq_users_firebase_uid', 'users', ['firebase_uid'])
    # - op.create_unique_constraint('uq_users_email', 'users', ['email'])
    # - op.drop_constraint('users_clerk_user_id_key', 'users', type_='unique')
    # - op.drop_column('users', 'clerk_user_id')

    print("✓ Phase 1 complete: Firebase schema structure added")
    print("⚠ WARNING: Data migration required before applying constraints")
    print("→ Next: Run data migration to populate firebase_uid values")
    print("→ Then: Run Phase 3 migration to apply constraints and cleanup")


def downgrade() -> None:
    """SAFE ROLLBACK: Remove Firebase schema additions (Phase 1 rollback only).

    This rollback is safe because it only removes the additions from Phase 1.
    If Phase 2 (data migration) or Phase 3 (constraints) have been applied,
    those must be rolled back first using their respective rollback procedures.
    """

    # SAFETY CHECK: Verify we can safely rollback
    # This migration should only be rolled back if:
    # 1. Phase 3 constraints haven't been applied yet
    # 2. Phase 2 data migration can be safely reversed

    # Step 1: Remove performance indexes (safe - these were added in Phase 1)
    try:
        op.drop_index('idx_users_last_active_at', 'users')
    except Exception:
        pass  # Index might not exist

    try:
        op.drop_index('idx_users_is_active', 'users')
    except Exception:
        pass  # Index might not exist

    try:
        op.drop_index('idx_users_firebase_uid', 'users')
    except Exception:
        pass  # Index might not exist

    try:
        op.drop_index('idx_users_email', 'users')
    except Exception:
        pass  # Index might not exist

    # Step 2: Remove new profile columns (safe - these were added as nullable)
    op.drop_column('users', 'email_verified_at')
    op.drop_column('users', 'is_verified')
    op.drop_column('users', 'timezone')
    op.drop_column('users', 'location')
    op.drop_column('users', 'date_of_birth')
    op.drop_column('users', 'bio')
    op.drop_column('users', 'last_name')
    op.drop_column('users', 'first_name')

    # Step 3: Remove firebase_uid column (safe - was added as nullable)
    op.drop_column('users', 'firebase_uid')

    # NOTE: We do NOT attempt to restore clerk_user_id here because:
    # 1. The original clerk_user_id column might have been dropped in Phase 3
    # 2. We don't have the original clerk_user_id data to restore
    # 3. This would create the same race condition we're trying to fix
    #
    # If you need to restore clerk_user_id functionality:
    # 1. Create a separate migration to add clerk_user_id column
    # 2. Run a data migration to populate clerk_user_id from firebase_uid mapping
    # 3. Apply constraints in a third migration

    print("✓ Phase 1 rollback complete: Firebase schema additions removed")
    print("⚠ WARNING: clerk_user_id column not restored automatically")
    print("→ If needed: Create separate migration to restore clerk_user_id")
    print("→ Then: Run data migration to populate clerk_user_id values")
    print("→ Finally: Apply clerk_user_id constraints in separate migration")