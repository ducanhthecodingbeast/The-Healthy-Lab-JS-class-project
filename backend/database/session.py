from pathlib import Path
import os

from sqlalchemy import create_engine
from sqlalchemy import inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker


DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "healthy_lab.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def create_db_and_tables():
    from database import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    apply_startup_schema_patches()


# This project uses create_all for lightweight local SQLite deployments; keep
# startup patches additive and idempotent instead of introducing Alembic here.
SQLITE_SCHEMA_PATCHES = {
    "order_items": [
        ("product_id", "ALTER TABLE order_items ADD COLUMN product_id INTEGER"),
        ("custom_data", "ALTER TABLE order_items ADD COLUMN custom_data TEXT"),
    ],
}


def apply_startup_schema_patches():
    if not DATABASE_URL.startswith("sqlite"):
        return

    with engine.begin() as connection:
        inspector = inspect(connection)
        table_names = set(inspector.get_table_names())
        for table_name, patches in SQLITE_SCHEMA_PATCHES.items():
            if table_name not in table_names:
                continue
            column_names = {column["name"] for column in inspector.get_columns(table_name)}
            for column_name, statement in patches:
                if column_name not in column_names:
                    connection.execute(text(statement))
                    column_names.add(column_name)


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
