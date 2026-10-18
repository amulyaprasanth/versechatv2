from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    pass


engine = create_engine(
    "sqlite:///versechat.db",
    echo=True,
)

Session = sessionmaker(
    bind=engine,
    autoflush=True,
)


def get_db():
    with Session() as session:
        yield session
