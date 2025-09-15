"""Alembic environment configuration for Corner League Media database."""

import asyncio
import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine

from alembic import context

# Add the app directory to sys.path so we can import our models
import sys
from pathlib import Path
app_dir = Path(__file__).parent.parent.parent
sys.path.append(str(app_dir))

# Import all SQLAlchemy models for autogenerate support
from app.database.models.base import Base
from app.database.models import user, team, article, game, feed_source, analytics

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the target metadata for 'autogenerate' support
target_metadata = Base.metadata

# Configure database URL from environment
def get_database_url():
    """Get database URL from environment variables."""
    # Try Supabase first
    supabase_url = os.getenv('SUPABASE_DATABASE_URL')
    if supabase_url:
        return supabase_url

    # Fallback to regular PostgreSQL
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        return database_url

    # Development fallback
    host = os.getenv('SUPABASE_DB_HOST', 'localhost')
    password = os.getenv('SUPABASE_DB_PASSWORD', 'postgres')
    name = os.getenv('SUPABASE_DB_NAME', 'sportsdb')

    return f"postgresql://postgres:{password}@{host}:5432/{name}"

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations with database connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
        # Include object names in autogenerate comparisons
        include_object=include_object,
        # Custom compare functions for better type detection
        compare_type=compare_type,
    )

    with context.begin_transaction():
        context.run_migrations()


def include_object(object, name, type_, reflected, compare_to):
    """Filter objects to include in autogenerate."""
    # Skip certain system tables/indexes
    if type_ == "table" and name.startswith("_"):
        return False

    # Include custom types and enums
    if type_ == "type":
        return True

    return True


def compare_type(context, inspected_column, metadata_column, inspected_type, metadata_type):
    """Custom type comparison for better enum/type handling."""
    # Handle enum types
    if hasattr(metadata_type, "enums") and hasattr(inspected_type, "enums"):
        return metadata_type.enums != inspected_type.enums

    # Default comparison
    return None


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    # Override the sqlalchemy.url in the config
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_database_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        do_run_migrations(connection)


def run_async_migrations() -> None:
    """Run migrations in async mode (for async database drivers)."""
    async def run_async_migrations_inner():
        configuration = config.get_section(config.config_ini_section)
        configuration["sqlalchemy.url"] = get_database_url()

        connectable = AsyncEngine(
            engine_from_config(
                configuration,
                prefix="sqlalchemy.",
                poolclass=pool.NullPool,
            )
        )

        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)

        await connectable.dispose()

    asyncio.run(run_async_migrations_inner())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()