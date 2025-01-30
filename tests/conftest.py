import time
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers
from sqlalchemy.exc import OperationalError
from orm import mapper_registry, start_mappers
from src.config import get_postgres_test_url

def wait_for_postgres_to_come_up(engine):
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            return engine.connect()
        except OperationalError:
            time.sleep(0.5)
    pytest.fail("Postgres never came up")

@pytest.fixture(scope="session")
def postgres_db():
    engine = create_engine(get_postgres_test_url())
    wait_for_postgres_to_come_up(engine)
    mapper_registry.metadata.create_all(engine)
    return engine

@pytest.fixture
def session_factory(postgres_db):
    start_mappers()
    yield sessionmaker(bind=postgres_db)
    clear_mappers()

@pytest.fixture
def session(session_factory):
    session = session_factory()
    yield session
    session.close()
    # Clean up tables after tests
    engine = session.get_bind()
    mapper_registry.metadata.drop_all(engine)
    mapper_registry.metadata.create_all(engine)


