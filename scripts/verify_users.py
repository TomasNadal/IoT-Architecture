from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config import get_postgres_uri
from src.adapters.orm import start_mappers

def verify_users():
    # Initialize SQLAlchemy mappers
    start_mappers()
    
    # Setup database connection
    engine = create_engine(get_postgres_uri())
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Query all users
        from src.domain.model import User
        users = session.query(User).all()
        
        print("\nExisting users:")
        for user in users:
            print(f"""
User:
- Email: {user.email}
- Role: {user.role}
- Permissions: {user.permissions}
            """)
    except Exception as e:
        print(f"Error querying users: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    verify_users() 