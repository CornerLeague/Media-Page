"""Database configuration and connection management for Corner League Media."""

import os
from contextlib import contextmanager
from typing import Generator, Optional
from urllib.parse import urlparse

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from .models.base import Base


class DatabaseConfig:
    """Database configuration class."""

    def __init__(self):
        self.database_url = self._get_database_url()
        self.test_database_url = self._get_test_database_url()
        self.echo = os.getenv('DATABASE_ECHO', 'false').lower() == 'true'
        self.pool_size = int(os.getenv('DATABASE_POOL_SIZE', '10'))
        self.max_overflow = int(os.getenv('DATABASE_MAX_OVERFLOW', '20'))
        self.pool_timeout = int(os.getenv('DATABASE_POOL_TIMEOUT', '30'))
        self.pool_recycle = int(os.getenv('DATABASE_POOL_RECYCLE', '3600'))

    def _get_database_url(self) -> str:
        """Get database URL from environment variables."""
        # Try Supabase URL first
        supabase_url = os.getenv('SUPABASE_DATABASE_URL')
        if supabase_url:
            return supabase_url

        # Try individual Supabase components
        host = os.getenv('SUPABASE_DB_HOST')
        password = os.getenv('SUPABASE_DB_PASSWORD')
        name = os.getenv('SUPABASE_DB_NAME')

        if host and password and name:
            user = os.getenv('SUPABASE_DB_USER', 'postgres')
            port = os.getenv('SUPABASE_DB_PORT', '5432')
            return f"postgresql://{user}:{password}@{host}:{port}/{name}"

        # Fallback to regular PostgreSQL
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            return database_url

        # Development fallback
        return "postgresql://postgres:postgres@localhost:5432/sportsdb"

    def _get_test_database_url(self) -> str:
        """Get test database URL."""
        test_url = os.getenv('TEST_DATABASE_URL')
        if test_url:
            return test_url

        # Use main database URL but change database name
        main_url = self.database_url
        parsed = urlparse(main_url)

        # Change database name to add _test suffix
        db_name = parsed.path.lstrip('/')
        test_db_name = f"{db_name}_test"

        return main_url.replace(f"/{db_name}", f"/{test_db_name}")

    @property
    def is_supabase(self) -> bool:
        """Check if using Supabase database."""
        return 'supabase' in self.database_url.lower()

    @property
    def is_local(self) -> bool:
        """Check if using local database."""
        return 'localhost' in self.database_url or '127.0.0.1' in self.database_url


# Global configuration instance
config = DatabaseConfig()


def create_database_engine(url: Optional[str] = None, **kwargs) -> Engine:
    """Create database engine with optimized settings."""
    database_url = url or config.database_url

    # Base engine arguments
    engine_args = {
        'echo': config.echo,
        'pool_pre_ping': True,  # Verify connections before use
        'pool_recycle': config.pool_recycle,
        **kwargs
    }

    # Connection pool settings (not for SQLite)
    if not database_url.startswith('sqlite'):
        engine_args.update({
            'pool_size': config.pool_size,
            'max_overflow': config.max_overflow,
            'pool_timeout': config.pool_timeout,
        })
    else:
        # SQLite-specific settings for testing
        engine_args.update({
            'poolclass': StaticPool,
            'connect_args': {'check_same_thread': False}
        })

    engine = create_engine(database_url, **engine_args)

    # Add connection event listeners
    _add_connection_listeners(engine)

    return engine


def _add_connection_listeners(engine: Engine) -> None:
    """Add connection event listeners for optimization."""

    @event.listens_for(engine, "connect")
    def set_postgresql_search_path(dbapi_connection, connection_record):
        """Set PostgreSQL search path and other optimizations."""
        if 'postgresql' in str(engine.url):
            with dbapi_connection.cursor() as cursor:
                # Set search path
                cursor.execute("SET search_path TO public")

                # Enable query plan optimization
                cursor.execute("SET random_page_cost = 1.1")
                cursor.execute("SET effective_cache_size = '1GB'")

                # Enable parallel queries (if supported)
                cursor.execute("SET max_parallel_workers_per_gather = 2")

    @event.listens_for(engine, "first_connect")
    def receive_first_connect(dbapi_connection, connection_record):
        """Handle first connection setup."""
        print(f"First database connection established to: {engine.url.host}")


# Global engine and session factory
engine = create_database_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Get database session with automatic cleanup."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_session_sync() -> Session:
    """Get database session (synchronous, manual management)."""
    return SessionLocal()


def init_database(drop_all: bool = False) -> None:
    """Initialize database tables."""
    if drop_all:
        print("Dropping all database tables...")
        Base.metadata.drop_all(bind=engine)

    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


def check_database_connection() -> bool:
    """Check if database connection is working."""
    try:
        with get_session() as session:
            result = session.execute(text("SELECT 1")).scalar()
            return result == 1
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False


def get_database_info() -> dict:
    """Get database connection information."""
    with get_session() as session:
        # Get PostgreSQL version
        try:
            version_result = session.execute(text("SELECT version()")).scalar()
            postgres_version = version_result.split()[1] if version_result else "Unknown"
        except Exception:
            postgres_version = "Unknown"

        # Get database name
        try:
            db_name = session.execute(text("SELECT current_database()")).scalar()
        except Exception:
            db_name = "Unknown"

        # Get current user
        try:
            current_user = session.execute(text("SELECT current_user")).scalar()
        except Exception:
            current_user = "Unknown"

        # Check extensions
        try:
            extensions_result = session.execute(
                text("SELECT extname FROM pg_extension ORDER BY extname")
            ).fetchall()
            extensions = [row[0] for row in extensions_result]
        except Exception:
            extensions = []

        return {
            'database_url': config.database_url,
            'database_name': db_name,
            'postgres_version': postgres_version,
            'current_user': current_user,
            'is_supabase': config.is_supabase,
            'is_local': config.is_local,
            'extensions': extensions,
            'pool_size': config.pool_size,
            'max_overflow': config.max_overflow,
        }


def reset_database() -> None:
    """Reset database (drop and recreate all tables)."""
    print("Resetting database...")
    init_database(drop_all=True)

    # Load seed data if available
    try:
        from .seed_data.load_teams import load_all_teams
        print("Loading seed data...")
        results = load_all_teams()
        print(f"Loaded teams: {results}")
    except ImportError:
        print("Seed data loader not available")
    except Exception as e:
        print(f"Error loading seed data: {e}")


def create_test_engine() -> Engine:
    """Create engine for testing."""
    return create_database_engine(config.test_database_url)


def setup_test_database() -> None:
    """Setup test database."""
    test_engine = create_test_engine()
    Base.metadata.create_all(bind=test_engine)


# Health check function
def health_check() -> dict:
    """Perform database health check."""
    try:
        with get_session() as session:
            # Basic connection test
            session.execute(text("SELECT 1"))

            # Test table existence
            tables_result = session.execute(
                text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
                """)
            ).fetchall()

            tables = [row[0] for row in tables_result]

            # Test indexes
            indexes_result = session.execute(
                text("""
                SELECT schemaname, indexname, tablename
                FROM pg_indexes
                WHERE schemaname = 'public'
                ORDER BY tablename, indexname
                """)
            ).fetchall()

            indexes = len(indexes_result)

            return {
                'status': 'healthy',
                'connection': True,
                'tables_count': len(tables),
                'tables': tables,
                'indexes_count': indexes,
                'timestamp': session.execute(text("SELECT NOW()")).scalar().isoformat()
            }

    except Exception as e:
        return {
            'status': 'unhealthy',
            'connection': False,
            'error': str(e),
            'timestamp': None
        }