from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session, sessionmaker

from src.core.config import get_settings


settings = get_settings()
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
REQUIRED_SCHEMA_TABLES = ("assets", "audit_log", "monitoring_states")


def get_db_session() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_ready() -> bool:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def check_database_schema_ready(required_tables: tuple[str, ...] = REQUIRED_SCHEMA_TABLES) -> bool:
    try:
        inspector = inspect(engine)
        return all(inspector.has_table(table_name) for table_name in required_tables)
    except Exception:
        return False
