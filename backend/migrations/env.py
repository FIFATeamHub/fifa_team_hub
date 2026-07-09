import logging
from logging.config import fileConfig
import os
import sys

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from flask import current_app

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

# Get database URL from environment or config
def get_engine_url():
    # Try to get from environment first (Docker)
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        return database_url.replace('%', '%%')
    
    # Fallback: try to get from Flask app context
    try:
        from flask import current_app
        db_url = current_app.config.get('SQLALCHEMY_DATABASE_URI')
        if db_url:
            return db_url.replace('%', '%%')
    except RuntimeError:
        pass
    
    # Fallback to local development URL
    return "sqlite:///./test.db"


# Set the sqlalchemy.url before anything else tries to use it
config.set_main_option('sqlalchemy.url', get_engine_url())

# This will be set properly in run_migrations_online
target_db = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_metadata():
    """Get metadata from Flask-SQLAlchemy"""
    try:
        from flask import current_app
        return current_app.extensions['migrate'].db.metadata
    except (RuntimeError, KeyError, AttributeError):
        # Return empty metadata when not in app context
        from sqlalchemy import MetaData
        return MetaData()


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=get_metadata(), literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    from app import create_app
    
    # Create app context for this migration run
    app = create_app()
    
    with app.app_context():
        from flask import current_app
        
        # this callback is used to prevent an auto-migration from being generated
        # when there are no changes to the schema
        # reference: http://alembic.zzzcomputing.com/en/latest/cookbook.html
        def process_revision_directives(context, revision, directives):
            if getattr(config.cmd_opts, 'autogenerate', False):
                script = directives[0]
                if script.upgrade_ops.is_empty():
                    directives[:] = []
                    logger.info('No changes in schema detected.')

        conf_args = current_app.extensions['migrate'].configure_args
        if conf_args.get("process_revision_directives") is None:
            conf_args["process_revision_directives"] = process_revision_directives

        connectable = current_app.extensions['migrate'].db.engine

        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=get_metadata(),
                **conf_args
            )

            with context.begin_transaction():
                context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
