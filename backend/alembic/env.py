from __future__ import annotations
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os, sys

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(BASE_DIR)

from app.db.base import Base  # noqa
from app.models.client import Client  # noqa
from app.models.session import ChatSession  # noqa
from app.models.event import ChatEvent  # noqa

config = context.config
fileConfig(config.config_file_name)

def run_migrations_offline():
    url = os.environ["APP_SQLALCHEMY_DATABASE_URI"]
    context.configure(url=url, target_metadata=Base.metadata, literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        url=os.environ["APP_SQLALCHEMY_DATABASE_URI"],
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=Base.metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()