from sqlalchemy import create_engine
from src.adapters.orm import mapper_registry
from src.config import get_postgres_uri

def drop_tables():
    engine = create_engine(get_postgres_uri())
    mapper_registry.metadata.drop_all(bind=engine)
    print("Tables dropped successfully!")

if __name__ == "__main__":
    drop_tables() 