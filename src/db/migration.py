import logging
from time import sleep
from src.logging import error, debug

from alembic.config import Config
from alembic import command
from sqlalchemy import Connection

from src.db.session import engine


def run_upgrade(conn: Connection, config: Config) -> None:
    debug("upgrading database.")
    config.attributes["connection"] = conn
    command.upgrade(config, "head")


async def upgrade_db() -> None:
    """upgrade DB via 'alembic upgrade head'"""
    while True:
        async with engine.begin() as conn:
            try:
                alembic_cfg = Config("alembic.ini")
                await conn.run_sync(run_upgrade, alembic_cfg)
                break
            except Exception as e:
                error(f"failed to upgrade. {e}")
                sleep(1)

    # re-enable logging, as alembic seems to disable it ¯\_(ツ)_/¯
    for logger in logging.root.manager.loggerDict.values():
        if hasattr(logger, "disabled"):
            logger.disabled = False
