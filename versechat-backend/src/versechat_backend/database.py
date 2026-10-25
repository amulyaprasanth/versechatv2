import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL, make_url
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Compose injects its environment directly. These files also allow running the
# backend locally against a Postgres container during development.
load_dotenv()
load_dotenv(".env.dev")


class Base(DeclarativeBase):
    pass


def build_database_url() -> str | URL:
    explicit_url = os.getenv("DATABASE_URL")
    if explicit_url:
        return explicit_url

    password = os.getenv("POSTGRES_PASSWORD")

    if not password:
        raise RuntimeError(
            "PostgreSQL is required. Set  POSTGRES_PASSWORD, or DATABASE_URL."
        )

    return URL.create(
        drivername="postgresql+psycopg",
        username=os.getenv("POSTGRES_USER", "versechat"),
        password=password,
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        database=os.getenv("POSTGRES_DB", "versechat"),
    )


def build_langgraph_database_url() -> str:
    """Return a psycopg-compatible URL for LangGraph's Postgres checkpointer."""
    database_url = make_url(build_database_url())
    if not database_url.drivername.startswith("postgresql"):
        raise RuntimeError("The LangGraph checkpointer requires a PostgreSQL URL.")

    # LangGraph's saver uses psycopg directly, not SQLAlchemy's driver-qualified
    # URL (postgresql+psycopg://).
    return database_url.set(drivername="postgresql").render_as_string(
        hide_password=False
    )


engine = create_engine(
    build_database_url(),
    pool_pre_ping=True,
    echo=os.getenv("SQL_ECHO", "0") == "1",
)

Session = sessionmaker(
    bind=engine,
    autoflush=True,
)


def get_db():
    with Session() as session:
        yield session
