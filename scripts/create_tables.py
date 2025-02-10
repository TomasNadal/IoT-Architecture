from sqlalchemy import create_engine
from src.adapters.orm import mapper_registry, start_mappers
from src.config import get_postgres_uri

def create_tables():
    engine = create_engine(get_postgres_uri())
    start_mappers()  # Need to call this first to register all mappings
    mapper_registry.metadata.create_all(bind=engine)
    print("Tables created successfully!")

if __name__ == "__main__":
    create_tables() 