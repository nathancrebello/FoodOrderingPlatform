import asyncio
import os
import logging
from logging.config import fileConfig

from sqlalchemy import pool, text
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from app.settings import Base
# Import all models to register them against Base metadata
from app.users_app.models import *
from app.conversations_app.models import *

# Configure Alembic
config = context.config

# Setup logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)

# Database URL configuration
database_url = (
    f"postgresql+asyncpg://"
    f"{os.getenv('SQL_USER', 'voiceagent_admin')}:"
    f"{os.getenv('SQL_PASSWORD', 'voiceagent_admin_234')}@"
    f"{os.getenv('SQL_HOST', 'localhost')}:"
    f"{os.getenv('SQL_PORT', '5432')}/"
    f"{os.getenv('SQL_DATABASE', 'voiceagent')}"
)

if not database_url:
    raise ValueError("Database configuration is incomplete")

config.set_main_option("sqlalchemy.url", database_url)
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations with explicit transaction control"""
    def do_migrations():
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            transaction_per_migration=False,  # Disable per-migration transactions
            include_schemas=True,
        )
        context.run_migrations()

    # Run migrations without transaction wrapper
    do_migrations()


async def run_migrations() -> None:
    """Run migrations with async support and explicit transaction handling"""
    config_section = config.get_section(config.config_ini_section)

    connectable = async_engine_from_config(
        config_section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    try:
        async with connectable.begin() as connection:
            # Verify database connection
            await connection.execute(text("SELECT 1"))

            # Run migrations within the explicit transaction
            await connection.run_sync(do_run_migrations)

            # No explicit commit needed here as we're using 'begin()'

    except Exception as e:
        logging.error(f"Migration failed: {str(e)}")
        raise
    finally:
        await connectable.dispose()


def run_migrations_online() -> None:
    """Entry point for online migrations"""
    try:
        asyncio.run(run_migrations())
    except Exception as e:
        logging.error(f"Failed to run online migrations: {str(e)}")
        raise


if context.is_offline_mode():
    logging.info("Running offline migrations")
    run_migrations_offline()
else:
    logging.info("Running online migrations")
    run_migrations_online()
