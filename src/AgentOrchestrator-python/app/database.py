"""SQLite engine and session helpers.

Mirrors ``AgentHQDemo.Api/Data/RetailDbContext.cs``. Where .NET registers a
``DbContext`` per request through DI, here a module-level engine is created once
and a fresh ``Session`` is yielded per request.
"""

from collections.abc import Iterator

from sqlmodel import Session, SQLModel, create_engine

# Same on-disk file the .NET version uses: "Data Source=retail.db".
DATABASE_URL = "sqlite:///retail.db"

engine = create_engine(DATABASE_URL, echo=False)


def create_db_and_tables() -> None:
    """Equivalent of ``db.Database.EnsureCreatedAsync()``."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    """FastAPI dependency yielding a database session."""
    with Session(engine) as session:
        yield session
