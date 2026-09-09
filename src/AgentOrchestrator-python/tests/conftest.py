"""Shared pytest fixtures."""

import pytest
from sqlalchemy import Engine
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.services.retail_analytics import RetailAnalyticsService


@pytest.fixture(name="engine")
def engine_fixture():
    """In-memory SQLite, equivalent to the .NET tests' ``DataSource=:memory:``.

    ``StaticPool`` keeps every connection pointed at the same in-memory database,
    which is what ``OpenConnection()`` achieves on the .NET side.
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture(name="session")
def session_fixture(engine: Engine):
    with Session(engine) as session:
        yield session


@pytest.fixture(name="service")
def service_fixture(session: Session) -> RetailAnalyticsService:
    return RetailAnalyticsService(session)
