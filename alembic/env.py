from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import AsyncEngine
from alembic import context
import asyncio
import os
import sys

# Добавляем путь к приложению
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.db import Base
from app.models import user, session, npc  # импорт моделей
from app.core.config import settings

config = context.config
fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Используем URL из настроек
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = AsyncEngine(
        engine_from_config(
            config.get_section(config.config_ini_section),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
            future=True,
        )
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
