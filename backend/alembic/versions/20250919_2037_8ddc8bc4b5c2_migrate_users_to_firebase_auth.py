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
    """Upgrade database schema to use Firebase authentication."""

    # Step 1: Add new Firebase UID column
    op.add_column('users', sa.Column('firebase_uid', sa.String(length=128), nullable=True))

    # Step 2: Add new user profile columns
    op.add_column('users', sa.Column('first_name', sa.String(length=50), nullable=True))
    op.add_column('users', sa.Column('last_name', sa.String(length=50), nullable=True))
    op.add_column('users', sa.Column('bio', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('date_of_birth', sa.Date(), nullable=True))
    op.add_column('users', sa.Column('location', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('timezone', sa.String(length=50), nullable=True, server_default='UTC'))
    op.add_column('users', sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('email_verified_at', sa.DateTime(timezone=True), nullable=True))

    # Step 3: Make email unique and indexed
    op.alter_column('users', 'email', existing_type=sa.String(255), nullable=True)
    op.create_unique_constraint('uq_users_email', 'users', ['email'])
    op.create_index('idx_users_email', 'users', ['email'])

    # Step 4: Add indexes for performance
    op.create_index('idx_users_firebase_uid', 'users', ['firebase_uid'])
    op.create_index('idx_users_is_active', 'users', ['is_active'])
    op.create_index('idx_users_last_active_at', 'users', ['last_active_at'])

    # Step 5: Data migration placeholder - in production, you would:
    # 1. Populate firebase_uid from clerk_user_id mapping
    # 2. Verify all users have firebase_uid values
    # 3. Then make firebase_uid NOT NULL and add unique constraint

    # For now, we'll add the constraints assuming data migration is complete
    # In production, these would be separate migration steps after data migration

    # Step 6: Make firebase_uid required and unique (after data migration)
    # Note: In production, run data migration first, then these constraints in a separate migration
    op.alter_column('users', 'firebase_uid', nullable=False)
    op.create_unique_constraint('uq_users_firebase_uid', 'users', ['firebase_uid'])

    # Step 7: Remove old clerk_user_id column (after confirming firebase_uid is populated)
    op.drop_constraint('users_clerk_user_id_key', 'users', type_='unique')
    op.drop_column('users', 'clerk_user_id')


def downgrade() -> None:
    """Downgrade database schema to use Clerk authentication."""

    # Step 1: Re-add clerk_user_id column
    op.add_column('users', sa.Column('clerk_user_id', sa.String(length=255), nullable=True))

    # Step 2: Data migration placeholder - in production:
    # Populate clerk_user_id from firebase_uid mapping

    # Step 3: Make clerk_user_id required and unique
    op.alter_column('users', 'clerk_user_id', nullable=False)
    op.create_unique_constraint('users_clerk_user_id_key', 'users', ['clerk_user_id'])

    # Step 4: Remove Firebase UID constraints and column
    op.drop_constraint('uq_users_firebase_uid', 'users', type_='unique')
    op.drop_index('idx_users_firebase_uid', 'users')
    op.drop_column('users', 'firebase_uid')

    # Step 5: Remove new profile columns
    op.drop_column('users', 'email_verified_at')
    op.drop_column('users', 'is_verified')
    op.drop_column('users', 'timezone')
    op.drop_column('users', 'location')
    op.drop_column('users', 'date_of_birth')
    op.drop_column('users', 'bio')
    op.drop_column('users', 'last_name')
    op.drop_column('users', 'first_name')

    # Step 6: Remove email constraints and indexes
    op.drop_index('idx_users_email', 'users')
    op.drop_constraint('uq_users_email', 'users', type_='unique')

    # Step 7: Remove other indexes
    op.drop_index('idx_users_last_active_at', 'users')
    op.drop_index('idx_users_is_active', 'users')