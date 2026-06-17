from pathlib import Path
import os

from sqlalchemy import create_engine
from sqlalchemy import inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker


DEFAULT_DB_PATH = Path(__file__).with_name("healthy_lab.db")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def create_db_and_tables():
    Base.metadata.create_all(bind=engine)
    if DATABASE_URL.startswith("sqlite"):
        with engine.begin() as connection:
            inspector = inspect(connection)
            if "order_items" in inspector.get_table_names():
                columns = {column["name"] for column in inspector.get_columns("order_items")}
                if "product_id" not in columns:
                    connection.execute(text("ALTER TABLE order_items ADD COLUMN product_id INTEGER"))


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
